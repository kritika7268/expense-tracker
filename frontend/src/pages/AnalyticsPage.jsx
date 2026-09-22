import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import {
  TrendingUp,
  PieChart as PieIcon,
  BarChart3,
  Calendar,
  Award,
  Wallet,
  ArrowUpRight,
  ArrowDownLeft,
  Percent,
} from 'lucide-react';

import api from '../services/api';
import { useCurrency } from '../hooks/useCurrency';
import { useToast } from '../context/ToastContext';
import LoadingSpinner from '../components/common/LoadingSpinner';
import CategoryIcon from '../components/common/CategoryIcon';
import ProgressBar from '../components/common/ProgressBar';

const PIE_COLORS = [
  '#6366f1',
  '#10b981',
  '#f59e0b',
  '#ec4899',
  '#06b6d4',
  '#8b5cf6',
  '#f43f5e',
  '#64748b',
  '#14b8a6',
  '#eab308',
];

export const AnalyticsPage = () => {
  const today = new Date();
  const [selectedMonth, setSelectedMonth] = useState(today.getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(today.getFullYear());

  const [monthlyTrends, setMonthlyTrends] = useState([]);
  const [categoryBreakdown, setCategoryBreakdown] = useState([]);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  const { format, currencySymbol } = useCurrency();
  const { error: toastError } = useToast();

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        const [trendsRes, catsRes, reportRes] = await Promise.all([
          api.get('/analytics/monthly?months=6'),
          api.get(`/analytics/categories?month=${selectedMonth}&year=${selectedYear}`),
          api.get(`/analytics/report?month=${selectedMonth}&year=${selectedYear}`),
        ]);

        if (trendsRes?.data) setMonthlyTrends(trendsRes.data);
        if (catsRes?.data) setCategoryBreakdown(catsRes.data);
        if (reportRes?.data) setReport(reportRes.data);
      } catch (err) {
        toastError(err.message || 'Failed to load analytics data');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [selectedMonth, selectedYear, toastError]);

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

  if (loading) {
    return <LoadingSpinner size="lg" message="Aggregating financial analytics and trendlines..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header & Date Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
            Financial Analytics & Reports
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Visual trends, category proportions, and periodic summary breakdowns.
          </p>
        </div>

        <div className="flex items-center gap-2 p-1 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
          <Calendar className="w-4 h-4 text-slate-400 ml-2" />
          <select
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(parseInt(e.target.value, 10))}
            className="bg-transparent text-xs sm:text-sm font-semibold text-slate-800 dark:text-slate-200 focus:outline-none py-1 pr-2"
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
            className="bg-transparent text-xs sm:text-sm font-semibold text-slate-800 dark:text-slate-200 focus:outline-none py-1 pr-2"
          >
            {[2024, 2025, 2026, 2027].map((y) => (
              <option key={y} value={y}>
                {y}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Monthly Report Executive Summary Card */}
      {report && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
                Monthly Statement
              </span>
              <h2 className="text-lg font-black text-slate-900 dark:text-white">
                {monthsList.find((m) => m.num === selectedMonth)?.name} {selectedYear} Financial Report
              </h2>
            </div>
            <div className="text-right">
              <span className="text-xs text-slate-500 dark:text-slate-400 block">Total Transactions</span>
              <span className="text-base font-bold text-slate-900 dark:text-white">{report.transaction_count} recorded</span>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4">
            <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800">
              <span className="text-xs text-slate-500 dark:text-slate-400 block">Income</span>
              <span className="text-base sm:text-lg font-bold text-emerald-600 dark:text-emerald-400 mt-1 block">
                {format(report.total_income)}
              </span>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800">
              <span className="text-xs text-slate-500 dark:text-slate-400 block">Expense</span>
              <span className="text-base sm:text-lg font-bold text-rose-600 dark:text-rose-400 mt-1 block">
                {format(report.total_expense)}
              </span>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800">
              <span className="text-xs text-slate-500 dark:text-slate-400 block">Net Savings</span>
              <span className={`text-base sm:text-lg font-bold mt-1 block ${report.total_savings >= 0 ? 'text-indigo-600 dark:text-indigo-400' : 'text-rose-600 dark:text-rose-400'}`}>
                {format(report.total_savings)}
              </span>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800">
              <span className="text-xs text-slate-500 dark:text-slate-400 block">Savings Rate</span>
              <span className="text-base sm:text-lg font-bold text-slate-900 dark:text-white mt-1 block">
                {report.savings_rate}%
              </span>
            </div>
          </div>

          {report.highest_spending_category && (
            <div className="mt-4 p-3.5 rounded-2xl bg-amber-50/70 dark:bg-amber-950/30 border border-amber-200/60 dark:border-amber-900/40 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 text-amber-900 dark:text-amber-200 font-medium">
                <Award className="w-4 h-4 text-amber-500" />
                <span>Highest Spending Category:</span>
                <span className="font-bold">{report.highest_spending_category.category_name}</span>
              </div>
              <span className="font-extrabold text-amber-900 dark:text-amber-200">
                {format(report.highest_spending_category.amount)} ({report.highest_spending_category.percentage}% of total)
              </span>
            </div>
          )}
        </div>
      )}

      {/* Row 1 Charts: Income vs Expense Bar + Category Donut */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Income vs Expense Comparison */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm">
          <div className="mb-4">
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              Income vs Expenses (6-Month Trend)
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Monthly cash flow comparison
            </p>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthlyTrends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
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
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                <Bar dataKey="income" name="Income" fill="#10b981" radius={[6, 6, 0, 0]} />
                <Bar dataKey="expense" name="Expense" fill="#f43f5e" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Spending Donut Chart */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm">
          <div className="mb-4">
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              Spending by Category
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Distribution for {monthsList.find((m) => m.num === selectedMonth)?.name} {selectedYear}
            </p>
          </div>

          <div className="h-64 w-full flex items-center justify-center">
            {categoryBreakdown.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryBreakdown}
                    dataKey="amount"
                    nameKey="category_name"
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={3}
                  >
                    {categoryBreakdown.map((entry, index) => (
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
              <div className="text-center text-xs text-slate-400 py-12">
                No expense transactions found for this period.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Row 2 Charts: Monthly Savings Trend + Top Categories List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Savings & Rate Trend Line Chart */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm">
          <div className="mb-4">
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              Savings Velocity Trend
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Net savings accumulated month-over-month
            </p>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={monthlyTrends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
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
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                <Line
                  type="monotone"
                  dataKey="savings"
                  name="Net Savings"
                  stroke="#6366f1"
                  strokeWidth={3}
                  dot={{ r: 4, fill: '#6366f1' }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Spending Categories Ranking List */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm">
          <div className="mb-4">
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              Top Categories Breakdown
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Detailed percentages of monthly expenses
            </p>
          </div>

          {categoryBreakdown.length > 0 ? (
            <div className="space-y-3.5 max-h-64 overflow-y-auto pr-1">
              {categoryBreakdown.map((cat, idx) => (
                <div key={cat.category_id} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className="w-4 text-slate-400 font-bold">#{idx + 1}</span>
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
            <div className="text-center text-xs text-slate-400 py-12">
              No categories recorded for this period.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
