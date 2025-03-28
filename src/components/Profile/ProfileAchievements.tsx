import React from 'react';
import { Trophy, Star, Target, Brain, BookOpen, Clock, Award } from 'lucide-react';

interface Achievement {
  id: number;
  title: string;
  description: string;
  icon: React.ElementType;
  progress: number;
  total: number;
  completed: boolean;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
}

const achievements: Achievement[] = [
  {
    id: 1,
    title: "Perfect Score",
    description: "Score 800 on any section",
    icon: Trophy,
    progress: 780,
    total: 800,
    completed: false,
    rarity: 'legendary'
  },
  {
    id: 2,
    title: "Quick Learner",
    description: "Complete 50 practice questions in one day",
    icon: Brain,
    progress: 50,
    total: 50,
    completed: true,
    rarity: 'common'
  },
  {
    id: 3,
    title: "Math Master",
    description: "Get 10 perfect scores on math practice sets",
    icon: Target,
    progress: 7,
    total: 10,
    completed: false,
    rarity: 'rare'
  },
  {
    id: 4,
    title: "Reading Champion",
    description: "Complete all reading comprehension sections",
    icon: BookOpen,
    progress: 15,
    total: 20,
    completed: false,
    rarity: 'epic'
  }
];

const rarityColors = {
  common: 'bg-gray-100 text-gray-600',
  rare: 'bg-blue-100 text-blue-600',
  epic: 'bg-purple-100 text-purple-600',
  legendary: 'bg-yellow-100 text-yellow-600'
};

export function ProfileAchievements() {
  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Achievements</h2>
        <p className="text-gray-600">Track your progress and earn rewards</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Statistics</h3>
            <Award className="w-6 h-6 text-indigo-600" />
          </div>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                <span>Total Achievements</span>
                <span>12/30</span>
              </div>
              <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-600 rounded-full" style={{ width: '40%' }} />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                <span>Rare Achievements</span>
                <span>3/10</span>
              </div>
              <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full bg-blue-600 rounded-full" style={{ width: '30%' }} />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                <span>Legendary Achievements</span>
                <span>1/5</span>
              </div>
              <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full bg-yellow-600 rounded-full" style={{ width: '20%' }} />
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Recent Unlocks</h3>
            <Star className="w-6 h-6 text-indigo-600" />
          </div>
          <div className="space-y-4">
            {achievements
              .filter(a => a.completed)
              .map(achievement => (
                <div key={achievement.id} className="flex items-center space-x-3">
                  <achievement.icon className="w-5 h-5 text-indigo-600" />
                  <span className="text-gray-800">{achievement.title}</span>
                  <span className="text-sm text-gray-500">2d ago</span>
                </div>
              ))}
          </div>
        </div>
      </div>

      <div className="space-y-6">
        {achievements.map(achievement => (
          <div key={achievement.id} className="bg-white p-6 rounded-xl shadow-sm">
            <div className="flex items-center space-x-4">
              <div className={`p-3 rounded-lg ${rarityColors[achievement.rarity]}`}>
                <achievement.icon className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-gray-900">{achievement.title}</h3>
                  <span className={`px-3 py-1 rounded-full text-sm ${rarityColors[achievement.rarity]}`}>
                    {achievement.rarity.charAt(0).toUpperCase() + achievement.rarity.slice(1)}
                  </span>
                </div>
                <p className="text-gray-600 text-sm mt-1">{achievement.description}</p>
                <div className="mt-4">
                  <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                    <span>Progress</span>
                    <span>{achievement.progress}/{achievement.total}</span>
                  </div>
                  <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-300 ${
                        achievement.completed ? 'bg-green-500' : 'bg-indigo-600'
                      }`}
                      style={{ width: `${(achievement.progress / achievement.total) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}