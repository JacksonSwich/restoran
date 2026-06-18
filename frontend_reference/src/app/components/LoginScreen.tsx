import { ChefHat, Shield, UserRound, Check } from 'lucide-react';
import { Role } from '../data/mockData';

interface Props {
  onLogin: (role: Role) => void;
}

const adminFeatures = [
  'Управление меню',
  'Отчеты и аналитика',
  'Управление клиентами',
  'Просмотр оплат',
  'Редактирование заказов',
  'Управление столиками',
];

const waiterFeatures = [
  'Работа со столиками',
  'Создание заказов',
  'Добавление блюд',
  'Изменение статусов',
  'Оплата заказов',
  'Просмотр меню',
];

export function LoginScreen({ onLogin }: Props) {
  return (
    <div
      style={{
        minHeight: '100vh',
        background: '#0E0F11',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Background pattern */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: `radial-gradient(circle at 20% 50%, rgba(201,164,92,0.04) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(31,111,80,0.04) 0%, transparent 50%)`,
          pointerEvents: 'none',
        }}
      />

      {/* Grid lines */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: `linear-gradient(rgba(48,52,59,0.3) 1px, transparent 1px),
            linear-gradient(90deg, rgba(48,52,59,0.3) 1px, transparent 1px)`,
          backgroundSize: '60px 60px',
          pointerEvents: 'none',
        }}
      />

      <div style={{ position: 'relative', zIndex: 1, textAlign: 'center', maxWidth: 880, padding: '0 24px', width: '100%' }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 14, marginBottom: 40 }}>
          <div
            style={{
              width: 56,
              height: 56,
              background: 'linear-gradient(135deg, #C9A45C, #A07B3A)',
              borderRadius: 16,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 40px rgba(201,164,92,0.3)',
            }}
          >
            <ChefHat size={28} color="#0E0F11" strokeWidth={2.5} />
          </div>
          <div style={{ textAlign: 'left' }}>
            <div style={{ fontFamily: 'Manrope', fontWeight: 800, fontSize: 32, color: '#F5F2EA', letterSpacing: '-0.04em', lineHeight: 1 }}>
              GastroHub
            </div>
            <div style={{ fontSize: 12, color: '#6F756F', letterSpacing: '0.1em', textTransform: 'uppercase', marginTop: 4 }}>
              Restaurant Management System
            </div>
          </div>
        </div>

        <h1 style={{ fontFamily: 'Manrope', fontSize: 28, fontWeight: 700, color: '#F5F2EA', marginBottom: 8, lineHeight: 1.2 }}>
          Система управления рестораном
        </h1>
        <p style={{ fontSize: 15, color: '#A9A39A', marginBottom: 48 }}>
          Выберите роль для входа в систему
        </p>

        {/* Role cards */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, maxWidth: 780, margin: '0 auto' }}>
          {/* Admin card */}
          <RoleCard
            icon={<Shield size={28} color="#C9A45C" />}
            title="Администратор"
            subtitle="Полный доступ к системе"
            features={adminFeatures}
            accentColor="#C9A45C"
            onClick={() => onLogin('admin')}
          />

          {/* Waiter card */}
          <RoleCard
            icon={<UserRound size={28} color="#3FA66B" />}
            title="Официант"
            subtitle="Рабочее место сотрудника"
            features={waiterFeatures}
            accentColor="#3FA66B"
            onClick={() => onLogin('waiter')}
          />
        </div>

        <p style={{ marginTop: 40, fontSize: 12, color: '#6F756F' }}>
          GastroHub POS · Версия 2.4.1 · 2026
        </p>
      </div>
    </div>
  );
}

function RoleCard({
  icon, title, subtitle, features, accentColor, onClick,
}: {
  icon: React.ReactNode;
  title: string;
  subtitle: string;
  features: string[];
  accentColor: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      style={{
        background: '#202328',
        border: `1px solid #30343B`,
        borderRadius: 16,
        padding: '32px 28px',
        textAlign: 'left',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        position: 'relative',
        overflow: 'hidden',
      }}
      onMouseEnter={(e) => {
        const el = e.currentTarget as HTMLButtonElement;
        el.style.borderColor = `${accentColor}44`;
        el.style.background = '#252932';
        el.style.transform = 'translateY(-2px)';
        el.style.boxShadow = `0 12px 40px rgba(0,0,0,0.4), 0 0 0 1px ${accentColor}22`;
      }}
      onMouseLeave={(e) => {
        const el = e.currentTarget as HTMLButtonElement;
        el.style.borderColor = '#30343B';
        el.style.background = '#202328';
        el.style.transform = 'translateY(0)';
        el.style.boxShadow = 'none';
      }}
    >
      <div
        style={{
          position: 'absolute',
          top: 0,
          right: 0,
          width: 120,
          height: 120,
          background: `radial-gradient(circle at top right, ${accentColor}08, transparent 70%)`,
          pointerEvents: 'none',
        }}
      />

      <div
        style={{
          width: 56,
          height: 56,
          borderRadius: 14,
          background: `${accentColor}12`,
          border: `1px solid ${accentColor}22`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: 20,
        }}
      >
        {icon}
      </div>

      <div style={{ fontFamily: 'Manrope', fontSize: 20, fontWeight: 700, color: '#F5F2EA', marginBottom: 4 }}>
        {title}
      </div>
      <div style={{ fontSize: 13, color: '#A9A39A', marginBottom: 24 }}>
        {subtitle}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {features.map((f) => (
          <div key={f} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div
              style={{
                width: 18,
                height: 18,
                borderRadius: '50%',
                background: `${accentColor}15`,
                border: `1px solid ${accentColor}33`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              <Check size={10} color={accentColor} strokeWidth={3} />
            </div>
            <span style={{ fontSize: 13, color: '#A9A39A' }}>{f}</span>
          </div>
        ))}
      </div>

      <div
        style={{
          marginTop: 28,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '12px 24px',
          background: `linear-gradient(135deg, ${accentColor}, ${accentColor}CC)`,
          borderRadius: 10,
          fontSize: 14,
          fontWeight: 700,
          color: '#0E0F11',
        }}
      >
        Войти как {title.toLowerCase()}
      </div>
    </button>
  );
}
