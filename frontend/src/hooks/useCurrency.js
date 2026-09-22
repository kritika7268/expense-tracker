import { useAuth } from '../context/AuthContext';
import { formatCurrency, getCurrencySymbol } from '../utils/formatters';

export const useCurrency = () => {
  const { user } = useAuth();
  const currencyCode = user?.currency || 'INR';

  return {
    currencyCode,
    currencySymbol: getCurrencySymbol(currencyCode),
    format: (amount) => formatCurrency(amount, currencyCode),
  };
};
