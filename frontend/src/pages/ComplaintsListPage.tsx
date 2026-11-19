import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { complaintsApi, categoriesApi } from '../api/client';
import { Complaint } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { CategoryBadge } from '../components/CategoryBadge';
import {
  PlusCircle,
  Search,
  ChevronLeft,
  ChevronRight,
  LayoutGrid,
  Table as TableIcon,
  Inbox,
  Sparkles,
} from 'lucide-react';

interface Props {
  navigate: (path: string) => void;
  initialStatus?: string;
}

export const ComplaintsListPage: React.FC<Props> = ({ navigate, initialStatus }) => {
  const { user } = useAuth();

  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters & State
  const [statusFilter, setStatusFilter] = useState<string>(initialStatus || 'All');
  const [categoryFilter, setCategoryFilter] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'cards' | 'table'>('cards');

  // Pagination
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  const fetchComplaints = async () => {
    setLoading(true);
    try {
      const statusParam = statusFilter !== 'All' ? statusFilter : undefined;
      const categoryParam = categoryFilter !== 'All' ? categoryFilter : undefined;
      const res = await complaintsApi.list(
        page,
        perPage,
        statusParam,
        categoryParam,
        searchQuery.trim() || undefined
      );
      setComplaints(res.complaints || []);
      setTotalPages(res.pages || 1);
      setTotalCount(res.total || 0);
    } catch (err) {
      console.error('Error fetching complaints:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const fetchCats = async () => {
      try {
        const list = await categoriesApi.listAvailable();
        if (list && list.length > 0) {
          setCategories(list.map((c) => c.name));
        }
      } catch {
        setCategories(['Academic', 'Hostel', 'Infrastructure', 'Other', 'Technical']);
      }
    };
    fetchCats();
  }, []);

  useEffect(() => {
    fetchComplaints();
  }, [page, perPage, statusFilter, categoryFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchComplaints();
  };

  const handleResetFilters = () => {
    setStatusFilter('All');
    setCategoryFilter('All');
    setSearchQuery('');
    setPage(1);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 animate-fade-in bg-grid-slate">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-[11px] font-black uppercase tracking-wider bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 ring-1 ring-inset ring-indigo-500/25 mb-1.5">
            <Sparkles className="w-3 h-3" />
            <span>Complaint Ledger</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white">
            {user?.role === 'admin' ? 'Campus Grievance Registry' : 'My Complaints'}
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 font-medium">
            {totalCount} total grievance {totalCount === 1 ? 'ticket' : 'tickets'} recorded on file
          </p>
        </div>

        <button
          onClick={() => navigate('/complaint/new')}
          className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-2xl font-black text-xs bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white shadow-lg shadow-indigo-500/25 transition-all self-start sm:self-auto"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Submit Grievance</span>
        </button>
      </div>

      {/* Control Bar: Filters & Search */}
      <div className="artistic-card rounded-3xl p-5 sm:p-6 shadow-xl space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
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
                      ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-md shadow-indigo-500/25'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200/80 dark:bg-slate-800/80 dark:text-slate-400 dark:hover:bg-slate-700'
                  }`}
                >
                  {st}
                </button>
              );
            })}
          </div>

          {/* View mode toggle */}
          <div className="flex items-center gap-1.5 self-end lg:self-auto bg-slate-100 dark:bg-slate-800/80 p-1 rounded-xl">
            <button
              onClick={() => setViewMode('cards')}
              title="Card Grid View"
              className={`p-1.5 rounded-lg text-xs transition-colors ${
                viewMode === 'cards'
                  ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-indigo-400 shadow-sm'
                  : 'text-slate-500 hover:text-slate-800 dark:text-slate-400'
              }`}
            >
              <LayoutGrid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('table')}
              title="Compact Table View"
              className={`p-1.5 rounded-lg text-xs transition-colors ${
                viewMode === 'table'
                  ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-indigo-400 shadow-sm'
                  : 'text-slate-500 hover:text-slate-800 dark:text-slate-400'
              }`}
            >
              <TableIcon className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Search & Category row */}
        <div className="flex flex-col sm:flex-row items-center gap-3 pt-3 border-t border-slate-100 dark:border-white/5">
          <form onSubmit={handleSearchSubmit} className="relative flex-1 w-full">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search complaints by title, keyword, or description..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl text-xs font-semibold bg-white/70 dark:bg-slate-800/70 border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all shadow-inner"
            />
          </form>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <select
              value={categoryFilter}
              onChange={(e) => {
                setCategoryFilter(e.target.value);
                setPage(1);
              }}
              className="w-full sm:w-auto px-4 py-2.5 rounded-xl text-xs font-bold bg-white/70 dark:bg-slate-800/70 border border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 shadow-sm"
            >
              <option value="All">All Departments</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>

            {(statusFilter !== 'All' || categoryFilter !== 'All' || searchQuery) && (
              <button
                type="button"
                onClick={handleResetFilters}
                className="px-3 py-2 rounded-xl text-xs font-bold text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors whitespace-nowrap"
              >
                Reset
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      {loading ? (
        <div className="py-24 flex justify-center">
          <div className="w-10 h-10 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : complaints.length === 0 ? (
        <div className="artistic-card rounded-3xl p-14 text-center shadow-xl space-y-4">
          <div className="w-16 h-16 rounded-3xl bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center mx-auto shadow-inner">
            <Inbox className="w-8 h-8" />
          </div>
          <div>
            <h3 className="text-base font-black text-slate-800 dark:text-slate-200">
              No matching complaints found
            </h3>
            <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto font-medium">
              {statusFilter !== 'All' || categoryFilter !== 'All' || searchQuery
                ? 'No grievance tickets match your current filters. Clear the search or status to view more.'
                : user?.role === 'admin'
                ? 'No complaints have been registered by students yet.'
                : 'You have not submitted any complaints yet.'}
            </p>
          </div>
          {statusFilter !== 'All' || categoryFilter !== 'All' || searchQuery ? (
            <button
              onClick={handleResetFilters}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-black bg-slate-100 hover:bg-slate-200 text-slate-800 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-white"
            >
              Reset Filters
            </button>
          ) : user?.role === 'admin' ? (
            <button
              onClick={() => navigate('/admin')}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-2xl text-xs font-black bg-purple-600 hover:bg-purple-700 text-white shadow-lg shadow-purple-500/25 transition-all"
            >
              <span>Go to Admin Hub</span>
            </button>
          ) : (
            <button
              onClick={() => navigate('/complaint/new')}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-2xl text-xs font-black bg-indigo-600 text-white shadow-lg"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Submit First Complaint</span>
            </button>
          )}
        </div>
      ) : viewMode === 'cards' ? (
        /* Card Grid View */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {complaints.map((c) => (
            <div
              key={c.id}
              onClick={() => navigate(`/complaints/${c.id}`)}
              className="artistic-card rounded-3xl p-6 hover-lift flex flex-col justify-between cursor-pointer group space-y-4"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-mono font-bold text-slate-400">
                    #{c.id}
                  </span>
                  <StatusBadge status={c.status} size="sm" />
                </div>

                <div>
                  <h3 className="text-base font-extrabold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors line-clamp-1">
                    {c.title}
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-3 leading-relaxed font-medium">
                    {c.description}
                  </p>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 dark:border-white/5 flex items-center justify-between text-xs">
                <CategoryBadge category={c.category} size="sm" />
                <span className="text-[11px] font-mono text-slate-400">
                  {c.created_at ? new Date(c.created_at).toLocaleDateString() : ''}
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Compact Table View */
        <div className="artistic-card rounded-3xl shadow-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 dark:bg-slate-800/80 text-slate-500 dark:text-slate-400 uppercase tracking-widest font-black text-[10px] border-b border-slate-200/80 dark:border-white/10">
                <tr>
                  <th className="px-6 py-4">ID</th>
                  <th className="px-6 py-4">Title</th>
                  <th className="px-6 py-4">Department</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Date</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-white/5">
                {complaints.map((c) => (
                  <tr
                    key={c.id}
                    onClick={() => navigate(`/complaints/${c.id}`)}
                    className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-4 font-mono font-bold text-slate-400">
                      #{c.id}
                    </td>
                    <td className="px-6 py-4 font-extrabold text-slate-900 dark:text-white max-w-xs truncate">
                      {c.title}
                    </td>
                    <td className="px-6 py-4">
                      <CategoryBadge category={c.category} size="sm" />
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={c.status} size="sm" />
                    </td>
                    <td className="px-6 py-4 text-slate-500 dark:text-slate-400 font-mono text-[11px]">
                      {c.created_at ? new Date(c.created_at).toLocaleDateString() : ''}
                    </td>
                    <td className="px-6 py-4 text-right font-black text-indigo-600 dark:text-indigo-400 hover:underline">
                      View Details
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Pagination Footer */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-4">
          <span className="text-xs text-slate-500 font-medium">
            Page <span className="font-extrabold text-slate-900 dark:text-white">{page}</span> of{' '}
            <span className="font-extrabold text-slate-900 dark:text-white">{totalPages}</span>
          </span>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="inline-flex items-center gap-1 px-4 py-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-300 disabled:opacity-40 hover:bg-slate-50 shadow-sm"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
              <span>Previous</span>
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="inline-flex items-center gap-1 px-4 py-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-300 disabled:opacity-40 hover:bg-slate-50 shadow-sm"
            >
              <span>Next</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
