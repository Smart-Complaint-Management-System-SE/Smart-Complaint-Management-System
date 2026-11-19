import React from 'react';
import { useAuth } from '../context/AuthContext';
import {
  MessageSquareWarning,
  ShieldCheck,
  CheckCircle2,
  Clock,
  ArrowRight,
  Sparkles,
  Users,
  Layers,
  ChevronRight,
  Zap,
  Lock,
  Search,
  Activity,
} from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';
import { CategoryBadge } from '../components/CategoryBadge';

interface Props {
  navigate: (path: string) => void;
}

export const HomePage: React.FC<Props> = ({ navigate }) => {
  const { user } = useAuth();

  return (
    <div className="space-y-24 pb-24 animate-fade-in bg-grid-slate">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-20 md:pt-24 md:pb-28">
        {/* Artistic glowing radial meshes */}
        <div className="absolute top-10 left-1/2 -translate-x-1/2 w-[800px] h-[450px] bg-gradient-to-tr from-indigo-500/20 via-purple-500/20 to-pink-500/10 blur-[130px] rounded-full pointer-events-none -z-10" />

        <div className="max-w-6xl mx-auto px-4 text-center space-y-8">
          <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full text-xs font-bold bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 ring-1 ring-inset ring-indigo-500/30 backdrop-blur-md shadow-sm">
            <Sparkles className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
            <span>Next-Generation Grievance Resolution Platform</span>
          </div>

          <h1 className="text-4xl sm:text-6xl md:text-7xl font-black tracking-tight text-slate-900 dark:text-white leading-[1.1]">
            Turn campus concerns into <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-500 bg-clip-text text-transparent">
              verified solutions.
            </span>
          </h1>

          <p className="max-w-2xl mx-auto text-base sm:text-lg text-slate-600 dark:text-slate-300 leading-relaxed font-medium">
            A transparent grievance portal connecting students, staff, and campus administration.
            Submit academic, hostel, or technical tickets and track their step-by-step resolution in real time.
          </p>

          {/* Action CTAs */}
          <div className="pt-2 flex flex-wrap items-center justify-center gap-4">
            {!user ? (
              <>
                <button
                  onClick={() => navigate('/login')}
                  className="inline-flex items-center gap-2.5 px-7 py-4 rounded-2xl font-black text-sm bg-gradient-to-r from-indigo-600 via-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white shadow-xl shadow-indigo-500/30 hover:shadow-indigo-500/45 hover:-translate-y-0.5 transition-all"
                >
                  <span>Submit a Complaint</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
                <button
                  onClick={() => navigate('/login')}
                  className="inline-flex items-center gap-2.5 px-7 py-4 rounded-2xl font-bold text-sm bg-white/80 hover:bg-white text-slate-800 border border-slate-200 dark:bg-slate-900/80 dark:hover:bg-slate-900 dark:text-slate-100 dark:border-white/10 shadow-lg shadow-black/5 hover:-translate-y-0.5 transition-all backdrop-blur-md"
                >
                  <ShieldCheck className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                  <span>Admin Portal</span>
                </button>
              </>
            ) : user.role === 'admin' ? (
              <button
                onClick={() => navigate('/admin')}
                className="inline-flex items-center gap-2.5 px-7 py-4 rounded-2xl font-black text-sm bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-xl shadow-purple-500/30 hover:-translate-y-0.5 transition-all"
              >
                <span>Open Admin Dashboard</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            ) : (
              <>
                <button
                  onClick={() => navigate('/complaint/new')}
                  className="inline-flex items-center gap-2.5 px-7 py-4 rounded-2xl font-black text-sm bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-xl shadow-indigo-500/30 hover:-translate-y-0.5 transition-all"
                >
                  <span>Submit Grievance</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
                <button
                  onClick={() => navigate('/dashboard')}
                  className="inline-flex items-center gap-2.5 px-7 py-4 rounded-2xl font-bold text-sm bg-white/80 text-slate-800 border border-slate-200 dark:bg-slate-900/80 dark:text-slate-100 dark:border-white/10 shadow-md hover:-translate-y-0.5 transition-all"
                >
                  <span>Go to My Dashboard</span>
                </button>
              </>
            )}
          </div>

          {/* Interactive Live Ticket Showcase Card inside Hero */}
          <div className="pt-8 max-w-2xl mx-auto">
            <div className="p-6 rounded-3xl artistic-card text-left space-y-4 hover-lift">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold text-slate-400">#4</span>
                  <CategoryBadge category="Academic" size="sm" />
                </div>
                <StatusBadge status="Resolved" size="sm" />
              </div>
              <div>
                <h3 className="text-base font-extrabold text-slate-900 dark:text-white">
                  Library 2nd Floor Study Room AC Fixed
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
                  The central library silent reading section air conditioning has been repaired and verified.
                </p>
              </div>
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-800 dark:text-emerald-300 font-medium flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5 text-emerald-600" />
                <span>
                  <strong>Admin Resolution:</strong> New compressor unit installed by campus maintenance.
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* KPI Impact Counters */}
      <section className="max-w-6xl mx-auto px-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-8 rounded-3xl artistic-card shadow-2xl">
          <div className="text-center p-3">
            <div className="text-3xl sm:text-4xl font-black bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              99.4%
            </div>
            <div className="text-[11px] font-extrabold uppercase tracking-widest text-slate-400 mt-1.5">
              Resolution Rate
            </div>
          </div>
          <div className="text-center p-3 border-l border-slate-100 dark:border-white/5">
            <div className="text-3xl sm:text-4xl font-black bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              &lt; 24h
            </div>
            <div className="text-[11px] font-extrabold uppercase tracking-widest text-slate-400 mt-1.5">
              Initial Triage
            </div>
          </div>
          <div className="text-center p-3 border-l border-slate-100 dark:border-white/5">
            <div className="text-3xl sm:text-4xl font-black bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
              100%
            </div>
            <div className="text-[11px] font-extrabold uppercase tracking-widest text-slate-400 mt-1.5">
              Audit Transparency
            </div>
          </div>
          <div className="text-center p-3 border-l border-slate-100 dark:border-white/5">
            <div className="text-3xl sm:text-4xl font-black bg-gradient-to-r from-amber-500 to-orange-500 bg-clip-text text-transparent">
              3-Tier
            </div>
            <div className="text-[11px] font-extrabold uppercase tracking-widest text-slate-400 mt-1.5">
              Strict Governance
            </div>
          </div>
        </div>
      </section>

      {/* Core Features Grid */}
      <section className="max-w-6xl mx-auto px-4 space-y-12">
        <div className="text-center space-y-3">
          <span className="text-xs font-black uppercase tracking-widest text-indigo-600 dark:text-indigo-400">
            Engineered For Clarity
          </span>
          <h2 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
            Enterprise Grievance Workflow
          </h2>
          <p className="text-slate-600 dark:text-slate-400 max-w-xl mx-auto text-sm font-medium">
            Designed for institutional scale, security, and immediate clarity between students and authorities.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-8 rounded-3xl artistic-card hover-lift space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-amber-500/10 text-amber-600 dark:text-amber-400 flex items-center justify-center ring-1 ring-amber-500/20 shadow-md">
              <Clock className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-extrabold text-slate-900 dark:text-white">
              Real-Time Visual Stepper
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-medium">
              Every complaint is paired with an interactive 3-stage progression timeline. Track exact timestamps,
              admin updates, and completion remarks.
            </p>
          </div>

          <div className="p-8 rounded-3xl artistic-card hover-lift space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 flex items-center justify-center ring-1 ring-indigo-500/20 shadow-md">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-extrabold text-slate-900 dark:text-white">
              Enforced State Transitions
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-medium">
              Strict state machine validation: Pending to In Progress, In Progress to Resolved with mandatory resolution
              remarks, and controlled reopening.
            </p>
          </div>

          <div className="p-8 rounded-3xl artistic-card hover-lift space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center justify-center ring-1 ring-purple-500/20 shadow-md">
              <Layers className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-extrabold text-slate-900 dark:text-white">
              Dynamic Category Management
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-medium">
              Categorize complaints under Academic, Infrastructure, Hostel, Technical, or custom administrative departments
              with instant filtering and analytics.
            </p>
          </div>
        </div>
      </section>

      {/* How it works workflow */}
      <section className="max-w-6xl mx-auto px-4">
        <div className="p-8 md:p-14 rounded-3xl bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white shadow-2xl relative overflow-hidden border border-white/10">
          <div className="relative z-10 space-y-8">
            <div className="max-w-xl">
              <span className="text-xs font-black uppercase tracking-widest text-indigo-400">
                Transparent Lifecycle
              </span>
              <h3 className="text-2xl sm:text-3xl font-black mt-1 text-white">
                How SCMS resolves issues in 3 steps
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2">
              <div className="space-y-3 p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md">
                <div className="w-9 h-9 rounded-xl bg-indigo-500 text-white font-black flex items-center justify-center text-sm shadow-md">
                  1
                </div>
                <h4 className="font-extrabold text-base text-white">Submit Grievance</h4>
                <p className="text-xs text-indigo-200/80 leading-relaxed font-medium">
                  Provide a concise title, pick the department, and describe your concern with real-time field validation.
                </p>
              </div>

              <div className="space-y-3 p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md">
                <div className="w-9 h-9 rounded-xl bg-purple-500 text-white font-black flex items-center justify-center text-sm shadow-md">
                  2
                </div>
                <h4 className="font-extrabold text-base text-white">Admin Triage</h4>
                <p className="text-xs text-indigo-200/80 leading-relaxed font-medium">
                  Authorised personnel assign priority, move the ticket to In Progress, and begin investigation.
                </p>
              </div>

              <div className="space-y-3 p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md">
                <div className="w-9 h-9 rounded-xl bg-emerald-500 text-white font-black flex items-center justify-center text-sm shadow-md">
                  3
                </div>
                <h4 className="font-extrabold text-base text-white">Resolution & Closure</h4>
                <p className="text-xs text-indigo-200/80 leading-relaxed font-medium">
                  The issue is marked Resolved with official administrator remarks visible directly on your dashboard.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
