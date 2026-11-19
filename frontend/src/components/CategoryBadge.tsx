import React from 'react';
import {
  GraduationCap,
  Building2,
  Home,
  Laptop,
  Tag,
  Bus,
  Utensils,
  Wifi,
} from 'lucide-react';

interface Props {
  category: string;
  size?: 'sm' | 'md';
}

export const getCategoryIcon = (category: string, className = 'w-3.5 h-3.5') => {
  const norm = (category || '').toLowerCase().trim();
  if (norm.includes('academic')) return <GraduationCap className={className} />;
  if (norm.includes('infra')) return <Building2 className={className} />;
  if (norm.includes('hostel')) return <Home className={className} />;
  if (norm.includes('tech') || norm.includes('wifi')) return <Laptop className={className} />;
  if (norm.includes('transport') || norm.includes('bus')) return <Bus className={className} />;
  if (norm.includes('mess') || norm.includes('food') || norm.includes('canteen'))
    return <Utensils className={className} />;
  if (norm.includes('net') || norm.includes('network')) return <Wifi className={className} />;
  return <Tag className={className} />;
};

const getCategoryTheme = (category: string) => {
  const norm = (category || '').toLowerCase().trim();
  if (norm.includes('academic')) {
    return 'bg-purple-500/10 text-purple-700 dark:text-purple-300 ring-purple-500/20';
  }
  if (norm.includes('hostel')) {
    return 'bg-orange-500/10 text-orange-700 dark:text-orange-300 ring-orange-500/20';
  }
  if (norm.includes('tech') || norm.includes('wifi')) {
    return 'bg-cyan-500/10 text-cyan-700 dark:text-cyan-300 ring-cyan-500/20';
  }
  if (norm.includes('infra')) {
    return 'bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 ring-indigo-500/20';
  }
  return 'bg-slate-500/10 text-slate-700 dark:text-slate-300 ring-slate-500/20';
};

export const CategoryBadge: React.FC<Props> = ({ category, size = 'md' }) => {
  const sizeClasses =
    size === 'sm'
      ? 'text-[11px] px-2.5 py-0.5 gap-1.5'
      : 'text-xs px-3 py-1 gap-2 font-bold';

  const themeClass = getCategoryTheme(category);

  return (
    <span
      className={`inline-flex items-center rounded-lg ring-1 ring-inset font-semibold backdrop-blur-sm transition-all ${themeClass} ${sizeClasses}`}
    >
      <span className="opacity-80">{getCategoryIcon(category)}</span>
      <span>{category}</span>
    </span>
  );
};
