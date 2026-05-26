import { kv } from "@vercel/kv";
import type { DecisionMap } from "@/lib/types";

const KV_KEY = "taxonomy:decisions_v1";

// In-memory fallback for local dev (no KV configured)
const localStore: DecisionMap = {};
const useKV = !!process.env.KV_REST_API_URL;

export async function GET() {
  try {
    const decisions: DecisionMap = useKV
      ? ((await kv.get<DecisionMap>(KV_KEY)) ?? {})
      : { ...localStore };
    return Response.json({ decisions });
  } catch {
    return Response.json({ decisions: {} });
  }
}

export async function POST(req: Request) {
  try {
    const { updates } = (await req.json()) as { updates: DecisionMap };
    let decisions: DecisionMap;
    if (useKV) {
      const existing = (await kv.get<DecisionMap>(KV_KEY)) ?? {};
      decisions = { ...existing, ...updates };
      await kv.set(KV_KEY, decisions);
    } else {
      Object.assign(localStore, updates);
      decisions = { ...localStore };
    }
    return Response.json({ decisions });
  } catch {
    return Response.json({ error: "Failed to save" }, { status: 500 });
  }
}
