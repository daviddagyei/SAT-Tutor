import React, { useState, useEffect } from 'react';
import { 
  ChevronLeft, 
  ChevronRight, 
  Flag, 
  Timer, 
  HelpCircle, 
  Infinity, 
  Target,
  Star,
  Zap,
  BookOpen,
  Calculator,
  PenTool
} from 'lucide-react';
import { useCourseStore } from '../../store/courseStore';
import { useBackendQuestions, FormattedQuestion } from '../../lib/practiceService';
import '../Math/math.css';

type QuestionType = 'math' | 'reading' | 'writing';
type AnswerChoice = 'A' | 'B' | 'C' | 'D';

interface Question {
  id: number;
  type: QuestionType;
  content: string;
  choices: Record<AnswerChoice, string>;
  correctAnswer: AnswerChoice;
  explanation: string;
  topic?: string;
}

interface PracticeMode {
  id: string;
  name: string;
  description: string;
  icon: React.ElementType;
}

const practiceModes: PracticeMode[] = [
  {
    id: 'subject',
    name: 'Subject Practice',
    description: 'Practice questions from specific subjects',
    icon: BookOpen
  },
  {
    id: 'topic',
    name: 'Topic Focus',
    description: 'Focus on specific topics within subjects',
    icon: Target
  },
  {
    id: 'infinite',
    name: 'Infinite Mode',
    description: 'Endless practice with real SAT questions',
    icon: Infinity
  }
];

const sampleQuestions: Question[] = [
  {
    id: 1,
    type: 'math',
    topic: 'Basic Algebra',
    content: 'If 3x + 5 = 14, what is the value of x?',
    choices: {
      A: '2',
      B: '3',
      C: '4',
      D: '5'
    },
    correctAnswer: 'B',
    explanation: 'To solve for x:\n1. Subtract 5 from both sides: 3x = 9\n2. Divide both sides by 3: x = 3'
  },
  {
    id: 2,
    type: 'reading',
    topic: 'Main Idea',
    content: `In the given passage, the author's primary purpose is to:
    
    "The development of agriculture marked a significant turning point in human history. Before farming, our ancestors were hunter-gatherers, moving from place to place in search of food. The transition to agricultural societies allowed humans to settle in permanent locations, leading to the development of cities and civilizations."`,
    choices: {
      A: 'Compare hunting and farming techniques',
      B: 'Explain the impact of agriculture on human civilization',
      C: 'Argue against modern farming practices',
      D: 'Describe ancient hunting methods'
    },
    correctAnswer: 'B',
    explanation: 'The passage focuses on how the development of agriculture led to permanent settlements and the rise of civilizations, making B the correct answer.'
  }
];

function QuestionTimer({ timeLimit = 25, onTimeUp }: { timeLimit?: number; onTimeUp?: () => void }) {
  const [timeLeft, setTimeLeft] = useState(timeLimit * 60);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          onTimeUp?.();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [onTimeUp, timeLimit]);

  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;

  return (
    <div className="flex items-center space-x-2 text-gray-600">
      <Timer className="w-5 h-5" />
      <span className="font-mono">
        {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
      </span>
    </div>
  );
}

function AnswerChoice({ 
  label, 
  content, 
  selected, 
  correct, 
  showAnswer,
  onSelect,
  disabled
}: {
  label: AnswerChoice;
  content: string;
  selected: boolean;
  correct: boolean;
  showAnswer: boolean;
  onSelect: () => void;
  disabled: boolean;
}) {
  return (
    <button
      onClick={onSelect}
      disabled={disabled}
      className={`w-full p-4 rounded-lg border-2 transition-all duration-200 ${
        selected
          ? showAnswer
            ? correct
              ? 'border-green-500 bg-green-50'
              : 'border-red-500 bg-red-50'
            : 'border-indigo-500 bg-indigo-50'
          : showAnswer && correct
          ? 'border-green-500 bg-green-50'
          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      <div className="flex items-start space-x-4">
        <span className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          selected
            ? showAnswer
              ? correct
                ? 'bg-green-500 text-white'
                : 'bg-red-500 text-white'
              : 'bg-indigo-500 text-white'
            : showAnswer && correct
            ? 'bg-green-500 text-white'
            : 'bg-gray-200 text-gray-700'
        }`}>
          {label}
        </span>
        <span className="text-left text-gray-800 choice-math">
          <SmartContentRenderer content={content} />
        </span>
      </div>
    </button>
  );
}

function PracticeModeSelection({ 
  onModeSelect 
}: { 
  onModeSelect: (mode: string) => void 
}) {
  return (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Choose Practice Mode</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {practiceModes.map((mode) => {
          const Icon = mode.icon;
          return (
            <button
              key={mode.id}
              onClick={() => onModeSelect(mode.id)}
              className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 border-2 border-transparent hover:border-indigo-500"
            >
              <div className="flex flex-col items-center text-center space-y-4">
                <div className="p-3 rounded-full bg-indigo-50">
                  <Icon className="w-8 h-8 text-indigo-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{mode.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{mode.description}</p>
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function SubjectSelection({
  onSubjectSelect,
  onBack
}: {
  onSubjectSelect: (subjects: string[]) => void;
  onBack: () => void;
}) {
  const { subjects } = useCourseStore();
  const [selectedSubjects, setSelectedSubjects] = useState<string[]>([]);

  const toggleSubject = (subjectId: string) => {
    setSelectedSubjects(prev => 
      prev.includes(subjectId)
        ? prev.filter(id => id !== subjectId)
        : [...prev, subjectId]
    );
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex items-center space-x-4 mb-6">
        <button
          onClick={onBack}
          className="p-2 hover:bg-gray-100 rounded-full"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>
        <h2 className="text-2xl font-bold text-gray-900">Select Subjects</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {subjects.map((subject) => {
          const Icon = subject.icon === 'Calculator' ? Calculator :
                      subject.icon === 'BookOpen' ? BookOpen :
                      PenTool;
          return (
            <button
              key={subject.id}
              onClick={() => toggleSubject(subject.id)}
              className={`p-6 rounded-xl shadow-sm transition-all duration-200 ${
                selectedSubjects.includes(subject.id)
                  ? 'bg-indigo-50 border-2 border-indigo-500'
                  : 'bg-white hover:bg-gray-50 border-2 border-transparent'
              }`}
            >
              <div className="flex items-center space-x-4">
                <div className={`p-3 rounded-lg ${
                  selectedSubjects.includes(subject.id)
                    ? 'bg-indigo-100 text-indigo-600'
                    : 'bg-gray-100 text-gray-600'
                }`}>
                  <Icon className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">{subject.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{subject.description}</p>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      <div className="flex justify-end">
        <button
          onClick={() => onSubjectSelect(selectedSubjects)}
          disabled={selectedSubjects.length === 0}
          className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Start Practice
        </button>
      </div>
    </div>
  );
}

function TopicSelection({
  onTopicSelect,
  onBack
}: {
  onTopicSelect: (topics: string[]) => void;
  onBack: () => void;
}) {
  const { subjects, topics } = useCourseStore();
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [selectedSubject, setSelectedSubject] = useState<string | null>(null);

  const toggleTopic = (topicId: string) => {
    setSelectedTopics(prev => 
      prev.includes(topicId)
        ? prev.filter(id => id !== topicId)
        : [...prev, topicId]
    );
  };

  const filteredTopics = selectedSubject
    ? topics.filter(topic => topic.subject_id === selectedSubject)
    : [];

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex items-center space-x-4 mb-6">
        <button
          onClick={onBack}
          className="p-2 hover:bg-gray-100 rounded-full"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>
        <h2 className="text-2xl font-bold text-gray-900">Select Topics</h2>
      </div>

      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Choose Subject</h3>
        <div className="grid grid-cols-3 gap-4">
          {subjects.map(subject => (
            <button
              key={subject.id}
              onClick={() => setSelectedSubject(subject.id)}
              className={`p-4 rounded-lg ${
                selectedSubject === subject.id
                  ? 'bg-indigo-50 border-2 border-indigo-500'
                  : 'bg-white border-2 border-transparent hover:border-gray-200'
              }`}
            >
              {subject.name}
            </button>
          ))}
        </div>
      </div>

      {selectedSubject && (
        <>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Topics</h3>
          <div className="space-y-4 mb-8">
            {filteredTopics.map(topic => (
              <button
                key={topic.id}
                onClick={() => toggleTopic(topic.id)}
                className={`w-full p-4 rounded-lg text-left ${
                  selectedTopics.includes(topic.id)
                    ? 'bg-indigo-50 border-2 border-indigo-500'
                    : 'bg-white border-2 border-transparent hover:border-gray-200'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">{topic.name}</h4>
                    <p className="text-sm text-gray-600">{topic.description}</p>
                  </div>
                  <div className="flex items-center">
                    {Array.from({ length: topic.difficulty }).map((_, i) => (
                      <Star
                        key={i}
                        className="w-4 h-4 text-yellow-400 fill-current"
                      />
                    ))}
                  </div>
                </div>
              </button>
            ))}
          </div>

          <div className="flex justify-end">
            <button
              onClick={() => onTopicSelect(selectedTopics)}
              disabled={selectedTopics.length === 0}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Start Practice
            </button>
          </div>
        </>
      )}
    </div>
  );
}

function GameModeStats({
  score,
  streak,
  questionsAnswered
}: {
  score: number;
  streak: number;
  questionsAnswered: number;
}) {
  return (
    <div className="grid grid-cols-3 gap-4 mb-6">
      <div className="bg-white p-4 rounded-lg shadow-sm text-center">
        <div className="text-sm text-gray-600">Score</div>
        <div className="text-2xl font-bold text-indigo-600">{score}</div>
      </div>
      <div className="bg-white p-4 rounded-lg shadow-sm text-center">
        <div className="text-sm text-gray-600">Streak</div>
        <div className="flex items-center justify-center">
          <Zap className="w-5 h-5 text-yellow-400" />
          <span className="text-2xl font-bold text-yellow-600 ml-1">{streak}</span>
        </div>
      </div>
      <div className="bg-white p-4 rounded-lg shadow-sm text-center">
        <div className="text-sm text-gray-600">Questions</div>
        <div className="text-2xl font-bold text-green-600">{questionsAnswered}</div>
      </div>
    </div>
  );
}

// Smart content renderer that selectively applies math formatting
const SmartContentRenderer: React.FC<{ content: string; className?: string }> = ({ 
  content, 
  className = '' 
}) => {
  // Instead of treating entire text as math or not-math, 
  // we'll selectively format only specific math patterns
  const processedContent = React.useMemo(() => {
    if (!content) return content;
    
    // Split content into segments and identify which ones need math formatting
    // This is a more conservative approach that only formats clear math expressions
    let processedText = content;
    
    // Only apply math formatting to very specific patterns
    // Function notation - f(x), g(x), h(x)
    processedText = processedText.replace(/\bf\s*\(\s*x\s*\)/gi, '<em>f</em>(<em>x</em>)');
    processedText = processedText.replace(/\bg\s*\(\s*x\s*\)/gi, '<em>g</em>(<em>x</em>)');
    processedText = processedText.replace(/\bh\s*\(\s*x\s*\)/gi, '<em>h</em>(<em>x</em>)');
    
    // Clear fractions (only with slash)
    processedText = processedText.replace(/\b(\d{1,3})\s*\/\s*(\d{1,3})\b/g, '<span class="fraction"><sup>$1</sup>⁄<sub>$2</sub></span>');
    
    // Mathematical exponents - be very careful to avoid years and book titles
    // Only format if it's clearly a mathematical context
    processedText = processedText.replace(/([a-z])\^(\d+)/g, '$1<sup>$2</sup>'); // variables like x^2
    processedText = processedText.replace(/([a-z])²/g, '$1<sup>2</sup>');
    processedText = processedText.replace(/([a-z])³/g, '$1<sup>3</sup>');
    processedText = processedText.replace(/([a-z])⁴/g, '$1<sup>4</sup>');
    
    // Mathematical expressions with parentheses
    processedText = processedText.replace(/\(([a-z])\^(\d+)\)/g, '(<em>$1</em><sup>$2</sup>)');
    
    // Mathematical operators
    processedText = processedText.replace(/\s*×\s*/g, ' × ');
    processedText = processedText.replace(/\s*÷\s*/g, ' ÷ ');
    processedText = processedText.replace(/\s*±\s*/g, ' ± ');
    processedText = processedText.replace(/\s*≤\s*/g, ' ≤ ');
    processedText = processedText.replace(/\s*≥\s*/g, ' ≥ ');
    processedText = processedText.replace(/\s*≠\s*/g, ' ≠ ');
    
    // Square roots
    processedText = processedText.replace(/√\(([^)]+)\)/g, '<span class="sqrt">√<span class="sqrt-content">$1</span></span>');
    processedText = processedText.replace(/√([a-z]+)/g, '<span class="sqrt">√<span class="sqrt-content">$1</span></span>');
    
    // Mathematical constants
    processedText = processedText.replace(/\bπ\b/g, '<em>π</em>');
    processedText = processedText.replace(/\b∞\b/g, '<em>∞</em>');
    
    // Mathematical variables in equations (be conservative)
    processedText = processedText.replace(/\b([a-z])\s*=\s*(\d+)/g, '<em>$1</em> = $2');
    processedText = processedText.replace(/(\d+)\s*([a-z])\s*([+\-=])/g, '$1<em>$2</em> $3');
    
    // Coordinate pairs
    processedText = processedText.replace(/\((-?\d+(?:\.\d+)?),\s*(-?\d+(?:\.\d+)?)\)/g, '($1, $2)');
    
    // Clean up extra spaces
    processedText = processedText.replace(/\s+/g, ' ').trim();
    
    return processedText;
  }, [content]);

  return (
    <span 
      className={`${className} whitespace-pre-wrap math-content`}
      dangerouslySetInnerHTML={{ __html: processedContent }}
    />
  );
};

export function PracticeQuestion() {
  const [mode, setMode] = useState<string | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<AnswerChoice | null>(null);
  const [showAnswer, setShowAnswer] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);
  const [score, setScore] = useState(0);
  const [streak, setStreak] = useState(0);
  const [questionsAnswered, setQuestionsAnswered] = useState(0);
  const [selectedSubjects, setSelectedSubjects] = useState<string[]>([]);
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [isInfiniteMode, setIsInfiniteMode] = useState(false);
  
  // New state for infinite mode questions
  const [currentInfiniteQuestion, setCurrentInfiniteQuestion] = useState<FormattedQuestion | null>(null);
  const { loading, error, getNextQuestion } = useBackendQuestions();

  // Get the current question based on mode
  const currentQuestion = isInfiniteMode && currentInfiniteQuestion 
    ? {
        id: parseInt(currentInfiniteQuestion.id.split('-').pop() || '0'),
        type: currentInfiniteQuestion.type,
        content: currentInfiniteQuestion.content,
        choices: currentInfiniteQuestion.choices as Record<AnswerChoice, string>,
        correctAnswer: currentInfiniteQuestion.correctAnswer as AnswerChoice,
        explanation: currentInfiniteQuestion.explanation,
        topic: currentInfiniteQuestion.category
      } 
    : sampleQuestions[currentQuestionIndex];

  // Function to load a new infinite mode question
  const loadNextInfiniteQuestion = () => {
    const selectedType = selectedSubjects.length > 0 ? selectedSubjects[0] : undefined;
    const nextQuestion = getNextQuestion(selectedType);
    if (nextQuestion) {
      setCurrentInfiniteQuestion(nextQuestion);
    }
  };

  useEffect(() => {
    // Load the first infinite mode question when entering that mode
    if (isInfiniteMode && !currentInfiniteQuestion && !loading) {
      loadNextInfiniteQuestion();
    }
  }, [isInfiniteMode, loading]);

  const handleAnswerSelect = (answer: AnswerChoice) => {
    if (!showAnswer) {
      setSelectedAnswer(answer);
      setShowAnswer(true);
      setQuestionsAnswered(prev => prev + 1);

      const isCorrect = answer === currentQuestion.correctAnswer;
      if (isCorrect) {
        setScore(prev => prev + (100 * (streak + 1)));
        setStreak(prev => prev + 1);
        setShowExplanation(true);
      } else {
        setStreak(0);
      }
    }
  };

  const handleNextQuestion = () => {
    if (isInfiniteMode) {
      // Get the next random question for infinite mode
      loadNextInfiniteQuestion();
      setSelectedAnswer(null);
      setShowAnswer(false);
      setShowExplanation(false);
    } else if (currentQuestionIndex < sampleQuestions.length - 1) {
      // Move to next question in standard mode
      setCurrentQuestionIndex(prev => prev + 1);
      setSelectedAnswer(null);
      setShowAnswer(false);
      setShowExplanation(false);
    }
  };

  const handleModeSelect = (selectedMode: string) => {
    setMode(selectedMode);
    if (selectedMode === 'infinite') {
      setIsInfiniteMode(true);
      // Start infinite mode directly
      handleStartPractice();
    }
  };

  const handleStartPractice = () => {
    setCurrentQuestionIndex(0);
    setSelectedAnswer(null);
    setShowAnswer(false);
    setShowExplanation(false);
    setScore(0);
    setStreak(0);
    setQuestionsAnswered(0);
  };

  const handleBack = () => {
    setMode(null);
    setSelectedSubjects([]);
    setSelectedTopics([]);
    setIsInfiniteMode(false);
    setCurrentInfiniteQuestion(null);
  };

  if (!mode) {
    return <PracticeModeSelection onModeSelect={handleModeSelect} />;
  }

  if (loading && isInfiniteMode) {
    return (
      <div className="max-w-4xl mx-auto p-6 text-center">
        <h2 className="text-xl font-medium text-gray-700">Loading questions...</h2>
        <div className="mt-4 flex justify-center">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-500"></div>
        </div>
      </div>
    );
  }

  if (error && isInfiniteMode) {
    return (
      <div className="max-w-4xl mx-auto p-6 text-center">
        <h2 className="text-xl font-medium text-red-600">Error loading questions</h2>
        <p className="mt-2 text-gray-600">{error}</p>
        <button
          onClick={handleBack}
          className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
        >
          Go Back
        </button>
      </div>
    );
  }

  if (mode === 'subject' && selectedSubjects.length === 0) {
    return (
      <SubjectSelection
        onSubjectSelect={(subjects) => {
          setSelectedSubjects(subjects);
          handleStartPractice();
        }}
        onBack={handleBack}
      />
    );
  }

  if (mode === 'topic' && selectedTopics.length === 0) {
    return (
      <TopicSelection
        onTopicSelect={(topics) => {
          setSelectedTopics(topics);
          handleStartPractice();
        }}
        onBack={handleBack}
      />
    );
  }

  // Ensure we have a question to display
  if (isInfiniteMode && !currentInfiniteQuestion) {
    return (
      <div className="max-w-4xl mx-auto p-6 text-center">
        <h2 className="text-xl font-medium text-gray-700">No questions available</h2>
        <button
          onClick={handleBack}
          className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
        >
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <button
              onClick={handleBack}
              className="p-2 hover:bg-gray-100 rounded-full"
            >
              <ChevronLeft className="w-6 h-6" />
            </button>
            <h2 className="text-2xl font-bold text-gray-900">Practice Question</h2>
            <span className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium">
              {currentQuestion.type.charAt(0).toUpperCase() + currentQuestion.type.slice(1)}
            </span>
          </div>
          <QuestionTimer
            onTimeUp={() => {
              if (!showAnswer) {
                setShowAnswer(true);
                setStreak(0);
              }
            }}
          />
        </div>

        <GameModeStats
          score={score}
          streak={streak}
          questionsAnswered={questionsAnswered}
        />
      </div>

      <div className="bg-white rounded-xl shadow-sm p-8">
        <div className="prose max-w-none mb-8">
          <div className="text-lg text-gray-800 question-math">
            <SmartContentRenderer content={currentQuestion.content} />
          </div>
        </div>

        <div className="space-y-4">
          {(Object.keys(currentQuestion.choices) as AnswerChoice[]).map((choice) => (
            <AnswerChoice
              key={choice}
              label={choice}
              content={currentQuestion.choices[choice]}
              selected={selectedAnswer === choice}
              correct={choice === currentQuestion.correctAnswer}
              showAnswer={showAnswer}
              onSelect={() => handleAnswerSelect(choice)}
              disabled={showAnswer}
            />
          ))}
        </div>

        {showExplanation && (
          <div className="mt-8 p-4 bg-green-50 rounded-lg">
            <div className="flex items-start space-x-3">
              <HelpCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-medium text-green-900">Explanation</h3>
                <div className="mt-1 text-green-700">
                  <SmartContentRenderer content={currentQuestion.explanation} />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="mt-6 flex items-center justify-between">
        <button
          onClick={() => setShowExplanation(true)}
          className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
        >
          <Flag className="w-5 h-5" />
          <span>Flag for Review</span>
        </button>

        {showAnswer && (
          <button
            onClick={handleNextQuestion}
            className="flex items-center space-x-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            <span>Next Question</span>
            <ChevronRight className="w-5 h-5" />
          </button>
        )}
      </div>
    </div>
  );
}