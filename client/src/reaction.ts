// Central place for reaction literals/types
export const REACTION = {
  LIKE: "like",
  DISLIKE: "dislike",
} as const;

export type ReactionKind = typeof REACTION[keyof typeof REACTION];
export type Reaction = ReactionKind | null;
