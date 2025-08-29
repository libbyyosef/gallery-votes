import React from 'react'
import { screen, within, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from '../App'
import { renderWithUI } from './testUtils'
import { REACTION } from '../reaction'

// Mock API
vi.mock('../api', async () => {
  const actual = await vi.importActual<any>('../api')
  return {
    ...actual,
    fetchImages: vi.fn().mockResolvedValue([
      {
        image_id: 1,
        source_url: 'https://picsum.photos/id/1/600/400.webp',
        likes: 3,
        dislikes: 1,
        is_liked: false,
        is_disliked: false,
      },
      {
        image_id: 2,
        source_url: 'https://picsum.photos/id/2/600/400.webp',
        likes: 5,
        dislikes: 0,
        is_liked: false,
        is_disliked: false,
      },
    ]),
    applyReaction: vi.fn().mockResolvedValue(undefined),
  }
})

describe('App (gallery)', () => {
  it('renders grid and lets you like (optimistic count)', async () => {
    renderWithUI(<App />)

    // Wait for first thumbnails to render
    const imgs = await screen.findAllByRole('img', { name: /image/i })
    expect(imgs.length).toBeGreaterThan(0)

    // Scope to the first card (Image 1)
    const img1 = screen.getByAltText('Image 1')
    const card = img1.closest('article') as HTMLElement
    const likeBtn = within(card).getByRole('button', { name: /^like$/i })

    await userEvent.click(likeBtn)

    // optimistic +1 from 3 -> 4
    expect(await within(card).findByText('4')).toBeInTheDocument()

    const { applyReaction } = await import('../api')
    expect(applyReaction).toHaveBeenCalledWith(1, null, REACTION.LIKE)
  })

  it('opens fullscreen modal, supports Next/Prev and closes with Escape', async () => {
    renderWithUI(<App />)

    // Open modal on first image
    await screen.findAllByRole('img', { name: /image/i })
    await userEvent.click(screen.getByAltText('Image 1'))

    const modal = await screen.findByRole('dialog')
    expect(within(modal).getByAltText('Image 1')).toBeInTheDocument()

    // Next -> Image 2
    await userEvent.click(within(modal).getByRole('button', { name: /next/i }))
    await waitFor(() =>
      expect(within(screen.getByRole('dialog')).getByAltText('Image 2')).toBeInTheDocument()
    )

    // Prev -> back to Image 1
    await userEvent.click(within(screen.getByRole('dialog')).getByRole('button', { name: /previous/i }))
    await waitFor(() =>
      expect(within(screen.getByRole('dialog')).getByAltText('Image 1')).toBeInTheDocument()
    )

    // Escape closes the modal (dialog disappears, grid image remains)
    await userEvent.keyboard('{Escape}')
    await waitFor(() =>
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    )
  })
})
