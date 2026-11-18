import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { complaintsApi, categoriesApi } from '../api/client';
import { Complaint, ComplaintStatus } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { CategoryBadge } from '../components/CategoryBadge';
import {
  ListFilter,
  PlusCircle,
  Search,
  Filter,
  ChevronLeft,
  ChevronRight,
  LayoutGrid,
  Table as TableIcon,
  Inbox,
  ArrowUpDown,
  Clock,
  ChevronDown,
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
        setCategories(['Academic', 'Infrastructure', 'Hostel', 'Technical', 'Other']);
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
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
            {user?.role === 'admin' ? 'Complaints Registry' : 'My Complaints'}
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            {totalCount} total grievance {totalCount === 1 ? 'ticket' : 'tickets'} recorded
          </p>
        </div>

        <button
          onClick={() => navigate('/complaint/new')}
          className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-500/25 transition-all self-start sm:self-auto"
        >
          <PlusCircle className="w-4 h-4" />
          <span>New Complaint</span>
        </button>
      </div>

      {/* Control Bar: Search, Status Chips, Category Selector, Layout Toggle */}
      <div className="bg-white dark:bg-slate-900 rounded-3xl p-5 shadow-sm border border-slate-200/80 dark:border-slate-800 space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          {/* Status Filter Chips */}
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
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
                    isActive
                      ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900 shadow-sm'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700'
                  }`}
                >
                  {st}
                </button>
              );
            })}
          </div>

          {/* View mode toggle */}
          <div className="flex items-center gap-1.5 self-end lg:self-auto bg-slate-100 dark:bg-slate-800 p-1 rounded-xl">
            <button
              onClick={() => setViewMode('cards')}
              title="Card Grid View"
              className={`p-1.5 rounded-lg text-xs font-medium transition-colors ${
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
              className={`p-1.5 rounded-lg text-xs font-medium transition-colors ${
                viewMode === 'table'
                  ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-indigo-400 shadow-sm'
                  : 'text-slate-500 hover:text-slate-800 dark:text-slate-400'
              }`}
            >
              <TableIcon className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Secondary row: Search & Category filter */}
        <div className="flex flex-col sm:flex-row items-center gap-3 pt-2 border-t border-slate-100 dark:border-slate-800">
          <form onSubmit={handleSearchSubmit} className="relative flex-1 w-full">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search complaints by title or description..."
              className="w-full pl-10 pr-4 py-2 rounded-xl text-xs font-medium bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
            />
          </form>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <select
              value={categoryFilter}
              onChange={(e) => {
                setCategoryFilter(e.target.value);
                setPage(1);
              }}
              className="w-full sm:w-auto px-3 py-2 rounded-xl text-xs font-semibold bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            >
              <option value="All">All Categories</option>
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
        <div className="py-20 flex justify-center">
          <div className="w-10 h-10 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : complaints.length === 0 ? (
        <div className="bg-white dark:bg-slate-900 rounded-3xl p-12 text-center border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center mx-auto">
            <Inbox className="w-7 h-7" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-800 dark:text-slate-200">
              No complaints found
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-sm mx-auto">
              {statusFilter !== 'All' || categoryFilter !== 'All' || searchQuery
                ? 'No tickets match the selected filters. Try clearing filters or changing search keywords.'
                : 'You have not submitted any complaints yet.'}
            </p>
          </div>
          {statusFilter !== 'All' || categoryFilter !== 'All' || searchQuery ? (
            <button
              onClick={handleResetFilters}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-800 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-white"
            >
              Clear all filters
            </button>
          ) : (
            <button
              onClick={() => navigate('/complaint/new')}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white shadow-md"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Submit Complaint</span>
            </button>
          )}
        </div>
      ) : viewMode === 'cards' ? (
        /* Card Grid View */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {complaints.map((c) => (
            <div
              key={c.id}
              onClick={() => navigate(`/complaints/${c.id}`)}
              className="bg-white dark:bg-slate-900 rounded-3xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm hover:shadow-xl hover:border-indigo-200 dark:hover:border-indigo-900/60 transition-all flex flex-col justify-between cursor-pointer group"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-mono font-bold text-slate-400">
                    #{c.id}
                  </span>
                  <StatusBadge status={c.status} size="sm" />
                </div>

                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors line-clamp-1">
                    {c.title}
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-3 leading-relaxed">
                    {c.description}
                  </p>
                </div>
              </div>

              <div className="pt-4 mt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
                <CategoryBadge category={c.category} size="sm" />
                <span className="text-[11px] text-slate-400 font-medium">
                  {c.created_at ? new Date(c.created_at).toLocaleDateString() : ''}
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Compact Table View */
        <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-slate-200/80 dark:border-slate-800 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 dark:text-slate-400 uppercase tracking-wider font-bold border-b border-slate-200/80 dark:border-slate-800">
                <tr>
                  <th className="px-5 py-3.5">ID</th>
                  <th className="px-5 py-3.5">Title</th>
                  <th className="px-5 py-3.5">Category</th>
                  <th className="px-5 py-3.5">Status</th>
                  <th className="px-5 py-3.5">Submitted</th>
                  <th className="px-5 py-3.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {complaints.map((c) => (
                  <tr
                    key={c.id}
                    onClick={() => navigate(`/complaints/${c.id}`)}
                    className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 cursor-pointer transition-colors"
                  >
                    <td className="px-5 py-3.5 font-mono font-bold text-slate-400">
                      #{c.id}
                    </td>
                    <td className="px-5 py-3.5 font-bold text-slate-900 dark:text-white max-w-xs truncate">
                      {c.title}
                    </td>
                    <td className="px-5 py-3.5">
                      <CategoryBadge category={c.category} size="sm" />
                    </td>
                    <td className="px-5 py-3.5">
                      <StatusBadge status={c.status} size="sm" />
                    </td>
                    <td className="px-5 py-3.5 text-slate-500 dark:text-slate-400">
                      {c.created_at ? new Date(c.created_at).toLocaleDateString() : ''}
                    </td>
                    <td className="px-5 py-3.5 text-right font-bold text-indigo-600 hover:text-indigo-700">
                      View
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
          <span className="text-xs text-slate-500 dark:text-slate-400">
            Page <span className="font-bold text-slate-900 dark:text-white">{page}</span> of{' '}
            <span className="font-bold text-slate-900 dark:text-white">{totalPages}</span>
          </span>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-bold bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 disabled:opacity-40 disabled:pointer-events-none hover:bg-slate-50"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
              <span>Previous</span>
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-bold bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 disabled:opacity-40 disabled:pointer-events-none hover:bg-slate-50"
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
