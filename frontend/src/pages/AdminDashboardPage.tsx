import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { adminApi, categoriesApi } from '../api/client';
import { Complaint, ComplaintStatus, AdminStats } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { CategoryBadge } from '../components/CategoryBadge';
import {
  ShieldCheck,
  Search,
  CheckCircle2,
  Clock,
  RefreshCw,
  FileText,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  X,
  ExternalLink,
  Tags,
  Sparkles,
} from 'lucide-react';

interface Props {
  navigate: (path: string) => void;
  initialManageId?: number | null;
}

const TRANSITIONS: Record<string, string[]> = {
  Pending: ['Pending', 'In Progress'],
  'In Progress': ['In Progress', 'Resolved'],
  Resolved: ['Resolved', 'In Progress'],
};

export const AdminDashboardPage: React.FC<Props> = ({ navigate, initialManageId }) => {
  const { user } = useAuth();
  const { success, error, warning } = useToast();

  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('All');
  const [categoryFilter, setCategoryFilter] = useState<string>('All');
  const [sortOrder, setSortOrder] = useState<string>('newest');
  const [searchQuery, setSearchQuery] = useState('');

  // Pagination
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  // Status Update Modal State
  const [managingComplaint, setManagingComplaint] = useState<Complaint | null>(null);
  const [newStatus, setNewStatus] = useState<ComplaintStatus>('In Progress');
  const [resolutionRemarks, setResolutionRemarks] = useState('');
  const [reopenReason, setReopenReason] = useState('');
  const [savingStatus, setSavingStatus] = useState(false);
  const [modalError, setModalError] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      const data = await adminApi.getStats();
      setStats(data);
    } catch (err) {
      console.warn('Could not load admin stats:', err);
    }
  };

  const fetchCategories = async () => {
    try {
      const list = await categoriesApi.listAdmin();
      setCategories(list.map((c) => c.name));
    } catch {
      setCategories(['Academic', 'Hostel', 'Infrastructure', 'Other', 'Technical']);
    }
  };

  const fetchComplaints = async () => {
    setLoading(true);
    try {
      const res = await adminApi.listComplaints({
        page,
        per_page: perPage,
        status: statusFilter !== 'All' ? statusFilter : undefined,
        category: categoryFilter !== 'All' ? categoryFilter : undefined,
        sort: sortOrder,
        search: searchQuery.trim() || undefined,
      });

      setComplaints(res.complaints || []);
      setTotalPages(res.pages || 1);
      setTotalCount(res.total || 0);

      if (initialManageId && res.complaints) {
        const found = res.complaints.find((c) => c.id === initialManageId);
        if (found) {
          openManageModal(found);
        }
      }
    } catch (err) {
      console.error('Error fetching admin complaints:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    fetchCategories();
  }, []);

  useEffect(() => {
    fetchComplaints();
  }, [page, perPage, statusFilter, categoryFilter, sortOrder]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchComplaints();
  };

  const openManageModal = (c: Complaint) => {
    setManagingComplaint(c);
    const allowed = TRANSITIONS[c.status] || [c.status];
    const defaultNext = allowed.find((s) => s !== c.status) || c.status;
    setNewStatus(defaultNext as ComplaintStatus);
    setResolutionRemarks(c.resolution || '');
    setReopenReason('');
    setModalError(null);
  };

  const closeManageModal = () => {
    setManagingComplaint(null);
    setModalError(null);
  };

  const handleStatusUpdateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!managingComplaint) return;

    setModalError(null);
    const oldStatus = managingComplaint.status;
    const isReopening = oldStatus === 'Resolved' && newStatus === 'In Progress';
    const isResolving = newStatus === 'Resolved';

    if (isResolving && !resolutionRemarks.trim() && !managingComplaint.resolution) {
      setModalError('Resolution remarks are required when marking a complaint as Resolved.');
      return;
    }

    if (isReopening && !reopenReason.trim()) {
      setModalError('A reason is required to reopen a resolved complaint.');
      return;
    }

    setSavingStatus(true);
    try {
      await adminApi.updateStatus(managingComplaint.id, {
        status: newStatus,
        resolution: resolutionRemarks.trim() || undefined,
        reason: reopenReason.trim() || undefined,
      });

      success(`Ticket #${managingComplaint.id} transitioned to "${newStatus}"!`);
      closeManageModal();
      fetchComplaints();
      fetchStats();
    } catch (err: any) {
      const msg = err.message || 'Failed to update complaint status.';
      setModalError(msg);
      error(msg);
    } finally {
      setSavingStatus(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in bg-grid-slate">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-purple-950 to-slate-900 text-white p-7 sm:p-10 shadow-2xl border border-white/10">
        <div className="absolute top-0 right-0 w-80 h-80 bg-purple-500/20 blur-3xl rounded-full pointer-events-none" />

        <div className="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider bg-purple-500/10 text-purple-300 ring-1 ring-inset ring-purple-500/30">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Institutional Oversight Console</span>
            </div>
            <h1 className="text-2xl sm:text-4xl font-black tracking-tight text-white">
              Administrator Grievance Hub
            </h1>
            <p className="text-xs sm:text-sm text-purple-200/80 font-medium max-w-xl">
              Triage student submissions, enforce strict state machine rules, and post verified resolutions.
            </p>
          </div>

          <button
            onClick={() => navigate('/admin/categories')}
            className="inline-flex items-center gap-2 px-6 py-3 rounded-2xl font-black text-xs bg-white/10 hover:bg-white/20 text-purple-200 border border-white/10 backdrop-blur-md transition-all self-start sm:self-auto shrink-0 shadow-lg"
          >
            <Tags className="w-4 h-4" />
            <span>Manage Categories</span>
          </button>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">
        <div
          onClick={() => {
            setStatusFilter('All');
            setPage(1);
          }}
          className="p-6 rounded-3xl artistic-card hover-lift cursor-pointer space-y-2"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-black uppercase tracking-wider text-slate-400">
              Total Registry
            </span>
            <FileText className="w-4 h-4 text-purple-500" />
          </div>
          <div className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white">
            {stats?.total ?? totalCount}
          </div>
          <div className="text-[11px] font-medium text-slate-400">Across all classifications</div>
        </div>

        <div
          onClick={() => {
            setStatusFilter('Pending');
            setPage(1);
          }}
          className="p-6 rounded-3xl artistic-card hover-lift cursor-pointer space-y-2"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-black uppercase tracking-wider text-slate-400">
              Pending
            </span>
            <Clock className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-3xl sm:text-4xl font-black text-amber-600 dark:text-amber-400">
            {stats?.pending ?? 0}
          </div>
          <div className="text-[11px] font-medium text-slate-400">Awaiting initial action</div>
        </div>

        <div
          onClick={() => {
            setStatusFilter('In Progress');
            setPage(1);
          }}
          className="p-6 rounded-3xl artistic-card hover-lift cursor-pointer space-y-2"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-black uppercase tracking-wider text-slate-400">
              In Progress
            </span>
            <RefreshCw className="w-4 h-4 text-blue-500" />
          </div>
          <div className="text-3xl sm:text-4xl font-black text-blue-600 dark:text-blue-400">
            {stats?.in_progress ?? 0}
          </div>
          <div className="text-[11px] font-medium text-slate-400">Under investigation</div>
        </div>

        <div
          onClick={() => {
            setStatusFilter('Resolved');
            setPage(1);
          }}
          className="p-6 rounded-3xl artistic-card hover-lift cursor-pointer space-y-2"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-black uppercase tracking-wider text-slate-400">
              Resolved
            </span>
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-3xl sm:text-4xl font-black text-emerald-600 dark:text-emerald-400">
            {stats?.resolved ?? 0}
          </div>
          <div className="text-[11px] font-medium text-slate-400">Verified & addressed</div>
        </div>
      </div>

      {/* Advanced Filter Toolbar */}
      <div className="artistic-card rounded-3xl p-6 shadow-xl space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          {/* Status Tabs */}
          <div className="flex flex-wrap items-center gap-2">
            {['All', 'Pending', 'In Progress', 'Resolved'].map((st) => {
              const isActive = statusFilter === st;
              return (
                <button
                  key={st}
                  onClick={() => {
                    setStatusFilter(st);
                    setPage(1);
                  }}
                  className={`px-4 py-2 rounded-xl text-xs font-black transition-all ${
                    isActive
                      ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-md shadow-purple-500/25'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800/80 dark:text-slate-400'
                  }`}
                >
                  {st}
                </button>
              );
            })}
          </div>

          {/* Sort & Category selector */}
          <div className="flex flex-wrap items-center gap-2.5">
            <select
              value={categoryFilter}
              onChange={(e) => {
                setCategoryFilter(e.target.value);
                setPage(1);
              }}
              className="px-4 py-2 rounded-xl text-xs font-bold bg-white/70 dark:bg-slate-800/70 border border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-purple-500/20 shadow-sm"
            >
              <option value="All">All Departments</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>

            <select
              value={sortOrder}
              onChange={(e) => {
                setSortOrder(e.target.value);
                setPage(1);
              }}
              className="px-4 py-2 rounded-xl text-xs font-bold bg-white/70 dark:bg-slate-800/70 border border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-purple-500/20 shadow-sm"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="id_asc">ID (Low to High)</option>
              <option value="id_desc">ID (High to Low)</option>
              <option value="title_asc">Title (A-Z)</option>
            </select>
          </div>
        </div>

        {/* Live Search */}
        <form onSubmit={handleSearchSubmit} className="relative">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by complaint title, user name, or keyword..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl text-xs font-semibold bg-white/70 dark:bg-slate-800/70 border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 transition-all shadow-inner"
          />
        </form>
      </div>

      {/* Main Table */}
      <div className="artistic-card rounded-3xl shadow-xl overflow-hidden">
        {loading ? (
          <div className="py-24 flex justify-center">
            <div className="w-10 h-10 border-3 border-purple-600 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : complaints.length === 0 ? (
          <div className="py-16 text-center space-y-2">
            <p className="text-sm font-black text-slate-800 dark:text-slate-200">
              No complaints match the selected filter criteria
            </p>
            <p className="text-xs text-slate-400">
              Clear or broaden your search keywords or status filter.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 dark:bg-slate-800/80 text-slate-500 dark:text-slate-400 uppercase tracking-widest font-black text-[10px] border-b border-slate-200/80 dark:border-white/10">
                <tr>
                  <th className="px-6 py-4">ID</th>
                  <th className="px-6 py-4">Applicant</th>
                  <th className="px-6 py-4">Complaint Title</th>
                  <th className="px-6 py-4">Department</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Submitted</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-white/5">
                {complaints.map((c) => (
                  <tr
                    key={c.id}
                    className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors"
                  >
                    <td className="px-6 py-4 font-mono font-bold text-slate-400">
                      #{c.id}
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-extrabold text-slate-900 dark:text-white">
                        {c.user_name || `User #${c.user_id}`}
                      </div>
                      {c.user_email && (
                        <div className="text-[11px] text-slate-400 truncate">{c.user_email}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-900 dark:text-white max-w-xs">
                      <div className="truncate font-extrabold">{c.title}</div>
                      <div className="text-[11px] text-slate-400 line-clamp-1 font-normal">
                        {c.description}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <CategoryBadge category={c.category} size="sm" />
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={c.status} size="sm" />
                    </td>
                    <td className="px-6 py-4 text-slate-500 dark:text-slate-400 whitespace-nowrap font-mono text-[11px]">
                      {c.created_at ? new Date(c.created_at).toLocaleDateString() : ''}
                    </td>
                    <td className="px-6 py-4 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => openManageModal(c)}
                          className="px-3.5 py-1.5 rounded-xl text-xs font-black bg-purple-500/10 hover:bg-purple-500/20 text-purple-700 dark:text-purple-300 ring-1 ring-inset ring-purple-500/25 transition-all shadow-sm"
                        >
                          Manage Status
                        </button>
                        <button
                          onClick={() => navigate(`/complaints/${c.id}`)}
                          className="p-1.5 rounded-xl text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
                          title="View Full Ticket Details"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-2">
          <span className="text-xs text-slate-500 font-medium">
            Page <span className="font-extrabold text-slate-900 dark:text-white">{page}</span> of{' '}
            <span className="font-extrabold text-slate-900 dark:text-white">{totalPages}</span>
          </span>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="inline-flex items-center gap-1 px-4 py-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-300 disabled:opacity-40 shadow-sm"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
              <span>Previous</span>
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="inline-flex items-center gap-1 px-4 py-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-300 disabled:opacity-40 shadow-sm"
            >
              <span>Next</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* Status Transition Modal */}
      {managingComplaint && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-md animate-fade-in">
          <div className="artistic-card rounded-3xl max-w-lg w-full p-6 sm:p-8 shadow-2xl space-y-5 animate-slide-up border border-purple-500/20">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-white/10">
              <div>
                <h3 className="text-base font-black text-slate-900 dark:text-white">
                  Update Status: Ticket #{managingComplaint.id}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 truncate max-w-xs font-medium">
                  {managingComplaint.title}
                </p>
              </div>
              <button
                onClick={closeManageModal}
                className="p-1 rounded-xl text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {modalError && (
              <div className="p-3.5 rounded-2xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 text-rose-800 dark:text-rose-200 text-xs font-semibold flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
                <span>{modalError}</span>
              </div>
            )}

            <form onSubmit={handleStatusUpdateSubmit} className="space-y-4">
              {/* Allowed Status Selector */}
              <div>
                <label className="block text-[11px] font-black uppercase tracking-widest text-slate-700 dark:text-slate-300 mb-2">
                  Select Permitted Transition
                </label>
                <div className="grid grid-cols-2 gap-2.5">
                  {(TRANSITIONS[managingComplaint.status] || [managingComplaint.status]).map((st) => {
                    const isSelected = newStatus === st;
                    return (
                      <button
                        key={st}
                        type="button"
                        onClick={() => setNewStatus(st as ComplaintStatus)}
                        className={`p-3.5 rounded-2xl border text-left text-xs font-extrabold flex items-center justify-between transition-all ${
                          isSelected
                            ? 'bg-purple-500/10 border-purple-500 text-purple-700 dark:text-purple-300 ring-2 ring-purple-500/25 shadow-md'
                            : 'bg-white/60 dark:bg-slate-800/40 border-slate-200 dark:border-white/5 text-slate-700 dark:text-slate-300'
                        }`}
                      >
                        <span>{st}</span>
                        {isSelected && <CheckCircle2 className="w-4 h-4 text-purple-600" />}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Resolution Remarks required when moving to Resolved */}
              {(newStatus === 'Resolved' || managingComplaint.status === 'Resolved') && (
                <div>
                  <label className="block text-[11px] font-black uppercase tracking-widest text-slate-700 dark:text-slate-300 mb-1.5">
                    Resolution Remarks {newStatus === 'Resolved' && <span className="text-rose-500">*</span>}
                  </label>
                  <textarea
                    rows={4}
                    value={resolutionRemarks}
                    onChange={(e) => setResolutionRemarks(e.target.value)}
                    placeholder="Enter official resolution details, actions completed, or verified steps taken..."
                    className="w-full px-4 py-3 rounded-2xl text-xs font-medium bg-white/70 dark:bg-slate-800/70 border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 shadow-inner"
                  />
                </div>
              )}

              {/* Reopen Reason required when moving Resolved -> In Progress */}
              {managingComplaint.status === 'Resolved' && newStatus === 'In Progress' && (
                <div>
                  <label className="block text-[11px] font-black uppercase tracking-widest text-slate-700 dark:text-slate-300 mb-1.5">
                    Reason for Reopening <span className="text-rose-500">*</span>
                  </label>
                  <textarea
                    rows={3}
                    required
                    value={reopenReason}
                    onChange={(e) => setReopenReason(e.target.value)}
                    placeholder="Detail why this resolved grievance is being reopened for further action..."
                    className="w-full px-4 py-3 rounded-2xl text-xs font-medium bg-white/70 dark:bg-slate-800/70 border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 shadow-inner"
                  />
                </div>
              )}

              <div className="pt-2 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={closeManageModal}
                  className="px-5 py-2.5 rounded-xl text-xs font-bold text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingStatus}
                  className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl text-xs font-black bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white shadow-lg shadow-purple-500/25 disabled:opacity-50"
                >
                  {savingStatus ? (
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <span>Save Transition</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
