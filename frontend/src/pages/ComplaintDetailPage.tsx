import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { complaintsApi, adminApi } from '../api/client';
import { ComplaintDetail, ComplaintStatus } from '../types';
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
  User as UserIcon,
  X,
  Edit3,
} from 'lucide-react';

interface Props {
  complaintId: number;
  navigate: (path: string) => void;
}

const TRANSITIONS: Record<string, string[]> = {
  Pending: ['Pending', 'In Progress'],
  'In Progress': ['In Progress', 'Resolved'],
  Resolved: ['Resolved', 'In Progress'],
};

export const ComplaintDetailPage: React.FC<Props> = ({ complaintId, navigate }) => {
  const { user } = useAuth();
  const { success, error } = useToast();
  const [complaint, setComplaint] = useState<ComplaintDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Status Modal State for Administrators
  const [isManageModalOpen, setIsManageModalOpen] = useState(false);
  const [newStatus, setNewStatus] = useState<ComplaintStatus>('In Progress');
  const [resolutionRemarks, setResolutionRemarks] = useState('');
  const [reopenReason, setReopenReason] = useState('');
  const [savingStatus, setSavingStatus] = useState(false);
  const [modalError, setModalError] = useState<string | null>(null);

  const fetchDetail = async () => {
    setLoading(true);
    try {
      const data = await complaintsApi.get(complaintId);
      setComplaint(data);
      if (data) {
        const allowed = TRANSITIONS[data.status] || [data.status];
        const next = allowed.find((s) => s !== data.status) || data.status;
        setNewStatus(next as ComplaintStatus);
        setResolutionRemarks(data.resolution || '');
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Could not load complaint details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
  }, [complaintId]);

  const openManageModal = () => {
    if (!complaint) return;
    const allowed = TRANSITIONS[complaint.status] || [complaint.status];
    const next = allowed.find((s) => s !== complaint.status) || complaint.status;
    setNewStatus(next as ComplaintStatus);
    setResolutionRemarks(complaint.resolution || '');
    setReopenReason('');
    setModalError(null);
    setIsManageModalOpen(true);
  };

  const handleStatusSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!complaint) return;

    setModalError(null);
    const oldStatus = complaint.status;
    const isReopening = oldStatus === 'Resolved' && newStatus === 'In Progress';
    const isResolving = newStatus === 'Resolved';

    if (isResolving && !resolutionRemarks.trim() && !complaint.resolution) {
      setModalError('Resolution remarks are required when marking a complaint as Resolved.');
      return;
    }

    if (isReopening && !reopenReason.trim()) {
      setModalError('A reason is required to reopen a resolved complaint.');
      return;
    }

    setSavingStatus(true);
    try {
      await adminApi.updateStatus(complaint.id, {
        status: newStatus,
        resolution: resolutionRemarks.trim() || undefined,
        reason: reopenReason.trim() || undefined,
      });

      success(`Ticket #${complaint.id} transitioned to "${newStatus}"!`);
      setIsManageModalOpen(false);
      fetchDetail();
    } catch (err: any) {
      const msg = err.message || 'Failed to update complaint status.';
      setModalError(msg);
      error(msg);
    } finally {
      setSavingStatus(false);
    }
  };

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
          onClick={() => navigate(user?.role === 'admin' ? '/admin' : '/complaints')}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-black bg-indigo-600 text-white shadow-md"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to {user?.role === 'admin' ? 'Admin Dashboard' : 'Complaints'}</span>
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

              {complaint.user_name && (
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-purple-500/10 text-purple-700 dark:text-purple-300 ring-1 ring-inset ring-purple-500/20 text-xs font-bold">
                  <UserIcon className="w-3.5 h-3.5" />
                  <span>Applicant: {complaint.user_name}</span>
                  {complaint.user_email && (
                    <span className="text-[11px] opacity-75">({complaint.user_email})</span>
                  )}
                </div>
              )}
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
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 self-start">
              <button
                onClick={openManageModal}
                className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-2xl text-xs font-black bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white shadow-xl shadow-purple-500/25 transition-all"
              >
                <Edit3 className="w-4 h-4" />
                <span>Update Status & Verify</span>
              </button>
            </div>
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

      {/* Admin Status Transition Modal */}
      {isManageModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-md animate-fade-in">
          <div className="artistic-card rounded-3xl max-w-lg w-full p-6 sm:p-8 shadow-2xl space-y-5 animate-slide-up border border-purple-500/20">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-white/10">
              <div>
                <h3 className="text-base font-black text-slate-900 dark:text-white">
                  Update Status: Ticket #{complaint.id}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 truncate max-w-xs font-medium">
                  {complaint.title}
                </p>
              </div>
              <button
                onClick={() => setIsManageModalOpen(false)}
                className="p-1 rounded-xl text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {modalError && (
              <div className="p-3.5 rounded-2xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900/60 text-rose-800 dark:text-rose-200 text-xs font-semibold flex items-start gap-2.5">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
                <span>{modalError}</span>
              </div>
            )}

            <form onSubmit={handleStatusSubmit} className="space-y-4">
              <div>
                <label className="block text-[11px] font-black uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1.5">
                  Select New Status <span className="text-rose-500">*</span>
                </label>
                <select
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value as ComplaintStatus)}
                  className="w-full px-4 py-2.5 rounded-xl text-sm font-semibold bg-white/70 dark:bg-slate-800/70 border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white focus:outline-none focus:ring-4 focus:ring-purple-500/15 focus:border-purple-500 shadow-inner"
                >
                  {(TRANSITIONS[complaint.status] || [complaint.status]).map((st) => (
                    <option key={st} value={st}>
                      {st} {st === complaint.status ? '(Current)' : ''}
                    </option>
                  ))}
                </select>
              </div>

              {newStatus === 'Resolved' && (
                <div className="space-y-1.5">
                  <label className="block text-[11px] font-black uppercase tracking-wider text-slate-700 dark:text-slate-300">
                    Resolution Remarks <span className="text-rose-500">*</span>
                  </label>
                  <textarea
                    rows={4}
                    required={!complaint.resolution}
                    value={resolutionRemarks}
                    onChange={(e) => setResolutionRemarks(e.target.value)}
                    placeholder="Document the corrective actions taken, maintenance performed, or resolution steps..."
                    className="w-full px-4 py-2.5 rounded-xl text-xs font-medium bg-white/70 dark:bg-slate-800/70 border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-4 focus:ring-purple-500/15 focus:border-purple-500 shadow-inner"
                  />
                </div>
              )}

              {complaint.status === 'Resolved' && newStatus === 'In Progress' && (
                <div className="space-y-1.5">
                  <label className="block text-[11px] font-black uppercase tracking-wider text-slate-700 dark:text-slate-300">
                    Reopening Reason <span className="text-rose-500">*</span>
                  </label>
                  <textarea
                    rows={3}
                    required
                    value={reopenReason}
                    onChange={(e) => setReopenReason(e.target.value)}
                    placeholder="Explain why this resolved ticket is being reopened for further investigation..."
                    className="w-full px-4 py-2.5 rounded-xl text-xs font-medium bg-white/70 dark:bg-slate-800/70 border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-4 focus:ring-purple-500/15 focus:border-purple-500 shadow-inner"
                  />
                </div>
              )}

              <div className="flex items-center justify-end gap-2.5 pt-2">
                <button
                  type="button"
                  onClick={() => setIsManageModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-bold text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingStatus}
                  className="px-6 py-2.5 rounded-xl text-xs font-black bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white shadow-xl shadow-purple-500/25 disabled:opacity-50 transition-all"
                >
                  {savingStatus ? 'Saving...' : 'Update & Verify'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
