import {
  LayoutDashboard, UtensilsCrossed, ClipboardList, BookOpen,
  Users, CreditCard, BarChart3, Settings, Table2, PlusCircle, ChefHat
} from 'lucide-react';
import { Role } from '../data/mockData';

type Screen = string;

interface NavItem {
  id: Screen;
  label: string;
  icon: React.ReactNode;
}

const adminItems: NavItem[] = [
  { id: 'dashboard', label: 'Главная', icon: <LayoutDashboard size={18} /> },
  { id: 'tables', label: 'Столики', icon: <Table2 size={18} /> },
  { id: 'orders', label: 'Заказы', icon: <ClipboardList size={18} /> },
  { id: 'menu', label: 'Меню', icon: <BookOpen size={18} /> },
  { id: 'customers', label: 'Клиенты', icon: <Users size={18} /> },
  { id: 'payments', label: 'Оплаты', icon: <CreditCard size={18} /> },
  { id: 'reports', label: 'Отчеты', icon: <BarChart3 size={18} /> },
  { id: 'settings', label: 'Настройки', icon: <Settings size={18} /> },
];

const waiterItems: NavItem[] = [
  { id: 'waiter-workspace', label: 'Рабочее место', icon: <LayoutDashboard size={18} /> },
  { id: 'tables', label: 'Столики', icon: <Table2 size={18} /> },
  { id: 'new-order', label: 'Новый заказ', icon: <PlusCircle size={18} /> },
  { id: 'orders', label: 'Заказы', icon: <ClipboardList size={18} /> },
  { id: 'menu', label: 'Меню', icon: <BookOpen size={18} /> },
  { id: 'payments', label: 'Оплата', icon: <CreditCard size={18} /> },
];

interface Props {
  role: Role;
  currentScreen: Screen;
  onNavigate: (screen: Screen) => void;
}

export function Sidebar({ role, currentScreen, onNavigate }: Props) {
  const items = role === 'admin' ? adminItems : waiterItems;

  return (
    <aside
      style={{
        width: 220,
        minWidth: 220,
        height: '100vh',
        background: '#15171A',
        borderRight: '1px solid #30343B',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        zIndex: 10,
      }}
    >
      {/* Logo */}
      <div
        style={{
          padding: '24px 20px',
          borderBottom: '1px solid #30343B',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div
            style={{
              width: 36,
              height: 36,
              background: 'linear-gradient(135deg, #C9A45C, #A07B3A)',
              borderRadius: 10,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <ChefHat size={18} color="#0E0F11" strokeWidth={2.5} />
          </div>
          <div>
            <div style={{ color: '#F5F2EA', fontFamily: 'Manrope', fontWeight: 800, fontSize: 16, letterSpacing: '-0.02em', lineHeight: 1 }}>
              GastroHub
            </div>
            <div style={{ color: '#6F756F', fontSize: 10, marginTop: 2, letterSpacing: '0.04em', textTransform: 'uppercase' }}>
              POS система
            </div>
          </div>
        </div>
      </div>

      {/* Role indicator */}
      <div
        style={{
          margin: '12px 16px',
          padding: '8px 12px',
          background: role === 'admin' ? 'rgba(201,164,92,0.08)' : 'rgba(31,111,80,0.08)',
          border: `1px solid ${role === 'admin' ? 'rgba(201,164,92,0.2)' : 'rgba(31,111,80,0.2)'}`,
          borderRadius: 8,
        }}
      >
        <div style={{ fontSize: 10, color: '#6F756F', letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: 2 }}>
          Роль
        </div>
        <div style={{ fontSize: 13, fontWeight: 600, color: role === 'admin' ? '#C9A45C' : '#3FA66B' }}>
          {role === 'admin' ? 'Администратор' : 'Официант'}
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: '8px 10px', overflowY: 'auto' }}>
        {items.map((item) => {
          const active = currentScreen === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: '10px 12px',
                borderRadius: 8,
                border: 'none',
                cursor: 'pointer',
                marginBottom: 2,
                background: active ? 'rgba(201,164,92,0.12)' : 'transparent',
                color: active ? '#C9A45C' : '#A9A39A',
                textAlign: 'left',
                fontSize: 14,
                fontWeight: active ? 600 : 400,
                transition: 'all 0.15s ease',
                position: 'relative',
              }}
              onMouseEnter={(e) => {
                if (!active) {
                  (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.04)';
                  (e.currentTarget as HTMLButtonElement).style.color = '#F5F2EA';
                }
              }}
              onMouseLeave={(e) => {
                if (!active) {
                  (e.currentTarget as HTMLButtonElement).style.background = 'transparent';
                  (e.currentTarget as HTMLButtonElement).style.color = '#A9A39A';
                }
              }}
            >
              {active && (
                <span
                  style={{
                    position: 'absolute',
                    left: 0,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    width: 3,
                    height: 20,
                    background: '#C9A45C',
                    borderRadius: '0 2px 2px 0',
                  }}
                />
              )}
              <span style={{ opacity: active ? 1 : 0.7 }}>{item.icon}</span>
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* Bottom */}
      <div
        style={{
          padding: '16px',
          borderTop: '1px solid #30343B',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #252932, #30343B)',
              border: '2px solid #30343B',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 12,
              fontWeight: 700,
              color: '#C9A45C',
              flexShrink: 0,
            }}
          >
            {role === 'admin' ? 'АД' : 'ОФ'}
          </div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600, color: '#F5F2EA' }}>
              {role === 'admin' ? 'Алексей Д.' : 'Максим В.'}
            </div>
            <div style={{ fontSize: 11, color: '#6F756F' }}>
              {role === 'admin' ? 'Администратор' : 'Официант'}
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
