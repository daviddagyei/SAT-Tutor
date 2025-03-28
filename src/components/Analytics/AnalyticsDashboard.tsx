import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import { format } from 'date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const generateDummyData = () => {
  const dates = Array.from({ length: 7 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - i);
    return format(date, 'MMM dd');
  }).reverse();

  return {
    labels: dates,
    datasets: [
      {
        label: 'Math Score',
        data: dates.map(() => Math.floor(Math.random() * 100) + 500),
        borderColor: 'rgb(99, 102, 241)',
        backgroundColor: 'rgba(99, 102, 241, 0.5)',
      },
      {
        label: 'Reading Score',
        data: dates.map(() => Math.floor(Math.random() * 100) + 500),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
      },
    ],
  };
};

const options = {
  responsive: true,
  plugins: {
    legend: {
      position: 'top' as const,
    },
    title: {
      display: true,
      text: 'Score Progress Over Time',
    },
  },
};

export function AnalyticsDashboard() {
  const progressData = generateDummyData();
  
  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Performance Analytics</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Average Score</h3>
          <p className="text-3xl font-bold text-indigo-600">1420</p>
          <p className="text-sm text-gray-500">+50 points from last week</p>
        </div>
        
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Questions Completed</h3>
          <p className="text-3xl font-bold text-blue-600">247</p>
          <p className="text-sm text-gray-500">Last 7 days</p>
        </div>
        
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Study Time</h3>
          <p className="text-3xl font-bold text-green-600">12.5h</p>
          <p className="text-sm text-gray-500">This week</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-sm">
        <Line options={options} data={progressData} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Topic Performance</h3>
          <Bar
            options={{
              indexAxis: 'y' as const,
              plugins: {
                title: {
                  display: true,
                  text: 'Accuracy by Topic',
                },
              },
            }}
            data={{
              labels: ['Algebra', 'Geometry', 'Grammar', 'Reading Comp', 'Vocabulary'],
              datasets: [
                {
                  label: 'Accuracy %',
                  data: [85, 72, 90, 68, 78],
                  backgroundColor: 'rgba(99, 102, 241, 0.5)',
                },
              ],
            }}
          />
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            {[
              { type: 'Practice Test', score: '720/800', date: '2h ago' },
              { type: 'Math Quiz', score: '9/10', date: '5h ago' },
              { type: 'Reading Practice', score: '85%', date: 'Yesterday' },
            ].map((activity, index) => (
              <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100">
                <div>
                  <p className="font-medium text-gray-800">{activity.type}</p>
                  <p className="text-sm text-gray-500">{activity.date}</p>
                </div>
                <span className="text-indigo-600 font-medium">{activity.score}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}