import React, { useState, useMemo } from 'react'
import { Box, HStack, Image, AspectRatio, IconButton, Text, Skeleton } from '@chakra-ui/react'
import { AiFillLike, AiFillDislike } from 'react-icons/ai'
import type { ImageItem, VoteAction } from '../types'
import type { Reaction } from '../state/images'

interface ImageCardProps {
  item: ImageItem
  onOpen: (item: ImageItem) => void
  onVote: (id: number, action: VoteAction) => Promise<void>
  index?: number
  reaction?: Reaction
}

const ABOVE_THE_FOLD = 12

const ImageCardInner: React.FC<ImageCardProps> = ({ item, onOpen, onVote, index = 0, reaction = null }) => {
  const { image_id, source_url, likes, dislikes } = item
  const [loaded, setLoaded] = useState(false)
  const [retry, setRetry] = useState(0)

  const imgSrc = useMemo(() => {
    if (!retry) return source_url
    const url = new URL(source_url)
    url.searchParams.set('retry', String(retry))
    return url.toString()
  }, [source_url, retry])

  const likeActive = reaction === 'like'
  const dislikeActive = reaction === 'dislike'

  return (
    <Box as="article" bg="app.card" borderRadius="md" boxShadow="elev" overflow="hidden" display="flex" flexDirection="column">
      <Box onClick={() => onOpen(item)} cursor="pointer" _hover={{ opacity: 0.98 }}>
        <AspectRatio ratio={4 / 3} w="100%">
          <Skeleton isLoaded={loaded} fadeDuration={0.3}>
            <Image
              src={imgSrc}
              alt={`Image ${image_id}`}
              objectFit="cover"
              loading={index < ABOVE_THE_FOLD ? 'eager' : 'lazy'}
              decoding="async"
              onLoad={() => setLoaded(true)}
              onError={() => { if (retry < 1) setRetry((r) => r + 1) }}
            />
          </Skeleton>
        </AspectRatio>
      </Box>

      <HStack px={3} py={3} justify="space-between">
        <HStack spacing={2}>
          <IconButton
            aria-label="Like"
            aria-pressed={likeActive}
            icon={<AiFillLike />}
            size="sm"
            onClick={() => onVote(image_id, 'like')}
            bg={likeActive ? 'app.like' : 'whiteAlpha.200'}
            color={likeActive ? '#08130a' : 'inherit'}
            _hover={{ filter: 'brightness(1.05)' }}
          />
          <Text as="span" minW="2ch" textAlign="right">{likes}</Text>
        </HStack>

        <HStack spacing={2}>
          <IconButton
            aria-label="Dislike"
            aria-pressed={dislikeActive}
            icon={<AiFillDislike />}
            size="sm"
            onClick={() => onVote(image_id, 'dislike')}
            bg={dislikeActive ? 'app.dislike' : 'whiteAlpha.200'}
            color={dislikeActive ? '#08130a' : 'inherit'}
            _hover={{ filter: 'brightness(1.05)' }}
          />
          <Text as="span" minW="2ch" textAlign="right">{dislikes}</Text>
        </HStack>
      </HStack>
    </Box>
  )
}

export const ImageCard = React.memo(ImageCardInner, (prev, next) => {
  return (
    prev.item === next.item &&
    prev.index === next.index &&
    prev.reaction === next.reaction &&
    prev.onOpen === next.onOpen &&
    prev.onVote === next.onVote
  )
})
ImageCard.displayName = 'ImageCard'
