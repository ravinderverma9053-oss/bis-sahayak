"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { analyze, type AnalysisResult } from "../lib/api";

const sampleQuestions = [
  "Do mobile chargers need BIS certification?",
  "What BIS steps apply to a refrigerator?",
  "How can I check gold hallmarking or HUID?",
  "Does my industrial switchgear need Scheme-X?",
];

export default function HomePage() {
  const [query, setQuery] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!query.trim() && !file) {
      setError("Ask a question or attach a PDF to start the readiness check.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const requestText = query.trim() || "Review the attached PDF and identify the closest BIS readiness path.";
      setResult(await analyze(requestText, file ?? undefined));
    } catch (reason) {
      setResult(null);
      setError(reason instanceof Error ? reason.message : "The readiness check could not be completed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="site-shell">
      <nav className="topbar">
        <Link className="brand" href="/"><span className="brand-mark">B</span><span>BIS <strong>Sahayak</strong></span></Link>
        <span className="helper">Prototype guidance</span>
      </nav>

      <header className="hero">
        <p className="eyebrow">BIS readiness assistant</p>
        <h1>Search a product question or analyse a PDF.</h1>
        <p className="hero-copy">Ask about any product, standard, QCO, certification route or compliance question. Attach a product document for additional readiness hints.</p>
      </header>

      <form className="search-card" onSubmit={submit}>
        <label className="search-label" htmlFor="question">What do you need help with?</label>
        <div className="search-row">
          <input className="search-input" id="question" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Example: Does my product need BIS certification?" />
          <button className="primary-button" type="submit" disabled={loading}>{loading ? "Checking…" : "Search guidance"}</button>
        </div>
        <div className="upload-row">
          <label className="file-label" htmlFor="pdf">Attach a PDF (optional, up to 10 MB)</label>
          <input className="file-input" id="pdf" type="file" accept="application/pdf,.pdf" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
          {file && <span className="file-name">Ready to review: {file.name}</span>}
        </div>
        <p className="helper">PDFs are read for text only. Ask broad questions freely; results are matched against the curated BIS guidance library and should be confirmed with BIS.</p>
      </form>

      <section className="topic-card" aria-label="Popular BIS searches">
        <p className="panel-kicker">Try a search</p>
        <div className="topic-row">
          {sampleQuestions.map((question) => <button className="topic-button" key={question} type="button" onClick={() => setQuery(question)}>{question}</button>)}
        </div>
      </section>

      {error && <p className="notice" role="alert">{error}</p>}

      {result && <section className="result-card" aria-live="polite">
        <div className="result-heading">
          <div><p className="eyebrow">{result.product.category}</p><h2>{result.product.name}</h2></div>
          <p className="status">{result.applicability.status}</p>
        </div>
        <p className="result-rationale">{result.product.rationale}</p>
        <h3>{result.applicability.headline}</h3>
        <p>{result.applicability.detail}</p>
        <h3>Official-source starting points</h3>
        <div className="source-grid">
          {result.sources.map((source) => <Link className="source-card" href={`/sources/${source.id}`} key={source.id}><strong>{source.title}</strong><span>{source.authority} · {source.relevance}</span></Link>)}
        </div>
      </section>}

      <p className="disclaimer">BIS Sahayak does not grant certification, make final coverage decisions, or replace the applicable BIS process.</p>
    </main>
  );
}
