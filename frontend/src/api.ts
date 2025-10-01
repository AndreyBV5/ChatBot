export type ChatResponse = {
  answer: string;
  intent: "faq" | "faq_suggest" | "fallback" | "empty";
  confidence: number;
  suggestions: string[];
};

export async function ask(message: string): Promise<ChatResponse> {
  const res = await fetch(`${import.meta.env.VITE_API_BASE}/api/chat/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  });
  if (!res.ok) throw new Error("API error");
  return res.json();
}

export type FAQItem = { id:number; question:string; answer:string; tags?:string };

export async function listFAQ(search=""): Promise<FAQItem[]> {
  const url = new URL(`${import.meta.env.VITE_API_BASE}/api/faq`);
  if (search) url.searchParams.set("search", search);
  const res = await fetch(url);
  if (!res.ok) throw new Error("API error");
  return res.json();
}
