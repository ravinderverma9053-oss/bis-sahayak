"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { analyze, type AnalysisResult } from "../lib/api";

const examples = ["Do mobile chargers need BIS certification?", "What BIS steps apply to a refrigerator?", "How can I check gold hallmarking or HUID?", "Does industrial switchgear need Scheme-X?"];

export default function HomePage() {
  const [query, setQuery] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!query.trim() && !file) return setError("Ask a question or attach a PDF to begin.");
    setLoading(true); setError("");
    try { setResult(await analyze(query.trim() || "Review the attached PDF for BIS readiness.", file ?? undefined)); }
    catch { setResult(null); setError("BIS Sahayak could not complete the readiness check."); }
    finally { setLoading(false); }
  }

  function restart() { setQuery(""); setFile(null); setResult(null); setError(""); }

  if (result) return (
    <main className="dashboard-shell">
      <nav className="topbar dashboard-nav"><Link className="brand" href="/"><span className="brand-mark">B</span><span>BIS <strong>Sahayak</strong></span></Link><button className="quiet-link" onClick={restart}>← Start another check</button></nav>
      <section className="readiness-hero"><div><p className="eyebrow">Readiness view / {result.requestId}</p><h1>{result.product.name}</h1><p className="lede">{result.intent.detail}</p></div><aside className="advisory"><strong>Advisory</strong><p>{result.advisory}</p></aside></section>
      <section className="context-grid"><article><p>Product context</p><strong>{result.product.category}</strong><span>{result.product.rationale}</span></article><article><p>Intent detected</p><strong>{result.intent.label}</strong><span>Tailored to your question or PDF.</span></article><article><p>Evidence mode</p><strong>{result.corpus.retrievalMode}</strong><span>{result.corpus.count} sources · {result.corpus.version}</span></article></section>
      <section className="applicability-panel"><span className="step-badge">01</span><div><p className="eyebrow">Applicable standard / scheme</p><h2>{result.applicability.headline}</h2><p>{result.applicability.detail}</p></div><em>{result.applicability.status}</em></section>
      <section className="content-grid"><div className="main-column"><p className="eyebrow">02 / requirements & testing</p><h2>What to validate next</h2><div className="requirement-list">{result.requirements.map((item, index) => <article key={item.title}><span>{String(index + 1).padStart(2, "0")}</span><div><h3>{item.title}</h3><p>{item.detail}</p><small>Evidence: {item.evidence}</small></div></article>)}</div><section className="testing-card"><p className="eyebrow">Testing direction</p>{result.testing.map((item) => <div className="testing-row" key={item.title}><strong>{item.title}</strong><div><p>{item.detail}</p><small>Evidence: {item.evidence}</small></div></div>)}</section></div><aside className="evidence-card"><p className="eyebrow">03 / document check</p><h2>Readiness evidence</h2><p className="muted">A guided checklist to confirm before an official application.</p><div className="document-list">{result.documents.map((item) => <article key={item.item}><span className="checkbox"/><div><strong>{item.item}</strong><p>{item.reason}</p></div><em>{item.state}</em></article>)}</div></aside></section>
      <section className="roadmap"><div className="roadmap-heading"><div><p className="eyebrow">04 / personalized next action</p><h2>Your compliance roadmap</h2></div><span>Evidence first, then action</span></div><div className="roadmap-grid">{result.roadmap.map((item) => <article key={item.number}><p>{String(item.number).padStart(2, "0")}</p><h3>{item.title}</h3><span>{item.detail}</span><small>{item.evidence.join(" · ")}</small></article>)}</div></section>
      <section className="sources-section"><div className="sources-heading"><div><p className="eyebrow">Evidence attached</p><h2>Relevant BIS sources</h2></div><span>{result.sources.length} retrieved sources</span></div><div className="source-grid detailed-sources">{result.sources.map((source) => <Link className="source-card" href={`/sources/${source.id}`} key={source.id}><p>{source.relevance} <span>{source.category}</span></p><h3>{source.title}</h3><span>{source.summary}</span><small>{source.authority}<br/>{source.version} · Checked {source.checkedOn}</small></Link>)}</div></section>
    </main>
  );

  return (
    <main className="site-shell"><nav className="topbar"><Link className="brand" href="/"><span className="brand-mark">B</span><span>BIS <strong>Sahayak</strong></span></Link><span className="helper">Prototype guidance</span></nav><header className="hero"><p className="eyebrow">BIS readiness assistant</p><h1>Search a product question or analyse a PDF.</h1><p className="hero-copy">Ask about any product, standard, QCO, certification route or compliance question.</p></header><form className="search-card" onSubmit={submit}><label className="search-label" htmlFor="question">What do you need help with?</label><div className="search-row"><input className="search-input" id="question" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Example: Does my product need BIS certification?"/><button className="primary-button" disabled={loading}>{loading ? "Checking…" : "Search guidance"}</button></div><div className="upload-row"><label className="file-label" htmlFor="pdf">Attach a PDF (optional, up to 10 MB)</label><input id="pdf" type="file" accept="application/pdf,.pdf" onChange={(event) => setFile(event.target.files?.[0] ?? null)}/>{file && <span>{file.name}</span>}</div><p className="helper">PDFs are read for text only and matched against the curated BIS guidance library.</p></form><section className="topic-card"><p className="eyebrow">Try a search</p><div className="topic-row">{examples.map((item) => <button className="topic-button" type="button" key={item} onClick={() => setQuery(item)}>{item}</button>)}</div></section>{error && <p className="notice">{error}</p>}<p className="disclaimer">BIS Sahayak does not grant certification, make final coverage decisions, or replace the applicable BIS process.</p></main>
  );
}
