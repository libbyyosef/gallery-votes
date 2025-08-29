import type { ImageItem } from "./types";
import { REACTION, type Reaction } from "./reaction";
export type { Reaction } from "./reaction";

/** Generate & download CSV using the current client state. */
export function downloadCSVClient(
  images: ImageItem[],
  reactions: Record<number, Reaction>
): void {
  const headers = [
    "Image URL",
    "Likes",
    "Dislikes",
    "Is Current User Liked",
    "Is Current User Dislike",
  ];

  const lines = images.map((it) => {
    const r = reactions[it.image_id] ?? null;
    const liked = r === REACTION.LIKE;
    const disliked = r === REACTION.DISLIKE;
    return [
      it.source_url,
      String(it.likes),
      String(it.dislikes),
      liked ? "true" : "false",
      disliked ? "true" : "false",
    ].map(csvEscape).join(",");
  });

  const csv = [headers.join(","), ...lines].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "votes.csv";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function csvEscape(s: string): string {
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}
