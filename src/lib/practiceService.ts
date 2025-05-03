import { useState, useEffect } from 'react';

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
const formatQuestion = (question: RawQuestion): FormattedQuestion => {
  const type = question.section.toLowerCase().includes('math') 
    ? 'math' 
    : question.section.toLowerCase().includes('reading') 
      ? 'reading' 
      : 'writing';
  
  // Generate a simple explanation for now (in a real app, you'd have real explanations)
  const explanation = `This question tests your knowledge of ${question.category}.`;
  
  return {
    id: question.id,
    type,
    content: question.stimulus,
    choices: question.choices || {},
    correctAnswer: question.correct || question.answer || 'A',
    explanation,
    category: question.category,
  };
};

export const useInfiniteQuestions = () => {
  const [questions, setQuestions] = useState<FormattedQuestion[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        setLoading(true);
        const response = await fetch('/digital_sat_full.json');
        if (!response.ok) {
          throw new Error('Failed to load questions');
        }
        const data: RawQuestion[] = await response.json();
        
        if (!data || data.length === 0) {
          throw new Error('No questions available');
        }
        
        const formattedQuestions = data.map(formatQuestion);
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
    getNextQuestion
  };
};