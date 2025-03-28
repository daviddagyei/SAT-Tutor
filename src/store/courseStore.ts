import { create } from 'zustand';
import { supabase } from '../lib/supabase';

interface Subject {
  id: string;
  name: string;
  description: string;
  icon: string;
}

interface Topic {
  id: string;
  subject_id: string;
  name: string;
  description: string;
  difficulty: number;
  order_index: number;
}

interface Progress {
  id: string;
  topic_id: string;
  completed_exercises: number;
  correct_answers: number;
  last_attempt_at: string;
}

interface CourseState {
  subjects: Subject[];
  topics: Topic[];
  progress: Progress[];
  selectedSubject: Subject | null;
  selectedTopic: Topic | null;
  loading: boolean;
  error: string | null;
  fetchSubjects: () => Promise<void>;
  fetchTopics: (subjectId: string) => Promise<void>;
  fetchProgress: () => Promise<void>;
  selectSubject: (subject: Subject) => void;
  selectTopic: (topic: Topic) => void;
  updateProgress: (topicId: string, completed: boolean, correct: boolean) => Promise<void>;
}

export const useCourseStore = create<CourseState>((set, get) => ({
  subjects: [],
  topics: [],
  progress: [],
  selectedSubject: null,
  selectedTopic: null,
  loading: false,
  error: null,

  fetchSubjects: async () => {
    set({ loading: true, error: null });
    try {
      const { data, error } = await supabase
        .from('subjects')
        .select('*')
        .order('name');
      
      if (error) throw error;
      set({ subjects: data });
    } catch (error: any) {
      set({ error: error.message });
    } finally {
      set({ loading: false });
    }
  },

  fetchTopics: async (subjectId: string) => {
    set({ loading: true, error: null });
    try {
      const { data, error } = await supabase
        .from('topics')
        .select('*')
        .eq('subject_id', subjectId)
        .order('order_index');
      
      if (error) throw error;
      set({ topics: data });
    } catch (error: any) {
      set({ error: error.message });
    } finally {
      set({ loading: false });
    }
  },

  fetchProgress: async () => {
    set({ loading: true, error: null });
    try {
      const { data, error } = await supabase
        .from('user_progress')
        .select('*')
        .eq('user_id', supabase.auth.getUser().then(({ data }) => data.user?.id));
      
      if (error) throw error;
      set({ progress: data || [] });
    } catch (error: any) {
      set({ error: error.message });
    } finally {
      set({ loading: false });
    }
  },

  selectSubject: (subject: Subject) => {
    set({ selectedSubject: subject, selectedTopic: null });
    get().fetchTopics(subject.id);
  },

  selectTopic: (topic: Topic) => {
    set({ selectedTopic: topic });
  },

  updateProgress: async (topicId: string, completed: boolean, correct: boolean) => {
    const user = await supabase.auth.getUser();
    const userId = user.data.user?.id;
    
    if (!userId) return;

    try {
      const { data: existing } = await supabase
        .from('user_progress')
        .select('*')
        .eq('user_id', userId)
        .eq('topic_id', topicId)
        .single();

      if (existing) {
        await supabase
          .from('user_progress')
          .update({
            completed_exercises: existing.completed_exercises + (completed ? 1 : 0),
            correct_answers: existing.correct_answers + (correct ? 1 : 0),
            last_attempt_at: new Date().toISOString()
          })
          .eq('id', existing.id);
      } else {
        await supabase
          .from('user_progress')
          .insert({
            user_id: userId,
            topic_id: topicId,
            completed_exercises: completed ? 1 : 0,
            correct_answers: correct ? 1 : 0,
            last_attempt_at: new Date().toISOString()
          });
      }

      await get().fetchProgress();
    } catch (error: any) {
      set({ error: error.message });
    }
  }
}));