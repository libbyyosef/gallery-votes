// src/App.tsx
import React, { useEffect, useState, useCallback, useRef } from "react";
import type { ImageItem, VoteAction } from "./types";
import { fetchImages, applyReaction } from "./api";
import type { Reaction } from "./api";
import { Header } from "./components/Header";
import { ImageCard } from "./components/ImageCard";
import { FullscreenModal } from "./components/FullscreenModal";
import { Box, SimpleGrid, Text } from "@chakra-ui/react";
import { useAtom } from "jotai";
import { imagesAtom, reactionsAtom } from "./state/images";
import { downloadCSVClient } from "./export";

const BATCH_SIZE = 16;
const STEP_MS = 200;

const App: React.FC = () => {
  const [images, setImages] = useAtom(imagesAtom);
  const [reactions, setReactions] = useAtom(reactionsAtom);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<ImageItem | null>(null);
  const [visibleCount, setVisibleCount] = useState(0);
  const didRevealRef = useRef(false);

  // Fetch once into atom
  useEffect(() => {
    if (images !== null) return;
    (async () => {
      try {
        const data = await fetchImages();
        setImages(data);
      } catch (e) {
        setError((e as Error).message);
      }
    })();
  }, [images, setImages]);

  // Progressive reveal (runs once after images load)
  useEffect(() => {
    if (!images || didRevealRef.current) return;
    didRevealRef.current = true;
    setVisibleCount(0);
    let shown = 0;
    const id = setInterval(() => {
      shown = Math.min(images.length, shown + BATCH_SIZE);
      setVisibleCount(shown);
      if (shown === images.length) clearInterval(id);
    }, STEP_MS);
    return () => clearInterval(id);
  }, [images]);

  // Instagram-style toggle with optimistic update
  const onVote = useCallback(
    async (id: number, action: VoteAction) => {
      const prev: Reaction = reactions[id] ?? null;
      const next: Reaction = prev === action ? null : action;

      const likesDelta =
        (prev === "like" ? -1 : 0) + (next === "like" ? +1 : 0);
      const dislikesDelta =
        (prev === "dislike" ? -1 : 0) + (next === "dislike" ? +1 : 0);

      // optimistic counts
      setImages((arr) =>
        arr
          ? arr.map((it) =>
              it.image_id !== id
                ? it
                : {
                    ...it,
                    likes: Math.max(0, it.likes + likesDelta),
                    dislikes: Math.max(0, it.dislikes + dislikesDelta),
                  }
            )
          : arr
      );

      // optimistic reaction
      setReactions((map) => {
        const copy = { ...map };
        if (next === null) delete copy[id];
        else copy[id] = next;
        return copy;
      });

      try {
        await applyReaction(id, prev, next);
      } catch (e) {
        // rollback counts
        setImages((arr) =>
          arr
            ? arr.map((it) =>
                it.image_id !== id
                  ? it
                  : {
                      ...it,
                      likes: Math.max(0, it.likes - likesDelta),
                      dislikes: Math.max(0, it.dislikes - dislikesDelta),
                    }
              )
            : arr
        );
        // rollback reaction
        setReactions((map) => {
          const copy = { ...map };
          if (prev === null) delete copy[id];
          else copy[id] = prev;
          return copy;
        });
        alert((e as Error).message);
      }
    },
    [reactions, setImages, setReactions]
  );

  // Live item for modal
  const selectedLive: ImageItem | null =
    selected && images
      ? images.find((it) => it.image_id === selected.image_id) ?? selected
      : selected;

  return (
    <Box bg="app.bg" minH="100%" color="app.text">
      <Header
        onExport={() => {
          if (!images) return;
          downloadCSVClient(images, reactions);
        }}
      />

      {/* Full-width content with small side padding */}
      <Box w="100%" px={{ base: 3, sm: 4, md: 6 }} py={4}>
        {error && (
          <Text color="tomato" textAlign="center">
            {error}
          </Text>
        )}

        {images === null && !error && (
          <Text textAlign="center" color="app.muted" mt={10}>
            Loading images…
          </Text>
        )}

        {images && (
          /**
           * Auto-fit grid:
           * - minChildWidth tells Chakra to create as many columns as fit.
           * - No fixed max container width, so it stretches to page edges.
           */
          <SimpleGrid
            minChildWidth={{ base: "160px", sm: "200px", md: "220px", lg: "240px" }}
            spacing={4}
            justifyItems="stretch"
            alignItems="stretch"
          >
            {images.slice(0, visibleCount).map((img, i) => (
              <ImageCard
                key={img.image_id}
                item={img}
                index={i}
                reaction={reactions[img.image_id] ?? null}
                onOpen={setSelected}
                onVote={onVote}
              />
            ))}
          </SimpleGrid>
        )}
      </Box>

      <FullscreenModal
        open={!!selectedLive}
        item={selectedLive}
        reaction={selectedLive ? reactions[selectedLive.image_id] ?? null : null}
        onClose={() => setSelected(null)}
        onVote={onVote}
      />
    </Box>
  );
};

export default App;
