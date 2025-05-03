import { supabase } from './supabase';

// Define the base URL for API calls
const API_BASE_URL = 'http://localhost:8000'; // Change this to your actual backend URL

// Service for handling practice-related API calls
export const practiceService = {
  // Fetch SAT practice questions from the backend
  async fetchSatQuestions(module?: string, questionType?: string) {
    try {
      // Build query parameters
      const queryParams = new URLSearchParams();
      if (module) queryParams.append('module', module);
      if (questionType) queryParams.append('question_type', questionType);
      
      // Get current user session for authentication
      const { data: { session } } = await supabase.auth.getSession();
      
      // Make request to backend
      const response = await fetch(`${API_BASE_URL}/api/v1/practice/sat-questions?${queryParams.toString()}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`Error fetching questions: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching SAT questions:', error);
      throw error;
    }
  },
  
  // Record practice session progress
  async recordProgress(topicId: string, correct: boolean) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      
      // Make request to backend to record progress
      const response = await fetch(`${API_BASE_URL}/api/v1/practice/record-progress`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`
        },
        body: JSON.stringify({
          topic_id: topicId,
          correct
        })
      });
      
      if (!response.ok) {
        throw new Error(`Error recording progress: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error recording practice progress:', error);
      throw error;
    }
  },
  
  // Direct Supabase update for progress (alternative approach)
  async updateProgressInSupabase(userId: string, topicId: string, completed: boolean, correct: boolean) {
    try {
      // Check if an entry already exists
      const { data: existingProgress } = await supabase
        .from('user_progress')
        .select('*')
        .eq('user_id', userId)
        .eq('topic_id', topicId)
        .single();
      
      if (existingProgress) {
        // Update existing progress
        const { data, error } = await supabase
          .from('user_progress')
          .update({
            completed_exercises: existingProgress.completed_exercises + (completed ? 1 : 0),
            correct_answers: existingProgress.correct_answers + (correct ? 1 : 0),
            last_attempt_at: new Date().toISOString()
          })
          .eq('id', existingProgress.id);
        
        if (error) throw error;
        return data;
      } else {
        // Insert new progress
        const { data, error } = await supabase
          .from('user_progress')
          .insert({
            user_id: userId,
            topic_id: topicId,
            completed_exercises: completed ? 1 : 0,
            correct_answers: correct ? 1 : 0,
            last_attempt_at: new Date().toISOString()
          });
        
        if (error) throw error;
        return data;
      }
    } catch (error) {
      console.error('Error updating progress in Supabase:', error);
      throw error;
    }
  }
};