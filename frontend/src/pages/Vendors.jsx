import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import VendorModal from '../components/VendorModal';
import { vendorApi } from '../services/api';
import { Building2, Plus, Search, Edit2, Trash2, Mail, Phone, MapPin, RefreshCw, FileText } from 'lucide-react';

const Vendors = () => {
  const [vendors, setVendors] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedVendor, setSelectedVendor] = useState(null);

  const fetchVendors = async () => {
    setLoading(true);
    try {
      const res = await vendorApi.getVendors(search);
      setVendors(res.data.vendors || []);
    } catch (err) {
      console.error("Failed fetching vendors:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchVendors();
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const handleOpenAdd = () => {
    setSelectedVendor(null);
    setIsModalOpen(true);
  };

  const handleOpenEdit = (vendor) => {
    setSelectedVendor(vendor);
    setIsModalOpen(true);
  };

  const handleDelete = async (vendor) => {
    if (!window.confirm(`Are you sure you want to delete vendor "${vendor.name}"?`)) return;
    try {
      await vendorApi.deleteVendor(vendor.id);
      fetchVendors();
    } catch (err) {
      alert("Failed to delete vendor.");
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar pageTitle="Vendor Management Foundation" />

        <main className="p-6 space-y-6 flex-1 overflow-y-auto">
          {/* Controls Header */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900 p-4 rounded-xl border border-slate-800 shadow-md">
            <div className="relative flex-1 max-w-md w-full">
              <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search vendors by name..."
                className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div className="flex items-center space-x-3 w-full sm:w-auto justify-end">
              <button
                onClick={fetchVendors}
                className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
                title="Refresh list"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
              <button
                onClick={handleOpenAdd}
                className="px-3.5 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-semibold shadow-md shadow-cyan-500/20 flex items-center space-x-2 transition-all"
              >
                <Plus className="w-4 h-4" />
                <span>Add Vendor</span>
              </button>
            </div>
          </div>

          {/* Vendors Table Card */}
          <div className="rounded-xl bg-slate-900 border border-slate-800 shadow-md overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950/60 text-slate-400 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-800">
                  <tr>
                    <th className="px-5 py-3.5">Vendor Name</th>
                    <th className="px-5 py-3.5">Normalized Identity</th>
                    <th className="px-5 py-3.5">Email</th>
                    <th className="px-5 py-3.5">Phone</th>
                    <th className="px-5 py-3.5">Invoices Linked</th>
                    <th className="px-5 py-3.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {loading ? (
                    <tr>
                      <td colSpan={6} className="px-5 py-10 text-center text-slate-500">
                        Loading vendor repository...
                      </td>
                    </tr>
                  ) : vendors.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-5 py-10 text-center text-slate-500">
                        <Building2 className="w-8 h-8 mx-auto text-slate-600 mb-2" />
                        No vendors registered. Click "Add Vendor" to create one.
                      </td>
                    </tr>
                  ) : (
                    vendors.map((v) => (
                      <tr key={v.id} className="hover:bg-slate-800/40 transition-colors">
                        <td className="px-5 py-3.5 font-semibold text-white">
                          <div className="flex items-center space-x-2">
                            <Building2 className="w-4 h-4 text-cyan-400 shrink-0" />
                            <span>{v.name}</span>
                          </div>
                        </td>
                        <td className="px-5 py-3.5 font-mono text-[11px] text-slate-400">
                          {v.normalized_name}
                        </td>
                        <td className="px-5 py-3.5 text-slate-300">
                          {v.email ? (
                            <span className="inline-flex items-center gap-1.5 text-slate-300">
                              <Mail className="w-3 h-3 text-slate-500" />
                              {v.email}
                            </span>
                          ) : (
                            <span className="text-slate-600">-</span>
                          )}
                        </td>
                        <td className="px-5 py-3.5 text-slate-300">
                          {v.phone ? (
                            <span className="inline-flex items-center gap-1.5 text-slate-300">
                              <Phone className="w-3 h-3 text-slate-500" />
                              {v.phone}
                            </span>
                          ) : (
                            <span className="text-slate-600">-</span>
                          )}
                        </td>
                        <td className="px-5 py-3.5">
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                            <FileText className="w-3 h-3 text-cyan-400" />
                            {v.invoice_count || 0}
                          </span>
                        </td>
                        <td className="px-5 py-3.5 text-right space-x-2">
                          <button
                            onClick={() => handleOpenEdit(v)}
                            className="inline-flex items-center space-x-1 p-1.5 rounded-lg bg-slate-800 hover:bg-cyan-500/10 text-slate-300 hover:text-cyan-400 border border-slate-700 hover:border-cyan-500/30 transition-colors"
                            title="Edit Vendor"
                          >
                            <Edit2 className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleDelete(v)}
                            className="inline-flex items-center space-x-1 p-1.5 rounded-lg bg-slate-800 hover:bg-rose-500/10 text-slate-300 hover:text-rose-400 border border-slate-700 hover:border-rose-500/30 transition-colors"
                            title="Delete Vendor"
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

      <VendorModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        vendor={selectedVendor}
        onSaveSuccess={fetchVendors}
      />
    </div>
  );
};

export default Vendors;
