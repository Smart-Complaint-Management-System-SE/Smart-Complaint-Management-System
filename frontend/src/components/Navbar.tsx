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
  User as UserIcon,
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
    return `inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm font-semibold transition-all ${
      isActive
        ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/70 dark:text-indigo-300 shadow-sm'
        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/70 dark:text-slate-400 dark:hover:text-slate-100 dark:hover:bg-slate-800/60'
    }`;
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200/80 dark:border-slate-800/80 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo / Brand */}
        <div
          onClick={() => handleNav(user ? (user.role === 'admin' ? '/admin' : '/dashboard') : '/')}
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 flex items-center justify-center text-white shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform">
            <MessageSquareWarning className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-lg tracking-tight text-slate-900 dark:text-white">
                SCMS
              </span>
              <span className="hidden sm:inline-block px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-indigo-100 text-indigo-700 dark:bg-indigo-950/90 dark:text-indigo-300 rounded-md">
                Smart Grievance
              </span>
            </div>
            <p className="hidden md:block text-[11px] text-slate-500 dark:text-slate-400 font-medium -mt-0.5">
              Complaint Management System
            </p>
          </div>
        </div>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center gap-1.5">
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
                className="ml-2 inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-500/25 transition-all"
              >
                Register
              </button>
            </>
          ) : user.role === 'admin' ? (
            <>
              <button onClick={() => handleNav('/admin')} className={navItemClass('/admin')}>
                <ShieldCheck className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                Admin Dashboard
              </button>
              <button
                onClick={() => handleNav('/admin/categories')}
                className={navItemClass('/admin/categories')}
              >
                <Tags className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                Categories
              </button>
              <button onClick={() => handleNav('/complaints')} className={navItemClass('/complaints')}>
                <ListFilter className="w-4 h-4" />
                User View
              </button>
            </>
          ) : (
            <>
              <button onClick={() => handleNav('/dashboard')} className={navItemClass('/dashboard')}>
                <LayoutDashboard className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                Dashboard
              </button>
              <button onClick={() => handleNav('/complaints')} className={navItemClass('/complaints')}>
                <ListFilter className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                My Complaints
              </button>
              <button
                onClick={() => handleNav('/complaint/new')}
                className="ml-2 inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-500/25 hover:shadow-indigo-500/35 transition-all"
              >
                <PlusCircle className="w-4 h-4" />
                Submit Complaint
              </button>
            </>
          )}
        </nav>

        {/* Right Tools: Theme Toggle & Profile Dropdown */}
        <div className="flex items-center gap-2.5">
          <button
            onClick={toggleTheme}
            aria-label="Toggle color theme"
            className="p-2.5 rounded-xl text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800/80 transition-colors"
          >
            {theme === 'dark' ? <Sun className="w-5 h-5 text-amber-400" /> : <Moon className="w-5 h-5 text-slate-600" />}
          </button>

          {user && (
            <div className="relative">
              <button
                onClick={() => setProfileDropdownOpen((prev) => !prev)}
                className="flex items-center gap-2.5 p-1.5 pl-2.5 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800/80 border border-transparent hover:border-slate-200 dark:hover:border-slate-700/60 transition-all"
              >
                <div className="hidden sm:block text-right">
                  <div className="text-xs font-bold text-slate-900 dark:text-slate-100 leading-tight">
                    {user.name}
                  </div>
                  <div className="text-[10px] font-medium text-slate-500 dark:text-slate-400">
                    {user.role === 'admin' ? 'Administrator' : 'Student / User'}
                  </div>
                </div>
                <div
                  className={`w-9 h-9 rounded-xl flex items-center justify-center font-bold text-xs shadow-sm ${
                    user.role === 'admin'
                      ? 'bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-300 border border-purple-200 dark:border-purple-800'
                      : 'bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800'
                  }`}
                >
                  {user.name.slice(0, 2).toUpperCase()}
                </div>
              </button>

              {/* Profile dropdown menu */}
              {profileDropdownOpen && (
                <>
                  <div
                    className="fixed inset-0 z-40"
                    onClick={() => setProfileDropdownOpen(false)}
                  />
                  <div className="absolute right-0 mt-2 w-64 rounded-2xl bg-white dark:bg-slate-900 shadow-2xl border border-slate-200 dark:border-slate-800 z-50 p-2 animate-slide-up">
                    <div className="px-3 py-2.5 border-b border-slate-100 dark:border-slate-800">
                      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                        Signed in as
                      </p>
                      <p className="text-sm font-bold text-slate-900 dark:text-white truncate">
                        {user.name}
                      </p>
                      <p className="text-xs text-slate-500 dark:text-slate-400 truncate mt-0.5">
                        {user.email}
                      </p>
                      <div className="mt-2 inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300">
                        Role: {user.role.toUpperCase()}
                      </div>
                    </div>

                    <div className="py-1">
                      {user.role === 'admin' ? (
                        <button
                          onClick={() => handleNav('/admin')}
                          className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/80 rounded-lg transition-colors"
                        >
                          <ShieldCheck className="w-4 h-4 text-purple-600" />
                          Admin Console
                        </button>
                      ) : (
                        <button
                          onClick={() => handleNav('/dashboard')}
                          className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/80 rounded-lg transition-colors"
                        >
                          <LayoutDashboard className="w-4 h-4 text-indigo-600" />
                          My Dashboard
                        </button>
                      )}
                    </div>

                    <div className="pt-1 border-t border-slate-100 dark:border-slate-800">
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-semibold text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-lg transition-colors"
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

          {/* Mobile menu trigger */}
          <button
            onClick={() => setMobileMenuOpen((prev) => !prev)}
            className="md:hidden p-2.5 rounded-xl text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile navigation drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 px-4 pt-3 pb-6 space-y-2 animate-fade-in">
          {!user ? (
            <>
              <button
                onClick={() => handleNav('/')}
                className="w-full text-left px-3 py-2.5 rounded-xl text-sm font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
              >
                Home
              </button>
              <button
                onClick={() => handleNav('/login')}
                className="w-full text-left px-3 py-2.5 rounded-xl text-sm font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
              >
                Sign In
              </button>
              <button
                onClick={() => handleNav('/register')}
                className="w-full text-center px-4 py-2.5 rounded-xl text-sm font-semibold bg-indigo-600 text-white shadow-md"
              >
                Create Account
              </button>
            </>
          ) : (
            <>
              {user.role === 'admin' ? (
                <>
                  <button
                    onClick={() => handleNav('/admin')}
                    className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm font-semibold text-slate-800 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
                  >
                    <ShieldCheck className="w-4 h-4 text-purple-600" />
                    Admin Dashboard
                  </button>
                  <button
                    onClick={() => handleNav('/admin/categories')}
                    className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm font-semibold text-slate-800 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
                  >
                    <Tags className="w-4 h-4 text-indigo-600" />
                    Manage Categories
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => handleNav('/dashboard')}
                    className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm font-semibold text-slate-800 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
                  >
                    <LayoutDashboard className="w-4 h-4 text-indigo-600" />
                    Dashboard
                  </button>
                  <button
                    onClick={() => handleNav('/complaint/new')}
                    className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm font-semibold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300"
                  >
                    <PlusCircle className="w-4 h-4" />
                    Submit Complaint
                  </button>
                </>
              )}
              <button
                onClick={() => handleNav('/complaints')}
                className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm font-semibold text-slate-800 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
              >
                <ListFilter className="w-4 h-4" />
                {user.role === 'admin' ? 'View as User' : 'My Complaints'}
              </button>
              <div className="pt-2 border-t border-slate-200 dark:border-slate-800">
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm font-semibold text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40"
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
