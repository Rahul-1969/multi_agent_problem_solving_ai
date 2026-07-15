import { create } from 'zustand';

const useToastStore = create((set, get) => ({
  toasts: [],
  addToast: (message, type = 'success', id = null) => {
    const toastId = id || Date.now();
    set((state) => {
      const exists = state.toasts.find(t => t.id === toastId);
      if (exists) {
        return { toasts: state.toasts.map(t => t.id === toastId ? { ...t, message, type } : t) };
      }
      return { toasts: [...state.toasts, { id: toastId, message, type }] };
    });
    
    if (type !== 'loading') {
      setTimeout(() => {
        get().dismiss(toastId);
      }, 3000);
    }
    return toastId;
  },
  success: (message) => get().addToast(message, 'success'),
  error: (message) => get().addToast(message, 'error'),
  warning: (message) => get().addToast(message, 'warning'),
  info: (message) => get().addToast(message, 'info'),
  loading: (message) => {
    const id = Date.now();
    get().addToast(message, 'loading', id);
    return id;
  },
  dismiss: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id)
    }))
}));

export default useToastStore;
