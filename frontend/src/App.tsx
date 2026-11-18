import React, { useEffect, useState } from 'react';
import { useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { HomePage } from './pages/HomePage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { ComplaintsListPage } from './pages/ComplaintsListPage';
import { SubmitComplaintPage } from './pages/SubmitComplaintPage';
import { ComplaintDetailPage } from './pages/ComplaintDetailPage';
import { AdminDashboardPage } from './pages/AdminDashboardPage';
import { CategoriesManagementPage } from './pages/CategoriesManagementPage';
import { ForbiddenPage } from './pages/ForbiddenPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { MessageSquareWarning, ShieldCheck, Heart } from 'lucide-react';

export const App: React.FC = () => {
  const { user, loading } = useAuth();
  const [currentPath, setCurrentPath] = useState<string>(window.location.pathname);
  const [searchParams, setSearchParams] = useState<URLSearchParams>(
    new URLSearchParams(window.location.search)
  );

  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname);
      setSearchParams(new URLSearchParams(window.location.search));
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigate = (path: string) => {
    const url = new URL(path, window.location.origin);
    window.history.pushState({}, '', path);
    setCurrentPath(url.pathname);
    setSearchParams(new URLSearchParams(url.search));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Initializing SCMS...
          </span>
        </div>
      </div>
    );
  }

  // Routing Logic
  const renderRoute = () => {
    // 1. Complaint Detail: /complaints/:id
    const complaintDetailMatch = currentPath.match(/^\/complaints\/(\d+)$/);
    if (complaintDetailMatch) {
      const id = parseInt(complaintDetailMatch[1], 10);
      if (!user) {
        return <LoginPage navigate={navigate} />;
      }
      return <ComplaintDetailPage complaintId={id} navigate={navigate} />;
    }

    switch (currentPath) {
      case '/':
        return <HomePage navigate={navigate} />;

      case '/login':
        if (user) {
          return user.role === 'admin' ? (
            <AdminDashboardPage navigate={navigate} />
          ) : (
            <DashboardPage navigate={navigate} />
          );
        }
        return <LoginPage navigate={navigate} />;

      case '/register':
        if (user) {
          return <DashboardPage navigate={navigate} />;
        }
        return <RegisterPage navigate={navigate} />;

      case '/dashboard':
        if (!user) return <LoginPage navigate={navigate} />;
        if (user.role === 'admin') return <AdminDashboardPage navigate={navigate} />;
        return <DashboardPage navigate={navigate} />;

      case '/complaint':
      case '/complaint/new':
        if (!user) return <LoginPage navigate={navigate} />;
        return <SubmitComplaintPage navigate={navigate} />;

      case '/complaints':
        if (!user) return <LoginPage navigate={navigate} />;
        return (
          <ComplaintsListPage
            navigate={navigate}
            initialStatus={searchParams.get('status') || undefined}
          />
        );

      case '/admin':
        if (!user) return <LoginPage navigate={navigate} />;
        if (user.role !== 'admin') return <ForbiddenPage navigate={navigate} />;
        return (
          <AdminDashboardPage
            navigate={navigate}
            initialManageId={
              searchParams.get('manage') ? parseInt(searchParams.get('manage')!, 10) : null
            }
          />
        );

      case '/admin/categories':
        if (!user) return <LoginPage navigate={navigate} />;
        if (user.role !== 'admin') return <ForbiddenPage navigate={navigate} />;
        return <CategoriesManagementPage navigate={navigate} />;

      default:
        return <NotFoundPage navigate={navigate} />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100 transition-colors">
      <Navbar currentPath={currentPath} navigate={navigate} />
      <main className="flex-1">{renderRoute()}</main>

      {/* Footer */}
      <footer className="border-t border-slate-200/80 dark:border-slate-800 bg-white/50 dark:bg-slate-950/50 backdrop-blur-sm py-8 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center text-white">
              <MessageSquareWarning className="w-4 h-4" />
            </div>
            <span className="text-xs font-bold text-slate-700 dark:text-slate-300">
              Smart Complaint Management System (SCMS)
            </span>
          </div>

          <div className="flex items-center gap-6 text-xs font-medium text-slate-500 dark:text-slate-400">
            <button onClick={() => navigate('/')} className="hover:text-indigo-600 transition-colors">
              Home
            </button>
            <button onClick={() => navigate('/dashboard')} className="hover:text-indigo-600 transition-colors">
              Dashboard
            </button>
            <button onClick={() => navigate('/complaint/new')} className="hover:text-indigo-600 transition-colors">
              Submit Grievance
            </button>
          </div>

          <div className="text-[11px] text-slate-400 flex items-center gap-1">
            <span>Enterprise React Edition</span>
            <span>•</span>
            <span>Version 2.0</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
