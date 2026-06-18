import { useState } from 'react';
import { Role } from './data/mockData';
import { LoginScreen } from './components/LoginScreen';
import { Sidebar } from './components/Sidebar';
import { TopBar } from './components/TopBar';
import { AdminDashboard } from './components/AdminDashboard';
import { WaiterWorkspace } from './components/WaiterWorkspace';
import { TablesScreen } from './components/TablesScreen';
import { NewOrderScreen } from './components/NewOrderScreen';
import { OrderDetailsScreen } from './components/OrderDetailsScreen';
import { OrdersListScreen } from './components/OrdersListScreen';
import { MenuScreen } from './components/MenuScreen';
import { CustomersScreen } from './components/CustomersScreen';
import { PaymentsScreen } from './components/PaymentsScreen';
import { ReportsScreen } from './components/ReportsScreen';
import { SettingsScreen } from './components/SettingsScreen';

type Screen =
  | 'dashboard'
  | 'waiter-workspace'
  | 'tables'
  | 'new-order'
  | 'order-details'
  | 'orders'
  | 'menu'
  | 'customers'
  | 'payments'
  | 'reports'
  | 'settings';

export default function App() {
  const [role, setRole] = useState<Role | null>(null);
  const [screen, setScreen] = useState<Screen>('dashboard');

  const handleLogin = (r: Role) => {
    setRole(r);
    setScreen(r === 'admin' ? 'dashboard' : 'waiter-workspace');
  };

  const handleLogout = () => {
    setRole(null);
    setScreen('dashboard');
  };

  const navigate = (s: string) => setScreen(s as Screen);

  if (!role) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  const renderScreen = () => {
    switch (screen) {
      case 'dashboard':
        return <AdminDashboard onNavigate={navigate} />;
      case 'waiter-workspace':
        return <WaiterWorkspace onNavigate={navigate} />;
      case 'tables':
        return <TablesScreen role={role} onNavigate={navigate} />;
      case 'new-order':
        return <NewOrderScreen onNavigate={navigate} />;
      case 'order-details':
        return <OrderDetailsScreen role={role} onNavigate={navigate} />;
      case 'orders':
        return <OrdersListScreen role={role} onNavigate={navigate} />;
      case 'menu':
        return <MenuScreen role={role} />;
      case 'customers':
        return <CustomersScreen role={role} />;
      case 'payments':
        return <PaymentsScreen role={role} />;
      case 'reports':
        return <ReportsScreen />;
      case 'settings':
        return <SettingsScreen />;
      default:
        return <AdminDashboard onNavigate={navigate} />;
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        height: '100vh',
        width: '100vw',
        background: '#0E0F11',
        overflow: 'hidden',
        fontFamily: "'Inter', 'Manrope', sans-serif",
      }}
    >
      <Sidebar role={role} currentScreen={screen} onNavigate={navigate} />

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <TopBar role={role} onLogout={handleLogout} onAction={() => navigate(role === 'admin' ? 'reports' : 'new-order')} />

        <main
          style={{
            flex: 1,
            overflow: 'hidden',
            background: '#0E0F11',
          }}
        >
          {renderScreen()}
        </main>
      </div>
    </div>
  );
}
