import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useStore = create(
  persist(
    (set) => ({
      user: null, // { id, name, email, preferences }
      setUser: (user) => set({ user }),
      logout: () => set({ user: null }),
      
      // We will keep a local copy of recent insights for quick viewing
      recentInsights: [],
      setRecentInsights: (insights) => set({ recentInsights: insights }),
      addInsight: (insight) => set((state) => ({ 
        recentInsights: [insight, ...state.recentInsights].slice(0, 20) 
      })),
    }),
    {
      name: 'fluxbase-agent-storage',
    }
  )
);

export default useStore;
