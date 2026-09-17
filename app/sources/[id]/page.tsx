"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { getSource, type Source } from "../../../lib/api";

export default function SourceDetailPage() {
  const params = useParams<{ id: string }>();
  const [source, setSource] = useState<Source | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getSource(params.id).then(setSource).catch((err: Error) => setError(err.message));
  }, [params.id]);

  return (
    <main className="site-shell source-shell">
      <nav className="topbar"><Link className="brand" href="/"><span className="brand-mark">B</span><span>BIS <strong>Sahayak</strong></span></Link><Link className="quiet-link" href="/">← Back to readiness view</Link></nav>
      {error && <section className="empty-state"><h1>Source unavailable</h1><p>{error}</p><Link className="primary-button inline-button" href="/">Start a new check</Link></section>}
      {!source && !error && <main className="loading-screen"><span className="loading-orbit" /> Loading source record…</main>}
      {source && <>
        <header className="source-header">
          <div><p className="eyebrow">{source.category} <span className="small-divider">/</span> {source.id}</p><h1>{source.title}</h1><p>{source.summary}</p></div>
          <a className="external-button" href={source.url} target="_blank" rel="noreferrer">Open official source <span>↗</span></a>
        </header>
        <section className="source-detail-grid">
          <article className="source-read-card"><p className="panel-kicker">How BIS Sahayak uses it</p><h2>{source.use}</h2><p>This record belongs to the prototype’s curated corpus. It supports guidance only when its version metadata remains current.</p><div className="tag-row">{source.tags.map((tag) => <span key={tag}>{tag}</span>)}</div></article>
          <aside className="source-metadata"><p className="panel-kicker">Source metadata</p><dl><dt>Authority</dt><dd>{source.authority}</dd><dt>Source version</dt><dd>{source.version}</dd><dt>Last updated</dt><dd>{source.lastUpdated}</dd><dt>Verified in corpus</dt><dd>{source.checkedOn}</dd><dt>Mode</dt><dd>Curated offline retrieval</dd></dl></aside>
        </section>
        <section className="source-caveat"><span>!</span><p>Open the original BIS page before relying on this information. QCO coverage, standard revisions, scheme requirements and laboratory scope can change.</p></section>
      </>}
    </main>
  );
}
