# BIS Sahayak

BIS Sahayak is a source-grounded prototype for the SIH26107 idea: an AI guidance layer that helps industries, MSMEs and consumers move from a product question to a clearer official next action.

> **Advisory:** This prototype offers readiness guidance only. It does not grant BIS certification, decide final product coverage, verify a hallmark or HUID, or replace BIS processes. Always confirm current requirements, QCO coverage, scope, version and application instructions with BIS.

## What the prototype includes

- A responsive React / Next.js interface with three core screens: product/query home, analysis and roadmap, and source details.
- Product and intent matching for a focused demo corpus: Laptop/Notebook/Tablet, gold jewellery / HUID, refrigerating appliances, Scheme-X / industrial queries, and a general QCO/standard route.
- Optional PDF upload. The FastAPI backend uses PyMuPDF to extract selectable text and labels the result when a PDF needs manual review.
- A 13-source curated corpus with source URLs, category, version or page metadata, last-updated information where published, and a corpus-check date.
- Evidence-linked requirements, testing direction, document readiness checks and a personalized next-action roadmap.
- Clickable official-source records and a prominent advisory boundary on every decision-oriented screen.

## Architecture

```text
Next.js frontend (React)  ->  FastAPI orchestration API  ->  Curated JSON corpus
                                           |
                                           +-> PyMuPDF text extraction for uploaded PDFs
```

This stays deliberately within the pitch deck’s realistic MVP boundary: one polished, source-grounded flow with a small verified corpus and no live BIS API calls. The API’s `retrieve()` function is a transparent mock hybrid matcher: product profiles take precedence, then keyword overlap ranks the remaining official records.

The data boundary supports the later technical direction in the deck without pretending those services run in the prototype:

- Replace `backend/app/data/sources.json` with PostgreSQL records.
- Replace `retrieve()` with pgvector or Chroma similarity search plus metadata filters.
- Keep FastAPI as the evidence-orchestration layer.
- Add an LLM only after preserving the rule that its output can cite retrieved official evidence and must retain the advisory boundary.

## Run locally

Open two terminals from this project folder.

### 1. Start the backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API starts at `http://127.0.0.1:8000`. Confirm it is healthy at `http://127.0.0.1:8000/health`.

### 2. Start the frontend

```powershell
cd frontend
npm install
npm run dev
```

Then open `http://localhost:3000`.

The frontend defaults to `http://127.0.0.1:8000` for the API. To point it elsewhere, create `frontend/.env.local`:

```text
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

## Try the intended demo scenarios

1. `I manufacture laptops and want to understand BIS readiness.`
2. `I sell gold jewellery. How can a customer verify a hallmark?`
3. `I need to check whether my product may be covered by a QCO.`
4. Upload a text-based product-specification PDF with any of the queries above. The document check will mark only simple text matches as found and keep the rest as verification work.

## Curated official-source corpus

The backend stores the source data in `backend/app/data/sources.json`. It contains these 13 official BIS / BIS LIMS records:

1. [Know Your Standards](https://standards.bis.gov.in/)
2. [Products under Compulsory Certification](https://www.bis.gov.in/product-certification/products-under-compulsory-certification/?lang=en)
3. [Scheme-II: Compulsory Registration Scheme](https://www.bis.gov.in/product-certification/products-under-compulsory-certification/scheme-ii-registration-scheme/?lang=en)
4. [Product Certification FAQ](https://www.bis.gov.in/product-certification/product-certification-faq/?lang=en)
5. [Product Certification Process](https://www.bis.gov.in/product-certification/product-certification-process/?lang=en)
6. [Product Specific Information](https://www.bis.gov.in/product-certification/product-specific-guideline/?lang=en)
7. [BIS Recognized Labs](https://lims.bis.gov.in/home/labs/)
8. [BIS Care App](https://www.bis.gov.in/bis-apps/?lang=en)
9. [Hallmarking Overview](https://www.bis.gov.in/hallmarking-overview/?lang=en)
10. [Guidance Document on Quality Control Orders](https://www.bis.gov.in/wp-content/uploads/2021/08/Guidance-Document-on-Quality-Control-Orders-QCOs.pdf)
11. [Scheme-X Certification FAQ](https://www.bis.gov.in/scheme-x-certification/faq-scheme-x-certification/?lang=en)
12. [Guidelines for Certification of Refrigerating Appliances](https://www.bis.gov.in/wp-content/uploads/2021/03/Guidelines_18032021.pdf)
13. [Scheme-X FAQ, Version 1 (April 2024)](https://www.bis.gov.in/wp-content/uploads/2024/04/FAQs-Scheme-X-10-April-2024.pdf)

Source records remain intentionally small, and the interface tells users to open the official page for a current decision.

## Project layout

```text
frontend/                 Next.js client
  app/                    Home, analysis and source-detail screens
  lib/api.ts              Typed API client and result models
backend/
  app/main.py             FastAPI routes, PDF extraction and prototype retrieval
  app/data/sources.json   Curated source corpus with metadata
```

## Deliberate MVP limits

- No live BIS API, authentication, payment, application submission or licence verification.
- No claim that an uploaded document satisfies BIS documentation requirements.
- No automated final standard/QCO/scheme applicability decision.
- No LLM-generated regulatory advice. This prototype uses deterministic, evidence-routed templates so the readiness language stays bounded and inspectable.
