import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import { StatusBadge, RiskBadge } from '../components/StatusBadge';
import InvoiceUploadModal from '../components/InvoiceUploadModal';
import { invoiceApi, purchaseOrderApi } from '../services/api';
import {
  FileText, Clock, CheckCircle2, AlertTriangle, UploadCloud,
  ArrowRight, RefreshCw, Cpu, ShieldCheck, ShieldAlert, ShoppingBag, Shield
} from 'lucide-react';

const Dashboard = () => {
  const [stats, setStats] = useState({
    total: 0, completed: 0, processing: 0, failed: 0,
    low_risk: 0, medium_risk: 0, high_risk: 0, duplicates: 0
  });
  const [poCount, setPoCount] = useState(0);
  const [recentInvoices, setRecentInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isUploadOpen, setIsUploadOpen] = useState(false);

  const fetchDashboardData = async () => {
    try {
      const [invRes, poRes] = await Promise.all([
        invoiceApi.getInvoices(),
        purchaseOrderApi.getPurchaseOrders().catch(() => ({ data: { purchase_orders: [] } }))
      ]);
      setStats(invRes.data.stats || {});
      setRecentInvoices((invRes.data.invoices || []).slice(0, 6));
      setPoCount((poRes.data.purchase_orders || []).length);
    } catch (err) {
      console.error("Failed loading dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar pageTitle="Platform Intelligence Dashboard" onOpenUploadModal={() => setIsUploadOpen(true)} />

        <main className="p-6 space-y-6 flex-1 overflow-y-auto">
          {/* Welcome Banner */}
          <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-slate-850 border border-slate-800 shadow-xl relative overflow-hidden flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="space-y-1 z-10">
              <div className="flex items-center space-x-2 text-cyan-400 text-xs font-semibold uppercase tracking-wider">
                <Cpu className="w-4 h-4" />
                <span>Review 2 Release • 60%+ Major Project Milestone</span>
              </div>
              <h2 className="text-xl font-bold text-white tracking-tight">Invoice Intelligence & Verification Platform</h2>
              <p className="text-xs text-slate-400 max-w-2xl">
                Automated document extraction (PyMuPDF & Tesseract OCR), duplicate detection, intelligent vendor matching, purchase order reconciliation, and explainable risk scoring.
              </p>
            </div>
            <div className="flex items-center space-x-3 z-10 shrink-0">
              <Link
                to="/purchase-orders"
                className="px-3.5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs border border-slate-700 flex items-center space-x-1.5 transition-all"
              >
                <ShoppingBag className="w-4 h-4 text-cyan-400" />
                <span>Manage POs</span>
              </Link>
              <button
                onClick={() => setIsUploadOpen(true)}
                className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-xs shadow-lg shadow-cyan-500/25 flex items-center space-x-2 transition-all"
              >
                <UploadCloud className="w-4 h-4" />
                <span>Upload Invoice</span>
              </button>
            </div>
          </div>

          {/* Primary Risk Intelligence Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Total Invoices */}
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-md">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-400">Total Invoices</span>
                <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  <FileText className="w-4 h-4" />
                </div>
              </div>
              <p className="text-2xl font-bold text-white mt-2">{loading ? '-' : (stats.total || 0)}</p>
              <p className="text-[11px] text-slate-500 mt-1">Processed in repository</p>
            </div>

            {/* Low Risk */}
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-md">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-emerald-400">Low Risk (Verified)</span>
                <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <ShieldCheck className="w-4 h-4" />
                </div>
              </div>
              <p className="text-2xl font-bold text-emerald-400 mt-2">{loading ? '-' : (stats.low_risk || 0)}</p>
              <p className="text-[11px] text-slate-500 mt-1">Passed all verification checks</p>
            </div>

            {/* Medium Risk */}
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-md">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-amber-400">Medium Risk</span>
                <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
                  <Shield className="w-4 h-4" />
                </div>
              </div>
              <p className="text-2xl font-bold text-amber-400 mt-2">{loading ? '-' : (stats.medium_risk || 0)}</p>
              <p className="text-[11px] text-slate-500 mt-1">Minor variance / review needed</p>
            </div>

            {/* High Risk */}
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-md">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-rose-400">High Risk (Flagged)</span>
                <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20">
                  <ShieldAlert className="w-4 h-4" />
                </div>
              </div>
              <p className="text-2xl font-bold text-rose-400 mt-2">{loading ? '-' : (stats.high_risk || 0)}</p>
              <p className="text-[11px] text-slate-500 mt-1">Duplicate / price mismatch flags</p>
            </div>
          </div>

          {/* Secondary Metrics Row */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 bg-slate-900/60 border border-slate-800/80 rounded-lg flex items-center justify-between">
              <div>
                <p className="text-[10px] text-slate-500 uppercase font-semibold">Active Purchase Orders</p>
                <p className="text-lg font-bold font-mono text-cyan-400 mt-0.5">{loading ? '-' : poCount}</p>
              </div>
              <ShoppingBag className="w-4 h-4 text-slate-600" />
            </div>

            <div className="p-3 bg-slate-900/60 border border-slate-800/80 rounded-lg flex items-center justify-between">
              <div>
                <p className="text-[10px] text-slate-500 uppercase font-semibold">Duplicates Detected</p>
                <p className="text-lg font-bold font-mono text-rose-400 mt-0.5">{loading ? '-' : (stats.duplicates || 0)}</p>
              </div>
              <ShieldAlert className="w-4 h-4 text-slate-600" />
            </div>

            <div className="p-3 bg-slate-900/60 border border-slate-800/80 rounded-lg flex items-center justify-between">
              <div>
                <p className="text-[10px] text-slate-500 uppercase font-semibold">In Extraction Queue</p>
                <p className="text-lg font-bold font-mono text-amber-400 mt-0.5">{loading ? '-' : (stats.processing || 0)}</p>
              </div>
              <Clock className="w-4 h-4 text-slate-600" />
            </div>

            <div className="p-3 bg-slate-900/60 border border-slate-800/80 rounded-lg flex items-center justify-between">
              <div>
                <p className="text-[10px] text-slate-500 uppercase font-semibold">Processing Success Rate</p>
                <p className="text-lg font-bold font-mono text-emerald-400 mt-0.5">
                  {stats.total > 0 ? `${Math.round(((stats.completed || 0) / stats.total) * 100)}%` : '100%'}
                </p>
              </div>
              <CheckCircle2 className="w-4 h-4 text-slate-600" />
            </div>
          </div>

          {/* Recent Invoices Table Card */}
          <div className="rounded-xl bg-slate-900 border border-slate-800 shadow-md overflow-hidden">
            <div className="p-5 border-b border-slate-800 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-white">Recent Processed Invoices</h3>
                <p className="text-xs text-slate-400">Latest accounts payable submissions & verification results</p>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={fetchDashboardData}
                  className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
                  title="Refresh list"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                </button>
                <Link
                  to="/invoices"
                  className="flex items-center space-x-1 px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-colors"
                >
                  <span>View Full Queue</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950/60 text-slate-400 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-800">
                  <tr>
                    <th className="px-5 py-3">ID</th>
                    <th className="px-5 py-3">Invoice #</th>
                    <th className="px-5 py-3">Vendor</th>
                    <th className="px-5 py-3">Total Amount</th>
                    <th className="px-5 py-3">PO Match</th>
                    <th className="px-5 py-3">Risk Assessment</th>
                    <th className="px-5 py-3">Status</th>
                    <th className="px-5 py-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {loading ? (
                    <tr>
                      <td colSpan={8} className="px-5 py-8 text-center text-slate-500">
                        Loading invoice queue...
                      </td>
                    </tr>
                  ) : recentInvoices.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="px-5 py-8 text-center text-slate-500">
                        No invoices uploaded yet. Click "Upload Invoice" to begin.
                      </td>
                    </tr>
                  ) : (
                    recentInvoices.map((inv) => (
                      <tr key={inv.id} className="hover:bg-slate-800/40 transition-colors">
                        <td className="px-5 py-3.5 font-mono text-slate-400">#{inv.id}</td>
                        <td className="px-5 py-3.5 font-medium text-white">
                          <div className="flex items-center space-x-1.5">
                            <span>{inv.invoice_number}</span>
                            {inv.is_duplicate && (
                              <span className="px-1 py-0.2 rounded text-[9px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">
                                DUP
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-5 py-3.5 text-slate-300">{inv.vendor_name || 'Unidentified'}</td>
                        <td className="px-5 py-3.5 font-mono font-medium text-emerald-400">
                          {inv.total_amount ? `${inv.currency || 'INR'} ${inv.total_amount.toLocaleString()}` : '-'}
                        </td>
                        <td className="px-5 py-3.5 capitalize font-mono text-[11px] text-slate-400">
                          {inv.po_match_status || 'unlinked'}
                        </td>
                        <td className="px-5 py-3.5">
                          <RiskBadge level={inv.risk_level} score={inv.risk_score} />
                        </td>
                        <td className="px-5 py-3.5">
                          <StatusBadge status={inv.processing_status} />
                        </td>
                        <td className="px-5 py-3.5 text-right">
                          <Link
                            to={`/invoices/${inv.id}`}
                            className="text-cyan-400 hover:text-cyan-300 font-medium hover:underline"
                          >
                            Review →
                          </Link>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </main>
      </div>

      <InvoiceUploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUploadSuccess={fetchDashboardData}
      />
    </div>
  );
};

export default Dashboard;
