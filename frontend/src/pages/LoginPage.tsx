import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import {
  MessageSquareWarning,
  Mail,
  Lock,
  Eye,
  EyeOff,
  ArrowRight,
  ShieldCheck,
  UserCheck,
  AlertCircle,
} from 'lucide-react';

interface Props {
  navigate: (path: string) => void;
}

export const LoginPage: React.FC<Props> = ({ navigate }) => {
  const { login } = useAuth();
  const { success, error } = useToast();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!email.trim() || !password) {
      setErrorMessage('Please enter both email and password.');
      return;
    }

    setLoading(true);
    try {
      const loggedUser = await login(email.trim(), password);
      success(`Welcome back, ${loggedUser.name}!`);
      if (loggedUser.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    } catch (err: any) {
      const msg = err.message || 'Invalid email or password.';
      setErrorMessage(msg);
      error(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleDemoFill = (type: 'user' | 'admin') => {
    setErrorMessage(null);
    if (type === 'admin') {
      setEmail('admin@example.com');
      setPassword('admin123');
    } else {
      setEmail('test@example.com');
      setPassword('password123');
    }
  };

  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center py-10 px-4 animate-fade-in">
      <div className="max-w-md w-full space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex p-3 rounded-2xl bg-indigo-600 text-white shadow-lg shadow-indigo-500/25 mb-2">
            <MessageSquareWarning className="w-8 h-8" />
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Sign in to your account
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Access your complaints dashboard and track issues
          </p>
        </div>

        {/* Demo Quick Fill Badges */}
        <div className="p-3.5 rounded-2xl bg-indigo-50/70 dark:bg-slate-900/80 border border-indigo-100 dark:border-slate-800 space-y-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-700 dark:text-indigo-300 block">
            Quick Demo Autofill:
          </span>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => handleDemoFill('user')}
              className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 shadow-sm hover:border-indigo-400 transition-colors"
            >
              <UserCheck className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
              <span>User Demo</span>
            </button>
            <button
              type="button"
              onClick={() => handleDemoFill('admin')}
              className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 shadow-sm hover:border-purple-400 transition-colors"
            >
              <ShieldCheck className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" />
              <span>Admin Demo</span>
            </button>
          </div>
        </div>

        {/* Form Card */}
        <div className="bg-white dark:bg-slate-900 rounded-3xl p-7 sm:p-8 shadow-xl border border-slate-200/80 dark:border-slate-800 space-y-5">
          {errorMessage && (
            <div className="p-3.5 rounded-xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900/60 text-rose-800 dark:text-rose-200 text-xs font-semibold flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600 dark:text-rose-400" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="email"
                className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1.5"
              >
                Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm font-medium bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1.5"
              >
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-11 py-2.5 rounded-xl text-sm font-medium bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 inline-flex items-center justify-center gap-2 py-3 px-4 rounded-xl font-bold text-sm bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-500/25 hover:shadow-indigo-500/35 disabled:opacity-50 disabled:pointer-events-none transition-all"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="pt-2 text-center text-xs text-slate-500 dark:text-slate-400">
            Don't have an account yet?{' '}
            <button
              onClick={() => navigate('/register')}
              className="font-bold text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300 underline underline-offset-4"
            >
              Create an account
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
