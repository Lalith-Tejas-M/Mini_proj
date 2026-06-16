import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, UploadCloud, History, LineChart, User } from 'lucide-react';

const Sidebar = () => {
  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Upload Knowledge', path: '/upload', icon: UploadCloud },
    { name: 'History', path: '/history', icon: History },
    { name: 'Analytics', path: '/analytics', icon: LineChart },
    { name: 'Profile', path: '/profile', icon: User },
  ];

  return (
    <div className="w-64 bg-surface border-r border-surfaceHighlight flex flex-col">
      <div className="p-6 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-white font-bold text-xl">
          K
        </div>
        <span className="font-bold text-lg tracking-wide text-textMain">Knowledge AI</span>
      </div>
      
      <nav className="flex-1 px-4 py-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                isActive 
                  ? 'bg-primary/10 text-primary font-medium' 
                  : 'text-textMuted hover:bg-surfaceHighlight hover:text-textMain'
              }`
            }
          >
            <item.icon size={20} />
            <span>{item.name}</span>
          </NavLink>
        ))}
      </nav>
      
      <div className="p-4 m-4 rounded-xl bg-surfaceHighlight border border-surfaceHighlight/50">
        <p className="text-xs text-textMuted text-center">
          Agentic Core v1.0<br/>Status: <span className="text-success">Online</span>
        </p>
      </div>
    </div>
  );
};

export default Sidebar;
