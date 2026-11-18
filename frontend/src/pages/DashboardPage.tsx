import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { complaintsApi } from '../api/client';
import { Complaint, UserStats } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { CategoryBadge } from '../components/CategoryBadge';
import {
  Clock,
  RefreshCw,
  CheckCircle2,
  PlusCircle,
  ArrowRight,
  Inbox,
  FileText,
  AlertTriangle,
  ChevronRight,
} from 'lucide-react';

interface Props {
  navigate: (path: string) => void;
}

export const DashboardPage: React.FC<Props> = ({ navigate }) => {
  const { user } = useAuth();
  const [stats, setStats] = useState<UserStats>({
    Pending: 0,
    'In Progress': 0,
    Resolved: 0,
    total: 0,
  });
  const [recentComplaints, setRecentComplaints] = useState<Complaint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const [statsData, complaintsData] = await Promise.all([
          complaintsApi.getUserStats().catch(() => ({
            Pending: 0,
            'In Progress': 0,
            Resolved: 0,
            total: 0,
          })),
          complaintsApi.list(1, 5).catch(() => ({ complaints: [] })),
        ]);
        setStats(statsData);
        setRecentComplaints(complaintsData.complaints || []);
      } catch (err) {
        console.error('Failed to load dashboard:', err);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  const total = stats.Pending + stats['In Progress'] + stats.Resolved;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      {/* Welcome Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-indigo-600 via-indigo-700 to-purple-700 text-white shadow-xl shadow-indigo-500/15">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-white/20 text-white backdrop-blur-md">
            <span>User Overview</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
            Welcome back, {user?.name || 'Student'}!
          </h1>
          <p className="text-sm text-indigo-100/90 font-medium">
            Monitor, submit, and track the status of your reported grievances.
          </p>
        </div>

        <button
          onClick={() => navigate('/complaint/new')}
          className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-2xl font-bold text-sm bg-white hover:bg-slate-100 text-indigo-700 shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all shrink-0"
        >
          <PlusCircle className="w-5 h-5 text-indigo-600" />
          <span>New Complaint</span>
        </button>
      </div>

      {/* KPI Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Pending Card */}
        <div
          onClick={() => navigate('/complaints?status=Pending')}
          className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Pending
            </span>
            <div className="w-9 h-9 rounded-xl bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white">
            {loading ? '-' : stats.Pending}
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Awaiting admin review</p>
        </div>

        {/* In Progress Card */}
        <div
          onClick={() => navigate('/complaints?status=In Progress')}
          className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              In Progress
            </span>
            <div className="w-9 h-9 rounded-xl bg-blue-100 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300 flex items-center justify-center group-hover:scale-110 transition-transform">
              <RefreshCw className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white">
            {loading ? '-' : stats['In Progress']}
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Currently being handled</p>
        </div>

        {/* Resolved Card */}
        <div
          onClick={() => navigate('/complaints?status=Resolved')}
          className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Resolved
            </span>
            <div className="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 flex items-center justify-center group-hover:scale-110 transition-transform">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white">
            {loading ? '-' : stats.Resolved}
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Successfully addressed</p>
        </div>

        {/* Total Card */}
        <div
          onClick={() => navigate('/complaints')}
          className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Total Filed
            </span>
            <div className="w-9 h-9 rounded-xl bg-purple-100 text-purple-700 dark:bg-purple-950/60 dark:text-purple-300 flex items-center justify-center group-hover:scale-110 transition-transform">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white">
            {loading ? '-' : total}
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">All complaints submitted</p>
        </div>
      </div>

      {/* Recent Complaints Section */}
      <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-7 shadow-sm border border-slate-200/80 dark:border-slate-800 space-y-5">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">
              Recent Complaints
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Your latest submitted tickets and their current resolution status
            </p>
          </div>
          <button
            onClick={() => navigate('/complaints')}
            className="inline-flex items-center gap-1.5 text-xs font-bold text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 hover:underline"
          >
            <span>View All</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        {loading ? (
          <div className="py-12 flex justify-center">
            <div className="w-8 h-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : recentComplaints.length === 0 ? (
          <div className="py-12 text-center space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center mx-auto">
              <Inbox className="w-6 h-6" />
            </div>
            <h4 className="text-sm font-bold text-slate-700 dark:text-slate-300">
              No complaints submitted yet
            </h4>
            <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
              Have an academic, hostel, or infrastructure issue? File a new complaint to get started.
            </p>
            <button
              onClick={() => navigate('/complaint/new')}
              className="mt-2 inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-500/20"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Submit First Complaint</span>
            </button>
          </div>
        ) : (
          <div className="divide-y divide-slate-100 dark:divide-slate-800/80">
            {recentComplaints.map((c) => (
              <div
                key={c.id}
                onClick={() => navigate(`/complaints/${c.id}`)}
                className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/80 dark:hover:bg-slate-800/40 px-3 rounded-2xl transition-colors cursor-pointer group"
              >
                <div className="space-y-1.5 flex-1 pr-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs font-mono font-bold text-slate-400">
                      #{c.id}
                    </span>
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                      {c.title}
                    </h4>
                    <CategoryBadge category={c.category} size="sm" />
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-1">
                    {c.description}
                  </p>
                </div>

                <div className="flex items-center justify-between sm:justify-end gap-3 shrink-0">
                  <StatusBadge status={c.status} size="sm" />
                  <span className="text-[11px] text-slate-400 font-medium">
                    {c.created_at ? new Date(c.created_at).toLocaleDateString() : ''}
                  </span>
                  <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-indigo-500 transition-colors" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
