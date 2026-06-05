import { useTranslation } from 'react-i18next';
import type { ComplianceStatus } from '@/types/employee';

interface StatusBadgeProps {
  status: ComplianceStatus;
  size?: 'sm' | 'md' | 'lg';
}

const statusConfig: Record<ComplianceStatus, { label: string; color: string; bg: string }> = {
  ready: { label: 'Ready', color: '#3ECF8E', bg: 'rgba(62, 207, 142, 0.1)' },
  review: { label: 'Review', color: '#F5A623', bg: 'rgba(245, 166, 35, 0.1)' },
  blocked: { label: 'Blocked', color: '#E53E3E', bg: 'rgba(229, 62, 62, 0.1)' },
  at_risk: { label: 'At Risk', color: '#F97316', bg: 'rgba(249, 115, 22, 0.1)' },
  pending: { label: 'Pending', color: '#94A3B8', bg: 'rgba(148, 163, 184, 0.1)' },
};

export default function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  const config = statusConfig[status] || statusConfig.pending;

  const sizeClasses = {
    sm: 'text-2xs px-1.5 py-0.5',
    md: 'text-xs px-2 py-0.5',
    lg: 'text-sm px-2.5 py-1',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium rounded-full ${sizeClasses[size]}`}
      style={{
        backgroundColor: config.bg,
        color: config.color,
      }}
    >
      <span
        className="w-1.5 h-1.5 rounded-full"
        style={{ backgroundColor: config.color }}
      />
      {config.label}
    </span>
  );
}