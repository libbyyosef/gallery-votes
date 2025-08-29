// src/components/ImageCard.tsx
import React from "react";
import { Box, HStack, Image, AspectRatio, IconButton, Text } from "@chakra-ui/react";
import { AiFillLike, AiFillDislike } from "react-icons/ai";
import type { ImageItem, VoteAction } from "../types";
import type { Reaction } from "../api";

type ImageCardProps = {
  item: ImageItem;
  onOpen: (item: ImageItem) => void;
  onVote: (id: number, action: VoteAction) => Promise<void>;
  index?: number;           // used for eager/lazy loading
  reaction?: Reaction | null;
};

const ABOVE_THE_FOLD = 12;

export const ImageCard: React.FC<ImageCardProps> = ({
  item,
  onOpen,
  onVote,
  index = 0,
  reaction = null,
}) => {
  const { image_id, source_url, likes, dislikes } = item;
  const isLiked = reaction === "like";
  const isDisliked = reaction === "dislike";

  // Light, semi-transparent buttons when inactive; solid themed when active
  const overlayBtnStyle = (kind: "like" | "dislike") => {
    const active = kind === "like" ? isLiked : isDisliked;
    const token = kind === "like" ? "app.like" : "app.dislike";

    return active
      ? {
          variant: "solid" as const,
          bg: token,
          color: "#08130a",
          _hover: { bg: token, filter: "brightness(1.05)" },
          _active: { transform: "scale(0.98)" },
          borderRadius: "full",
          size: "sm",
          "aria-pressed": true,
        }
      : {
          variant: "solid" as const,
          bg: "whiteAlpha.700",            // ⬅️ light & semi-transparent
          color: "blackAlpha.900",
          borderWidth: "1px",
          borderColor: "blackAlpha.200",
          _hover: { bg: "whiteAlpha.800" },
          _active: { transform: "scale(0.98)" },
          borderRadius: "full",
          size: "sm",
          "aria-pressed": false,
        };
  };

  return (
    <Box
      as="article"
      bg="app.card"
      borderRadius="md"
      boxShadow="elev"
      overflow="hidden"
      display="flex"
      flexDirection="column"
    >
      {/* Clickable image area; overlay holds buttons inside the same box */}
      <Box
        position="relative"
        onClick={() => onOpen(item)}
        cursor="pointer"
        _hover={{ opacity: 0.98 }}
        lineHeight={0} // remove inline image baseline gap
      >
        <AspectRatio ratio={4 / 3} w="100%">
          <Image
            src={source_url}
            alt={`Image ${image_id}`}
            objectFit="cover"
            display="block" // no top whitespace
            loading={index < ABOVE_THE_FOLD ? "eager" : "lazy"}
            decoding="async"
          />
        </AspectRatio>

        {/* Bottom overlay with buttons + counts (clicks here won't open the modal) */}
        <HStack
          position="absolute"
          left={0}
          right={0}
          bottom={0}
          px={3}
          py={2}
          justify="space-between"
          onClick={(e) => e.stopPropagation()}
          bgGradient="linear(to-t, rgba(0,0,0,0.55), rgba(0,0,0,0))"
        >
          <HStack spacing={2}>
            <IconButton
              aria-label="Like"
              title="Like"
              icon={<AiFillLike />}
              onClick={() => onVote(image_id, "like")}
              {...overlayBtnStyle("like")}
            />
            <Text as="span" minW="2ch" textAlign="right" color="whiteAlpha.900">
              {likes}
            </Text>
          </HStack>

          <HStack spacing={2}>
            <IconButton
              aria-label="Dislike"
              title="Dislike"
              icon={<AiFillDislike />}
              onClick={() => onVote(image_id, "dislike")}
              {...overlayBtnStyle("dislike")}
            />
            <Text as="span" minW="2ch" textAlign="right" color="whiteAlpha.900">
              {dislikes}
            </Text>
          </HStack>
        </HStack>
      </Box>
    </Box>
  );
};
