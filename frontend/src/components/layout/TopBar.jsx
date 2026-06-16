import React from 'react';
import { Search, Bell } from 'lucide-react';
import useStore from '../../store/useStore';

const TopBar = () => {
  const user = useStore(state => state.user);

  return (
    <div className="h-16 bg-surface/50 backdrop-blur-md border-b border-surfaceHighlight flex items-center justify-between px-6 sticky top-0 z-10">
      <div className="flex-1 max-w-xl">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-textMuted" size={18} />
          <input 
            type="text" 
            placeholder="Search memory..." 
            className="w-full bg-background border border-surfaceHighlight rounded-full py-2 pl-10 pr-4 text-sm focus:outline-none focus:border-primary transition-colors text-textMain"
          />
        </div>
      </div>
      
      <div className="flex items-center gap-4 ml-4">
        <button className="p-2 text-textMuted hover:text-textMain transition-colors relative">
          <Bell size={20} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-primary rounded-full"></span>
        </button>
        <div className="flex items-center gap-3 pl-4 border-l border-surfaceHighlight">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-medium text-textMain">{user?.name || 'Guest'}</p>
            <p className="text-xs text-textMuted">{user?.email || 'Not logged in'}</p>
          </div>
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary to-primaryHover flex items-center justify-center font-bold text-white shadow-lg">
            {user?.name?.charAt(0) || 'G'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TopBar;
