import React, { useState, useEffect } from 'react';
import {
  PiggyBank,
  Plus,
  AlertTriangle,
  Edit2,
  Trash2,
  Calendar,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
} from 'lucide-react';

import api from '../services/api';
import { useCurrency } from '../hooks/useCurrency';
import { useToast } from '../context/ToastContext';
import ProgressBar from '../components/common/ProgressBar';
import Modal from '../components/common/Modal';
import ConfirmDialog from '../components/common/ConfirmDialog';
import LoadingSpinner from '../components/common/LoadingSpinner';
import EmptyState from '../components/common/EmptyState';
import CategoryIcon from '../components/common/CategoryIcon';

export const BudgetsPage = () => {
  const today = new Date();
  const [selectedMonth, setSelectedMonth] = useState(today.getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(today.getFullYear());

  const [budgetData, setBudgetData] = useState(null);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modal State for Set/Edit Budget
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingBudget, setEditingBudget] = useState(null);
  const [budgetCategoryId, setBudgetCategoryId] = useState('');
  const [budgetAmount, setBudgetAmount] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [modalError, setModalError] = useState('');

  // Delete State
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const { format, currencySymbol } = useCurrency();
  const { success, error: toastError } = useToast();

  // Fetch expense categories
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const res = await api.get('/categories?type=expense');
        if (res?.data) {
          setCategories(res.data);
        }
      } catch (err) {
        console.error('Failed to load expense categories', err);
      }
    };
    fetchCategories();
  }, []);

  // Fetch budgets for selected month/year
  const fetchBudgets = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/budgets?month=${selectedMonth}&year=${selectedYear}`);
      if (res?.data) {
        setBudgetData(res.data);
      }
    } catch (err) {
      toastError(err.message || 'Failed to load budgets');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBudgets();
  }, [selectedMonth, selectedYear]);

  const handleOpenCreateModal = () => {
    setEditingBudget(null);
    setBudgetAmount('');
    setModalError('');
    if (categories.length > 0) {
      setBudgetCategoryId(String(categories[0].id));
    }
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (b) => {
    setEditingBudget(b);
    setBudgetCategoryId(String(b.category_id));
    setBudgetAmount(String(b.amount));
    setModalError('');
    setIsModalOpen(true);
  };

  const handleSaveBudget = async (e) => {
    e.preventDefault();
    setModalError('');

    const numAmt = parseFloat(budgetAmount);
    if (isNaN(numAmt) || numAmt <= 0) {
      setModalError('Please enter an amount greater than 0');
      return;
    }
    if (!budgetCategoryId) {
      setModalError('Please select a category');
      return;
    }

    setSubmitting(true);
    try {
      if (editingBudget) {
        await api.put(`/budgets/${editingBudget.id}`, {
          amount: numAmt,
          category_id: parseInt(budgetCategoryId, 10),
          month: selectedMonth,
          year: selectedYear,
        });
        success('Budget updated successfully');
      } else {
        await api.post('/budgets', {
          amount: numAmt,
          category_id: parseInt(budgetCategoryId, 10),
          month: selectedMonth,
          year: selectedYear,
        });
        success('Monthly budget set successfully');
      }
      setIsModalOpen(false);
      fetchBudgets();
    } catch (err) {
      setModalError(err.message || 'Failed to save budget');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteBudget = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await api.delete(`/budgets/${deleteTarget.id}`);
      success('Budget removed');
      setDeleteTarget(null);
      fetchBudgets();
    } catch (err) {
      toastError(err.message || 'Failed to delete budget');
    } finally {
      setDeleting(false);
    }
  };

  const {
    total_budget = 0,
    total_spent = 0,
    total_remaining = 0,
    overall_percentage = 0,
    budgets = [],
  } = budgetData || {};

  const monthsList = [
    { num: 1, name: 'January' },
    { num: 2, name: 'February' },
    { num: 3, name: 'March' },
    { num: 4, name: 'April' },
    { num: 5, name: 'May' },
    { num: 6, name: 'June' },
    { num: 7, name: 'July' },
    { num: 8, name: 'August' },
    { num: 9, name: 'September' },
    { num: 10, name: 'October' },
    { num: 11, name: 'November' },
    { num: 12, name: 'December' },
  ];

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
            Monthly Budgets
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Set proactive spending guardrails and track category consumption in real time.
          </p>
        </div>

        <div className="flex items-center gap-2.5 flex-wrap">
          {/* Month / Year Picker */}
          <div className="flex items-center gap-1.5 p-1 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
            <select
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(parseInt(e.target.value, 10))}
              className="bg-transparent text-xs sm:text-sm font-semibold text-slate-800 dark:text-slate-200 focus:outline-none px-2 py-1"
            >
              {monthsList.map((m) => (
                <option key={m.num} value={m.num}>
                  {m.name}
                </option>
              ))}
            </select>
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(parseInt(e.target.value, 10))}
              className="bg-transparent text-xs sm:text-sm font-semibold text-slate-800 dark:text-slate-200 focus:outline-none px-2 py-1"
            >
              {[2024, 2025, 2026, 2027].map((y) => (
                <option key={y} value={y}>
                  {y}
                </option>
              ))}
            </select>
          </div>

          <button
            type="button"
            onClick={handleOpenCreateModal}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-sm font-semibold shadow-sm shadow-indigo-600/20 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Set New Budget</span>
          </button>
        </div>
      </div>

      {/* Overview Statistics Banner */}
      {total_budget > 0 && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Overall Monthly Allowance
              </span>
              <div className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white mt-1">
                {format(total_budget)}
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-left">
              <div>
                <span className="text-xs text-slate-500 dark:text-slate-400 block">Total Spent</span>
                <span className="text-base font-bold text-slate-900 dark:text-white">{format(total_spent)}</span>
              </div>
              <div>
                <span className="text-xs text-slate-500 dark:text-slate-400 block">Remaining</span>
                <span className="text-base font-bold text-emerald-600 dark:text-emerald-400">{format(total_remaining)}</span>
              </div>
              <div>
                <span className="text-xs text-slate-500 dark:text-slate-400 block">Overall Utilization</span>
                <span className="text-base font-bold text-indigo-600 dark:text-indigo-400">{overall_percentage}%</span>
              </div>
            </div>
          </div>

          <ProgressBar percentage={overall_percentage} className="h-3" />
        </div>
      )}

      {/* Budgets Grid */}
      {loading ? (
        <LoadingSpinner size="lg" message="Calculating budget usage and thresholds..." />
      ) : budgets.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {budgets.map((b) => {
            let statusBadgeClass = 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-900/40';
            if (b.status === 'Over Budget') {
              statusBadgeClass = 'bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-400 border-rose-200 dark:border-rose-900/40';
            } else if (b.status === 'Near Limit') {
              statusBadgeClass = 'bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-900/40';
            }

            return (
              <div
                key={b.id}
                className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="flex items-center gap-3">
                      <div className="p-2.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 border border-indigo-100 dark:border-indigo-900/50">
                        <CategoryIcon name={b.category?.icon || 'Tag'} className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="font-bold text-base text-slate-900 dark:text-white leading-snug">
                          {b.category?.name || 'Category'}
                        </h3>
                        <span className="text-xs text-slate-500 dark:text-slate-400">
                          Target: {format(b.amount)}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => handleOpenEditModal(b)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-indigo-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                        title="Edit Budget"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setDeleteTarget(b)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                        title="Delete Budget"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Warning Message Pill if Near Limit / Over Budget */}
                  {b.warning_message && (
                    <div className="mb-3 p-2 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/50 text-amber-800 dark:text-amber-300 text-xs font-medium flex items-center gap-2">
                      <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                      <span>{b.warning_message}</span>
                    </div>
                  )}

                  {/* Progress bar */}
                  <div className="space-y-2 mt-4">
                    <ProgressBar percentage={b.percentage} className="h-2.5" />
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-600 dark:text-slate-400">
                        Spent: <span className="font-bold text-slate-900 dark:text-white">{format(b.spent)}</span>
                      </span>
                      <span className="font-bold text-slate-700 dark:text-slate-300">
                        {b.percentage}%
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mt-5 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Remaining</span>
                    <span className="font-bold text-slate-800 dark:text-slate-200">
                      {format(b.remaining)}
                    </span>
                  </div>

                  <span className={`px-2.5 py-1 rounded-full text-xs font-bold border ${statusBadgeClass}`}>
                    {b.status}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <EmptyState
          icon={PiggyBank}
          title="No budgets set for this month"
          description={`You have not established monthly budget limits for ${monthsList.find((m) => m.num === selectedMonth)?.name} ${selectedYear}.`}
          actionText="Create First Budget"
          onAction={handleOpenCreateModal}
        />
      )}

      {/* Set / Edit Budget Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingBudget ? 'Edit Category Budget' : 'Set Monthly Budget'}
      >
        {modalError && (
          <div className="mb-4 p-3 rounded-xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900/50 text-rose-700 dark:text-rose-300 text-xs font-medium flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{modalError}</span>
          </div>
        )}

        <form onSubmit={handleSaveBudget} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1.5">
              Expense Category
            </label>
            <select
              required
              disabled={!!editingBudget}
              value={budgetCategoryId}
              onChange={(e) => setBudgetCategoryId(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-60"
            >
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1.5">
              Monthly Budget Amount ({currencySymbol})
            </label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              required
              value={budgetAmount}
              onChange={(e) => setBudgetAmount(e.target.value)}
              placeholder="e.g. 5000"
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm font-bold text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-3">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-xs disabled:opacity-50"
            >
              {submitting ? 'Saving...' : 'Save Budget'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDeleteBudget}
        title="Remove Budget"
        message={`Are you sure you want to remove the ${deleteTarget?.category?.name} budget?`}
        confirmText="Remove Budget"
        isLoading={deleting}
      />
    </div>
  );
};

export default BudgetsPage;
