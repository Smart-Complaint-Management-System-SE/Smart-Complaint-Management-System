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
      desc: 'Complaint received and queued',
      date: formatDate(createdAt),
      done: true,
      active: isPending,
      icon: Clock,
      color: 'amber',
    },
    {
      title: 'In Progress',
      desc: 'Administrator is investigating & addressing issue',
      date: isInProgress || isResolved ? formatDate(updatedAt || createdAt) : 'Pending review',
      done: isInProgress || isResolved,
      active: isInProgress,
      icon: RefreshCw,
      color: 'blue',
    },
    {
      title: 'Resolved',
      desc: resolution ? 'Resolution provided' : 'Awaiting final resolution',
      date: isResolved ? formatDate(updatedAt || createdAt) : 'Awaiting resolution',
      done: isResolved,
      active: isResolved,
      icon: Sparkles,
      color: 'emerald',
    },
  ];

  return (
    <div className="w-full py-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative">
        {/* Connecting progress line on medium+ screens */}
        <div className="hidden md:block absolute top-7 left-12 right-12 h-1 bg-slate-200 dark:bg-slate-800 -z-0">
          <div
            className="h-full bg-gradient-to-r from-amber-500 via-blue-500 to-emerald-500 transition-all duration-500 rounded-full"
            style={{
              width: isResolved ? '100%' : isInProgress ? '50%' : '5%',
            }}
          />
        </div>

        {steps.map((step, idx) => {
          const Icon = step.icon;
          return (
            <div key={idx} className="relative z-10 flex flex-col md:items-center md:text-center">
              <div className="flex items-center gap-4 md:flex-col md:gap-3">
                <div
                  className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-300 shadow-md ${
                    step.done
                      ? step.active
                        ? step.color === 'emerald'
                          ? 'bg-emerald-600 text-white ring-4 ring-emerald-200 dark:ring-emerald-900/50 shadow-emerald-500/20'
                          : step.color === 'blue'
                          ? 'bg-blue-600 text-white ring-4 ring-blue-200 dark:ring-blue-900/50 shadow-blue-500/20'
                          : 'bg-amber-500 text-white ring-4 ring-amber-200 dark:ring-amber-900/50 shadow-amber-500/20'
                        : 'bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900'
                      : 'bg-slate-100 dark:bg-slate-800/80 text-slate-400 border-2 border-dashed border-slate-300 dark:border-slate-700'
                  }`}
                >
                  {step.done && !step.active ? (
                    <Check className="w-6 h-6 stroke-[3]" />
                  ) : (
                    <Icon className={`w-6 h-6 ${step.active && step.icon === RefreshCw ? 'animate-spin' : ''}`} />
                  )}
                </div>

                <div className="flex-1 md:w-full">
                  <div className="flex items-center md:justify-center gap-2">
                    <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                      Step {idx + 1}
                    </span>
                    {step.active && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300">
                        Current
                      </span>
                    )}
                  </div>
                  <h4 className="text-base font-bold text-slate-900 dark:text-white mt-0.5">
                    {step.title}
                  </h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-[220px] md:mx-auto">
                    {step.desc}
                  </p>
                  <p className="text-[11px] font-medium text-slate-400 dark:text-slate-500 mt-1">
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
