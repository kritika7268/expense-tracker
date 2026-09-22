import { CURRENCIES } from './constants';

export const getCurrencySymbol = (currencyCode = 'INR') => {
  const match = CURRENCIES.find((c) => c.code === currencyCode);
  return match ? match.symbol : '₹';
};

export const formatCurrency = (amount, currencyCode = 'INR') => {
  const symbol = getCurrencySymbol(currencyCode);
  const num = Number(amount) || 0;
  
  // Format with thousands separator and two decimal places
  const formattedNum = new Intl.NumberFormat('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num);

  return `${symbol}${formattedNum}`;
};

export const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(date);
};

export const formatPercentage = (val) => {
  const num = Number(val) || 0;
  return `${num.toFixed(1)}%`;
};
