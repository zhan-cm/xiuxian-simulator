import { create } from 'zustand'

interface UiState {
  draft: string
  historyExpanded: boolean
  codexOpen: boolean
  setDraft: (draft: string) => void
  toggleHistory: () => void
  toggleCodex: () => void
  closeCodex: () => void
  clearDraft: () => void
}

export const useUiStore = create<UiState>((set) => ({
  draft: '',
  historyExpanded: false,
  codexOpen: false,
  setDraft: (draft) => set({ draft }),
  toggleHistory: () => set((state) => ({ historyExpanded: !state.historyExpanded })),
  toggleCodex: () => set((state) => ({ codexOpen: !state.codexOpen })),
  closeCodex: () => set({ codexOpen: false }),
  clearDraft: () => set({ draft: '' }),
}))
