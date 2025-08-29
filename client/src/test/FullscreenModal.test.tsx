import React from 'react'
import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithUI } from './testUtils'
import { FullscreenModal } from '../components/FullscreenModal'
import { REACTION } from '../reaction'

const item = {
  image_id: 42,
  source_url: 'https://picsum.photos/id/42/600/400.webp',
  likes: 3,
  dislikes: 1,
  is_liked: false,
  is_disliked: false,
}

describe('FullscreenModal', () => {
  it('renders + like / dislike call onVote', async () => {
    const onVote = vi.fn().mockResolvedValue(undefined)
    const onClose = vi.fn()
    const onPrev = vi.fn()
    const onNext = vi.fn()

    renderWithUI(
      <FullscreenModal
        open
        item={item}
        reaction={null}
        onClose={onClose}
        onVote={onVote}
        onPrev={onPrev}
        onNext={onNext}
      />
    )

    const dialog = await screen.findByRole('dialog')
    expect(within(dialog).getByAltText('Image 42')).toBeInTheDocument()

    await userEvent.click(within(dialog).getByRole('button', { name: /^like$/i }))
    expect(onVote).toHaveBeenCalledWith(42, REACTION.LIKE)

    await userEvent.click(within(dialog).getByRole('button', { name: /^dislike$/i }))
    expect(onVote).toHaveBeenCalledWith(42, REACTION.DISLIKE)
  })

  it('left/right buttons call onPrev/onNext', async () => {
    const onPrev = vi.fn()
    const onNext = vi.fn()

    renderWithUI(
      <FullscreenModal
        open
        item={item}
        reaction={null}
        onClose={() => {}}
        onVote={async () => {}}
        onPrev={onPrev}
        onNext={onNext}
      />
    )

    const dialog = await screen.findByRole('dialog')
    await userEvent.click(within(dialog).getByRole('button', { name: /next/i }))
    await userEvent.click(within(dialog).getByRole('button', { name: /previous/i }))

    expect(onNext).toHaveBeenCalled()
    expect(onPrev).toHaveBeenCalled()
  })
})
