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

export type Requirement = {
  title: string;
  detail: string;
  evidence: string;
};

export type DocumentCheck = {
  item: string;
  reason: string;
  state: "Not provided" | "Needs verification" | "Found in upload" | "Review manually";
};

export type RoadmapStep = {
  number: number;
  title: string;
  detail: string;
  evidence: string[];
};

export type AnalysisResult = {
  requestId: string;
  product: { name: string; category: string; confidence: string; rationale: string };
  intent: { label: string; detail: string };
  advisory: string;
  applicability: { headline: string; detail: string; status: "Potential match" | "Needs official confirmation" };
  requirements: Requirement[];
  testing: { title: string; detail: string; evidence: string }[];
  documents: DocumentCheck[];
  roadmap: RoadmapStep[];
  sources: SourceHit[];
  corpus: { count: number; version: string; retrievalMode: string };
  upload?: { name: string; extractedCharacters: number; status: string };
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

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

export function formatSourceLabel(id: string, sources: SourceHit[]) {
  return sources.find((source) => source.id === id)?.title ?? id;
}
