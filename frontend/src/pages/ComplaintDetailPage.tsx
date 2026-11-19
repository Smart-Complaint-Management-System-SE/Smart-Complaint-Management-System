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
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
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
      <div className="max-w-2xl mx-auto px-4 py-20 text-center space-y-4">
        <div className="w-14 h-14 rounded-3xl bg-amber-500/10 text-amber-600 flex items-center justify-center mx-auto shadow-inner">
          <AlertCircle className="w-7 h-7" />
        </div>
        <h2 className="text-xl font-black text-slate-800 dark:text-white">
          Ticket Not Accessible
        </h2>
        <p className="text-xs text-slate-400 font-medium max-w-sm mx-auto">
          {errorMsg || 'The requested ticket does not exist or you do not have permission to view it.'}
        </p>
        <button
          onClick={() => navigate('/complaints')}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-black bg-indigo-600 text-white shadow-md"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Complaints</span>
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in bg-grid-slate">
      {/* Back button */}
      <button
        type="button"
        onClick={() => navigate(user?.role === 'admin' ? '/admin' : '/complaints')}
        className="inline-flex items-center gap-2 text-xs font-black uppercase tracking-wider text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Return to {user?.role === 'admin' ? 'Admin Dashboard' : 'My Complaints'}</span>
      </button>

      {/* Ticket Container */}
      <div className="artistic-card rounded-3xl p-6 sm:p-10 shadow-2xl space-y-8">
        {/* Header Strip */}
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 border-b border-slate-100 dark:border-white/5 pb-6">
          <div className="space-y-3">
            <div className="flex flex-wrap items-center gap-2.5">
              <span className="text-xs font-mono font-black px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                Ticket #{complaint.id}
              </span>
              <CategoryBadge category={complaint.category} />
              <StatusBadge status={complaint.status} size="md" />
            </div>

            <h1 className="text-2xl sm:text-4xl font-black tracking-tight text-slate-900 dark:text-white">
              {complaint.title}
            </h1>

            <div className="flex flex-wrap items-center gap-5 text-xs text-slate-400 font-medium pt-1">
              <div className="flex items-center gap-1.5 font-mono">
                <Calendar className="w-3.5 h-3.5" />
                <span>
                  Submitted: {complaint.created_at ? new Date(complaint.created_at).toLocaleString() : ''}
                </span>
              </div>
              {complaint.updated_at && (
                <div className="flex items-center gap-1.5 font-mono">
                  <Clock className="w-3.5 h-3.5" />
                  <span>
                    Updated: {new Date(complaint.updated_at).toLocaleString()}
                  </span>
                </div>
              )}
            </div>
          </div>

          {user?.role === 'admin' && (
            <button
              onClick={() => navigate(`/admin?manage=${complaint.id}`)}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-black bg-purple-600 hover:bg-purple-700 text-white shadow-lg shadow-purple-500/25 self-start"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>Manage in Admin Console</span>
            </button>
          )}
        </div>

        {/* Visual Progression Stepper */}
        <div className="py-2">
          <ComplaintTimeline
            status={complaint.status}
            createdAt={complaint.created_at}
            updatedAt={complaint.updated_at}
            resolution={complaint.resolution}
          />
        </div>

        {/* Official Resolution Showcase */}
        {complaint.resolution && (
          <div className="p-7 rounded-3xl bg-gradient-to-br from-emerald-500/10 via-teal-500/5 to-transparent border border-emerald-500/25 space-y-3 animate-slide-up shadow-sm">
            <div className="flex items-center gap-2 text-xs font-black uppercase tracking-wider text-emerald-800 dark:text-emerald-300">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <span>Verified Administrator Resolution</span>
            </div>
            <div className="p-4 rounded-2xl bg-white/70 dark:bg-slate-900/60 border border-emerald-500/20 text-sm text-slate-800 dark:text-slate-100 font-medium leading-relaxed whitespace-pre-line shadow-inner">
              {complaint.resolution}
            </div>
          </div>
        )}

        {/* Full Description Section */}
        <div className="space-y-2">
          <h2 className="text-[11px] font-black uppercase tracking-widest text-slate-400">
            Complaint Description
          </h2>
          <div className="p-6 rounded-2xl bg-slate-50/80 dark:bg-slate-800/40 border border-slate-100 dark:border-white/5 text-sm text-slate-800 dark:text-slate-200 leading-relaxed whitespace-pre-wrap font-medium">
            {complaint.description}
          </div>
        </div>

        {/* History / Audit Log */}
        {complaint.history && complaint.history.length > 0 && (
          <div className="space-y-4 pt-6 border-t border-slate-100 dark:border-white/5">
            <div className="flex items-center gap-2">
              <History className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              <h2 className="text-[11px] font-black uppercase tracking-widest text-slate-700 dark:text-slate-300">
                Resolution History & Audit Log
              </h2>
            </div>

            <div className="space-y-3">
              {complaint.history.map((h) => (
                <div
                  key={h.id}
                  className="p-4 rounded-2xl bg-slate-50/80 dark:bg-slate-800/40 border border-slate-200/60 dark:border-white/5 text-xs space-y-2"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-slate-400">State Transition:</span>
                      <span className="font-extrabold text-slate-700 dark:text-slate-300">{h.old_status}</span>
                      <span className="text-slate-400">→</span>
                      <span className="font-extrabold text-indigo-600 dark:text-indigo-400">{h.new_status}</span>
                    </div>
                    <span className="text-[11px] font-mono text-slate-400">
                      {h.created_at ? new Date(h.created_at).toLocaleString() : ''}
                    </span>
                  </div>
                  {h.note && (
                    <p className="text-slate-600 dark:text-slate-300 font-medium pl-3 border-l-2 border-indigo-400">
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
