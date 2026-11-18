import React from 'react';
import { ComplaintStatus } from '../types';
import { Check, Clock, RefreshCw, Sparkles } from 'lucide-react';

interface Props {
  status: ComplaintStatus | string;
  createdAt: string;
  updatedAt?: string | null;
  resolution?: string | null;
}

export const ComplaintTimeline: React.FC<Props> = ({
  status,
  createdAt,
  updatedAt,
  resolution,
}) => {
  const isPending = status === 'Pending';
  const isInProgress = status === 'In Progress';
  const isResolved = status === 'Resolved';

  const formatDate = (isoString?: string | null) => {
    if (!isoString) return '';
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  const steps = [
    {
      title: 'Submitted',
      desc: 'Complaint logged in the registry',
      date: formatDate(createdAt),
      done: true,
      active: isPending,
      icon: Clock,
      gradient: 'from-amber-500 to-orange-500',
      activeRing: 'ring-amber-500/30 dark:ring-amber-400/40',
    },
    {
      title: 'In Progress',
      desc: 'Admin investigation & active triage',
      date: isInProgress || isResolved ? formatDate(updatedAt || createdAt) : 'Pending triage',
      done: isInProgress || isResolved,
      active: isInProgress,
      icon: RefreshCw,
      gradient: 'from-blue-600 to-cyan-500',
      activeRing: 'ring-blue-500/30 dark:ring-blue-400/40',
    },
    {
      title: 'Resolved',
      desc: resolution ? 'Verified resolution delivered' : 'Awaiting administrative action',
      date: isResolved ? formatDate(updatedAt || createdAt) : 'Awaiting resolution',
      done: isResolved,
      active: isResolved,
      icon: Sparkles,
      gradient: 'from-emerald-500 to-teal-500',
      activeRing: 'ring-emerald-500/30 dark:ring-emerald-400/40',
    },
  ];

  return (
    <div className="w-full py-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
        {/* Artistic glowing connector line */}
        <div className="hidden md:block absolute top-7 left-14 right-14 h-1.5 bg-slate-200/80 dark:bg-slate-800 rounded-full -z-0 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-amber-500 via-blue-500 to-emerald-500 rounded-full transition-all duration-700 shadow-sm"
            style={{
              width: isResolved ? '100%' : isInProgress ? '50%' : '15%',
            }}
          />
        </div>

        {steps.map((step, idx) => {
          const Icon = step.icon;
          return (
            <div key={idx} className="relative z-10 flex flex-col md:items-center md:text-center group">
              <div className="flex items-center gap-4 md:flex-col md:gap-3">
                <div
                  className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-300 shadow-lg ${
                    step.done
                      ? step.active
                        ? `bg-gradient-to-br ${step.gradient} text-white ring-8 ${step.activeRing} scale-105 shadow-xl`
                        : 'bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900'
                      : 'bg-slate-100 dark:bg-slate-800/80 text-slate-400 border-2 border-dashed border-slate-300 dark:border-slate-700'
                  }`}
                >
                  {step.done && !step.active ? (
                    <Check className="w-6 h-6 stroke-[3]" />
                  ) : (
                    <Icon
                      className={`w-6 h-6 ${step.active && step.icon === RefreshCw ? 'animate-spin' : ''}`}
                    />
                  )}
                </div>

                <div className="flex-1 md:w-full">
                  <div className="flex items-center md:justify-center gap-2">
                    <span className="text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500">
                      Phase 0{idx + 1}
                    </span>
                    {step.active && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 ring-1 ring-inset ring-indigo-500/25">
                        Active Stage
                      </span>
                    )}
                  </div>
                  <h4 className="text-base font-extrabold text-slate-900 dark:text-white mt-1">
                    {step.title}
                  </h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-[220px] md:mx-auto font-medium">
                    {step.desc}
                  </p>
                  <p className="text-[11px] font-semibold text-slate-400 dark:text-slate-500 mt-1.5 font-mono">
                    {step.date}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
