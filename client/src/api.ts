import type { ImageItem } from "./types";
import { REACTION, type Reaction } from "./reaction";
export type { Reaction } from "./reaction";


const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/+$/, '');

export async function fetchCounters(
  ids: number[]
): Promise<Record<number, { likes: number; dislikes: number }>> {
  if (ids.length === 0) return {};
  const params = new URLSearchParams();
  ids.forEach((id) => params.append("ids", String(id)));
  const res = await fetch(`${API_BASE}/images/counters?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch counters");
  const arr = (await res.json()) as { image_id: number; likes: number; dislikes: number }[];
  const map: Record<number, { likes: number; dislikes: number }> = {};
  for (const r of arr) map[r.image_id] = { likes: r.likes, dislikes: r.dislikes };
  return map;
}


async function post(url: string, init?: RequestInit): Promise<void> {
  const res = await fetch(url, { method: "POST", ...init });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText} at ${url}${text ? `: ${text}` : ""}`);
  }
}

export async function fetchImages(): Promise<ImageItem[]> {
  const res = await fetch(`${API_BASE}/images/get_all_images`);
  if (!res.ok) throw new Error("Failed to load images");
  const data = (await res.json()) as ImageItem[];
  return data;
}


/**
 * Apply an Instagram-style reaction transition.
 * prev -> next:
 *  - none -> like/dislike
 *  - like  -> none/dislike
 *  - dislike -> none/like
 * Calls counters-only image endpoints.
 */
export async function applyReaction(
  imageId: number,
  prev: Reaction,
  next: Reaction
): Promise<void> {
  if (prev === next) return;

  const likeURL = `${API_BASE}/images/like/${imageId}`;
  const dislikeURL = `${API_BASE}/images/dislike/${imageId}`;
  const unlikeURL = `${API_BASE}/images/unlike/${imageId}`;
  const undislikeURL = `${API_BASE}/images/undislike/${imageId}`;

  // none -> like / dislike
  if (prev === null && next ===  REACTION.LIKE) return post(likeURL);
  if (prev === null && next === REACTION.DISLIKE) return post(dislikeURL);

  // like -> none / dislike
  if (prev === REACTION.LIKE && next === null) return post(unlikeURL);
  if (prev === REACTION.LIKE && next ===REACTION.DISLIKE) {
    await post(unlikeURL);
    return post(dislikeURL);
  }

  // dislike -> none / like
  if (prev === REACTION.DISLIKE && next === null) return post(undislikeURL);
  if (prev === REACTION.DISLIKE && next === REACTION.LIKE) {
    await post(undislikeURL);
    return post(likeURL);
  }
}


