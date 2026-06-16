import React from 'react';
import useStore from '../store/useStore';
import { User, LogOut } from 'lucide-react';

const Profile = () => {
  const { user, logout } = useStore();

  return (
    <div className="max-w-2xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold text-textMain mb-2">User Profile</h1>
        <p className="text-textMuted">Manage your preferences and agent persona.</p>
      </div>

      <div className="glass-panel p-8">
        <div className="flex items-center gap-6 mb-8 pb-8 border-b border-surfaceHighlight">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary to-primaryHover flex items-center justify-center font-bold text-white text-3xl shadow-lg shadow-primary/25">
            {user?.name?.charAt(0) || <User size={32} />}
          </div>
          <div>
            <h2 className="text-2xl font-bold text-textMain">{user?.name || 'Guest'}</h2>
            <p className="text-textMuted">{user?.email || 'Not logged in'}</p>
          </div>
        </div>

        <div className="space-y-6">
          <div>
            <h3 className="text-sm font-semibold text-textMuted uppercase tracking-wider mb-4">Account Actions</h3>
            <button 
              onClick={logout}
              className="flex items-center gap-2 px-6 py-2.5 bg-danger/10 hover:bg-danger/20 text-danger rounded-xl font-medium transition-colors border border-danger/20"
            >
              <LogOut size={18} />
              Sign Out
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
