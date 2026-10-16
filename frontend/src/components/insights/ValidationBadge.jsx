import { ShieldCheck, ShieldAlert, AlertCircle } from 'lucide-react';

const ValidationBadge = ({ passed, status }) => {
  // Determine normalized status
  let currentStatus = status;
  if (!currentStatus) {
    if (passed === true) currentStatus = 'validated';
    else if (passed === false) currentStatus = 'validation_failed';
    else return null;
  }

  if (currentStatus === 'validated') {
    return (
      <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border bg-success/10 text-success border-success/20">
        <ShieldCheck size={14} />
        <span>Validated</span>
      </div>
    );
  }

  if (currentStatus === 'validation_unavailable') {
    return (
      <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border bg-warning/10 text-warning border-warning/20" title="Auditor service was unavailable during generation">
        <AlertCircle size={14} />
        <span>Validation Unavailable</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border bg-danger/10 text-danger border-danger/20" title="Failed rules or auditor rubric">
      <ShieldAlert size={14} />
      <span>Validation Failed</span>
    </div>
  );
};

export default ValidationBadge;
