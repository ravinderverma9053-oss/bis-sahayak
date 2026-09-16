export type Source = {
  id: string;
  title: string;
  authority: string;
  category: string;
  url: string;
  summary: string;
  use: string;
  version: string;
  lastUpdated: string;
  checkedOn: string;
  tags: string[];
  relatedIds: string[];
};

export type SourceHit = Pick<Source, "id" | "title" | "authority" | "category" | "url" | "summary" | "version" | "checkedOn"> & {
  relevance: "Primary" | "Supporting";
};

export type AnalysisResult = {
  requestId: string;
  product: { name: string; category: string; confidence: string; rationale: string };
  intent: { label: string; detail: string };
  advisory: string;
  applicability: { headline: string; detail: string; status: "Potential match" | "Needs official confirmation" };
  requirements: { title: string; detail: string; evidence: string }[];
  testing: { title: string; detail: string; evidence: string }[];
  documents: { item: string; reason: string; state: "Not provided" | "Needs verification" | "Found in upload" | "Review manually" }[];
  roadmap: { number: number; title: string; detail: string; evidence: string[] }[];
  sources: SourceHit[];
  corpus: { count: number; version: string; retrievalMode: string };
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export async function analyze(query: string, file?: File): Promise<AnalysisResult> {
  const data = new FormData();
  data.append("query", query);
  if (file) data.append("file", file);
  const response = await fetch(`${API_BASE}/api/analyze`, { method: "POST", body: data });
  if (!response.ok) throw new Error("BIS Sahayak could not complete the readiness check.");
  return response.json() as Promise<AnalysisResult>;
}

export async function getSource(id: string): Promise<Source> {
  const response = await fetch(`${API_BASE}/api/sources/${id}`, { cache: "no-store" });
  if (!response.ok) throw new Error("That source record is unavailable.");
  return response.json() as Promise<Source>;
}
