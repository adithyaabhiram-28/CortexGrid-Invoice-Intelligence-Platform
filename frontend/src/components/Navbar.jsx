import React from 'react';
import { useAuth } from '../context/AuthContext';
import { LogOut, User, UploadCloud } from 'lucide-react';

const Navbar = ({ pageTitle, onOpenUploadModal }) => {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 px-6 flex items-center justify-between sticky top-0 z-10">
      <div>
        <h2 className="text-lg font-semibold text-white tracking-tight">{pageTitle}</h2>
      </div>

      <div className="flex items-center space-x-4">
        {onOpenUploadModal && (
          <button
            onClick={onOpenUploadModal}
            className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-semibold shadow-md shadow-cyan-500/20 transition-all duration-150"
          >
            <UploadCloud className="w-4 h-4" />
            <span>Upload Invoice</span>
          </button>
        )}

        <div className="h-4 w-[1px] bg-slate-800"></div>

        {/* User Profile */}
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 font-semibold text-xs">
            {user?.name ? user.name.charAt(0).toUpperCase() : <User className="w-4 h-4" />}
          </div>
          <div className="hidden sm:block text-left">
            <p className="text-xs font-semibold text-slate-200">{user?.name || 'User'}</p>
            <span className="text-[10px] uppercase font-bold text-cyan-400 bg-cyan-950 px-1.5 py-0.5 rounded border border-cyan-800">
              {user?.role === 'admin' ? 'Admin' : 'Finance User'}
            </span>
          </div>
        </div>

        {/* Logout Button */}
        <button
          onClick={logout}
          title="Logout"
          className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800/80 transition-colors"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};

export default Navbar;
