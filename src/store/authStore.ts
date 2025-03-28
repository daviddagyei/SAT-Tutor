import { create } from 'zustand';
import { supabase } from '../lib/supabase';

interface AuthState {
  user: any | null;
  session: any | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, name: string) => Promise<void>;
  signOut: () => Promise<void>;
  setSession: (session: any) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  session: null,
  loading: true,
  signIn: async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    if (error) throw error;
    set({ user: data.user, session: data.session });
  },
  signUp: async (email, password, name) => {
    const { data: { user }, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: name,
        },
      },
    });
    if (error) throw error;
    
    // Create user profile in the profiles table
    if (user) {
      const { error: profileError } = await supabase
        .from('profiles')
        .insert([
          {
            id: user.id,
            full_name: name,
            email: email,
          },
        ]);
      if (profileError) throw profileError;
    }
  },
  signOut: async () => {
    await supabase.auth.signOut();
    set({ user: null, session: null });
  },
  setSession: (session) => set({ session, user: session?.user ?? null }),
}));

// Set up auth state listener
supabase.auth.onAuthStateChange((event, session) => {
  useAuthStore.getState().setSession(session);
});