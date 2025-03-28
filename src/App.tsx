import React, { useState } from 'react';
import {
  BookOpen,
  BarChart3,
  Trophy,
  Users,
  Settings,
  LogOut,
  Bell,
  Brain,
  Target,
  Clock,
  TrendingUp,
  Star,
  Calendar,
  CheckCircle2,
  X,
  ChevronLeft,
  ChevronRight,
  Flag,
  Timer,
  HelpCircle,
  GraduationCap
} from 'lucide-react';
import { useAuthStore } from './store/authStore';
import { LoginForm } from './components/Auth/LoginForm';
import { AnalyticsDashboard } from './components/Analytics/AnalyticsDashboard';
import { CommunityForum } from './components/Community/CommunityForum';
import { ProfileAchievements } from './components/Profile/ProfileAchievements';
import { PracticeQuestion } from './components/Practice/PracticeQuestion';
import { CourseSection } from './components/Course/CourseSection';
import { SettingsSection } from './components/Settings/SettingsSection';

function SidebarLink({ 
  icon: Icon, 
  label, 
  active = false, 
  onClick 
}: { 
  icon: React.ElementType;
  label: string;
  active?: boolean;
  onClick?: () => void;
}) {
  return (
    <a
      href="#"
      onClick={(e) => {
        e.preventDefault();
        onClick?.();
      }}
      className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 transform hover:scale-102 ${
        active 
          ? 'bg-indigo-50 text-indigo-600' 
          : 'text-gray-600 hover:bg-gray-50'
      }`}
    >
      <Icon className="w-5 h-5" />
      <span className="font-medium">{label}</span>
    </a>
  );
}

function NotificationPanel({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  if (!isOpen) return null;

  return (
    <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
      <div className="p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800">Notifications</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="space-y-4">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <CheckCircle2 className="w-5 h-5 text-green-500" />
            </div>
            <div>
              <p className="text-sm text-gray-800">You completed today's practice session!</p>
              <p className="text-xs text-gray-500">2 hours ago</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <Star className="w-5 h-5 text-yellow-500" />
            </div>
            <div>
              <p className="text-sm text-gray-800">New achievement unlocked: Math Master</p>
              <p className="text-xs text-gray-500">Yesterday</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function App() {
  const [activeSection, setActiveSection] = useState('Dashboard');
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const { user, signOut } = useAuthStore();

  if (!user) {
    return <LoginForm />;
  }

  const renderContent = () => {
    switch (activeSection) {
      case 'Courses':
        return <CourseSection />;
      case 'Analytics':
        return <AnalyticsDashboard />;
      case 'Community':
        return <CommunityForum />;
      case 'Achievements':
        return <ProfileAchievements />;
      case 'Practice':
        return <PracticeQuestion />;
      case 'Settings':
        return <SettingsSection />;
      default:
        return <AnalyticsDashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 px-4 py-6">
        <div className="flex items-center space-x-3 px-4 mb-8">
          <BookOpen className="w-8 h-8 text-indigo-600" />
          <span className="text-xl font-bold text-gray-800">SAT Prep</span>
        </div>
        
        <nav className="space-y-1">
          <SidebarLink 
            icon={Brain} 
            label="Dashboard" 
            active={activeSection === 'Dashboard'} 
            onClick={() => setActiveSection('Dashboard')}
          />
          <SidebarLink 
            icon={GraduationCap} 
            label="Courses" 
            active={activeSection === 'Courses'}
            onClick={() => setActiveSection('Courses')}
          />
          <SidebarLink 
            icon={Target} 
            label="Practice" 
            active={activeSection === 'Practice'}
            onClick={() => setActiveSection('Practice')}
          />
          <SidebarLink 
            icon={BarChart3} 
            label="Analytics" 
            active={activeSection === 'Analytics'}
            onClick={() => setActiveSection('Analytics')}
          />
          <SidebarLink 
            icon={Trophy} 
            label="Achievements" 
            active={activeSection === 'Achievements'}
            onClick={() => setActiveSection('Achievements')}
          />
          <SidebarLink 
            icon={Users} 
            label="Community" 
            active={activeSection === 'Community'}
            onClick={() => setActiveSection('Community')}
          />
          <SidebarLink 
            icon={Settings} 
            label="Settings" 
            active={activeSection === 'Settings'}
            onClick={() => setActiveSection('Settings')}
          />
        </nav>

        <div className="mt-auto pt-8">
          <button 
            onClick={() => signOut()}
            className="flex items-center space-x-3 text-gray-600 hover:text-gray-800 px-4 py-3 w-full transition-colors duration-200 hover:bg-gray-50 rounded-lg"
          >
            <LogOut className="w-5 h-5" />
            <span className="font-medium">Sign Out</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-800">{activeSection}</h1>
            <div className="flex items-center space-x-4">
              <div className="relative">
                <button 
                  className={`p-2 rounded-lg transition-colors duration-200 ${
                    isNotificationsOpen 
                      ? 'bg-gray-100 text-gray-800' 
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                  onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
                >
                  <Bell className="w-6 h-6" />
                </button>
                <NotificationPanel 
                  isOpen={isNotificationsOpen}
                  onClose={() => setIsNotificationsOpen(false)}
                />
              </div>
              <div className="flex items-center space-x-3">
                <img
                  src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=32&h=32&q=80"
                  alt="Profile"
                  className="w-8 h-8 rounded-full ring-2 ring-white"
                />
                <span className="font-medium text-gray-800">Alex Chen</span>
              </div>
            </div>
          </div>
        </header>

        {/* Dynamic Content */}
        {renderContent()}
      </div>
    </div>
  );
}

export default App;