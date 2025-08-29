export type ImageItem = {
  image_id: number;
  source_url: string;
  likes: number;
  dislikes: number;
  is_liked: boolean;
  is_disliked: boolean;
};

export type VoteAction = "like" | "dislike";
