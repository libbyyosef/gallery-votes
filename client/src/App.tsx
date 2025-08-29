// src/App.tsx
import React, { useEffect, useState, useCallback, useRef } from "react";
import type { ImageItem, VoteAction } from "./types";
import { fetchImages, downloadCSV, applyReaction, fetchCounters } from "./api";
import type { Reaction } from "./api";
import { Header } from "./components/Header";
import { ImageCard } from "./components/ImageCard";
import { FullscreenModal } from "./components/FullscreenModal";
import { Box, Container, SimpleGrid, Text } from "@chakra-ui/react";
import { useAtom } from "jotai";
import { imagesAtom, reactionsAtom } from "./state/images";

const BATCH_SIZE = 16;          // progressive reveal size
const STEP_MS = 200;            // reveal cadence
const POLL_MS = 5000;           // counters poll interval
const WRITE_SETTLE_MS = 1200;   // skip polling briefly after a local write

const App: React.FC = () => {
  const [images, setImages] = useAtom(imagesAtom);
  const [reactions, setReactions] = useAtom(reactionsAtom);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<ImageItem | null>(null);
  const [visibleCount, setVisibleCount] = useState(0);
  const didRevealRef = useRef(false);
  const lastWriteRef = useRef(0);

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

      // compute optimistic deltas
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

      // record write time (pause poll briefly)
      lastWriteRef.current = Date.now();

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

  // Poll only counters so different users see each other's likes within seconds
  useEffect(() => {
    if (!images || images.length === 0) return;

    const interval = setInterval(async () => {
      if (Date.now() - lastWriteRef.current < WRITE_SETTLE_MS) return;
      try {
        const idList = images.map((it) => it.image_id);
        const map = await fetchCounters(idList);
        setImages((arr) =>
          arr
            ? arr.map((it) => {
                const c = map[it.image_id];
                return c ? { ...it, likes: c.likes, dislikes: c.dislikes } : it;
              })
            : arr
        );
      } catch {
        // ignore transient polling errors
      }
    }, POLL_MS);

    return () => clearInterval(interval);
  }, [images, setImages]);

  return (
    <Box bg="app.bg" minH="100%" color="app.text">
      <Header onExport={downloadCSV} />

      <Container maxW="7xl" py={4}>
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
          <SimpleGrid columns={{ base: 2, md: 3, lg: 4, xl: 5 }} spacing={4}>
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
      </Container>

      <FullscreenModal
        open={!!selected}
        item={selected}
        reaction={selected ? reactions[selected.image_id] ?? null : null}
        onClose={() => setSelected(null)}
        onVote={onVote}
      />
    </Box>
  );
};

export default App;
