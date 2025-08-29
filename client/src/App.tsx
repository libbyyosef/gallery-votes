import React, { useEffect, useState, useCallback, useRef } from "react";
import type { ImageItem } from "./types";
import { fetchImages, applyReaction } from "./api";
import type { Reaction } from "./api";
import { Header } from "./components/Header";
import { ImageCard } from "./components/ImageCard";
import { FullscreenModal } from "./components/FullscreenModal";
import { Box, SimpleGrid, Text } from "@chakra-ui/react";
import { useAtom } from "jotai";
import { imagesAtom, reactionsAtom } from "./state/images";
import { downloadCSVClient } from "./export";
import { REACTION } from "./reaction";

const BATCH_SIZE = 16;  
const STEP_MS = 200;    
const POLL_MS = 5000;   
const WRITE_PAUSE_MS = 1500; 

const App: React.FC = () => {
  const [images, setImages] = useAtom(imagesAtom);           
  const [reactions, setReactions] = useAtom(reactionsAtom);  
  const [error, setError] = useState<string | null>(null);

  const [selected, setSelected] = useState<ImageItem | null>(null);
  const [selectedIdx, setSelectedIdx] = useState<number>(-1); 

  const [visibleCount, setVisibleCount] = useState(0);
  const didRevealRef = useRef(false);

  // track last write time to pause polling right after a like/dislike
  const lastWriteRef = useRef(0);

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

  const onVote = useCallback(
    async (id: number, action: Reaction) => {
      const prev: Reaction = reactions[id] ?? null;
      const next: Reaction = prev === action ? null : action;

      const likesDelta =
        (prev === REACTION.LIKE ? -1 : 0) + (next === REACTION.LIKE ? +1 : 0);
      const dislikesDelta =
        (prev === REACTION.DISLIKE ? -1 : 0) + (next === REACTION.DISLIKE ? +1 : 0);

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

      setReactions((map) => {
        const copy: Record<number, Reaction> = { ...map };
        if (next === null) delete copy[id];
        else copy[id] = next;
        return copy;
      });

      lastWriteRef.current = Date.now();

      try {
        await applyReaction(id, prev, next);
      } catch (e) {
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
        setReactions((map) => {
          const copy: Record<number, Reaction> = { ...map };
          if (prev === null) delete copy[id];
          else copy[id] = prev;
          return copy;
        });
        alert((e as Error).message);
      }
    },
    [reactions, setImages, setReactions]
  );

  // Polling: every few seconds merge ONLY counters so users see each other's likes
  useEffect(() => {
    if (!images || images.length === 0) return;

    const interval = setInterval(async () => {
      if (document.hidden) return;
      if (Date.now() - lastWriteRef.current < WRITE_PAUSE_MS) return;

      try {
        const fresh = await fetchImages();
        const map = new Map<number, ImageItem>(fresh.map((f) => [f.image_id, f]));
        setImages((prev) =>
          prev
            ? prev.map((it) => {
                const f = map.get(it.image_id);
                return f ? { ...it, likes: f.likes, dislikes: f.dislikes } : it;
              })
            : prev
        );
      } catch {
      }
    }, POLL_MS);

    // recreate interval only if image count changes
    return () => clearInterval(interval);
  }, [images?.length, setImages]);

  const openAtIndex = useCallback((item: ImageItem, idx: number) => {
    setSelected(item);
    setSelectedIdx(idx);
  }, []);

  const goPrev = useCallback(() => {
    if (!images || selectedIdx < 0) return;
    const idx = (selectedIdx - 1 + images.length) % images.length;
    setSelectedIdx(idx);
    setSelected(images[idx]);
  }, [images, selectedIdx]);

  const goNext = useCallback(() => {
    if (!images || selectedIdx < 0) return;
    const idx = (selectedIdx + 1) % images.length;
    setSelectedIdx(idx);
    setSelected(images[idx]);
  }, [images, selectedIdx]);

  useEffect(() => {
    if (!images || selectedIdx < 0) return;
    const current = images[selectedIdx];
    if (!current) return;

    setSelected(current);
  }, [images, selectedIdx]);

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
                onOpen={(item) => openAtIndex(item, i)} 
                onVote={onVote}
              />
            ))}
          </SimpleGrid>
        )}
      </Box>

      <FullscreenModal
        open={!!selected}
        item={selected}
        reaction={selected ? reactions[selected.image_id] ?? null : null}
        onClose={() => {
          setSelected(null);
          setSelectedIdx(-1);
        }}
        onVote={onVote}
        onPrev={goPrev}
        onNext={goNext}
      />
    </Box>
  );
};

export default App;
