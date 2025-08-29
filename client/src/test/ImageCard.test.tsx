import React from 'react'
import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithUI } from './testUtils'
import { ImageCard } from '../components/ImageCard'
import { REACTION } from '../reaction'

describe('ImageCard', () => {
  it('invokes onVote with REACTION.LIKE (scoped to card)', async () => {
    const item = {
      image_id: 99,
      source_url: 'https://picsum.photos/id/99/600/400.webp',
      likes: 0,
      dislikes: 0,
      is_liked: false,
      is_disliked: false,
    }
    const onVote = vi.fn().mockResolvedValue(undefined)
    const onOpen = vi.fn()

    renderWithUI(
      <ImageCard item={item} onOpen={onOpen} onVote={onVote} index={0} reaction={null} />
    )

    const card = screen.getByRole('article')
    const likeBtn = within(card).getByRole('button', { name: /^like$/i })
    await userEvent.click(likeBtn)

    expect(onVote).toHaveBeenCalledWith(99, REACTION.LIKE)
  })
})
