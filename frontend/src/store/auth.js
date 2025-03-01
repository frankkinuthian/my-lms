import { create } from "zustand";
import { mountStoreDevtool } from "simple-zustand-devtools";

// Creates a global state store for authentication-related data
const useAuthStore = create((set, get) => ({
  // Stores all user data retrieved from the backend
  allUserData: null,
  // Indicates whether the application is currently loading data
  loading: false,

  // Returns a simplified user object containing user_id and username
  user: () => ({
    user_id: get().allUserData?.user_id || null,
    username: get().allUserData?.username || null,
  }),

  // Updates the allUserData state with the provided user object
  setUser: (user) =>
    set({
      allUserData: user,
    }),

  // Updates the loading state with the provided boolean value
  setLoading: (loading) => set({ loading }),

  // Checks if a user is logged in by verifying if allUserData is not null
  isLoggedIn: () => get().allUserData !== null,
}));

// Enables the Zustand devtools in development mode for debugging
if (import.meta.env.DEV) {
  mountStoreDevtool("Store", useAuthStore);
}

export { useAuthStore };
