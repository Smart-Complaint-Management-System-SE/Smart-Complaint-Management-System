import React from 'react';
import { ShieldAlert, ArrowLeft, Home } from 'lucide-react';

interface Props {
  navigate: (path: string) => void;
}

export const ForbiddenPage: React.FC<Props> = ({ navigate }) => {
  return (
    <div className="min-h-[calc(100vh-10rem)] flex items-center justify-center p-4 animate-fade-in bg-grid-slate">
      <div className="max-w-md w-full text-center space-y-6 artistic-card p-8 sm:p-10 rounded-3xl shadow-2xl">
        <div className="w-16 h-16 rounded-3xl bg-rose-500/10 text-rose-600 dark:text-rose-400 ring-1 ring-inset ring-rose-500/20 flex items-center justify-center mx-auto shadow-inner">
          <ShieldAlert className="w-8 h-8" />
        </div>

        <div className="space-y-2">
          <span className="text-xs font-mono font-black tracking-widest text-rose-500 uppercase">
            Error 403
          </span>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white">
            Access Forbidden
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed font-medium">
            You do not have administrative privileges to access this console page.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <button
            onClick={() => navigate('/dashboard')}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-2xl text-xs font-bold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white shadow-xl shadow-indigo-500/25 transition-all"
          >
            <Home className="w-4 h-4" />
            <span>Go to Dashboard</span>
          </button>
          <button
            onClick={() => navigate('/')}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-2xl text-xs font-bold text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800 transition-colors"
          >
            <span>Return Home</span>
          </button>
        </div>
      </div>
    </div>
  );
};
