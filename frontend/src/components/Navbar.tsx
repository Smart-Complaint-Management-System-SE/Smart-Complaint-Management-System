import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  MessageSquareWarning,
  LayoutDashboard,
  PlusCircle,
  ListFilter,
  ShieldCheck,
  Tags,
  LogOut,
  Sun,
  Moon,
  Menu,
  X,
  ChevronDown,
} from 'lucide-react';

interface Props {
  currentPath: string;
  navigate: (path: string) => void;
}

export const Navbar: React.FC<Props> = ({ currentPath, navigate }) => {
  const { user, logout, theme, toggleTheme } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);

  const handleNav = (path: string) => {
    navigate(path);
    setMobileMenuOpen(false);
    setProfileDropdownOpen(false);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItemClass = (path: string) => {
    const isActive = currentPath === path;
    return `relative inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
      isActive
        ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/25'
        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80 dark:text-slate-400 dark:hover:text-slate-100 dark:hover:bg-slate-800/60'
    }`;
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-slate-950/80 backdrop-blur-xl transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <div
          onClick={() => handleNav(user ? (user.role === 'admin' ? '/admin' : '/dashboard') : '/')}
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="relative">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 flex items-center justify-center text-white shadow-lg shadow-indigo-500/25 group-hover:scale-105 group-hover:shadow-indigo-500/35 transition-all">
              <MessageSquareWarning className="w-5 h-5" />
            </div>
            <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 border-2 border-white dark:border-slate-950 rounded-full"></span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-black text-lg tracking-tight bg-gradient-to-r from-slate-900 via-indigo-950 to-purple-950 dark:from-white dark:via-indigo-200 dark:to-purple-200 bg-clip-text text-transparent">
                SCMS
              </span>
              <span className="hidden sm:inline-block px-2 py-0.5 text-[9px] font-black uppercase tracking-wider bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 ring-1 ring-inset ring-indigo-500/20 rounded-md">
                Smart Grievance
              </span>
            </div>
            <p className="hidden md:block text-[11px] text-slate-500 dark:text-slate-400 font-medium -mt-0.5">
              Complaint Management System
            </p>
          </div>
        </div>

        {/* Desktop Nav Items */}
        <nav className="hidden md:flex items-center gap-1.5 p-1 rounded-2xl bg-slate-100/60 dark:bg-slate-900/60 border border-slate-200/60 dark:border-white/5">
          {!user ? (
            <>
              <button onClick={() => handleNav('/')} className={navItemClass('/')}>
                Home
              </button>
              <button onClick={() => handleNav('/login')} className={navItemClass('/login')}>
                Sign In
              </button>
              <button
                onClick={() => handleNav('/register')}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-500/25 hover:shadow-indigo-500/35 transition-all"
              >
                Get Started
              </button>
            </>
          ) : user.role === 'admin' ? (
            <>
              <button onClick={() => handleNav('/admin')} className={navItemClass('/admin')}>
                <ShieldCheck className="w-3.5 h-3.5" />
                Admin Dashboard
              </button>
              <button
                onClick={() => handleNav('/admin/categories')}
                className={navItemClass('/admin/categories')}
              >
                <Tags className="w-3.5 h-3.5" />
                Categories
              </button>
              <button onClick={() => handleNav('/complaints')} className={navItemClass('/complaints')}>
                <ListFilter className="w-3.5 h-3.5" />
                Registry View
              </button>
            </>
          ) : (
            <>
              <button onClick={() => handleNav('/dashboard')} className={navItemClass('/dashboard')}>
                <LayoutDashboard className="w-3.5 h-3.5" />
                Dashboard
              </button>
              <button onClick={() => handleNav('/complaints')} className={navItemClass('/complaints')}>
                <ListFilter className="w-3.5 h-3.5" />
                My Complaints
              </button>
              <button
                onClick={() => handleNav('/complaint/new')}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white shadow-md shadow-indigo-500/25 transition-all"
              >
                <PlusCircle className="w-3.5 h-3.5" />
                <span>Submit Ticket</span>
              </button>
            </>
          )}
        </nav>

        {/* Right Controls: Theme Toggle & User Avatar */}
        <div className="flex items-center gap-3">
          <button
            onClick={toggleTheme}
            aria-label="Toggle visual theme"
            className="p-2.5 rounded-xl text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800/80 transition-colors"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
          </button>

          {user && (
            <div className="relative">
              <button
                onClick={() => setProfileDropdownOpen((prev) => !prev)}
                className="flex items-center gap-2.5 p-1.5 pl-3 rounded-2xl hover:bg-slate-100 dark:hover:bg-slate-800/80 border border-slate-200/60 dark:border-white/10 transition-all group"
              >
                <div className="hidden sm:block text-right">
                  <div className="text-xs font-extrabold text-slate-900 dark:text-slate-100 leading-tight">
                    {user.name}
                  </div>
                  <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                    {user.role}
                  </div>
                </div>
                <div
                  className={`w-9 h-9 rounded-xl flex items-center justify-center font-black text-xs shadow-md ${
                    user.role === 'admin'
                      ? 'bg-gradient-to-br from-purple-600 to-indigo-600 text-white shadow-purple-500/25'
                      : 'bg-gradient-to-br from-indigo-600 to-cyan-600 text-white shadow-indigo-500/25'
                  }`}
                >
                  {user.name.slice(0, 2).toUpperCase()}
                </div>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-200 transition-transform" />
              </button>

              {/* Profile dropdown menu */}
              {profileDropdownOpen && (
                <>
                  <div
                    className="fixed inset-0 z-40"
                    onClick={() => setProfileDropdownOpen(false)}
                  />
                  <div className="absolute right-0 mt-2 w-64 rounded-3xl bg-white dark:bg-slate-900 shadow-2xl border border-slate-200/80 dark:border-white/10 z-50 p-2.5 animate-slide-up">
                    <div className="px-3.5 py-3 border-b border-slate-100 dark:border-slate-800/80">
                      <p className="text-[10px] font-black uppercase tracking-wider text-slate-400">
                        Signed in as
                      </p>
                      <p className="text-sm font-extrabold text-slate-900 dark:text-white truncate mt-0.5">
                        {user.name}
                      </p>
                      <p className="text-xs text-slate-500 dark:text-slate-400 truncate">
                        {user.email}
                      </p>
                      <div className="mt-2.5">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider ${
                            user.role === 'admin'
                              ? 'bg-purple-500/10 text-purple-700 dark:text-purple-300 ring-1 ring-inset ring-purple-500/20'
                              : 'bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 ring-1 ring-inset ring-indigo-500/20'
                          }`}
                        >
                          Role: {user.role}
                        </span>
                      </div>
                    </div>

                    <div className="py-1.5 space-y-1">
                      {user.role === 'admin' ? (
                        <button
                          onClick={() => handleNav('/admin')}
                          className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-bold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/80 rounded-xl transition-colors"
                        >
                          <ShieldCheck className="w-4 h-4 text-purple-600" />
                          Admin Console
                        </button>
                      ) : (
                        <button
                          onClick={() => handleNav('/dashboard')}
                          className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-bold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/80 rounded-xl transition-colors"
                        >
                          <LayoutDashboard className="w-4 h-4 text-indigo-600" />
                          User Dashboard
                        </button>
                      )}
                    </div>

                    <div className="pt-1.5 border-t border-slate-100 dark:border-slate-800/80">
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-bold text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-xl transition-colors"
                      >
                        <LogOut className="w-4 h-4" />
                        Sign Out
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          )}

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileMenuOpen((prev) => !prev)}
            className="md:hidden p-2 rounded-xl text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 dark:border-white/10 bg-white/95 dark:bg-slate-950/95 backdrop-blur-xl px-4 py-4 space-y-2 animate-fade-in">
          {!user ? (
            <>
              <button
                onClick={() => handleNav('/')}
                className="w-full text-left px-3 py-2.5 rounded-xl text-xs font-bold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
              >
                Home
              </button>
              <button
                onClick={() => handleNav('/login')}
                className="w-full text-left px-3 py-2.5 rounded-xl text-xs font-bold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
              >
                Sign In
              </button>
              <button
                onClick={() => handleNav('/register')}
                className="w-full text-center px-4 py-2.5 rounded-xl text-xs font-bold bg-indigo-600 text-white shadow-md"
              >
                Get Started
              </button>
            </>
          ) : (
            <>
              {user.role === 'admin' ? (
                <>
                  <button
                    onClick={() => handleNav('/admin')}
                    className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-xs font-bold text-slate-800 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
                  >
                    <ShieldCheck className="w-4 h-4 text-purple-600" />
                    Admin Dashboard
                  </button>
                  <button
                    onClick={() => handleNav('/admin/categories')}
                    className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-xs font-bold text-slate-800 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
                  >
                    <Tags className="w-4 h-4 text-indigo-600" />
                    Manage Categories
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => handleNav('/dashboard')}
                    className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-xs font-bold text-slate-800 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
                  >
                    <LayoutDashboard className="w-4 h-4 text-indigo-600" />
                    Dashboard
                  </button>
                  <button
                    onClick={() => handleNav('/complaint/new')}
                    className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-xs font-bold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300"
                  >
                    <PlusCircle className="w-4 h-4" />
                    Submit Ticket
                  </button>
                </>
              )}
              <button
                onClick={() => handleNav('/complaints')}
                className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-xs font-bold text-slate-800 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
              >
                <ListFilter className="w-4 h-4" />
                Registry View
              </button>
              <div className="pt-2 border-t border-slate-200 dark:border-white/10">
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-xs font-bold text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40"
                >
                  <LogOut className="w-4 h-4" />
                  Sign Out
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </header>
  );
};
