import React from 'react';
import { useAuth } from '../context/AuthContext';
import {
  MessageSquareWarning,
  ShieldCheck,
  Zap,
  CheckCircle2,
  Clock,
  ArrowRight,
  Sparkles,
  Users,
  Layers,
  ChevronRight,
} from 'lucide-react';

interface Props {
  navigate: (path: string) => void;
}

export const HomePage: React.FC<Props> = ({ navigate }) => {
  const { user } = useAuth();

  return (
    <div className="space-y-20 pb-20 animate-fade-in">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-16 md:pt-20 md:pb-24">
        {/* Ambient background glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] bg-gradient-to-tr from-indigo-500/20 via-purple-500/20 to-pink-500/10 blur-[100px] rounded-full pointer-events-none -z-10" />

        <div className="max-w-5xl mx-auto px-4 text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200/80 dark:bg-indigo-950/60 dark:text-indigo-300 dark:border-indigo-800/80 shadow-sm animate-pulse-subtle">
            <Sparkles className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
            <span>Next-Generation Grievance Resolution Platform</span>
          </div>

          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-[1.15]">
            Resolve issues faster with <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              Smart Complaint Tracking
            </span>
          </h1>

          <p className="max-w-2xl mx-auto text-base sm:text-lg text-slate-600 dark:text-slate-300 leading-relaxed font-normal">
            A unified, transparent portal for students and administration. Submit academic, hostel, or
            technical concerns and track their step-by-step resolution in real time.
          </p>

          <div className="pt-4 flex flex-wrap items-center justify-center gap-4">
            {!user ? (
              <>
                <button
                  onClick={() => navigate('/login')}
                  className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-xl font-bold text-sm bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-500/30 hover:shadow-indigo-500/40 hover:-translate-y-0.5 transition-all"
                >
                  <span>Submit a Complaint</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
                <button
                  onClick={() => navigate('/login')}
                  className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl font-semibold text-sm bg-white hover:bg-slate-50 text-slate-800 border border-slate-200 dark:bg-slate-900 dark:hover:bg-slate-800 dark:text-slate-100 dark:border-slate-800 shadow-sm transition-all"
                >
                  <ShieldCheck className="w-4 h-4 text-purple-600" />
                  <span>Admin Access</span>
                </button>
              </>
            ) : user.role === 'admin' ? (
              <button
                onClick={() => navigate('/admin')}
                className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-xl font-bold text-sm bg-purple-600 hover:bg-purple-700 text-white shadow-lg shadow-purple-500/30 hover:-translate-y-0.5 transition-all"
              >
                <span>Go to Admin Dashboard</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            ) : (
              <>
                <button
                  onClick={() => navigate('/complaint/new')}
                  className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-xl font-bold text-sm bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-500/30 hover:-translate-y-0.5 transition-all"
                >
                  <span>File New Complaint</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
                <button
                  onClick={() => navigate('/dashboard')}
                  className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl font-semibold text-sm bg-white hover:bg-slate-50 text-slate-800 border border-slate-200 dark:bg-slate-900 dark:hover:bg-slate-800 dark:text-slate-100 dark:border-slate-800 shadow-sm transition-all"
                >
                  <span>View My Dashboard</span>
                </button>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Live Impact Counters Strip */}
      <section className="max-w-6xl mx-auto px-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-6 rounded-2xl bg-white/70 dark:bg-slate-900/70 border border-slate-200/80 dark:border-slate-800 backdrop-blur-md shadow-xl">
          <div className="text-center p-3">
            <div className="text-3xl font-extrabold text-indigo-600 dark:text-indigo-400">99.4%</div>
            <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 mt-1 uppercase tracking-wider">
              Resolution Rate
            </div>
          </div>
          <div className="text-center p-3 border-l border-slate-100 dark:border-slate-800">
            <div className="text-3xl font-extrabold text-purple-600 dark:text-purple-400">&lt; 24h</div>
            <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 mt-1 uppercase tracking-wider">
              First Response
            </div>
          </div>
          <div className="text-center p-3 border-l border-slate-100 dark:border-slate-800">
            <div className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400">100%</div>
            <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 mt-1 uppercase tracking-wider">
              Audit Transparency
            </div>
          </div>
          <div className="text-center p-3 border-l border-slate-100 dark:border-slate-800">
            <div className="text-3xl font-extrabold text-amber-600 dark:text-amber-400">3-Tier</div>
            <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 mt-1 uppercase tracking-wider">
              State Governance
            </div>
          </div>
        </div>
      </section>

      {/* Feature Showcase Grid */}
      <section className="max-w-6xl mx-auto px-4 space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-xs font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
            Platform Capabilities
          </h2>
          <h3 className="text-3xl font-extrabold text-slate-900 dark:text-white">
            Everything you need for seamless complaint handling
          </h3>
          <p className="text-slate-600 dark:text-slate-400 max-w-xl mx-auto text-sm">
            Designed for accountability, speed, and clear communication between students, staff, and leadership.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-7 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-md hover:shadow-xl transition-all group">
            <div className="w-12 h-12 rounded-xl bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-400 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
              <Clock className="w-6 h-6" />
            </div>
            <h4 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
              Real-Time Status Tracking
            </h4>
            <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
              Track the exact stage of your complaint: Pending, In Progress, and Resolved with live timeline
              steppers and instant progress updates.
            </p>
          </div>

          <div className="p-7 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-md hover:shadow-xl transition-all group">
            <div className="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-400 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h4 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
              Strict State Machine
            </h4>
            <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
              Complaints can only transition through validated states: Pending to In Progress, In Progress to Resolved
              with compulsory remarks, and controlled reopening.
            </p>
          </div>

          <div className="p-7 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-md hover:shadow-xl transition-all group">
            <div className="w-12 h-12 rounded-xl bg-purple-100 text-purple-700 dark:bg-purple-950/60 dark:text-purple-400 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
              <Layers className="w-6 h-6" />
            </div>
            <h4 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
              Dynamic Categorization
            </h4>
            <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
              Organize complaints under Academic, Infrastructure, Hostel, Technical, or custom administrative categories
              with instant filter and search.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works 3-Step Walkthrough */}
      <section className="max-w-6xl mx-auto px-4 py-8">
        <div className="p-8 md:p-12 rounded-3xl bg-gradient-to-br from-indigo-900 via-slate-900 to-purple-950 text-white shadow-2xl relative overflow-hidden">
          <div className="relative z-10 space-y-8">
            <div className="max-w-xl">
              <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                Simple Workflow
              </span>
              <h3 className="text-2xl sm:text-3xl font-extrabold mt-1 text-white">
                How SCMS resolves issues in 3 steps
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
              <div className="space-y-3 p-5 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md">
                <div className="w-8 h-8 rounded-lg bg-indigo-500 text-white font-bold flex items-center justify-center text-sm">
                  1
                </div>
                <h5 className="font-bold text-base text-white">Submit Grievance</h5>
                <p className="text-xs text-indigo-200/80 leading-relaxed">
                  Log in, specify title, select department category, and provide details with automatic timestamping.
                </p>
              </div>

              <div className="space-y-3 p-5 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md">
                <div className="w-8 h-8 rounded-lg bg-purple-500 text-white font-bold flex items-center justify-center text-sm">
                  2
                </div>
                <h5 className="font-bold text-base text-white">Admin Triage & Action</h5>
                <p className="text-xs text-indigo-200/80 leading-relaxed">
                  Administrators review the complaint, move it to In Progress, and coordinate with concerned authorities.
                </p>
              </div>

              <div className="space-y-3 p-5 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md">
                <div className="w-8 h-8 rounded-lg bg-emerald-500 text-white font-bold flex items-center justify-center text-sm">
                  3
                </div>
                <h5 className="font-bold text-base text-white">Resolution & Feedback</h5>
                <p className="text-xs text-indigo-200/80 leading-relaxed">
                  The issue is marked Resolved with detailed resolution remarks visible directly on your dashboard.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
