import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import { StatusBadge, RiskBadge } from '../components/StatusBadge';
import InvoiceUploadModal from '../components/InvoiceUploadModal';
import { invoiceApi } from '../services/api';
import { Search, Filter, Trash2, Eye, UploadCloud, RefreshCw, FileText, ShieldAlert, ShoppingBag } from 'lucide-react';

const Invoices = () => {
  const [invoices, setInvoices] = useState([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [isUploadOpen, setIsUploadOpen] = useState(false);

  const fetchInvoices = async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (statusFilter) params.status = statusFilter;
      if (riskFilter) params.risk_level = riskFilter;
      const res = await invoiceApi.getInvoices(params);
      setInvoices(res.data.invoices || []);
    } catch (err) {
      console.error("Failed fetching invoices:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchInvoices();
    }, 300);
    return () => clearTimeout(timer);
  }, [search, statusFilter, riskFilter]);

  const handleDelete = async (id) => {
    if (!window.confirm(`Are you sure you want to delete invoice #${id}?`)) return;
    try {
      await invoiceApi.deleteInvoice(id);
      fetchInvoices();
    } catch (err) {
      alert("Failed deleting invoice.");
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar pageTitle="Invoice Verification & Risk Repository" onOpenUploadModal={() => setIsUploadOpen(true)} />

        <main className="p-6 space-y-6 flex-1 overflow-y-auto">
          {/* Controls Bar */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900 p-4 rounded-xl border border-slate-800 shadow-md">
            <div className="flex flex-1 flex-wrap items-center gap-3 w-full sm:w-auto">
              <div className="relative flex-1 min-w-[200px] max-w-md">
                <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search by invoice #, vendor, or file..."
                  className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="relative">
                <Filter className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="pl-8 pr-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-cyan-500 cursor-pointer"
                >
                  <option value="">All Statuses</option>
                  <option value="queued">Queued</option>
                  <option value="processing">Processing</option>
                  <option value="completed">Completed</option>
                  <option value="failed">Failed</option>
                </select>
              </div>

              <div className="relative">
                <select
                  value={riskFilter}
                  onChange={(e) => setRiskFilter(e.target.value)}
                  className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-cyan-500 cursor-pointer"
                >
                  <option value="">All Risk Levels</option>
                  <option value="LOW">Low Risk</option>
                  <option value="MEDIUM">Medium Risk</option>
                  <option value="HIGH">High Risk</option>
                </select>
              </div>
            </div>

            <div className="flex items-center space-x-3 w-full sm:w-auto justify-end">
              <button
                onClick={fetchInvoices}
                className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
                title="Refresh list"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsUploadOpen(true)}
                className="px-3.5 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-semibold shadow-md shadow-cyan-500/20 flex items-center space-x-2 transition-all"
              >
                <UploadCloud className="w-4 h-4" />
                <span>Upload PDF</span>
              </button>
            </div>
          </div>

          {/* Invoice Table Card */}
          <div className="rounded-xl bg-slate-900 border border-slate-800 shadow-md overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950/60 text-slate-400 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-800">
                  <tr>
                    <th className="px-5 py-3.5">ID</th>
                    <th className="px-5 py-3.5">Invoice #</th>
                    <th className="px-5 py-3.5">Vendor</th>
                    <th className="px-5 py-3.5">Invoice Date</th>
                    <th className="px-5 py-3.5">Total Amount</th>
                    <th className="px-5 py-3.5">PO Status</th>
                    <th className="px-5 py-3.5">Risk Level</th>
                    <th className="px-5 py-3.5">Status</th>
                    <th className="px-5 py-3.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {loading ? (
                    <tr>
                      <td colSpan={9} className="px-5 py-10 text-center text-slate-500">
                        Fetching invoice data...
                      </td>
                    </tr>
                  ) : invoices.length === 0 ? (
                    <tr>
                      <td colSpan={9} className="px-5 py-10 text-center text-slate-500">
                        <FileText className="w-8 h-8 mx-auto text-slate-600 mb-2" />
                        No matching invoices found in repository.
                      </td>
                    </tr>
                  ) : (
                    invoices.map((inv) => (
                      <tr key={inv.id} className="hover:bg-slate-800/40 transition-colors">
                        <td className="px-5 py-3.5 font-mono text-slate-400">#{inv.id}</td>
                        <td className="px-5 py-3.5 font-medium text-white">
                          <div className="flex items-center space-x-2">
                            <span>{inv.invoice_number}</span>
                            {inv.is_duplicate && (
                              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30 flex items-center space-x-1" title={`Duplicate of #${inv.duplicate_of_id}`}>
                                <ShieldAlert className="w-3 h-3" />
                                <span>DUP</span>
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-5 py-3.5 text-slate-300">
                          {inv.vendor_name || <span className="text-slate-500 italic">Unidentified</span>}
                        </td>
                        <td className="px-5 py-3.5 text-slate-400 font-mono">{inv.invoice_date || '-'}</td>
                        <td className="px-5 py-3.5 font-mono font-medium text-emerald-400">
                          {inv.total_amount ? `${inv.currency || 'INR'} ${inv.total_amount.toLocaleString()}` : '-'}
                        </td>
                        <td className="px-5 py-3.5">
                          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium capitalize ${
                            inv.po_match_status === 'matched' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                            inv.po_match_status === 'mismatched' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                            'bg-slate-800 text-slate-400'
                          }`}>
                            <ShoppingBag className="w-3 h-3" />
                            <span>{inv.po_match_status || 'unlinked'}</span>
                          </span>
                        </td>
                        <td className="px-5 py-3.5">
                          <RiskBadge level={inv.risk_level} score={inv.risk_score} />
                        </td>
                        <td className="px-5 py-3.5">
                          <StatusBadge status={inv.processing_status} />
                        </td>
                        <td className="px-5 py-3.5 text-right space-x-2">
                          <Link
                            to={`/invoices/${inv.id}`}
                            className="inline-flex items-center space-x-1 p-1.5 rounded-lg bg-slate-800 hover:bg-cyan-500/10 text-slate-300 hover:text-cyan-400 border border-slate-700 hover:border-cyan-500/30 transition-colors"
                            title="Review Invoice"
                          >
                            <Eye className="w-3.5 h-3.5" />
                          </Link>
                          <button
                            onClick={() => handleDelete(inv.id)}
                            className="inline-flex items-center space-x-1 p-1.5 rounded-lg bg-slate-800 hover:bg-rose-500/10 text-slate-300 hover:text-rose-400 border border-slate-700 hover:border-rose-500/30 transition-colors"
                            title="Delete Invoice"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
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
        onUploadSuccess={fetchInvoices}
      />
    </div>
  );
};

export default Invoices;
