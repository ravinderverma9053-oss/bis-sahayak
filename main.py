from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Literal
from uuid import uuid4

import pymupdf
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
ROOT = Path(__file__).resolve().parent
SOURCES_PATH = ROOT / "sources.json"
SOURCES = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
SOURCE_BY_ID = {source["id"]: source for source in SOURCES}

app = FastAPI(title="BIS Sahayak prototype API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class SourceRecord(BaseModel):
    id: str
    title: str
    authority: str
    category: str
    url: str
    summary: str
    use: str
    version: str
    lastUpdated: str
    checkedOn: str
    tags: list[str]
    relatedIds: list[str]


def public_source(source: dict) -> dict:
    return {key: value for key, value in source.items() if key != "keywords"}


def extract_pdf_text(upload: UploadFile) -> tuple[str, str]:
    if upload.content_type not in {"application/pdf", "application/x-pdf"} and not (upload.filename or "").lower().endswith(".pdf"):
        return "", "Only PDF upload is available in this prototype."
    contents = upload.file.read()
    if len(contents) > 10_000_000:
        return "", "The PDF is larger than the 10 MB prototype limit."
    try:
        document = pymupdf.open(stream=contents, filetype="pdf")
        text = "\n".join(page.get_text("text") for page in document)
        document.close()
        if not text.strip():
            return "", "No selectable text found; an image-only PDF needs manual review."
        return text[:100_000], "Text extracted for readiness hints"
    except Exception:
        return "", "The file could not be read; inspect it manually before relying on any checklist."


def normalise(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def retrieve(query: str, profile: str) -> list[dict]:
    profile_sources = {
        "laptop": ["scheme-ii-registration", "products-under-compulsory-certification", "product-specific-information", "bis-lims-recognized-labs"],
        "gold": ["bis-care-app", "hallmarking-overview", "bis-lims-recognized-labs", "know-your-standards"],
        "refrigerator": ["refrigerating-appliances-guideline", "products-under-compulsory-certification", "product-specific-information", "qco-guidance"],
        "scheme-x": ["scheme-x-faq", "scheme-x-faq-april-2024", "product-specific-information", "bis-lims-recognized-labs"],
        "general": ["products-under-compulsory-certification", "product-certification-faq", "know-your-standards", "qco-guidance"],
    }
    preferred = profile_sources[profile]
    query_words = normalise(query)
    ranked: list[tuple[float, dict]] = []
    for source in SOURCES:
        source_words = normalise(" ".join([source["title"], source["summary"], " ".join(source["keywords"])]))
        score = len(query_words & source_words) / max(1, len(query_words))
        if source["id"] in preferred:
            score += 10 - preferred.index(source["id"])
        ranked.append((score, source))
    ranked.sort(key=lambda item: item[0], reverse=True)
    selected = [item[1] for item in ranked[:4]]
    return [
        {
            **{key: source[key] for key in ["id", "title", "authority", "category", "url", "summary", "version", "checkedOn"]},
            "relevance": "Primary" if index < 2 else "Supporting",
        }
        for index, source in enumerate(selected)
    ]


def classify(query: str) -> str:
    words = normalise(query)
    if words & {"gold", "jewellery", "jewelry", "huid", "hallmark", "hallmarking", "purity"}:
        return "gold"
    if words & {"laptop", "laptops", "notebook", "notebooks", "tablet", "tablets", "computer", "computers", "electronics", "adapter", "adapters", "charger", "chargers", "62368"}:
        return "laptop"
    if words & {"refrigerator", "fridge", "freezer", "refrigerating"}:
        return "refrigerator"
    if "scheme" in words and "x" in words or words & {"switchgear", "controlgear", "industrial"}:
        return "scheme-x"
    return "general"


def intent_for(query: str, profile: str) -> tuple[str, str]:
    words = normalise(query)
    if profile == "gold":
        return "Consumer verification", "Guidance for using official BIS hallmarking and verification services."
    if words & {"qco", "mandatory", "compulsory", "covered", "applicable"}:
        return "Applicability check", "A source-grounded prompt to confirm whether a current QCO or compulsory pathway applies."
    if words & {"test", "testing", "lab", "laboratory"}:
        return "Testing direction", "Guidance for finding the relevant product material and checking a laboratory’s current scope."
    if words & {"document", "application", "licence", "license", "apply"}:
        return "Application readiness", "A readiness view for the official certification or registration route."
    return "Compliance readiness", "A product-first readiness check covering standards, evidence and an official next action."


def found_state(text: str, terms: list[str]) -> Literal["Not provided", "Found in upload", "Needs verification"]:
    if not text:
        return "Not provided"
    return "Found in upload" if any(term.lower() in text.lower() for term in terms) else "Needs verification"


def document_items(profile: str, pdf_text: str) -> list[dict]:
    if profile == "gold":
        return [
            {"item": "HUID or hallmark details", "reason": "Needed for the official Verify HUID route.", "state": found_state(pdf_text, ["HUID", "hallmark"])},
            {"item": "Purchase invoice / jeweller details", "reason": "Keep the transaction evidence available if you need to raise an issue.", "state": found_state(pdf_text, ["invoice", "bill", "jeweller", "jeweler"])},
            {"item": "Assay report, if already tested", "reason": "An official test route should issue an assay report with article identification.", "state": found_state(pdf_text, ["assay report", "assaying", "test report"])},
        ]
    if profile == "scheme-x":
        return [
            {"item": "Technical file", "reason": "Scheme-X FAQ identifies a complete technical file as necessary for grant of licence.", "state": found_state(pdf_text, ["technical file"])},
            {"item": "Product compliance / test reports", "reason": "Check the current Scheme-X guidance for the acceptable evidence route.", "state": found_state(pdf_text, ["test report", "compliance report"])},
            {"item": "Product and manufacturing scope", "reason": "The official scheme scope must match the product and applicant context.", "state": found_state(pdf_text, ["manufacturer", "factory", "product model", "product description"])},
        ]
    return [
        {"item": "Exact product model and technical specification", "reason": "Needed to verify the correct product category and Indian Standard.", "state": found_state(pdf_text, ["model", "specification", "technical", "datasheet"])},
        {"item": "Current test reports and test plan", "reason": "Compare this evidence with the current product-specific guidance and applicable scheme.", "state": found_state(pdf_text, ["test report", "test plan", "laboratory"])},
        {"item": "Manufacturing and quality-control evidence", "reason": "Official certification guidance refers to manufacturing infrastructure, process controls, quality control and testing capability.", "state": found_state(pdf_text, ["quality control", "manufacturing", "factory", "process control"])},
        {"item": "Current QCO / scheme applicability record", "reason": "Coverage must be confirmed against the live official listing, scope and amendments.", "state": "Needs verification"},
    ]


def analysis_template(query: str, profile: str, pdf_text: str) -> dict:
    intent_label, intent_detail = intent_for(query, profile)
    shared_advisory = "This is an AI readiness view, not a BIS certification decision. Confirm current applicability, versions and submission requirements through official BIS processes."
    templates = {
        "laptop": {
            "product": {"name": "Laptop / notebook computer", "category": "Electronics & IT goods", "confidence": "High signal", "rationale": "Your language matched the prototype’s Laptop/Notebook/Tablets example."},
            "applicability": {"headline": "Potential Scheme-II electronics match", "detail": "The current BIS Scheme-II listing includes Laptop/Notebook/Tablets against IS/IEC 62368-1:2023. Confirm your exact product, notification scope, amendments and route directly with BIS.", "status": "Needs official confirmation"},
            "requirements": [
                {"title": "Confirm the exact product category and IS reference", "detail": "Start with the live Scheme-II listing and Know Your Standards. The prototype match is a routing hint, not a legal classification.", "evidence": "Scheme-II: Compulsory Registration Scheme"},
                {"title": "Check the current compulsory pathway", "detail": "Review the active compulsory-certification listing, applicable notifications and their amendments before committing to a compliance route.", "evidence": "Products under Compulsory Certification"},
                {"title": "Replace the readiness checklist with product-specific guidance", "detail": "Locate any product manual, Scheme of Inspection and Testing material or other product-specific guidance that applies to the confirmed product.", "evidence": "Product Specific Information"},
            ],
            "testing": [
                {"title": "Evidence planning", "detail": "Identify the current test evidence expected for the confirmed route. Do not infer a test list from a category label alone.", "evidence": "Product Specific Information"},
                {"title": "Laboratory scope", "detail": "Use the live BIS LIMS directory, then inspect the laboratory’s listed scope before contacting it.", "evidence": "BIS Recognized Labs"},
            ],
            "roadmap": [
                {"number": 1, "title": "Lock the product description", "detail": "Record model, configuration and intended market context.", "evidence": ["Your input"]},
                {"number": 2, "title": "Verify coverage", "detail": "Check the current BIS Scheme-II and compulsory listings.", "evidence": ["Scheme-II listing", "Compulsory listings"]},
                {"number": 3, "title": "Read product guidance", "detail": "Gather the current product-specific requirements and test direction.", "evidence": ["Product Specific Information"]},
                {"number": 4, "title": "Validate test capability", "detail": "Check a possible laboratory’s current scope in BIS LIMS.", "evidence": ["BIS Recognized Labs"]},
                {"number": 5, "title": "Use the official route", "detail": "Proceed only through the applicable BIS process after confirmation.", "evidence": ["Official BIS process"]},
            ],
        },
        "gold": {
            "product": {"name": "Gold jewellery / hallmark query", "category": "Consumer hallmarking", "confidence": "High signal", "rationale": "Your language matched hallmarking, gold or HUID terms."},
            "applicability": {"headline": "Use the official HUID verification route", "detail": "BIS CARE provides a Verify HUID feature for Hallmarked Jewellery. BIS Sahayak cannot verify a HUID, hallmark, purity or jeweller claim itself.", "status": "Needs official confirmation"},
            "requirements": [
                {"title": "Keep the HUID or hallmark details", "detail": "The official verification flow needs the item’s HUID. Do not treat a photograph or AI interpretation as authenticity evidence.", "evidence": "BIS Care App"},
                {"title": "Use BIS CARE for official verification", "detail": "Verify the Hallmarked Jewellery item through BIS CARE’s Verify HUID function.", "evidence": "BIS Care App"},
                {"title": "Escalate a purity concern to an official test route", "detail": "A consumer can get jewellery or a sample tested by a BIS recognized Assaying and Hallmarking Centre on a chargeable basis.", "evidence": "Hallmarking Overview"},
            ],
            "testing": [
                {"title": "Consumer assay route", "detail": "Consult a BIS recognized Assaying and Hallmarking Centre for testing; request and retain the assay report with item identification.", "evidence": "Hallmarking Overview"},
                {"title": "Verification boundary", "detail": "The readiness view provides a route only. The official app and centre determine the relevant verification outcome.", "evidence": "BIS Care App"},
            ],
            "roadmap": [
                {"number": 1, "title": "Find the HUID", "detail": "Collect the HUID and transaction details from the article or invoice.", "evidence": ["Your input"]},
                {"number": 2, "title": "Verify in BIS CARE", "detail": "Use the official Verify HUID service.", "evidence": ["BIS Care App"]},
                {"number": 3, "title": "Save the result", "detail": "Keep the official verification result with your purchase details.", "evidence": ["Consumer record"]},
                {"number": 4, "title": "Use an assay route if needed", "detail": "Locate a BIS recognized Assaying and Hallmarking Centre for a purity concern.", "evidence": ["Hallmarking Overview"]},
                {"number": 5, "title": "Follow official resolution channels", "detail": "Use the appropriate official BIS consumer service for the verified issue.", "evidence": ["BIS official services"]},
            ],
        },
        "refrigerator": {
            "product": {"name": "Refrigerating appliance", "category": "Household appliance", "confidence": "High signal", "rationale": "Your language matched the prototype’s refrigerator/freezer guidance record."},
            "applicability": {"headline": "Product-specific guidance found in the demo corpus", "detail": "The corpus includes BIS guidance for refrigerating appliances and named standards. Confirm the latest standard version, notified amendments and the current compulsory listing before acting.", "status": "Needs official confirmation"},
            "requirements": [
                {"title": "Confirm appliance type and standard", "detail": "The guidance distinguishes refrigerators, freezers and frost-free appliances. Match the exact product type before using a standard reference.", "evidence": "Guidelines for Certification of Refrigerating Appliances"},
                {"title": "Confirm current compulsory coverage", "detail": "Use the live compulsory-certification hub and the current order or amendment rather than relying on a historical guidance document alone.", "evidence": "Products under Compulsory Certification"},
                {"title": "Find product-specific documents", "detail": "Use the product-specific information hub for current manuals, testing and any relevant supporting guidance.", "evidence": "Product Specific Information"},
            ],
            "testing": [
                {"title": "Current test direction", "detail": "Derive exact tests from the confirmed current standard and associated product material, not this overview.", "evidence": "Product Specific Information"},
                {"title": "Laboratory scope", "detail": "Inspect live BIS LIMS scope records before selecting a possible laboratory.", "evidence": "BIS Recognized Labs"},
            ],
            "roadmap": [
                {"number": 1, "title": "Describe the appliance", "detail": "Record the appliance type and product configuration.", "evidence": ["Your input"]},
                {"number": 2, "title": "Confirm the current listing", "detail": "Compare it with live compulsory-certification information.", "evidence": ["BIS compulsory listings"]},
                {"number": 3, "title": "Confirm the IS version", "detail": "Check the latest standard and notified amendments.", "evidence": ["Product-specific guidance"]},
                {"number": 4, "title": "Validate test route", "detail": "Use live laboratory-scope information and official guidance.", "evidence": ["BIS LIMS"]},
                {"number": 5, "title": "Proceed through BIS", "detail": "Use the official applicable certification route.", "evidence": ["BIS process"]},
            ],
        },
        "scheme-x": {
            "product": {"name": "Industrial product / Scheme-X query", "category": "Potential Scheme-X pathway", "confidence": "Keyword signal", "rationale": "Your language contains Scheme-X or industrial-product terms."},
            "applicability": {"headline": "Possible Scheme-X route, subject to scope confirmation", "detail": "Confirm that the product falls inside current Scheme-X coverage before using the Scheme-X document or test evidence prompts below.", "status": "Needs official confirmation"},
            "requirements": [
                {"title": "Confirm Scheme-X scope first", "detail": "Scheme selection depends on the current official product listing and scope, not a keyword match.", "evidence": "Scheme-X Certification FAQ"},
                {"title": "Prepare technical evidence only after scope confirmation", "detail": "The versioned Scheme-X FAQ identifies a technical file as necessary for grant of licence under that scheme.", "evidence": "Scheme-X FAQ, Version 1 (April 2024)"},
                {"title": "Check product-specific guidance", "detail": "Use current product manuals, SIT and other product-specific information to build a final checklist.", "evidence": "Product Specific Information"},
            ],
            "testing": [
                {"title": "Product compliance evidence", "detail": "Check the current official Scheme-X guidance for allowed report sources and requirements.", "evidence": "Scheme-X FAQ, Version 1 (April 2024)"},
                {"title": "Laboratory scope", "detail": "Validate the current scope of a possible test laboratory in BIS LIMS.", "evidence": "BIS Recognized Labs"},
            ],
            "roadmap": [
                {"number": 1, "title": "Document the product", "detail": "Capture model, intended use and exact product category.", "evidence": ["Your input"]},
                {"number": 2, "title": "Confirm Scheme-X scope", "detail": "Check the current official compulsory listing.", "evidence": ["Scheme-X FAQ"]},
                {"number": 3, "title": "Assemble the technical file", "detail": "Only if Scheme-X applies, follow current official material.", "evidence": ["Versioned Scheme-X FAQ"]},
                {"number": 4, "title": "Validate test evidence", "detail": "Confirm route and lab scope through official sources.", "evidence": ["BIS LIMS"]},
                {"number": 5, "title": "Apply through BIS", "detail": "Use the official process when requirements are confirmed.", "evidence": ["Official BIS process"]},
            ],
        },
        "general": {
            "product": {"name": "Product / compliance query", "category": "Needs product qualification", "confidence": "Open query", "rationale": "The prototype needs a product name, model or clearer context to narrow the source match."},
            "applicability": {"headline": "Potential BIS coverage requires a product match", "detail": "Certification is generally voluntary, while specified products can fall under mandatory compliance through a current QCO or other applicable route. Use the official listing to verify your specific product.", "status": "Needs official confirmation"},
            "requirements": [
                {"title": "Define the product precisely", "detail": "Record the product name, model, category, intended use and manufacturing or import context before looking for an IS number.", "evidence": "Your input + Know Your Standards"},
                {"title": "Search the official standard and product listing", "detail": "Use Know Your Standards and the current compulsory-certification pages; a keyword result is only a starting point.", "evidence": "Know Your Standards"},
                {"title": "Check whether a current QCO applies", "detail": "Compare the product with the live official listing, QCO scope, commencement date, amendments and any exemption that may matter.", "evidence": "Guidance Document on Quality Control Orders"},
            ],
            "testing": [
                {"title": "Requirements before a test plan", "detail": "Locate current product-specific material before deciding tests, samples or equipment.", "evidence": "Product Specific Information"},
                {"title": "Possible laboratories", "detail": "Use the live BIS LIMS directory and inspect a laboratory’s individual scope.", "evidence": "BIS Recognized Labs"},
            ],
            "roadmap": [
                {"number": 1, "title": "Clarify the product", "detail": "Capture model, intended use and market context.", "evidence": ["Your input"]},
                {"number": 2, "title": "Find the standard", "detail": "Search the official BIS standards service.", "evidence": ["Know Your Standards"]},
                {"number": 3, "title": "Check official coverage", "detail": "Review the current product and QCO listings.", "evidence": ["Compulsory certification", "QCO guidance"]},
                {"number": 4, "title": "Build verified evidence", "detail": "Read current product-specific requirements and test direction.", "evidence": ["Product Specific Information"]},
                {"number": 5, "title": "Use the official process", "detail": "Proceed only through the confirmed BIS route.", "evidence": ["BIS official process"]},
            ],
        },
    }
    selected = templates[profile]
    return {
        "requestId": f"BIS-{date.today().strftime('%y%m%d')}-{uuid4().hex[:5].upper()}",
        "product": selected["product"],
        "intent": {"label": intent_label, "detail": intent_detail},
        "advisory": shared_advisory,
        "applicability": selected["applicability"],
        "requirements": selected["requirements"],
        "testing": selected["testing"],
        "documents": document_items(profile, pdf_text),
        "roadmap": selected["roadmap"],
        "sources": retrieve(query, profile),
        "corpus": {"count": len(SOURCES), "version": "BIS-SAHAYAK/0.1", "retrievalMode": "Curated hybrid match"},
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "corpusSources": len(SOURCES), "mode": "curated prototype"}


@app.get("/api/sources")
def list_sources() -> list[SourceRecord]:
    return [SourceRecord(**public_source(source)) for source in SOURCES]


@app.get("/api/sources/{source_id}")
def get_source(source_id: str) -> SourceRecord:
    source = SOURCE_BY_ID.get(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source record not found")
    return SourceRecord(**public_source(source))


@app.post("/api/analyze")
def analyze(query: str = Form(""), file: UploadFile | None = File(None)) -> dict:
    pdf_text = ""
    upload = None
    if file is not None and file.filename:
        pdf_text, status = extract_pdf_text(file)
        upload = {"name": file.filename, "extractedCharacters": len(pdf_text), "status": status}
    all_text = f"{query}\n{pdf_text}"
    if not all_text.strip():
        raise HTTPException(status_code=422, detail="Provide a product question or PDF.")
    profile = classify(all_text)
    result = analysis_template(all_text, profile, pdf_text)
    if upload:
        result["upload"] = upload
    return result
