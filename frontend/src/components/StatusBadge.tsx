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
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs font-semibold px-2.5 py-1 gap-1.5',
    lg: 'text-sm font-semibold px-3.5 py-1.5 gap-2',
  }[size];

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-3.5 h-3.5',
    lg: 'w-4 h-4',
  }[size];

  if (normStatus === 'Resolved') {
    return (
      <span
        className={`inline-flex items-center rounded-full font-medium bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800/60 shadow-sm ${sizeClasses}`}
      >
        {showIcon && <CheckCircle2 className={`${iconSizes} text-emerald-600 dark:text-emerald-400`} />}
        <span>Resolved</span>
      </span>
    );
  }

  if (normStatus === 'In Progress') {
    return (
      <span
        className={`inline-flex items-center rounded-full font-medium bg-blue-50 text-blue-700 border border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-800/60 shadow-sm ${sizeClasses}`}
      >
        {showIcon && <RefreshCw className={`${iconSizes} text-blue-600 dark:text-blue-400 animate-spin`} style={{ animationDuration: '6s' }} />}
        <span>In Progress</span>
      </span>
    );
  }

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800/60 shadow-sm ${sizeClasses}`}
    >
      {showIcon && <Clock className={`${iconSizes} text-amber-600 dark:text-amber-400`} />}
      <span>Pending</span>
    </span>
  );
};
