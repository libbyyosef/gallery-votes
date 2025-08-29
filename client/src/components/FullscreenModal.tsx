// src/components/FullscreenModal.tsx
import React from "react";
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalBody,
  IconButton,
  Box,
  HStack,
  Text,
  Image,
} from "@chakra-ui/react";
import { AiOutlineClose, AiFillLike, AiFillDislike } from "react-icons/ai";
import type { ImageItem, VoteAction } from "../types";
import type { Reaction } from "../api";

type Props = {
  open: boolean;
  item: ImageItem | null;
  reaction: Reaction | null;
  onClose: () => void;
  onVote: (id: number, action: VoteAction) => Promise<void>;
};

export const FullscreenModal: React.FC<Props> = ({
  open,
  item,
  reaction,
  onClose,
  onVote,
}) => {
  if (!item) return null;
  const { image_id, source_url, likes, dislikes } = item;

  const isLiked = reaction === "like";
  const isDisliked = reaction === "dislike";

  // Same style as ImageCard overlay buttons (light, semi-transparent when inactive)
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
          bg: "whiteAlpha.700",
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
    <Modal isOpen={open} onClose={onClose} size="6xl" isCentered>
      <ModalOverlay />
      <ModalContent
        bg="transparent"
        boxShadow="none"
        m={0}
        maxW="min(92vw, 1200px)"
        maxH="88vh"
        position="relative"
      >
        {/* Colored Close button (light, semi-transparent) */}
        <IconButton
          aria-label="Close"
          icon={<AiOutlineClose />}
          position="absolute"
          top="12px"
          right="12px"
          onClick={onClose}
          zIndex={2}
          borderRadius="full"
          size="sm"
          variant="solid"
          bg="whiteAlpha.700"
          color="blackAlpha.900"
          borderWidth="1px"
          borderColor="blackAlpha.200"
          _hover={{ bg: "whiteAlpha.800" }}
          _active={{ transform: "scale(0.98)" }}
        />

        <ModalBody p={0} display="flex" alignItems="center" justifyContent="center">
          {/* Rounded container that clips the image & overlay */}
          <Box
            lineHeight={0}
            w="100%"
            maxH="86vh"
            position="relative"
            borderRadius="lg"
            overflow="hidden"
            boxShadow="xl"
          >
            <Image
              src={source_url}
              alt={`Image ${image_id}`}
              w="100%"
              h="auto"
              maxH="80vh"
              objectFit="contain"
              display="block"
              mx="auto"
            />

            {/* Bottom overlay with centered controls */}
            <Box
              position="absolute"
              left={0}
              right={0}
              bottom={0}
              px={3}
              py={2}
              bgGradient="linear(to-t, rgba(0,0,0,0.55), rgba(0,0,0,0))"
              onClick={(e) => e.stopPropagation()}
            >
              <HStack justify="center" spacing={6}>
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
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};
