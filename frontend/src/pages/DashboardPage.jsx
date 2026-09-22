import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Wallet,
  ArrowUpRight,
  ArrowDownLeft,
  PiggyBank,
  Percent,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  Plus,
  Calendar,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';

import api from '../services/api';
import { useCurrency } from '../hooks/useCurrency';
import StatCard from '../components/common/StatCard';
import ProgressBar from '../components/common/ProgressBar';
import LoadingSpinner from '../components/common/LoadingSpinner';
import EmptyState from '../components/common/EmptyState';
import CategoryIcon from '../components/common/CategoryIcon';
import { formatDate } from '../utils/formatters';

const PIE_COLORS = [
  '#6366f1', // indigo
  '#10b981', // emerald
  '#f59e0b', // amber
  '#ec4899', // pink
  '#06b6d4', // cyan
  '#8b5cf6', // purple
  '#f43f5e', // rose
  '#64748b', // slate
];

export const DashboardPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { format, currencySymbol } = useCurrency();

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.get('/dashboard/summary');
      if (res?.data) {
        setData(res.data);
      }
    } catch (err) {
      setError(err.message || 'Failed to load dashboard metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading) {
    return <LoadingSpinner size="lg" message="Loading live dashboard analytics..." />;
  }

  if (error) {
    return (
      <div className="p-6 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 rounded-2xl text-center">
        <AlertTriangle className="w-10 h-10 text-rose-500 mx-auto mb-2" />
        <h3 className="text-base font-bold text-rose-800 dark:text-rose-200">Unable to load dashboard</h3>
        <p className="text-sm text-rose-600 dark:text-rose-400 mt-1 mb-4">{error}</p>
        <button
          onClick={fetchDashboard}
          className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-semibold"
        >
          Try Again
        </button>
      </div>
    );
  }

  const {
    total_balance = 0,
    current_month_income = 0,
    current_month_expense = 0,
    current_month_savings = 0,
    savings_rate = 0,
    total_budget = 0,
    budget_spent = 0,
    budget_remaining = 0,
    budget_used_percentage = 0,
    budget_warnings = [],
    recent_transactions = [],
    top_spending_categories = [],
    monthly_trends = [],
  } = data || {};

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
            Financial Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Real-time balance, spending velocity, and category budget health.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Link
            to="/transactions/add"
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-sm font-semibold shadow-sm shadow-indigo-600/20 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Add Transaction</span>
          </Link>
        </div>
      </div>

      {/* Budget Warning Banners */}
      {budget_warnings.length > 0 && (
        <div className="space-y-2">
          {budget_warnings.map((warning, index) => (
            <div
              key={index}
              className="flex items-center gap-3 p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/60 text-amber-900 dark:text-amber-200 text-sm shadow-xs animate-in fade-in"
            >
              <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0" />
              <div className="flex-1 font-medium">{warning}</div>
              <Link
                to="/budgets"
                className="text-xs font-bold text-amber-700 dark:text-amber-400 hover:underline shrink-0"
              >
                Review Budgets →
              </Link>
            </div>
          ))}
        </div>
      )}

      {/* Primary KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
        <StatCard
          title="Total Net Balance"
          value={format(total_balance)}
          subtitle="Cumulative (All-time)"
          icon={Wallet}
          color="indigo"
        />

        <StatCard
          title="This Month Income"
          value={format(current_month_income)}
          subtitle="Current calendar month"
          icon={ArrowUpRight}
          color="emerald"
        />

        <StatCard
          title="This Month Expenses"
          value={format(current_month_expense)}
          subtitle="Current calendar month"
          icon={ArrowDownLeft}
          color="rose"
        />

        <StatCard
          title="Monthly Savings Rate"
          value={`${savings_rate}%`}
          subtitle={`Net saved: ${format(current_month_savings)}`}
          icon={Percent}
          color={savings_rate >= 20 ? 'emerald' : savings_rate > 0 ? 'amber' : 'rose'}
        />
      </div>

      {/* Budget Overview Card */}
      {total_budget > 0 && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 sm:p-6 shadow-sm">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400">
                <PiggyBank className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                  Monthly Budget Guardrail
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {format(budget_spent)} spent of {format(total_budget)} active monthly budget
                </p>
              </div>
            </div>

            <div className="text-right">
              <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${
                budget_used_percentage >= 100
                  ? 'bg-rose-100 dark:bg-rose-950/60 text-rose-700 dark:text-rose-400'
                  : budget_used_percentage >= 80
                  ? 'bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400'
                  : 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400'
              }`}>
                {budget_used_percentage}% utilized
              </span>
            </div>
          </div>

          <ProgressBar percentage={budget_used_percentage} className="h-3 my-2" />

          <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400 mt-2">
            <span>Spent: {format(budget_spent)}</span>
            <span>Remaining: {format(budget_remaining)}</span>
          </div>
        </div>
      )}

      {/* Visual Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Income vs Expense Bar Chart */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 sm:p-6 shadow-sm flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Income vs Expenses (Last 6 Months)
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Monthly cashflow comparison
              </p>
            </div>
            <Link to="/analytics" className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline">
              Detailed Analytics →
            </Link>
          </div>

          <div className="h-64 sm:h-72 w-full mt-auto">
            {monthly_trends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={monthly_trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <XAxis dataKey="month" stroke="#94a3b8" fontSize={11} tickLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} tickFormatter={(v) => `${currencySymbol}${v >= 1000 ? (v/1000).toFixed(0) + 'k' : v}`} />
                  <Tooltip
                    formatter={(val) => format(val)}
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      borderColor: '#334155',
                      borderRadius: '12px',
                      color: '#fff',
                      fontSize: '12px',
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                  <Bar dataKey="income" name="Income" fill="#10b981" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="expense" name="Expense" fill="#ef4444" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <EmptyState title="No trend data" description="Add transactions to view monthly charts." />
            )}
          </div>
        </div>

        {/* Category Breakdown Donut */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 sm:p-6 shadow-sm flex flex-col">
          <div className="mb-3">
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              Spending by Category
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Current month expense distribution
            </p>
          </div>

          <div className="h-64 w-full flex items-center justify-center">
            {top_spending_categories.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={top_spending_categories}
                    dataKey="amount"
                    nameKey="category_name"
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={3}
                  >
                    {top_spending_categories.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(val) => format(val)}
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      borderColor: '#334155',
                      borderRadius: '12px',
                      color: '#fff',
                      fontSize: '12px',
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <EmptyState title="No expenses this month" description="Expenses will automatically form category breakdown." />
            )}
          </div>
        </div>
      </div>

      {/* Bottom Grid: Recent Transactions & Top Spending Categories */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Transactions List */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 sm:p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Recent Transactions
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Latest transactions posted to your account
              </p>
            </div>
            <Link
              to="/transactions"
              className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
            >
              <span>View All</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {recent_transactions.length > 0 ? (
            <div className="divide-y divide-slate-100 dark:divide-slate-800">
              {recent_transactions.map((t) => (
                <div key={t.id} className="py-3.5 flex items-center justify-between gap-3">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className={`p-2.5 rounded-xl shrink-0 ${
                      t.type === 'income'
                        ? 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400'
                        : 'bg-rose-50 dark:bg-rose-950/50 text-rose-600 dark:text-rose-400'
                    }`}>
                      <CategoryIcon name={t.category?.icon || 'Tag'} className="w-4 h-4" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-semibold text-slate-900 dark:text-white truncate">
                        {t.title}
                      </p>
                      <p className="text-xs text-slate-500 dark:text-slate-400 truncate">
                        {t.category?.name || 'Category'} • {formatDate(t.transaction_date)} • {t.payment_method}
                      </p>
                    </div>
                  </div>

                  <div className="text-right shrink-0">
                    <span className={`text-sm font-bold ${
                      t.type === 'income'
                        ? 'text-emerald-600 dark:text-emerald-400'
                        : 'text-slate-900 dark:text-white'
                    }`}>
                      {t.type === 'income' ? '+' : '-'}{format(t.amount)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              title="No recent transactions"
              description="Get started by recording your first transaction."
              actionText="Add Transaction"
              onAction={() => window.location.href = '/transactions/add'}
            />
          )}
        </div>

        {/* Top Spending Categories Ranking */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 sm:p-6 shadow-sm">
          <div className="mb-4">
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              Top Expenses Ranking
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Highest monthly expenses by category
            </p>
          </div>

          {top_spending_categories.length > 0 ? (
            <div className="space-y-4">
              {top_spending_categories.map((cat, idx) => (
                <div key={cat.category_id} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className="w-5 text-slate-400 font-bold">#{idx + 1}</span>
                      <CategoryIcon name={cat.category_icon || 'Tag'} className="w-3.5 h-3.5 text-slate-500" />
                      <span className="font-semibold text-slate-800 dark:text-slate-200">
                        {cat.category_name}
                      </span>
                    </div>
                    <span className="font-bold text-slate-900 dark:text-white">
                      {format(cat.amount)} ({cat.percentage}%)
                    </span>
                  </div>
                  <ProgressBar percentage={cat.percentage} className="h-1.5" />
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              title="No spending recorded"
              description="Top categories will appear once expenses are added."
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
