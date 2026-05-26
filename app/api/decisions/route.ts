import { Redis } from "@upstash/redis";
import type { DecisionMap } from "@/lib/types";

const KV_KEY = "taxonomy:decisions_v1";

// In-memory fallback for local dev (no Redis configured)
const localStore: DecisionMap = {};
const hasRedis = !!(process.env.UPSTASH_REDIS_REST_URL && process.env.UPSTASH_REDIS_REST_TOKEN);
const redis = hasRedis ? Redis.fromEnv() : null;

export async function GET() {
  try {
    const decisions: DecisionMap = redis
      ? ((await redis.get<DecisionMap>(KV_KEY)) ?? {})
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
    if (redis) {
      const existing = (await redis.get<DecisionMap>(KV_KEY)) ?? {};
      decisions = { ...existing, ...updates };
      await redis.set(KV_KEY, decisions);
    } else {
      Object.assign(localStore, updates);
      decisions = { ...localStore };
    }
    return Response.json({ decisions });
  } catch {
    return Response.json({ error: "Failed to save" }, { status: 500 });
  }
}
