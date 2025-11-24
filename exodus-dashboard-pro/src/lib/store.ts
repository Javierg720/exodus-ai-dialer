import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AppState {
  darkMode: boolean
  sidebarOpen: boolean
  toggleDarkMode: () => void
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      darkMode: true,
      sidebarOpen: true,
      toggleDarkMode: () => set((state) => {
        const newDarkMode = !state.darkMode
        // Apply to document immediately
        if (newDarkMode) {
          document.documentElement.classList.add('dark')
        } else {
          document.documentElement.classList.remove('dark')
        }
        return { darkMode: newDarkMode }
      }),
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
    }),
    {
      name: 'exodus-storage',
    }
  )
)
