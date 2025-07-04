import { supabase } from './supabase';
import { useState, useEffect } from 'react';

// Define the base URL for API calls
const API_BASE_URL = 'http://localhost:8000'; // Change this to your actual backend URL

// Question interfaces
export interface FormattedQuestion {
  id: string;
  type: 'math' | 'reading' | 'writing';
  content: string;
  choices: Record<string, string>;
  correctAnswer: string;
  explanation: string;
  category?: string;
}

interface RawQuestion {
  id: string;
  section: string;
  module: number;
  question_number: number;
  type: string;
  category: string;
  stimulus: string;
  choices?: Record<string, string>;
  correct?: string;
  answer?: string;
}

// Format a raw question from the API to our application format
const formatQuestion = (question: any): FormattedQuestion => {
  // Map section to type
  const type = question.section === 'Math' 
    ? 'math' 
    : question.section === 'Reading and Writing' 
      ? 'reading' 
      : 'writing';
  
  return {
    id: question.id,
    type,
    content: question.content,
    choices: question.choices || {},
    correctAnswer: question.correctAnswer || 'A',
    explanation: question.explanation || 'Detailed explanation would be provided here.',
    category: question.category,
  };
};

// Service for handling practice-related API calls
export const practiceService = {
  // Fetch SAT practice questions from the backend
  async fetchSatQuestions(module?: string, questionType?: string, section?: string) {
    try {
      // Build query parameters
      const queryParams = new URLSearchParams();
      if (module) queryParams.append('module', module);
      if (questionType) queryParams.append('question_type', questionType);
      if (section) queryParams.append('section', section);
      
      // Make request to backend (removed authentication for now)
      const response = await fetch(`${API_BASE_URL}/api/v1/practice/sat-questions?${queryParams.toString()}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (!response.ok) {
        throw new Error(`Error fetching questions: ${response.status}`);
      }
      
      const rawQuestions = await response.json();
      return rawQuestions.map(formatQuestion);
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
  },
  
  // Fetch questions from local JSON file
  async fetchLocalQuestions() {
    try {
      const response = await fetch('/digital_sat_full.json');
      if (!response.ok) {
        throw new Error('Failed to load questions');
      }
      const data: RawQuestion[] = await response.json();
      
      if (!data || data.length === 0) {
        throw new Error('No questions available');
      }
      
      return data.map(formatQuestion);
    } catch (error) {
      console.error('Error fetching local questions:', error);
      throw error;
    }
  }
};

// React hook for using questions with backend API
export const useBackendQuestions = () => {
  const [questions, setQuestions] = useState<FormattedQuestion[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        setLoading(true);
        const formattedQuestions = await practiceService.fetchSatQuestions();
        setQuestions(formattedQuestions);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchQuestions();
  }, []);

  // Get a random question, filtered by type if specified
  const getNextQuestion = (questionType?: string): FormattedQuestion | null => {
    if (questions.length === 0) return null;

    let filteredQuestions = questions;
    
    // Filter by type if specified
    if (questionType) {
      filteredQuestions = questions.filter(q => 
        q.type.toLowerCase().includes(questionType.toLowerCase())
      );
      
      // If no matches, return a random question from all questions
      if (filteredQuestions.length === 0) {
        filteredQuestions = questions;
      }
    }
    
    // Get a random question
    const randomIndex = Math.floor(Math.random() * filteredQuestions.length);
    return filteredQuestions[randomIndex];
  };

  return {
    loading,
    error,
    questions,
    getNextQuestion
  };
};