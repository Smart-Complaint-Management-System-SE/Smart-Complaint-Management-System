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
  FileText,
  Inbox,
  ChevronRight,
  TrendingUp,
  Sparkles,
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
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in bg-grid-slate">
      {/* Top Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-indigo-900 via-slate-900 to-purple-900 text-white p-7 sm:p-10 shadow-2xl border border-white/10">
        <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-500/20 blur-3xl rounded-full pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-white/10 text-indigo-200 border border-white/10 backdrop-blur-md">
              <Sparkles className="w-3.5 h-3.5 text-indigo-300" />
              <span>Student Overview Portal</span>
            </div>
            <h1 className="text-2xl sm:text-4xl font-black tracking-tight text-white">
              Welcome back, {user?.name || 'Student'}!
            </h1>
            <p className="text-xs sm:text-sm text-indigo-200/80 font-medium max-w-xl">
              Track the progress of your submitted grievances and view verified administrative resolutions.
            </p>
          </div>

          <button
            onClick={() => navigate('/complaint/new')}
            className="inline-flex items-center justify-center gap-2.5 px-6 py-3.5 rounded-2xl font-black text-xs sm:text-sm bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white shadow-xl shadow-indigo-500/30 hover:-translate-y-0.5 transition-all self-start md:self-auto shrink-0"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Submit New Ticket</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Pending Card */}
        <div
          onClick={() => navigate('/complaints?status=Pending')}
          className="p-6 rounded-3xl artistic-card hover-lift cursor-pointer space-y-3 group"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-black uppercase tracking-wider text-slate-400">
              Pending Triage
            </span>
            <div className="w-10 h-10 rounded-2xl bg-amber-500/10 text-amber-600 dark:text-amber-400 flex items-center justify-center ring-1 ring-amber-500/20 shadow-sm group-hover:scale-110 transition-transform">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white">
            {loading ? '-' : stats.Pending}
          </div>
          <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-amber-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${total ? (stats.Pending / total) * 100 : 0}%` }}
            />
          </div>
          <p className="text-[11px] font-medium text-slate-400">Awaiting administrative assignment</p>
        </div>

        {/* In Progress Card */}
        <div
          onClick={() => navigate('/complaints?status=In Progress')}
          className="p-6 rounded-3xl artistic-card hover-lift cursor-pointer space-y-3 group"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-black uppercase tracking-wider text-slate-400">
              In Progress
            </span>
            <div className="w-10 h-10 rounded-2xl bg-blue-500/10 text-blue-600 dark:text-blue-400 flex items-center justify-center ring-1 ring-blue-500/20 shadow-sm group-hover:scale-110 transition-transform">
              <RefreshCw className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white">
            {loading ? '-' : stats['In Progress']}
          </div>
          <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-blue-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${total ? (stats['In Progress'] / total) * 100 : 0}%` }}
            />
          </div>
          <p className="text-[11px] font-medium text-slate-400">Currently undergoing active investigation</p>
        </div>

        {/* Resolved Card */}
        <div
          onClick={() => navigate('/complaints?status=Resolved')}
          className="p-6 rounded-3xl artistic-card hover-lift cursor-pointer space-y-3 group"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-black uppercase tracking-wider text-slate-400">
              Resolved
            </span>
            <div className="w-10 h-10 rounded-2xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center ring-1 ring-emerald-500/20 shadow-sm group-hover:scale-110 transition-transform">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white">
            {loading ? '-' : stats.Resolved}
          </div>
          <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-emerald-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${total ? (stats.Resolved / total) * 100 : 0}%` }}
            />
          </div>
          <p className="text-[11px] font-medium text-slate-400">Resolved with official remarks</p>
        </div>

        {/* Total Filed Card */}
        <div
          onClick={() => navigate('/complaints')}
          className="p-6 rounded-3xl artistic-card hover-lift cursor-pointer space-y-3 group"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-black uppercase tracking-wider text-slate-400">
              Total Filed
            </span>
            <div className="w-10 h-10 rounded-2xl bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center justify-center ring-1 ring-purple-500/20 shadow-sm group-hover:scale-110 transition-transform">
              <FileText className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white">
            {loading ? '-' : total}
          </div>
          <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-purple-500 h-full rounded-full w-full" />
          </div>
          <p className="text-[11px] font-medium text-slate-400">All submitted grievance tickets</p>
        </div>
      </div>

      {/* Recent Complaints Section */}
      <div className="artistic-card rounded-3xl p-6 sm:p-8 space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/5 pb-4">
          <div>
            <h2 className="text-lg font-black text-slate-900 dark:text-white">
              Recent Grievance Tickets
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Live status progression and latest updates
            </p>
          </div>
          <button
            onClick={() => navigate('/complaints')}
            className="inline-flex items-center gap-1.5 text-xs font-black text-indigo-600 dark:text-indigo-400 hover:underline"
          >
            <span>View All ({total})</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        {loading ? (
          <div className="py-16 flex justify-center">
            <div className="w-10 h-10 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : recentComplaints.length === 0 ? (
          <div className="py-14 text-center space-y-3">
            <div className="w-14 h-14 rounded-3xl bg-slate-100 dark:bg-slate-800/80 text-slate-400 flex items-center justify-center mx-auto shadow-inner">
              <Inbox className="w-7 h-7" />
            </div>
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200">
              No tickets on record
            </h4>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Need assistance with facilities, academics, or hostel issues? File a new grievance ticket.
            </p>
            <button
              onClick={() => navigate('/complaint/new')}
              className="mt-3 inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-black bg-indigo-600 text-white shadow-md shadow-indigo-500/20"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Submit Ticket</span>
            </button>
          </div>
        ) : (
          <div className="divide-y divide-slate-100 dark:divide-white/5">
            {recentComplaints.map((c) => (
              <div
                key={c.id}
                onClick={() => navigate(`/complaints/${c.id}`)}
                className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50/80 dark:hover:bg-slate-800/40 px-3.5 rounded-2xl transition-all cursor-pointer group"
              >
                <div className="space-y-1.5 flex-1 pr-4">
                  <div className="flex flex-wrap items-center gap-2.5">
                    <span className="text-xs font-mono font-bold text-slate-400">
                      #{c.id}
                    </span>
                    <h4 className="text-sm font-extrabold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                      {c.title}
                    </h4>
                    <CategoryBadge category={c.category} size="sm" />
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-1 font-medium">
                    {c.description}
                  </p>
                </div>

                <div className="flex items-center justify-between sm:justify-end gap-4 shrink-0">
                  <StatusBadge status={c.status} size="sm" />
                  <span className="text-[11px] font-mono text-slate-400">
                    {c.created_at ? new Date(c.created_at).toLocaleDateString() : ''}
                  </span>
                  <ChevronRight className="w-4 h-4 text-slate-300 dark:text-slate-600 group-hover:text-indigo-500 transition-colors" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
