import React, { useState } from 'react';
import { 
  User, 
  Moon, 
  Sun, 
  Bell, 
  Shield, 
  Trash2, 
  LogOut,
  Save,
  X,
  Check,
  ChevronRight
} from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

export function SettingsSection() {
  const { user, signOut } = useAuthStore();
  const [darkMode, setDarkMode] = useState(false);
  const [notifications, setNotifications] = useState(true);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleSaveProfile = async () => {
    setSaving(true);
    // TODO: Implement profile update
    await new Promise(resolve => setTimeout(resolve, 1000));
    setSaving(false);
  };

  const handleDeleteAccount = async () => {
    // TODO: Implement account deletion
    await signOut();
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-8">Settings</h2>

      <div className="space-y-8">
        {/* Profile Settings */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
            <User className="w-5 h-5 mr-2" />
            Profile Settings
          </h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Profile Picture
              </label>
              <div className="flex items-center space-x-4">
                <img
                  src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
                  alt="Profile"
                  className="w-16 h-16 rounded-full"
                />
                <button className="px-4 py-2 text-sm text-indigo-600 hover:bg-indigo-50 rounded-lg">
                  Change Photo
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  defaultValue="Alex Chen"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  defaultValue={user?.email}
                  disabled
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Bio
              </label>
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                rows={3}
                defaultValue="SAT prep enthusiast aiming for a perfect score!"
              />
            </div>

            <div className="flex justify-end">
              <button
                onClick={handleSaveProfile}
                disabled={saving}
                className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                <Save className="w-4 h-4 mr-2" />
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>

        {/* Appearance */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">
            Appearance
          </h3>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {darkMode ? (
                <Moon className="w-5 h-5 text-gray-600" />
              ) : (
                <Sun className="w-5 h-5 text-gray-600" />
              )}
              <span className="text-gray-700">Dark Mode</span>
            </div>
            <button
              onClick={() => setDarkMode(!darkMode)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                darkMode ? 'bg-indigo-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  darkMode ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>

        {/* Notifications */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
            <Bell className="w-5 h-5 mr-2" />
            Notifications
          </h3>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-700">Email Notifications</span>
              <button
                onClick={() => setNotifications(!notifications)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  notifications ? 'bg-indigo-600' : 'bg-gray-200'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    notifications ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          </div>
        </div>

        {/* Privacy & Security */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
            <Shield className="w-5 h-5 mr-2" />
            Privacy & Security
          </h3>

          <div className="space-y-4">
            <button
              onClick={() => {}}
              className="w-full flex items-center justify-between px-4 py-2 text-left hover:bg-gray-50 rounded-lg"
            >
              <span className="text-gray-700">Change Password</span>
              <ChevronRight className="w-5 h-5 text-gray-400" />
            </button>

            <button
              onClick={() => {}}
              className="w-full flex items-center justify-between px-4 py-2 text-left hover:bg-gray-50 rounded-lg"
            >
              <span className="text-gray-700">Two-Factor Authentication</span>
              <ChevronRight className="w-5 h-5 text-gray-400" />
            </button>

            <button
              onClick={() => {}}
              className="w-full flex items-center justify-between px-4 py-2 text-left hover:bg-gray-50 rounded-lg"
            >
              <span className="text-gray-700">Data & Privacy</span>
              <ChevronRight className="w-5 h-5 text-gray-400" />
            </button>
          </div>
        </div>

        {/* Danger Zone */}
        <div className="bg-red-50 rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-red-900 mb-6">
            Danger Zone
          </h3>

          {showDeleteConfirm ? (
            <div className="bg-white rounded-lg p-4">
              <p className="text-gray-700 mb-4">
                Are you sure you want to delete your account? This action cannot be undone.
              </p>
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  className="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  <X className="w-4 h-4 mr-2" />
                  Cancel
                </button>
                <button
                  onClick={handleDeleteAccount}
                  className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  <Check className="w-4 h-4 mr-2" />
                  Confirm Delete
                </button>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="flex items-center px-4 py-2 text-red-600 hover:bg-red-100 rounded-lg"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete Account
            </button>
          )}
        </div>

        {/* Sign Out */}
        <div className="flex justify-end">
          <button
            onClick={signOut}
            className="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}