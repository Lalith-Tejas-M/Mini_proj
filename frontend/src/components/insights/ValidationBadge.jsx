import React from 'react';
import { ShieldCheck, ShieldAlert } from 'lucide-react';

const ValidationBadge = ({ passed }) => {
  if (passed === undefined || passed === null) return null;

  return (
    <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border
      ${passed 
        ? 'bg-success/10 text-success border-success/20' 
        : 'bg-warning/10 text-warning border-warning/20'
      }`}
    >
      {passed ? <ShieldCheck size={14} /> : <ShieldAlert size={14} />}
      {passed ? 'Validated' : 'Low Confidence'}
    </div>
  );
};

export default ValidationBadge;
