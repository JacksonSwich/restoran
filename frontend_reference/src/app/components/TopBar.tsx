import { useState, useEffect } from 'react';
import { Search, Bell, LogOut, Plus, FileText } from 'lucide-react';
import { Role } from '../data/mockData';

interface Props {
  role: Role;
  onLogout: () => void;
  onAction: () => void;
}

export function TopBar({ role, onLogout, onAction }: Props) {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 60000);
    return () => clearInterval(t);
  }, []);

  const formatted = time.toLocaleDateString('ru-RU', {
    weekday: 'short', day: 'numeric', month: 'short',
  }) + ' · ' + time.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });

  return (
    <header
      style={{
        height: 64,
        background: '#15171A',
        borderBottom: '1px solid #30343B',
        display: 'flex',
        alignItems: 'center',
        padding: '0 24px',
        gap: 16,
        flexShrink: 0,
      }}
    >
      {/* Search */}
      <div
        style={{
          flex: 1,
          maxWidth: 420,
          position: 'relative',
        }}
      >
        <Search
          size={16}
          color="#6F756F"
          style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)' }}
        />
        <input
          type="text"
          placeholder="Поиск заказа, столика, клиента или блюда"
          style={{
            width: '100%',
            background: '#0E0F11',
            border: '1px solid #30343B',
            borderRadius: 8,
            padding: '8px 12px 8px 36px',
            color: '#F5F2EA',
            fontSize: 13,
            outline: 'none',
          }}
        />
      </div>

      <div style={{ flex: 1 }} />

      {/* Date */}
      <div style={{ color: '#A9A39A', fontSize: 13, whiteSpace: 'nowrap' }}>
        {formatted}
      </div>

      {/* Role badge */}
      <div
        style={{
          padding: '5px 12px',
          background: role === 'admin' ? 'rgba(201,164,92,0.1)' : 'rgba(63,166,107,0.1)',
          border: `1px solid ${role === 'admin' ? 'rgba(201,164,92,0.25)' : 'rgba(63,166,107,0.25)'}`,
          borderRadius: 20,
          fontSize: 12,
          fontWeight: 600,
          color: role === 'admin' ? '#C9A45C' : '#3FA66B',
          whiteSpace: 'nowrap',
        }}
      >
        Роль: {role === 'admin' ? 'Администратор' : 'Официант'}
      </div>

      {/* Notifications */}
      <button
        style={{
          width: 36,
          height: 36,
          borderRadius: 8,
          background: '#202328',
          border: '1px solid #30343B',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          position: 'relative',
        }}
      >
        <Bell size={16} color="#A9A39A" />
        <span
          style={{
            position: 'absolute',
            top: 6,
            right: 6,
            width: 8,
            height: 8,
            background: '#C9A45C',
            borderRadius: '50%',
            border: '2px solid #15171A',
          }}
        />
      </button>

      {/* Action button */}
      <button
        onClick={onAction}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          padding: '8px 16px',
          background: 'linear-gradient(135deg, #C9A45C, #A07B3A)',
          color: '#0E0F11',
          border: 'none',
          borderRadius: 8,
          fontSize: 13,
          fontWeight: 700,
          cursor: 'pointer',
          whiteSpace: 'nowrap',
          transition: 'opacity 0.15s',
        }}
        onMouseEnter={(e) => (e.currentTarget.style.opacity = '0.85')}
        onMouseLeave={(e) => (e.currentTarget.style.opacity = '1')}
      >
        {role === 'admin' ? (
          <>
            <FileText size={14} />
            Создать отчет
          </>
        ) : (
          <>
            <Plus size={14} />
            Создать заказ
          </>
        )}
      </button>

      {/* User */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div
          style={{
            width: 34,
            height: 34,
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #252932, #30343B)',
            border: '2px solid #C9A45C44',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 12,
            fontWeight: 700,
            color: '#C9A45C',
            cursor: 'pointer',
          }}
        >
          {role === 'admin' ? 'АД' : 'ОФ'}
        </div>
      </div>

      {/* Logout */}
      <button
        onClick={onLogout}
        title="Выйти"
        style={{
          width: 34,
          height: 34,
          borderRadius: 8,
          background: 'transparent',
          border: '1px solid #30343B',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          color: '#6F756F',
          transition: 'all 0.15s',
        }}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLButtonElement).style.color = '#C94C4C';
          (e.currentTarget as HTMLButtonElement).style.borderColor = '#C94C4C44';
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLButtonElement).style.color = '#6F756F';
          (e.currentTarget as HTMLButtonElement).style.borderColor = '#30343B';
        }}
      >
        <LogOut size={15} />
      </button>
    </header>
  );
}
