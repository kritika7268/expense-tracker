# Expensely Frontend

A high-performance personal finance dashboard built with React, Vite, Tailwind CSS, Lucide Icons, and Recharts.

## Features
- **Responsive Architecture**: Fluid layouts for Desktop, Tablet, and Mobile with slide-over navigation drawer.
- **Theme Support**: Seamless Dark/Light mode persisted to `localStorage`.
- **Real-Time Visualizations**: Interactive Recharts components for cashflow comparison, category distribution donut, and savings velocity trendline.
- **Dynamic Currency Formatting**: Multi-currency support (`INR ₹`, `USD $`, `EUR €`, `GBP £`) dynamic across all views and cards.
- **CSV Data Export**: Direct download of filtered transaction tables in standard RFC-4180 format.
- **Secure Token Interceptor**: Centralized Axios client managing JWT authentication and session timeouts.

## Setup & Running

### Windows (PowerShell / CMD)
```powershell
# Navigate to frontend directory
cd expense-tracker/frontend

# Install dependencies
npm.cmd install

# Start development server
npm.cmd run dev
```

Local URL: [http://localhost:5173](http://localhost:5173)
