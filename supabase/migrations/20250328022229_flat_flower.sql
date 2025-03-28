/*
  # Add SAT Courses and Topics

  1. New Tables
    - `subjects`
      - `id` (uuid, primary key)
      - `name` (text) - Math, Reading, or Writing
      - `description` (text)
      - `icon` (text) - Icon name from Lucide
      - `created_at` (timestamptz)

    - `topics`
      - `id` (uuid, primary key)
      - `subject_id` (uuid, references subjects)
      - `name` (text)
      - `description` (text)
      - `difficulty` (int) - 1 to 5
      - `order` (int) - For ordering topics within a subject
      - `created_at` (timestamptz)

    - `user_progress`
      - `id` (uuid, primary key)
      - `user_id` (uuid, references profiles)
      - `topic_id` (uuid, references topics)
      - `completed_exercises` (int)
      - `correct_answers` (int)
      - `last_attempt_at` (timestamptz)
      - `created_at` (timestamptz)

  2. Security
    - Enable RLS on all tables
    - Add policies for authenticated users
*/

-- Create subjects table
CREATE TABLE subjects (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  description text NOT NULL,
  icon text NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- Create topics table
CREATE TABLE topics (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  subject_id uuid REFERENCES subjects ON DELETE CASCADE,
  name text NOT NULL,
  description text NOT NULL,
  difficulty int NOT NULL CHECK (difficulty BETWEEN 1 AND 5),
  order_index int NOT NULL,
  created_at timestamptz DEFAULT now(),
  UNIQUE (subject_id, order_index)
);

-- Create user progress table
CREATE TABLE user_progress (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES profiles ON DELETE CASCADE,
  topic_id uuid REFERENCES topics ON DELETE CASCADE,
  completed_exercises int DEFAULT 0,
  correct_answers int DEFAULT 0,
  last_attempt_at timestamptz,
  created_at timestamptz DEFAULT now(),
  UNIQUE (user_id, topic_id)
);

-- Enable RLS
ALTER TABLE subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_progress ENABLE ROW LEVEL SECURITY;

-- Policies for subjects
CREATE POLICY "Subjects are viewable by all authenticated users"
  ON subjects
  FOR SELECT
  TO authenticated
  USING (true);

-- Policies for topics
CREATE POLICY "Topics are viewable by all authenticated users"
  ON topics
  FOR SELECT
  TO authenticated
  USING (true);

-- Policies for user_progress
CREATE POLICY "Users can view their own progress"
  ON user_progress
  FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own progress"
  ON user_progress
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own progress"
  ON user_progress
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id);

-- Insert initial subjects
INSERT INTO subjects (name, description, icon) VALUES
  ('Math', 'Master SAT Math concepts from basic algebra to advanced problem-solving', 'Calculator'),
  ('Reading', 'Develop critical reading skills and improve comprehension', 'BookOpen'),
  ('Writing', 'Learn essential grammar rules and writing techniques', 'PenTool');

-- Insert initial topics for Math
INSERT INTO topics (subject_id, name, description, difficulty, order_index) VALUES
  ((SELECT id FROM subjects WHERE name = 'Math'), 'Basic Algebra', 'Linear equations, inequalities, and basic algebraic expressions', 1, 1),
  ((SELECT id FROM subjects WHERE name = 'Math'), 'Advanced Algebra', 'Quadratic equations, functions, and complex expressions', 3, 2),
  ((SELECT id FROM subjects WHERE name = 'Math'), 'Geometry', 'Angles, triangles, circles, and coordinate geometry', 2, 3),
  ((SELECT id FROM subjects WHERE name = 'Math'), 'Statistics', 'Mean, median, mode, standard deviation, and probability', 2, 4),
  ((SELECT id FROM subjects WHERE name = 'Math'), 'Advanced Functions', 'Polynomial, rational, and exponential functions', 4, 5);

-- Insert initial topics for Reading
INSERT INTO topics (subject_id, name, description, difficulty, order_index) VALUES
  ((SELECT id FROM subjects WHERE name = 'Reading'), 'Main Idea', 'Identifying central themes and main ideas in passages', 1, 1),
  ((SELECT id FROM subjects WHERE name = 'Reading'), 'Supporting Details', 'Finding and analyzing evidence that supports main ideas', 2, 2),
  ((SELECT id FROM subjects WHERE name = 'Reading'), 'Inference', 'Drawing conclusions based on implicit information', 3, 3),
  ((SELECT id FROM subjects WHERE name = 'Reading'), 'Author''s Purpose', 'Understanding author''s intent and rhetorical strategies', 3, 4),
  ((SELECT id FROM subjects WHERE name = 'Reading'), 'Vocabulary in Context', 'Understanding word meanings in context', 2, 5);

-- Insert initial topics for Writing
INSERT INTO topics (subject_id, name, description, difficulty, order_index) VALUES
  ((SELECT id FROM subjects WHERE name = 'Writing'), 'Grammar Basics', 'Subject-verb agreement and verb tenses', 1, 1),
  ((SELECT id FROM subjects WHERE name = 'Writing'), 'Punctuation', 'Proper use of commas, semicolons, and other punctuation marks', 2, 2),
  ((SELECT id FROM subjects WHERE name = 'Writing'), 'Sentence Structure', 'Combining sentences and avoiding run-ons', 2, 3),
  ((SELECT id FROM subjects WHERE name = 'Writing'), 'Rhetorical Skills', 'Organization, transitions, and rhetorical techniques', 3, 4),
  ((SELECT id FROM subjects WHERE name = 'Writing'), 'Style and Tone', 'Maintaining consistent style and appropriate tone', 3, 5);