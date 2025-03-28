import React, { useEffect } from 'react';
import { Calculator, BookOpen, PenTool, ChevronRight, Star } from 'lucide-react';
import { useCourseStore } from '../../store/courseStore';

const icons = {
  Calculator,
  BookOpen,
  PenTool
};

export function CourseSection() {
  const {
    subjects,
    topics,
    progress,
    selectedSubject,
    loading,
    error,
    fetchSubjects,
    selectSubject,
    selectTopic
  } = useCourseStore();

  useEffect(() => {
    fetchSubjects();
  }, [fetchSubjects]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-600 p-4">
        Error: {error}
      </div>
    );
  }

  const getTopicProgress = (topicId: string) => {
    const topicProgress = progress.find(p => p.topic_id === topicId);
    if (!topicProgress) return { completed: 0, accuracy: 0 };
    
    const accuracy = topicProgress.completed_exercises > 0
      ? (topicProgress.correct_answers / topicProgress.completed_exercises) * 100
      : 0;
    
    return {
      completed: topicProgress.completed_exercises,
      accuracy
    };
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {subjects.map(subject => {
          const Icon = icons[subject.icon as keyof typeof icons];
          return (
            <button
              key={subject.id}
              onClick={() => selectSubject(subject)}
              className={`p-6 rounded-xl shadow-sm transition-all duration-200 ${
                selectedSubject?.id === subject.id
                  ? 'bg-indigo-50 border-2 border-indigo-500'
                  : 'bg-white hover:bg-gray-50 border-2 border-transparent'
              }`}
            >
              <div className="flex items-start space-x-4">
                <div className={`p-3 rounded-lg ${
                  selectedSubject?.id === subject.id
                    ? 'bg-indigo-100 text-indigo-600'
                    : 'bg-gray-100 text-gray-600'
                }`}>
                  <Icon className="w-6 h-6" />
                </div>
                <div className="flex-1 text-left">
                  <h3 className="font-semibold text-gray-900">{subject.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{subject.description}</p>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {selectedSubject && topics.length > 0 && (
        <div className="mt-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">
            {selectedSubject.name} Topics
          </h2>
          <div className="space-y-4">
            {topics.map(topic => {
              const progress = getTopicProgress(topic.id);
              return (
                <div
                  key={topic.id}
                  onClick={() => selectTopic(topic)}
                  className="bg-white rounded-lg shadow-sm p-6 cursor-pointer hover:bg-gray-50 transition-colors duration-200"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h3 className="font-semibold text-gray-900">{topic.name}</h3>
                        <div className="flex items-center">
                          {Array.from({ length: topic.difficulty }).map((_, i) => (
                            <Star
                              key={i}
                              className="w-4 h-4 text-yellow-400 fill-current"
                            />
                          ))}
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{topic.description}</p>
                      
                      {progress.completed > 0 && (
                        <div className="mt-4 flex items-center space-x-4 text-sm">
                          <span className="text-gray-600">
                            Completed: {progress.completed} exercises
                          </span>
                          <span className="text-gray-600">
                            Accuracy: {progress.accuracy.toFixed(1)}%
                          </span>
                        </div>
                      )}
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-400" />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}