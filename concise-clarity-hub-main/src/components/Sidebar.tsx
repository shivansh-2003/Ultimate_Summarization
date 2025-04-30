import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FileText, User, Mic, Play, Video, Globe, File } from 'lucide-react';
import { cn } from '@/lib/utils';

type NavItem = {
  name: string;
  path: string;
  icon: React.ElementType;
};

const navItems: NavItem[] = [
  { name: 'Document', path: '/app/document', icon: FileText },
  { name: 'Legal', path: '/app/legal', icon: File },
  { name: 'Resume', path: '/app/resume', icon: User },
  { name: 'Audio', path: '/app/audio', icon: Mic },
  { name: 'YouTube', path: '/app/youtube', icon: Play },
  { name: 'Video', path: '/app/video', icon: Video },
  { name: 'Website', path: '/app/website', icon: Globe },
];

interface SidebarProps {
  isOpen: boolean;
  toggleSidebar: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, toggleSidebar }) => {
  const location = useLocation();

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="md:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={toggleSidebar}
        />
      )}
      
      {/* Sidebar */}
      <aside 
        className={cn(
          "fixed md:static inset-y-0 left-0 z-50 md:z-0 w-64 bg-jetBlack transform transition-transform duration-300 ease-in-out",
          isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0",
          "flex flex-col border-r border-muted"
        )}
      >
        <div className="flex items-center justify-between p-4 border-b border-muted">
          <Link to="/" className="text-lg font-semibold text-white">
            <span className="text-white">Ultimate</span>{" "}
            <span className="text-vibrantOrange">Summarizer</span>
          </Link>
          <button
            onClick={toggleSidebar}
            className="md:hidden text-white hover:text-vibrantOrange"
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              width="24" 
              height="24" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            >
              <path d="M18 6 6 18"></path>
              <path d="m6 6 12 12"></path>
            </svg>
          </button>
        </div>
        
        <nav className="flex-1 p-4 overflow-y-auto">
          <ul className="space-y-2">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              const Icon = item.icon;
              return (
                <li key={item.name}>
                  <Link
                    to={item.path}
                    className={cn(
                      "flex items-center gap-3 px-3 py-3 rounded-md transition-colors",
                      isActive 
                        ? "bg-vibrantOrange text-white" 
                        : "text-white hover:bg-darkGray"
                    )}
                  >
                    <Icon 
                      className={cn(
                        "w-5 h-5",
                        isActive ? "text-white" : "text-white"
                      )} 
                    />
                    <span>{item.name}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        <div className="p-4 border-t border-muted">
          <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-white hover:text-vibrantOrange transition-colors">
            <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" className="feather feather-github">
              <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
            </svg>
            <span>GitHub</span>
          </a>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
