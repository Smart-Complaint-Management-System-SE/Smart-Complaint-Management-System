import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { complaintsApi, categoriesApi } from '../api/client';
import { getCategoryIcon } from '../components/CategoryBadge';
import {
  ArrowLeft,
  AlertCircle,
  Send,
  Sparkles,
  Info,
  Check,
} from 'lucide-react';

interface Props {
  navigate: (path: string) => void;
}

const DEFAULT_CATEGORIES = [
  'Academic',
  'Hostel',
  'Infrastructure',
  'Other',
  'Technical',
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
      let msg = err.message || 'Failed to submit complaint. Please try again.';
      if (msg.includes('<!doctype') || msg.includes('<html')) {
        msg = 'Session expired. Please try submitting again.';
      }
      setFormError(msg);
      error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 space-y-6 animate-fade-in bg-grid-slate">
      {/* Back button */}
      <button
        type="button"
        onClick={() => navigate('/dashboard')}
        className="inline-flex items-center gap-2 text-xs font-black uppercase tracking-wider text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Return to Dashboard</span>
      </button>

      {/* Main Form Card */}
      <div className="artistic-card rounded-3xl p-6 sm:p-10 shadow-2xl space-y-8">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-black bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 ring-1 ring-inset ring-indigo-500/30 mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Grievance Submission Studio</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white">
            Submit a Grievance Ticket
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1 font-medium">
            Provide concise details about the issue. Campus personnel will review and advance status through the resolution pipeline.
          </p>
        </div>

        {formError && (
          <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900/60 text-rose-800 dark:text-rose-200 text-xs font-semibold flex items-start gap-2.5 animate-slide-up">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
            <span>{formError}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Department Selection Cards */}
          <div className="space-y-2.5">
            <label className="block text-[11px] font-black uppercase tracking-widest text-slate-700 dark:text-slate-300">
              Department Classification <span className="text-rose-500">*</span>
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
              {categories.map((cat) => {
                const isSelected = selectedCategory === cat;
                return (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => setSelectedCategory(cat)}
                    className={`relative flex flex-col items-center justify-center p-4 rounded-2xl border text-center transition-all ${
                      isSelected
                        ? 'bg-gradient-to-b from-indigo-50 to-indigo-100/60 dark:from-indigo-950/80 dark:to-indigo-900/40 border-indigo-500 text-indigo-700 dark:text-indigo-200 ring-2 ring-indigo-500/30 shadow-lg scale-102'
                        : 'bg-white/60 dark:bg-slate-800/40 border-slate-200/80 dark:border-white/5 text-slate-700 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-700'
                    }`}
                  >
                    {isSelected && (
                      <span className="absolute top-2 right-2 w-4 h-4 bg-indigo-600 rounded-full flex items-center justify-center text-white">
                        <Check className="w-2.5 h-2.5 stroke-[3]" />
                      </span>
                    )}
                    <div
                      className={`w-10 h-10 rounded-xl flex items-center justify-center mb-2.5 ${
                        isSelected
                          ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/30'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400'
                      }`}
                    >
                      {getCategoryIcon(cat, 'w-5 h-5')}
                    </div>
                    <span className="text-xs font-black">{cat}</span>
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
                className="text-[11px] font-black uppercase tracking-widest text-slate-700 dark:text-slate-300"
              >
                Complaint Title <span className="text-rose-500">*</span>
              </label>
              <span
                className={`text-[11px] font-mono font-bold ${
                  title.length > 90 ? 'text-amber-500' : 'text-slate-400'
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
              className="w-full px-4 py-3 rounded-2xl text-sm font-semibold bg-white/70 dark:bg-slate-800/70 border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-4 focus:ring-indigo-500/15 focus:border-indigo-500 transition-all shadow-inner"
            />
          </div>

          {/* Description Textarea */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center">
              <label
                htmlFor="complaint-description"
                className="text-[11px] font-black uppercase tracking-widest text-slate-700 dark:text-slate-300"
              >
                Detailed Description <span className="text-rose-500">*</span>
              </label>
              <span className="text-[11px] text-slate-400 font-mono font-semibold">
                {description.length} chars
              </span>
            </div>
            <textarea
              id="complaint-description"
              required
              rows={6}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Provide complete context, room number, equipment identifier, and observed behavior to help administrators resolve the grievance promptly..."
              className="w-full px-4 py-3 rounded-2xl text-sm font-medium bg-white/70 dark:bg-slate-800/70 border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-4 focus:ring-indigo-500/15 focus:border-indigo-500 transition-all resize-y shadow-inner"
            />
          </div>

          {/* Helpful Tips Card */}
          <div className="p-4 rounded-2xl bg-indigo-50/70 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/40 text-xs text-indigo-900 dark:text-indigo-200 flex items-start gap-3">
            <Info className="w-4 h-4 shrink-0 mt-0.5 text-indigo-600 dark:text-indigo-400" />
            <div className="space-y-0.5 leading-relaxed">
              <p className="font-bold">Tips for faster resolution:</p>
              <p className="text-indigo-700/90 dark:text-indigo-300/80 font-medium">
                Include physical location details (building, floor, wing). Administrators verify each report and record official resolution remarks upon completion.
              </p>
            </div>
          </div>

          {/* Action buttons */}
          <div className="pt-2 flex flex-col-reverse sm:flex-row items-center justify-end gap-3">
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="w-full sm:w-auto px-6 py-3 rounded-2xl text-xs font-bold text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3.5 rounded-2xl font-black text-xs sm:text-sm bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white shadow-xl shadow-indigo-500/30 hover:shadow-indigo-500/45 disabled:opacity-50 transition-all"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Submit Grievance</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
