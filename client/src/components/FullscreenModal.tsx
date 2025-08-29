import React, { useState, useMemo } from 'react'
import {
  Modal, ModalOverlay, ModalContent, ModalBody, IconButton, HStack, Box, Text, Skeleton
} from '@chakra-ui/react'
  // not using @chakra-ui/icons to avoid extra dep; use plain "×" button
import { AiFillLike, AiFillDislike } from 'react-icons/ai'
import type { ImageItem, VoteAction } from '../types'
import type { Reaction } from '../state/images'

interface FullscreenModalProps {
  open: boolean
  item: ImageItem | null
  onClose: () => void
  onVote: (id: number, action: VoteAction) => Promise<void>
  reaction?: Reaction
}

export const FullscreenModal: React.FC<FullscreenModalProps> = ({ open, item, onClose, onVote, reaction = null }) => {
  const [loaded, setLoaded] = useState(false)
  const [retry, setRetry] = useState(0)

  const imgSrc = useMemo(() => {
    if (!item) return ''
    if (!retry) return item.source_url
    const url = new URL(item.source_url)
    url.searchParams.set('retry', String(retry))
    return url.toString()
  }, [item, retry])

  const likeActive = reaction === 'like'
  const dislikeActive = reaction === 'dislike'

  return (
    <Modal isOpen={open} onClose={onClose} size="6xl" isCentered>
      <ModalOverlay />
      <ModalContent bg="transparent" boxShadow="none" overflow="hidden">
        <ModalBody p={0} position="relative">
          {/* Close button slightly inset from top-right */}
          <IconButton
            aria-label="Close"
            onClick={onClose}
            position="absolute"
            top={3}
            right={3}
            zIndex={2}
            size="sm"
            bg="blackAlpha.600"
            color="white"
            _hover={{ bg: 'blackAlpha.700' }}
            icon={<Box as="span" fontSize="lg" lineHeight={1}>×</Box>}
          />

          {/* The image */}
          <Box w="100%" bg="black" display="flex" justifyContent="center" alignItems="center">
            {item && (
              <Skeleton isLoaded={loaded} fadeDuration={0.3} w="100%">
                <Box as="img"
                  src={imgSrc}
                  alt={`Image ${item.image_id}`}
                  style={{ width: '100%', height: 'auto', display: 'block', objectFit: 'contain', maxHeight: '80vh' }}
                  loading="eager"
                  onLoad={() => setLoaded(true)}
                  onError={() => { if (retry < 1) setRetry(r => r + 1) }}
                />
              </Skeleton>
            )}
          </Box>

          {/* Controls over a dark bar */}
          {item && (
            <HStack
              spacing={6}
              px={4}
              py={3}
              bg="blackAlpha.600"
              backdropFilter="blur(4px)"
              align="center"
              justify="center"
            >
              <HStack spacing={3}>
                <IconButton
                  aria-label="Like"
                  aria-pressed={likeActive}
                  icon={<AiFillLike size={22} />}
                  size="md"
                  onClick={() => onVote(item.image_id, 'like')}
                  bg={likeActive ? 'app.like' : 'whiteAlpha.300'}
                  color={likeActive ? '#08130a' : 'white'}
                  _hover={{ filter: 'brightness(1.05)' }}
                />
                <Text color="white" minW="2ch" textAlign="right">{item.likes}</Text>
              </HStack>

              <HStack spacing={3}>
                <IconButton
                  aria-label="Dislike"
                  aria-pressed={dislikeActive}
                  icon={<AiFillDislike size={22} />}
                  size="md"
                  onClick={() => onVote(item.image_id, 'dislike')}
                  bg={dislikeActive ? 'app.dislike' : 'whiteAlpha.300'}
                  color={dislikeActive ? '#08130a' : 'white'}
                  _hover={{ filter: 'brightness(1.05)' }}
                />
                <Text color="white" minW="2ch" textAlign="right">{item.dislikes}</Text>
              </HStack>
            </HStack>
          )}
        </ModalBody>
      </ModalContent>
    </Modal>
  )
}
