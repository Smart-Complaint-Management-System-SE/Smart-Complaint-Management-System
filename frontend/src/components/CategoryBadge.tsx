import React from 'react';
import {
  GraduationCap,
  Building2,
  Home,
  Laptop,
  HelpCircle,
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
  const norm = category.toLowerCase().trim();
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

export const CategoryBadge: React.FC<Props> = ({ category, size = 'md' }) => {
  const sizeClasses = size === 'sm' ? 'text-xs px-2 py-0.5 gap-1' : 'text-xs px-2.5 py-1 gap-1.5 font-medium';

  return (
    <span
      className={`inline-flex items-center rounded-lg bg-slate-100 text-slate-700 border border-slate-200/80 dark:bg-slate-800/80 dark:text-slate-300 dark:border-slate-700/60 transition-colors ${sizeClasses}`}
    >
      <span className="text-slate-500 dark:text-slate-400">{getCategoryIcon(category)}</span>
      <span>{category}</span>
    </span>
  );
};
