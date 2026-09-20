import type { ReadinessStatus } from '../api/types';

const statusConfig: Record<string, { className: string; label: string }> = {
  GREEN: { className: 'badge-green', label: 'Verified' },
  AMBER: { className: 'badge-amber', label: 'Under Review' },
  RED: { className: 'badge-red', label: 'Issues Found' },
  CREATED: { className: 'badge-neutral', label: 'Created' },
  RUNNING: { className: 'badge-blue', label: 'Verifying…' },
  UNKNOWN: { className: 'badge-neutral', label: 'Unknown' },
  COMPLETED: { className: 'badge-green', label: 'Completed' },
};

interface Props {
  status: ReadinessStatus | string;
}

export default function StatusBadge({ status }: Props) {
  const cfg = statusConfig[status] || statusConfig.UNKNOWN;
  return (
    <span className={`badge ${cfg.className}`}>
      <span className="badge-dot" />
      {cfg.label}
    </span>
  );
}
