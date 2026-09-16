"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { analyze, type AnalysisResult } from "../lib/api";

export default function HomePage() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    try {
      setResult(await analyze(query.trim()));
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
        <h1>Find the next verified step for your product.</h1>
        <p className="hero-copy">Describe your product or compliance question to receive a source-grounded readiness view and links to official BIS information.</p>
      </header>

      <form className="search-card" onSubmit={submit}>
        <label className="search-label" htmlFor="question">What do you need help with?</label>
        <div className="search-row">
          <input className="search-input" id="question" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Example: I manufacture laptops and need BIS readiness guidance." />
          <button className="primary-button" type="submit" disabled={loading}>{loading ? "Checking…" : "Get guidance"}</button>
        </div>
        <p className="helper">This prototype provides readiness guidance only; confirm current requirements with BIS.</p>
      </form>

      {error && <p className="notice" role="alert">{error}</p>}

      {result && <section className="result-card" aria-live="polite">
        <div className="result-heading">
          <div><p className="eyebrow">{result.product.category}</p><h2>{result.product.name}</h2></div>
          <p className="status">{result.applicability.status}</p>
        </div>
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
