import React from 'react';
import { ComplaintStatus } from '../types';
import { Clock, RefreshCw, CheckCircle2 } from 'lucide-react';

interface Props {
  status: ComplaintStatus | string;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

export const StatusBadge: React.FC<Props> = ({ status, size = 'md', showIcon = true }) => {
  const normStatus = status === 'In Progress' ? 'In Progress' : status === 'Resolved' ? 'Resolved' : 'Pending';

  const sizeClasses = {
    sm: 'text-[11px] px-2.5 py-0.5 gap-1.5 font-semibold',
    md: 'text-xs px-3 py-1 gap-2 font-bold',
    lg: 'text-sm px-4 py-1.5 gap-2.5 font-bold',
  }[size];

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-3.5 h-3.5',
    lg: 'w-4 h-4',
  }[size];

  if (normStatus === 'Resolved') {
    return (
      <span
        className={`inline-flex items-center rounded-full bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 ring-1 ring-inset ring-emerald-500/25 dark:ring-emerald-400/30 backdrop-blur-sm ${sizeClasses}`}
      >
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-60"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
        </span>
        {showIcon && <CheckCircle2 className={`${iconSizes} text-emerald-600 dark:text-emerald-400`} />}
        <span>Resolved</span>
      </span>
    );
  }

  if (normStatus === 'In Progress') {
    return (
      <span
        className={`inline-flex items-center rounded-full bg-blue-500/10 text-blue-700 dark:text-blue-300 ring-1 ring-inset ring-blue-500/25 dark:ring-blue-400/30 backdrop-blur-sm ${sizeClasses}`}
      >
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-60"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
        </span>
        {showIcon && (
          <RefreshCw
            className={`${iconSizes} text-blue-600 dark:text-blue-400 animate-spin`}
            style={{ animationDuration: '4s' }}
          />
        )}
        <span>In Progress</span>
      </span>
    );
  }

  return (
    <span
      className={`inline-flex items-center rounded-full bg-amber-500/10 text-amber-700 dark:text-amber-300 ring-1 ring-inset ring-amber-500/25 dark:ring-amber-400/30 backdrop-blur-sm ${sizeClasses}`}
    >
      <span className="relative flex h-2 w-2">
        <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
      </span>
      {showIcon && <Clock className={`${iconSizes} text-amber-600 dark:text-amber-400`} />}
      <span>Pending</span>
    </span>
  );
};
