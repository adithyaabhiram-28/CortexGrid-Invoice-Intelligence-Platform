import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach JWT token to outgoing requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('cortexgrid_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor to handle auth failures
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token on 401 Unauthorized
      localStorage.removeItem('cortexgrid_token');
      localStorage.removeItem('cortexgrid_user');
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getMe: () => api.get('/auth/me'),
};

export const vendorApi = {
  getVendors: (search = '') => api.get(`/vendors?search=${encodeURIComponent(search)}`),
  getVendor: (id) => api.get(`/vendors/${id}`),
  createVendor: (vendorData) => api.post('/vendors', vendorData),
  updateVendor: (id, vendorData) => api.put(`/vendors/${id}`, vendorData),
  deleteVendor: (id) => api.delete(`/vendors/${id}`),
};

export const purchaseOrderApi = {
  getPurchaseOrders: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return api.get(`/purchase-orders?${query}`);
  },
  getPurchaseOrder: (id) => api.get(`/purchase-orders/${id}`),
  createPurchaseOrder: (poData) => api.post('/purchase-orders', poData),
  updatePurchaseOrder: (id, poData) => api.put(`/purchase-orders/${id}`, poData),
  deletePurchaseOrder: (id) => api.delete(`/purchase-orders/${id}`),
};

export const invoiceApi = {
  uploadInvoice: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/invoices/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  getInvoices: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return api.get(`/invoices?${query}`);
  },
  getInvoice: (id) => api.get(`/invoices/${id}`),
  getInvoiceStatus: (id) => api.get(`/invoices/${id}/status`),
  deleteInvoice: (id) => api.delete(`/invoices/${id}`),
  linkPurchaseOrder: (invoiceId, poId) => api.post(`/invoices/${invoiceId}/link-po`, { purchase_order_id: poId }),
  reprocessInvoice: (invoiceId) => api.post(`/invoices/${invoiceId}/reprocess`),
};

export default api;
