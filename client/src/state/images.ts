import { atom } from 'jotai'
import type { ImageItem } from '../types'

/** The gallery items; null = not fetched yet */
export const imagesAtom = atom<ImageItem[] | null>(null)

/** Your per-image reaction: 'like' | 'dislike' | null */
export type Reaction = 'like' | 'dislike' | null
export const reactionsAtom = atom<Record<number, Reaction>>({})
