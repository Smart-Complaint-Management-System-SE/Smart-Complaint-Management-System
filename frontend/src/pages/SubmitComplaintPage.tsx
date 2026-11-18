import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { complaintsApi, categoriesApi } from '../api/client';
import { Category } from '../types';
import { getCategoryIcon } from '../components/CategoryBadge';
import {
  PlusCircle,
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  FileText,
  Send,
  HelpCircle,
  Sparkles,
} from 'lucide-react';

interface Props {
  navigate: (path: string) => void;
}

const DEFAULT_CATEGORIES = [
  'Academic',
  'Infrastructure',
  'Hostel',
  'Technical',
  'Other',
];

export const SubmitComplaintPage: React.FC<Props> = ({ navigate }) => {
  const { user } = useAuth();
  const { success, error } = useToast();

  const [categories, setCategories] = useState<string[]>(DEFAULT_CATEGORIES);
  const [selectedCategory, setSelectedCategory] = useState<string>('Academic');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const list = await categoriesApi.listAvailable();
        if (list && list.length > 0) {
          const names = list.map((c) => c.name);
          setCategories(names);
          if (!names.includes(selectedCategory)) {
            setSelectedCategory(names[0]);
          }
        }
      } catch {
        // Fallback to default categories
        setCategories(DEFAULT_CATEGORIES);
      }
    };
    fetchCategories();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    const trimmedTitle = title.trim();
    const trimmedDesc = description.trim();

    if (!trimmedTitle || !trimmedDesc || !selectedCategory) {
      setFormError('Title, description, and category are required.');
      return;
    }

    if (trimmedTitle.length > 100) {
      setFormError('Title must be 100 characters or fewer.');
      return;
    }

    setLoading(true);
    try {
      const res = await complaintsApi.create(trimmedTitle, trimmedDesc, selectedCategory);
      success('Complaint submitted successfully!');
      if (res?.complaint?.id) {
        navigate(`/complaints/${res.complaint.id}`);
      } else {
        navigate('/complaints');
      }
    } catch (err: any) {
      const msg = err.message || 'Failed to submit complaint. Please try again.';
      setFormError(msg);
      error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 space-y-6 animate-fade-in">
      {/* Top Navigation */}
      <button
        type="button"
        onClick={() => navigate('/dashboard')}
        className="inline-flex items-center gap-2 text-xs font-bold text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Dashboard</span>
      </button>

      {/* Main Form Container */}
      <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-10 shadow-xl border border-slate-200/80 dark:border-slate-800 space-y-8">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300 mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span>New Grievance Ticket</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
            Submit a Complaint
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Provide details about your issue. Administrators will triage, update status, and post resolutions.
          </p>
        </div>

        {formError && (
          <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900/60 text-rose-800 dark:text-rose-200 text-xs font-semibold flex items-start gap-2.5">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
            <span>{formError}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Category Picker (Cards Grid) */}
          <div className="space-y-2.5">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
              Select Category <span className="text-rose-500">*</span>
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
              {categories.map((cat) => {
                const isSelected = selectedCategory === cat;
                return (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => setSelectedCategory(cat)}
                    className={`flex flex-col items-center justify-center p-3.5 rounded-2xl border text-center transition-all ${
                      isSelected
                        ? 'bg-indigo-50 dark:bg-indigo-950/60 border-indigo-500 text-indigo-700 dark:text-indigo-300 ring-2 ring-indigo-500/20 shadow-md'
                        : 'bg-slate-50 dark:bg-slate-800/60 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-600'
                    }`}
                  >
                    <div
                      className={`w-9 h-9 rounded-xl flex items-center justify-center mb-2 ${
                        isSelected
                          ? 'bg-indigo-600 text-white shadow-sm'
                          : 'bg-white dark:bg-slate-700 text-slate-500 dark:text-slate-300'
                      }`}
                    >
                      {getCategoryIcon(cat, 'w-4 h-4')}
                    </div>
                    <span className="text-xs font-bold">{cat}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Title Input */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center">
              <label
                htmlFor="complaint-title"
                className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300"
              >
                Complaint Title <span className="text-rose-500">*</span>
              </label>
              <span
                className={`text-[11px] font-mono ${
                  title.length > 90 ? 'text-amber-600 font-bold' : 'text-slate-400'
                }`}
              >
                {title.length}/100
              </span>
            </div>
            <input
              id="complaint-title"
              type="text"
              required
              maxLength={100}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. WiFi outage in Library 2nd floor"
              className="w-full px-4 py-3 rounded-2xl text-sm font-medium bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
            />
          </div>

          {/* Description Textarea */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center">
              <label
                htmlFor="complaint-description"
                className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300"
              >
                Detailed Description <span className="text-rose-500">*</span>
              </label>
              <span className="text-[11px] text-slate-400 font-mono">
                {description.length} chars
              </span>
            </div>
            <textarea
              id="complaint-description"
              required
              rows={6}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the issue in detail, including specific location, time observed, and any impact..."
              className="w-full px-4 py-3 rounded-2xl text-sm font-medium bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all resize-y"
            />
          </div>

          {/* Action buttons */}
          <div className="pt-2 flex flex-col-reverse sm:flex-row items-center justify-end gap-3">
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="w-full sm:w-auto px-5 py-3 rounded-2xl text-sm font-semibold text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-2xl font-bold text-sm bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/35 disabled:opacity-50 transition-all"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Submit Complaint</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
