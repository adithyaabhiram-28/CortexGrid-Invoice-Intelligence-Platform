import React from 'react';
import { Clock, Loader2, CheckCircle2, AlertTriangle, FileUp, ShieldCheck, ShieldAlert, Shield } from 'lucide-react';

export const StatusBadge = ({ status }) => {
  const normalized = (status || '').toLowerCase();

  switch (normalized) {
    case 'queued':
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
          <Clock className="w-3.5 h-3.5 animate-pulse" />
          Queued
        </span>
      );
    case 'processing':
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
          Processing
        </span>
      );
    case 'completed':
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          <CheckCircle2 className="w-3.5 h-3.5" />
          Completed
        </span>
      );
    case 'failed':
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
          <AlertTriangle className="w-3.5 h-3.5" />
          Failed
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-500/10 text-slate-400 border border-slate-500/20">
          <FileUp className="w-3.5 h-3.5" />
          {status || 'Uploaded'}
        </span>
      );
  }
};

export const RiskBadge = ({ level, score }) => {
  const normLevel = (level || 'LOW').toUpperCase();

  switch (normLevel) {
    case 'HIGH':
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/15 text-rose-400 border border-rose-500/30 shadow-sm">
          <ShieldAlert className="w-3.5 h-3.5" />
          <span>High Risk</span>
          {score !== undefined && <span className="text-[10px] opacity-80 font-mono">({score})</span>}
        </span>
      );
    case 'MEDIUM':
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/30 shadow-sm">
          <Shield className="w-3.5 h-3.5" />
          <span>Medium Risk</span>
          {score !== undefined && <span className="text-[10px] opacity-80 font-mono">({score})</span>}
        </span>
      );
    case 'LOW':
    default:
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-sm">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Low Risk</span>
          {score !== undefined && <span className="text-[10px] opacity-80 font-mono">({score})</span>}
        </span>
      );
  }
};

export default StatusBadge;
