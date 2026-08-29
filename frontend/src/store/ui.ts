import { create } from 'zustand'

interface UiState {
  draft: string
  historyExpanded: boolean
  setDraft: (draft: string) => void
  toggleHistory: () => void
  clearDraft: () => void
}

export const useUiStore = create<UiState>((set) => ({
  draft: '',
  historyExpanded: false,
  setDraft: (draft) => set({ draft }),
  toggleHistory: () => set((state) => ({ historyExpanded: !state.historyExpanded })),
  clearDraft: () => set({ draft: '' }),
}))
