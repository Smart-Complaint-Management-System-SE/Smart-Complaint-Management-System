import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { complaintsApi } from '../api/client';
import { ComplaintDetail } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { CategoryBadge } from '../components/CategoryBadge';
import { ComplaintTimeline } from '../components/ComplaintTimeline';
import {
  ArrowLeft,
  Calendar,
  Clock,
  Sparkles,
  History,
  FileText,
  User as UserIcon,
  ShieldCheck,
  CheckCircle2,
  RefreshCw,
} from 'lucide-react';

interface Props {
  complaintId: number;
  navigate: (path: string) => void;
}

export const ComplaintDetailPage: React.FC<Props> = ({ complaintId, navigate }) => {
  const { user } = useAuth();
  const [complaint, setComplaint] = useState<ComplaintDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    const fetchDetail = async () => {
      setLoading(true);
      try {
        const data = await complaintsApi.get(complaintId);
        setComplaint(data);
      } catch (err: any) {
        setErrorMsg(err.message || 'Could not load complaint details.');
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [complaintId]);

  if (loading) {
    return (
      <div className="py-24 flex justify-center">
        <div className="w-10 h-10 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (errorMsg || !complaint) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center space-y-4">
        <h2 className="text-xl font-bold text-slate-800 dark:text-white">
          Complaint Not Found
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          {errorMsg || 'The complaint ticket you are trying to view does not exist or you do not have permission to view it.'}
        </p>
        <button
          onClick={() => navigate('/complaints')}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 text-white"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Complaints</span>
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      {/* Top Breadcrumb / Navigation */}
      <button
        type="button"
        onClick={() => navigate(user?.role === 'admin' ? '/admin' : '/complaints')}
        className="inline-flex items-center gap-2 text-xs font-bold text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to {user?.role === 'admin' ? 'Admin Dashboard' : 'My Complaints'}</span>
      </button>

      {/* Main Ticket Banner */}
      <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 shadow-xl border border-slate-200/80 dark:border-slate-800 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 border-b border-slate-100 dark:border-slate-800 pb-6">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2.5">
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                Ticket #{complaint.id}
              </span>
              <CategoryBadge category={complaint.category} />
              <StatusBadge status={complaint.status} size="md" />
            </div>

            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
              {complaint.title}
            </h1>

            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 dark:text-slate-400 font-medium pt-1">
              <div className="flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                <span>
                  Submitted: {complaint.created_at ? new Date(complaint.created_at).toLocaleString() : ''}
                </span>
              </div>
              {complaint.updated_at && (
                <div className="flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-slate-400" />
                  <span>
                    Last Updated: {new Date(complaint.updated_at).toLocaleString()}
                  </span>
                </div>
              )}
            </div>
          </div>

          {user?.role === 'admin' && (
            <button
              onClick={() => navigate(`/admin?manage=${complaint.id}`)}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold bg-purple-600 hover:bg-purple-700 text-white shadow-md self-start"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>Manage in Admin Console</span>
            </button>
          )}
        </div>

        {/* Real-time Status Progression Timeline */}
        <div className="py-2">
          <ComplaintTimeline
            status={complaint.status}
            createdAt={complaint.created_at}
            updatedAt={complaint.updated_at}
            resolution={complaint.resolution}
          />
        </div>

        {/* Official Resolution Showcase Box */}
        {complaint.resolution && (
          <div className="p-6 rounded-2xl bg-emerald-50/90 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/80 space-y-2 animate-slide-up">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-800 dark:text-emerald-300">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <span>Official Administrator Resolution Remarks</span>
            </div>
            <p className="text-sm text-emerald-950 dark:text-emerald-100 font-medium leading-relaxed whitespace-pre-line pl-6 border-l-2 border-emerald-400 dark:border-emerald-600">
              {complaint.resolution}
            </p>
          </div>
        )}

        {/* Full Description Section */}
        <div className="space-y-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Complaint Description
          </h3>
          <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800 text-sm text-slate-800 dark:text-slate-200 leading-relaxed whitespace-pre-wrap">
            {complaint.description}
          </div>
        </div>

        {/* History / Audit Log */}
        {complaint.history && complaint.history.length > 0 && (
          <div className="space-y-3 pt-4 border-t border-slate-100 dark:border-slate-800">
            <div className="flex items-center gap-2">
              <History className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                Resolution History & Timeline Log
              </h3>
            </div>

            <div className="space-y-3">
              {complaint.history.map((h) => (
                <div
                  key={h.id}
                  className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800 text-xs space-y-1.5"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-slate-500">Status changed:</span>
                      <span className="font-bold text-slate-700 dark:text-slate-300">{h.old_status}</span>
                      <span className="text-slate-400">→</span>
                      <span className="font-bold text-indigo-600 dark:text-indigo-400">{h.new_status}</span>
                    </div>
                    <span className="text-[11px] text-slate-400">
                      {h.created_at ? new Date(h.created_at).toLocaleString() : ''}
                    </span>
                  </div>
                  {h.note && (
                    <p className="text-slate-600 dark:text-slate-300 font-medium pl-2 border-l-2 border-indigo-400">
                      {h.note}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
