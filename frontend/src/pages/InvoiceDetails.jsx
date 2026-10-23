import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import { StatusBadge, RiskBadge } from '../components/StatusBadge';
import { invoiceApi, purchaseOrderApi } from '../services/api';
import {
  ArrowLeft, FileText, Calendar, DollarSign, Building2, Hash,
  AlertCircle, CheckCircle2, Loader2, Copy, Check, ShieldAlert,
  ShieldCheck, RefreshCw, ShoppingBag, Sparkles, Link as LinkIcon
} from 'lucide-react';

const InvoiceDetails = () => {
  const { id } = useParams();
  const [invoice, setInvoice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('verification'); // 'verification', 'fields', 'raw_text'
  const [copied, setCopied] = useState(false);
  const [reprocessing, setReprocessing] = useState(false);
  const [availablePOs, setAvailablePOs] = useState([]);
  const [selectedPOId, setSelectedPOId] = useState('');
  const [linkingPO, setLinkingPO] = useState(false);

  const fetchInvoiceDetails = async () => {
    try {
      const res = await invoiceApi.getInvoice(id);
      setInvoice(res.data.invoice);
      setSelectedPOId(res.data.invoice.purchase_order_id || '');
    } catch (err) {
      console.error("Error loading invoice details:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPOs = async () => {
    try {
      const res = await purchaseOrderApi.getPurchaseOrders();
      setAvailablePOs(res.data.purchase_orders || []);
    } catch (e) {
      console.error("Error loading purchase orders:", e);
    }
  };

  useEffect(() => {
    fetchInvoiceDetails();
    fetchPOs();
  }, [id]);

  // Status Polling Effect if invoice is in queued or processing state
  useEffect(() => {
    if (!invoice) return;
    if (invoice.processing_status === 'queued' || invoice.processing_status === 'processing') {
      const interval = setInterval(async () => {
        try {
          const statusRes = await invoiceApi.getInvoiceStatus(id);
          if (statusRes.data.status !== invoice.processing_status) {
            fetchInvoiceDetails();
          }
        } catch (e) {
          console.error("Polling error:", e);
        }
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [invoice, id]);

  const handleCopyText = () => {
    if (invoice?.extracted_text) {
      navigator.clipboard.writeText(invoice.extracted_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleReprocess = async () => {
    setReprocessing(true);
    try {
      await invoiceApi.reprocessInvoice(id);
      await fetchInvoiceDetails();
    } catch (err) {
      alert("Failed to reprocess invoice.");
    } finally {
      setReprocessing(false);
    }
  };

  const handleLinkPO = async () => {
    setLinkingPO(true);
    try {
      const poVal = selectedPOId ? parseInt(selectedPOId) : null;
      await invoiceApi.linkPurchaseOrder(id, poVal);
      await fetchInvoiceDetails();
    } catch (e) {
      alert("Failed updating Purchase Order link.");
    } finally {
      setLinkingPO(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar pageTitle={`Invoice Review #${id}`} />

        <main className="p-6 space-y-6 flex-1 overflow-y-auto">
          {/* Top Navigation & Action Buttons */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <Link
              to="/invoices"
              className="inline-flex items-center space-x-2 text-xs font-semibold text-slate-400 hover:text-cyan-400 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Invoices Repository</span>
            </Link>

            {invoice && (
              <div className="flex items-center space-x-3">
                <button
                  onClick={handleReprocess}
                  disabled={reprocessing}
                  className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-semibold border border-slate-700 transition-colors disabled:opacity-50"
                  title="Re-run Extraction & Verification"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${reprocessing ? 'animate-spin text-cyan-400' : ''}`} />
                  <span>{reprocessing ? 'Re-analyzing...' : 'Re-verify Invoice'}</span>
                </button>
                <RiskBadge level={invoice.risk_level} score={invoice.risk_score} />
                <StatusBadge status={invoice.processing_status} />
              </div>
            )}
          </div>

          {loading ? (
            <div className="p-12 text-center text-slate-500">
              <Loader2 className="w-8 h-8 animate-spin mx-auto text-cyan-400 mb-3" />
              <p className="text-xs font-medium">Retrieving invoice data & verification records...</p>
            </div>
          ) : !invoice ? (
            <div className="p-12 bg-slate-900 border border-slate-800 rounded-xl text-center text-slate-400">
              Invoice not found.
            </div>
          ) : (
            <>
              {/* Risk Assessment Banner */}
              <div className={`p-5 rounded-xl border shadow-lg ${
                invoice.risk_level === 'HIGH' ? 'bg-rose-950/20 border-rose-500/30' :
                invoice.risk_level === 'MEDIUM' ? 'bg-amber-950/20 border-amber-500/30' :
                'bg-emerald-950/20 border-emerald-500/30'
              }`}>
                <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      {invoice.risk_level === 'HIGH' ? (
                        <ShieldAlert className="w-5 h-5 text-rose-400 shrink-0" />
                      ) : (
                        <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0" />
                      )}
                      <h3 className="text-sm font-bold text-white tracking-wide">
                        Explainable Risk Assessment: <span className={
                          invoice.risk_level === 'HIGH' ? 'text-rose-400' :
                          invoice.risk_level === 'MEDIUM' ? 'text-amber-400' : 'text-emerald-400'
                        }>{invoice.risk_level} RISK ({invoice.risk_score}/100)</span>
                      </h3>
                    </div>
                    <p className="text-xs text-slate-400">
                      Evaluated using transparent accounts-payable verification rules (Duplicate check, PO reconciliation, Vendor registry).
                    </p>
                  </div>

                  {/* Visual Risk Score Meter */}
                  <div className="w-full md:w-56 space-y-1.5">
                    <div className="flex justify-between text-[11px] font-mono text-slate-400">
                      <span>Risk Index</span>
                      <span className="font-bold text-white">{invoice.risk_score} / 100</span>
                    </div>
                    <div className="w-full h-2.5 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                      <div
                        className={`h-full transition-all duration-500 ${
                          invoice.risk_score > 60 ? 'bg-gradient-to-r from-amber-500 to-rose-500' :
                          invoice.risk_score > 25 ? 'bg-gradient-to-r from-emerald-500 to-amber-500' :
                          'bg-emerald-500'
                        }`}
                        style={{ width: `${Math.max(invoice.risk_score, 5)}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

                {/* Risk Factors Breakdown */}
                {invoice.risk_factors && invoice.risk_factors.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-slate-800/80 space-y-2">
                    <p className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">
                      Identified Risk Factors:
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {invoice.risk_factors.map((factor, idx) => (
                        <div key={idx} className="flex items-start space-x-2 text-xs p-2 rounded bg-slate-950/60 border border-slate-800/60">
                          <span className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-bold shrink-0 ${
                            factor.severity === 'HIGH' ? 'bg-rose-500/20 text-rose-400' :
                            factor.severity === 'MEDIUM' ? 'bg-amber-500/20 text-amber-400' :
                            'bg-slate-800 text-slate-300'
                          }`}>
                            +{factor.points}
                          </span>
                          <span className="text-slate-300 leading-tight">{factor.description}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Core Extracted Fields Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-1">
                  <div className="flex items-center space-x-2 text-slate-400 text-xs">
                    <Hash className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Invoice Number</span>
                  </div>
                  <p className="text-base font-bold text-white font-mono">{invoice.invoice_number}</p>
                </div>

                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-1">
                  <div className="flex items-center space-x-2 text-slate-400 text-xs">
                    <Building2 className="w-3.5 h-3.5 text-blue-400" />
                    <span>Vendor</span>
                  </div>
                  <p className="text-base font-bold text-white truncate">
                    {invoice.vendor_name || 'Unlinked / Unknown'}
                  </p>
                </div>

                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-1">
                  <div className="flex items-center space-x-2 text-slate-400 text-xs">
                    <Calendar className="w-3.5 h-3.5 text-amber-400" />
                    <span>Invoice Date</span>
                  </div>
                  <p className="text-base font-bold text-white font-mono">{invoice.invoice_date || 'Not Detected'}</p>
                </div>

                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-1">
                  <div className="flex items-center space-x-2 text-slate-400 text-xs">
                    <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Total Amount</span>
                  </div>
                  <p className="text-base font-bold text-emerald-400 font-mono">
                    {invoice.total_amount ? `${invoice.currency || 'INR'} ${invoice.total_amount.toLocaleString()}` : 'Not Detected'}
                  </p>
                </div>
              </div>

              {/* Main Content Tabs */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-md">
                <div className="flex items-center justify-between border-b border-slate-800 px-5">
                  <div className="flex space-x-6">
                    <button
                      onClick={() => setActiveTab('verification')}
                      className={`py-3 text-xs font-semibold border-b-2 transition-colors ${
                        activeTab === 'verification'
                          ? 'border-cyan-400 text-cyan-400'
                          : 'border-transparent text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      Verification Intelligence
                    </button>
                    <button
                      onClick={() => setActiveTab('fields')}
                      className={`py-3 text-xs font-semibold border-b-2 transition-colors ${
                        activeTab === 'fields'
                          ? 'border-cyan-400 text-cyan-400'
                          : 'border-transparent text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      Extraction Metadata
                    </button>
                    <button
                      onClick={() => setActiveTab('raw_text')}
                      className={`py-3 text-xs font-semibold border-b-2 transition-colors ${
                        activeTab === 'raw_text'
                          ? 'border-cyan-400 text-cyan-400'
                          : 'border-transparent text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      Extracted Text Buffer
                    </button>
                  </div>

                  {activeTab === 'raw_text' && (
                    <button
                      onClick={handleCopyText}
                      className="flex items-center space-x-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-colors"
                    >
                      {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copied ? 'Copied' : 'Copy Text'}</span>
                    </button>
                  )}
                </div>

                <div className="p-6">
                  {/* TAB 1: VERIFICATION INTELLIGENCE */}
                  {activeTab === 'verification' && (
                    <div className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {/* 1. Duplicate Invoice Verification Card */}
                        <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Duplicate Check</span>
                            {invoice.is_duplicate ? (
                              <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">
                                Duplicate Detected
                              </span>
                            ) : (
                              <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                                Unique Invoice
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-slate-300">
                            {invoice.is_duplicate ? (
                              <span className="text-rose-400">
                                Identical invoice number detected! Duplicates Invoice #{invoice.duplicate_of_id} in the database.
                              </span>
                            ) : (
                              <span className="text-slate-400">
                                No duplicate record matching this invoice number exists.
                              </span>
                            )}
                          </p>
                        </div>

                        {/* 2. Vendor Matching Card */}
                        <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Vendor Match</span>
                            <span className={`px-2 py-0.5 rounded text-[11px] font-bold capitalize ${
                              invoice.vendor_match_status === 'matched' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                              invoice.vendor_match_status === 'ambiguous' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                              'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                            }`}>
                              {invoice.vendor_match_status}
                            </span>
                          </div>
                          <div className="text-xs space-y-1 text-slate-300">
                            <p><span className="text-slate-500">Extracted:</span> {invoice.raw_vendor_name || 'None'}</p>
                            <p><span className="text-slate-500">Registry:</span> {invoice.vendor_name || 'Unregistered'}</p>
                            <p><span className="text-slate-500">Match Confidence:</span> {Math.round((invoice.vendor_match_score || 0) * 100)}%</p>
                          </div>
                        </div>

                        {/* 3. Purchase Order Match Card */}
                        <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">PO Reconciliation</span>
                            <span className={`px-2 py-0.5 rounded text-[11px] font-bold capitalize ${
                              invoice.po_match_status === 'matched' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                              invoice.po_match_status === 'mismatched' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                              'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                            }`}>
                              {invoice.po_match_status}
                            </span>
                          </div>
                          <div className="text-xs space-y-1 text-slate-300">
                            <p><span className="text-slate-500">Linked PO:</span> {invoice.linked_po_number || invoice.po_number || 'None'}</p>
                            {invoice.po_match_status === 'mismatched' && (
                              <p className="text-rose-400 font-medium">
                                Variance: {invoice.currency} {invoice.po_amount_diff > 0 ? `+${invoice.po_amount_diff.toLocaleString()}` : invoice.po_amount_diff.toLocaleString()}
                              </p>
                            )}
                            {invoice.po_match_status === 'matched' && (
                              <p className="text-emerald-400">Total exactly matches PO line amount.</p>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Purchase Order Manual Assignment Section */}
                      <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <ShoppingBag className="w-4 h-4 text-cyan-400" />
                            <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                              Purchase Order Linking & Variance Reconciliation
                            </h4>
                          </div>
                          <span className="text-xs text-slate-400">
                            Currently linked: {invoice.linked_po_number || 'No PO'}
                          </span>
                        </div>

                        <div className="flex flex-col sm:flex-row items-center space-y-2 sm:space-y-0 sm:space-x-3">
                          <select
                            value={selectedPOId}
                            onChange={(e) => setSelectedPOId(e.target.value)}
                            className="w-full sm:flex-1 px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
                          >
                            <option value="">-- No Linked Purchase Order --</option>
                            {availablePOs.map(po => (
                              <option key={po.id} value={po.id}>
                                {po.po_number} - {po.vendor_name || 'Vendor'} ({po.currency} {po.total_amount?.toLocaleString()})
                              </option>
                            ))}
                          </select>
                          <button
                            onClick={handleLinkPO}
                            disabled={linkingPO}
                            className="w-full sm:w-auto px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold flex items-center justify-center space-x-1.5 transition-colors disabled:opacity-50"
                          >
                            <LinkIcon className="w-3.5 h-3.5" />
                            <span>{linkingPO ? 'Updating...' : 'Save PO Association'}</span>
                          </button>
                        </div>
                      </div>

                      {/* AI-Assisted Document Insights Section */}
                      <div className="p-4 bg-gradient-to-r from-slate-950 to-slate-900 border border-slate-800 rounded-xl space-y-2">
                        <div className="flex items-center space-x-2 text-cyan-400 text-xs font-bold uppercase tracking-wider">
                          <Sparkles className="w-4 h-4 text-cyan-400" />
                          <span>AI-Assisted Invoice Intelligence (Optional Gemini Engine)</span>
                        </div>
                        {invoice.ai_summary ? (
                          <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800 text-xs text-slate-200 leading-relaxed font-mono">
                            {invoice.ai_summary}
                          </div>
                        ) : (
                          <p className="text-xs text-slate-400 leading-relaxed">
                            CortexGrid verification engine operates deterministically. To enable plain-language generative executive summaries, provide a <code className="text-cyan-400 font-mono">GEMINI_API_KEY</code> in <code className="text-slate-300 font-mono">backend/.env</code>.
                          </p>
                        )}
                      </div>
                    </div>
                  )}

                  {/* TAB 2: EXTRACTION METADATA */}
                  {activeTab === 'fields' && (
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="p-3.5 bg-slate-950 rounded-lg border border-slate-800/80 flex justify-between">
                          <span className="text-xs text-slate-400">Invoice Number:</span>
                          <span className="text-xs font-semibold text-white font-mono">{invoice.invoice_number || 'N/A'}</span>
                        </div>
                        <div className="p-3.5 bg-slate-950 rounded-lg border border-slate-800/80 flex justify-between">
                          <span className="text-xs text-slate-400">Extracted Vendor:</span>
                          <span className="text-xs font-semibold text-white">{invoice.raw_vendor_name || 'N/A'}</span>
                        </div>
                        <div className="p-3.5 bg-slate-950 rounded-lg border border-slate-800/80 flex justify-between">
                          <span className="text-xs text-slate-400">Matched Registered Vendor:</span>
                          <span className="text-xs font-semibold text-cyan-400">{invoice.vendor_name || 'Unmatched'}</span>
                        </div>
                        <div className="p-3.5 bg-slate-950 rounded-lg border border-slate-800/80 flex justify-between">
                          <span className="text-xs text-slate-400">Billed Date:</span>
                          <span className="text-xs font-semibold text-white font-mono">{invoice.invoice_date || 'N/A'}</span>
                        </div>
                        <div className="p-3.5 bg-slate-950 rounded-lg border border-slate-800/80 flex justify-between">
                          <span className="text-xs text-slate-400">Extracted PO Ref:</span>
                          <span className="text-xs font-semibold text-white font-mono">{invoice.po_number || 'N/A'}</span>
                        </div>
                        <div className="p-3.5 bg-slate-950 rounded-lg border border-slate-800/80 flex justify-between">
                          <span className="text-xs text-slate-400">Total Billed Amount:</span>
                          <span className="text-xs font-semibold text-emerald-400 font-mono">
                            {invoice.total_amount ? `${invoice.currency} ${invoice.total_amount.toLocaleString()}` : 'N/A'}
                          </span>
                        </div>
                        <div className="p-3.5 bg-slate-950 rounded-lg border border-slate-800/80 flex justify-between">
                          <span className="text-xs text-slate-400">Extraction Confidence:</span>
                          <span className="text-xs font-semibold text-cyan-400 font-mono">
                            {Math.round((invoice.extraction_confidence || 0) * 100)}%
                          </span>
                        </div>
                        <div className="p-3.5 bg-slate-950 rounded-lg border border-slate-800/80 flex justify-between">
                          <span className="text-xs text-slate-400">Stored Filename:</span>
                          <span className="text-xs font-mono text-slate-300 truncate max-w-[200px]" title={invoice.file_name}>
                            {invoice.file_name}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* TAB 3: RAW TEXT */}
                  {activeTab === 'raw_text' && (
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-xs text-slate-400">
                        <span>Extracted Document Characters</span>
                        <span className="font-mono text-[11px]">
                          Length: {(invoice.extracted_text || '').length} characters
                        </span>
                      </div>
                      <pre className="p-4 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-slate-300 leading-relaxed overflow-x-auto whitespace-pre-wrap max-h-96 selection:bg-cyan-500 selection:text-white">
                        {invoice.extracted_text || 'No text extracted or processing in progress.'}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
};

export default InvoiceDetails;
