import React, { useState, useEffect } from 'react';
import { X, ShoppingBag, Plus, Trash2, AlertCircle, Loader2 } from 'lucide-react';
import { purchaseOrderApi, vendorApi } from '../services/api';

/**
 * Safely round numbers to two decimal places without floating-point artifacts.
 */
const roundToTwo = (num) => {
  const n = Number(num);
  if (isNaN(n) || !isFinite(n)) return 0;
  return Math.round((n + Number.EPSILON) * 100) / 100;
};

const PurchaseOrderModal = ({ isOpen, onClose, onSaveSuccess, po = null }) => {
  const [poNumber, setPoNumber] = useState('');
  const [vendorId, setVendorId] = useState('');
  const [poDate, setPoDate] = useState('');
  const [currency, setCurrency] = useState('INR');
  const [description, setDescription] = useState('');
  const [vendors, setVendors] = useState([]);
  const [items, setItems] = useState([
    { item_description: '', quantity: 1, unit_price: '', total_amount: 0 }
  ]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      loadVendors();
      if (po) {
        setPoNumber(po.po_number || '');
        setVendorId(po.vendor_id ? String(po.vendor_id) : '');
        setPoDate(po.po_date || '');
        setCurrency(po.currency || 'INR');
        setDescription(po.description || '');
        setItems(
          po.items?.length
            ? po.items.map((it) => {
                const q = parseFloat(it.quantity) || 0;
                const p = parseFloat(it.unit_price) || 0;
                return {
                  id: it.id,
                  item_description: it.item_description || '',
                  quantity: it.quantity ?? 1,
                  unit_price: it.unit_price ?? '',
                  total_amount: roundToTwo(q * p),
                };
              })
            : [{ item_description: '', quantity: 1, unit_price: '', total_amount: 0 }]
        );
      } else {
        setPoNumber('');
        setVendorId('');
        setPoDate(new Date().toISOString().split('T')[0]);
        setCurrency('INR');
        setDescription('');
        setItems([{ item_description: '', quantity: 1, unit_price: '', total_amount: 0 }]);
      }
      setError('');
    }
  }, [isOpen, po]);

  const loadVendors = async () => {
    try {
      const res = await vendorApi.getVendors();
      setVendors(res.data.vendors || []);
    } catch (e) {
      console.error("Failed fetching vendors for PO modal:", e);
    }
  };

  if (!isOpen) return null;

  const handleItemChange = (index, field, value) => {
    setItems((prevItems) =>
      prevItems.map((item, idx) => {
        if (idx !== index) return item;

        const updatedItem = {
          ...item,
          [field]: value,
        };

        const qtyVal = field === 'quantity' ? value : updatedItem.quantity;
        const priceVal = field === 'unit_price' ? value : updatedItem.unit_price;

        const q = parseFloat(qtyVal);
        const p = parseFloat(priceVal);

        const safeQty = !isNaN(q) && isFinite(q) ? q : 0;
        const safePrice = !isNaN(p) && isFinite(p) ? p : 0;

        updatedItem.total_amount = roundToTwo(safeQty * safePrice);
        return updatedItem;
      })
    );
  };

  const addItemRow = () => {
    setItems((prevItems) => [
      ...prevItems,
      { item_description: '', quantity: 1, unit_price: '', total_amount: 0 },
    ]);
  };

  const removeItemRow = (idx) => {
    setItems((prevItems) => {
      if (prevItems.length <= 1) return prevItems;
      return prevItems.filter((_, i) => i !== idx);
    });
  };

  const calculateGrandTotal = () => {
    const total = items.reduce((sum, itm) => {
      const lineTotal = parseFloat(itm.total_amount);
      return sum + (!isNaN(lineTotal) && isFinite(lineTotal) ? lineTotal : 0);
    }, 0);
    return roundToTwo(total);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!poNumber.trim()) {
      setError('PO Number is required.');
      return;
    }

    const grandTotal = calculateGrandTotal();
    const formattedItems = items
      .filter((it) => it.item_description.trim())
      .map((it) => {
        const q = parseFloat(it.quantity) || 0;
        const p = parseFloat(it.unit_price) || 0;
        return {
          item_description: it.item_description.trim(),
          quantity: q,
          unit_price: p,
          total_amount: roundToTwo(q * p),
        };
      });

    const payload = {
      po_number: poNumber.trim().toUpperCase(),
      vendor_id: vendorId ? parseInt(vendorId, 10) : null,
      po_date: poDate,
      total_amount: grandTotal,
      currency,
      description: description.trim(),
      items: formattedItems,
    };

    setSubmitting(true);
    setError('');

    try {
      if (po) {
        await purchaseOrderApi.updatePurchaseOrder(po.id, payload);
      } else {
        await purchaseOrderApi.createPurchaseOrder(payload);
      }
      onSaveSuccess();
      onClose();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save Purchase Order. Please check inputs.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm overflow-y-auto">
      <div className="bg-slate-900 border border-slate-800 rounded-xl w-full max-w-2xl shadow-2xl overflow-hidden my-8">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <ShoppingBag className="w-5 h-5 text-cyan-400" />
            <h3 className="text-base font-semibold text-white">
              {po ? 'Edit Purchase Order' : 'Create New Purchase Order (PO)'}
            </h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4 max-h-[80vh] overflow-y-auto">
          {error && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg flex items-center space-x-2 text-rose-400 text-xs font-medium">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                PO Number <span className="text-rose-400">*</span>
              </label>
              <input
                type="text"
                required
                value={poNumber}
                onChange={(e) => setPoNumber(e.target.value)}
                placeholder="e.g. PO-2026-7890"
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono uppercase"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Associated Vendor</label>
              <select
                value={vendorId}
                onChange={(e) => setVendorId(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
              >
                <option value="">-- Select Registered Vendor (Optional) --</option>
                {vendors.map(v => (
                  <option key={v.id} value={v.id}>{v.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Issue Date</label>
              <input
                type="date"
                value={poDate}
                onChange={(e) => setPoDate(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-100 focus:outline-none focus:border-cyan-500 font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Currency</label>
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
              >
                <option value="INR">INR (₹)</option>
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (€)</option>
                <option value="GBP">GBP (£)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Description / Notes</label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g. IT Equipment and Hardware Procurement"
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          {/* Line Items Section */}
          <div className="pt-2">
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                PO Line Items
              </label>
              <button
                type="button"
                onClick={addItemRow}
                className="inline-flex items-center space-x-1 text-xs text-cyan-400 hover:text-cyan-300 font-medium"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Item</span>
              </button>
            </div>

            {/* Explicit Column Labels */}
            <div className="flex items-center space-x-2 px-2.5 text-[11px] font-medium text-slate-400 mb-1">
              <span className="flex-1">Item Description</span>
              <span className="w-20 text-center">Quantity</span>
              <span className="w-28 text-right">Unit Price</span>
              <span className="w-24 text-right">Line Total</span>
              <span className="w-6"></span>
            </div>

            <div className="space-y-2">
              {items.map((item, idx) => (
                <div key={idx} className="flex items-center space-x-2 bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                  <input
                    type="text"
                    placeholder="e.g. Dell UltraSharp 27 Monitor"
                    value={item.item_description}
                    onChange={(e) => handleItemChange(idx, 'item_description', e.target.value)}
                    className="flex-1 px-2.5 py-1.5 bg-slate-900 border border-slate-800 rounded text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500"
                  />
                  <input
                    type="number"
                    min="0"
                    step="any"
                    placeholder="Qty"
                    title="Quantity"
                    value={item.quantity}
                    onChange={(e) => handleItemChange(idx, 'quantity', e.target.value)}
                    className="w-20 px-2 py-1.5 bg-slate-900 border border-slate-800 rounded text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500 font-mono text-center"
                  />
                  <input
                    type="number"
                    min="0"
                    step="any"
                    placeholder="Unit Price"
                    title="Unit Price"
                    value={item.unit_price}
                    onChange={(e) => handleItemChange(idx, 'unit_price', e.target.value)}
                    className="w-28 px-2 py-1.5 bg-slate-900 border border-slate-800 rounded text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500 font-mono text-right"
                  />
                  <div className="w-24 text-right font-mono text-xs text-emerald-400 font-medium pr-1">
                    {(parseFloat(item.total_amount) || 0).toLocaleString()}
                  </div>
                  <button
                    type="button"
                    onClick={() => removeItemRow(idx)}
                    disabled={items.length === 1}
                    className="text-slate-500 hover:text-rose-400 p-1 disabled:opacity-30 transition-colors"
                    title="Remove item"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>

            {/* Total Display */}
            <div className="flex justify-end items-center space-x-3 pt-3 text-right">
              <span className="text-xs text-slate-400">Total PO Amount:</span>
              <span className="text-sm font-bold font-mono text-emerald-400">
                {currency} {calculateGrandTotal().toLocaleString()}
              </span>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex items-center space-x-2 px-5 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-semibold shadow-lg shadow-cyan-500/20 disabled:opacity-50 transition-all"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Saving PO...</span>
                </>
              ) : (
                <span>{po ? 'Update PO' : 'Create Purchase Order'}</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PurchaseOrderModal;
