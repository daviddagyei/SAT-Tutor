/*
  # Add missing INSERT policy for profiles
  
  This migration adds the missing policy that allows new users to create their profile
  after signing up. Without this policy, new user registration fails with:
  "new row violates row-level security policy for table 'profiles'"
*/

CREATE POLICY "Users can insert their own profile"
  ON profiles
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = id);
