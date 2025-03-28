# SAT Prep Platform

A modern, interactive SAT preparation platform built with React, TypeScript, and Supabase.

## 🚀 Features

- **Authentication System**
  - Email/password signup and login
  - Profile management
  - Session persistence

- **Interactive Dashboard**
  - Performance analytics
  - Progress tracking
  - Score visualization
  - Study time monitoring

- **Practice System**
  - Multiple practice modes:
    - Subject-specific practice
    - Topic focus mode
    - Infinite practice mode (AI-powered)
  - Real-time scoring
    - Point system
    - Streak tracking
  - Detailed explanations
  - Timer functionality

- **Course Management**
  - Organized by subjects and topics
  - Difficulty levels
  - Progress tracking
  - Adaptive learning path

- **Community Features**
  - Discussion forum
  - Post sharing
  - User interactions

- **Achievement System**
  - Progress-based rewards
  - Skill recognition
  - Learning milestones

- **Settings & Customization**
  - Dark/Light mode
  - Notification preferences
  - Privacy controls
  - Account management

## 🛠 Technology Stack

- **Frontend**
  - React 18
  - TypeScript
  - Tailwind CSS
  - Chart.js
  - Lucide React (icons)
  - Zustand (state management)

- **Backend**
  - Supabase
  - PostgreSQL
  - Row Level Security (RLS)

## 📦 Project Structure

```
src/
├── components/
│   ├── Analytics/
│   │   └── AnalyticsDashboard.tsx
│   ├── Auth/
│   │   ├── LoginForm.tsx
│   │   └── RegisterForm.tsx
│   ├── Community/
│   │   └── CommunityForum.tsx
│   ├── Course/
│   │   └── CourseSection.tsx
│   ├── Practice/
│   │   └── PracticeQuestion.tsx
│   ├── Profile/
│   │   └── ProfileAchievements.tsx
│   └── Settings/
│       └── SettingsSection.tsx
├── store/
│   ├── authStore.ts
│   └── courseStore.ts
├── lib/
│   └── supabase.ts
└── App.tsx
```

## 🗄️ Database Schema

### Tables

1. **profiles**
   - `id` (uuid, PK)
   - `full_name` (text)
   - `email` (text)
   - `created_at` (timestamp)
   - `updated_at` (timestamp)

2. **subjects**
   - `id` (uuid, PK)
   - `name` (text)
   - `description` (text)
   - `icon` (text)
   - `created_at` (timestamp)

3. **topics**
   - `id` (uuid, PK)
   - `subject_id` (uuid, FK)
   - `name` (text)
   - `description` (text)
   - `difficulty` (integer)
   - `order_index` (integer)
   - `created_at` (timestamp)

4. **user_progress**
   - `id` (uuid, PK)
   - `user_id` (uuid, FK)
   - `topic_id` (uuid, FK)
   - `completed_exercises` (integer)
   - `correct_answers` (integer)
   - `last_attempt_at` (timestamp)
   - `created_at` (timestamp)

## 🔐 Security

### Row Level Security (RLS)

- **profiles**: Users can only view and update their own profiles
- **subjects**: Viewable by all authenticated users
- **topics**: Viewable by all authenticated users
- **user_progress**: Users can only view and update their own progress

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sat-prep-platform
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   Create a `.env` file:
   ```
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

## 🧪 Practice Modes

### Subject Practice
- Choose specific subjects
- Track progress per subject
- Adaptive difficulty

### Topic Focus
- Select specific topics
- Detailed explanations
- Progress tracking

### Infinite Mode
- AI-generated questions
- Continuous practice
- Dynamic difficulty adjustment

## 📊 Analytics

The dashboard provides:
- Score trends
- Topic performance
- Study time tracking
- Achievement progress
- Recent activity

## 👥 User Management

### Authentication
- Email/password signup
- Profile customization
- Session management

### Profile Features
- Progress tracking
- Achievement system
- Performance statistics

## 🎯 Future Enhancements

1. **AI Integration**
   - Personalized question generation
   - Adaptive learning paths
   - Performance prediction

2. **Social Features**
   - Study groups
   - Peer comparison
   - Leaderboards

3. **Content Expansion**
   - More practice questions
   - Video explanations
   - Study guides

4. **Mobile App**
   - Cross-platform support
   - Offline mode
   - Push notifications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.