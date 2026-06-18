import { Building2, Users, Layers, MapPin, CreditCard, Check, Shield, UserRound } from 'lucide-react';

const sections = [
  { id: 'profile', label: 'Профиль ресторана', icon: <Building2 size={16} /> },
  { id: 'users', label: 'Пользователи и роли', icon: <Users size={16} /> },
  { id: 'statuses', label: 'Статусы заказов', icon: <Layers size={16} /> },
  { id: 'zones', label: 'Зоны столиков', icon: <MapPin size={16} /> },
  { id: 'payments', label: 'Способы оплаты', icon: <CreditCard size={16} /> },
];

const adminPermissions = [
  'Управление меню',
  'Управление столиками',
  'Просмотр отчетов',
  'Управление клиентами',
  'Просмотр оплат',
  'Редактирование заказов',
];

const waiterPermissions = [
  'Создание заказов',
  'Добавление блюд',
  'Изменение статусов',
  'Оплата заказов',
  'Просмотр меню',
  'Просмотр столиков',
];

const orderStatuses = [
  { key: 'new', label: 'Новый', color: '#4A7BD0' },
  { key: 'cooking', label: 'Готовится', color: '#D98A35' },
  { key: 'ready', label: 'Готов', color: '#3FA66B' },
  { key: 'served', label: 'Подан', color: '#9B6CDD' },
  { key: 'paid', label: 'Оплачен', color: '#1F6F50' },
  { key: 'cancelled', label: 'Отменен', color: '#C94C4C' },
];

export function SettingsScreen() {
  return (
    <div style={{ display: 'flex', height: '100%', overflow: 'hidden' }}>
      {/* Sidebar */}
      <div style={{
        width: 220, flexShrink: 0, background: '#15171A', borderRight: '1px solid #30343B',
        padding: '24px 14px', display: 'flex', flexDirection: 'column', gap: 4,
      }}>
        <div style={{ fontSize: 11, color: '#6F756F', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 10, paddingLeft: 8 }}>
          Настройки
        </div>
        {sections.map((s, i) => (
          <button
            key={s.id}
            style={{
              display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px',
              borderRadius: 8, border: 'none', cursor: 'pointer', textAlign: 'left',
              background: i === 1 ? 'rgba(201,164,92,0.1)' : 'transparent',
              color: i === 1 ? '#C9A45C' : '#A9A39A',
              fontSize: 13, fontWeight: i === 1 ? 600 : 400,
              borderLeft: `3px solid ${i === 1 ? '#C9A45C' : 'transparent'}`,
            }}
          >
            {s.icon}
            {s.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: 28, display: 'flex', flexDirection: 'column', gap: 24 }}>
        <div>
          <h1 style={{ fontFamily: 'Manrope', fontSize: 24, fontWeight: 800, color: '#F5F2EA', marginBottom: 4 }}>Настройки</h1>
          <p style={{ fontSize: 13, color: '#6F756F' }}>Управление системой и правами доступа</p>
        </div>

        {/* Restaurant profile */}
        <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 12, padding: 24 }}>
          <h3 style={{ fontSize: 15, fontWeight: 600, color: '#F5F2EA', marginBottom: 20 }}>Профиль ресторана</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            {[
              { label: 'Название', value: 'GastroHub' },
              { label: 'Телефон', value: '+7 (495) 123-45-67' },
              { label: 'Адрес', value: 'Москва, ул. Тверская, 24' },
              { label: 'Email', value: 'info@gastrohub.ru' },
            ].map(f => (
              <div key={f.label}>
                <label style={{ fontSize: 11, color: '#6F756F', display: 'block', marginBottom: 6, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                  {f.label}
                </label>
                <input
                  type="text"
                  defaultValue={f.value}
                  style={{
                    width: '100%', background: '#15171A', border: '1px solid #30343B',
                    borderRadius: 8, padding: '10px 14px', color: '#F5F2EA', fontSize: 13, boxSizing: 'border-box',
                  }}
                />
              </div>
            ))}
          </div>
          <button style={{ ...btnPrimary, marginTop: 20 }}>Сохранить изменения</button>
        </div>

        {/* Role permissions */}
        <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 12, padding: 24 }}>
          <h3 style={{ fontSize: 15, fontWeight: 600, color: '#F5F2EA', marginBottom: 6 }}>Права доступа по ролям</h3>
          <p style={{ fontSize: 12, color: '#6F756F', marginBottom: 20 }}>Настройка разрешений для каждой роли</p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
            <RolePermissions
              icon={<Shield size={20} color="#C9A45C" />}
              role="Администратор"
              permissions={adminPermissions}
              color="#C9A45C"
            />
            <RolePermissions
              icon={<UserRound size={20} color="#3FA66B" />}
              role="Официант"
              permissions={waiterPermissions}
              color="#3FA66B"
            />
          </div>
        </div>

        {/* Order statuses */}
        <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 12, padding: 24 }}>
          <h3 style={{ fontSize: 15, fontWeight: 600, color: '#F5F2EA', marginBottom: 20 }}>Статусы заказов</h3>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            {orderStatuses.map(s => (
              <div key={s.key} style={{
                display: 'flex', alignItems: 'center', gap: 8,
                padding: '10px 16px', background: `${s.color}10`,
                border: `1px solid ${s.color}30`, borderRadius: 10,
              }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: s.color, flexShrink: 0 }} />
                <span style={{ fontSize: 13, color: '#F5F2EA', fontWeight: 500 }}>{s.label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Zones */}
        <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 12, padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <h3 style={{ fontSize: 15, fontWeight: 600, color: '#F5F2EA' }}>Зоны столиков</h3>
            <button style={btnPrimary}>Добавить зону</button>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {['Основной зал', 'VIP-зона', 'Терраса'].map(zone => (
              <div key={zone} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '12px 16px', background: '#15171A', border: '1px solid #30343B',
                borderRadius: 8,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <MapPin size={16} color="#C9A45C" />
                  <span style={{ fontSize: 14, color: '#F5F2EA' }}>{zone}</span>
                </div>
                <button style={btnSecondary}>Редактировать</button>
              </div>
            ))}
          </div>
        </div>

        {/* Payment methods */}
        <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 12, padding: 24 }}>
          <h3 style={{ fontSize: 15, fontWeight: 600, color: '#F5F2EA', marginBottom: 16 }}>Способы оплаты</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {[
              { label: 'Наличные', enabled: true },
              { label: 'Банковская карта', enabled: true },
              { label: 'Онлайн-оплата', enabled: true },
            ].map(m => (
              <div key={m.label} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '12px 16px', background: '#15171A', border: '1px solid #30343B', borderRadius: 8,
              }}>
                <span style={{ fontSize: 14, color: '#F5F2EA' }}>{m.label}</span>
                <div style={{
                  width: 44, height: 24, borderRadius: 12,
                  background: m.enabled ? 'rgba(63,166,107,0.2)' : '#252932',
                  border: `1px solid ${m.enabled ? '#3FA66B' : '#30343B'}`,
                  position: 'relative', cursor: 'pointer',
                }}>
                  <div style={{
                    position: 'absolute', top: 3, left: m.enabled ? 22 : 3,
                    width: 16, height: 16, borderRadius: '50%',
                    background: m.enabled ? '#3FA66B' : '#5C6068',
                    transition: 'left 0.2s',
                  }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function RolePermissions({ icon, role, permissions, color }: {
  icon: React.ReactNode; role: string; permissions: string[]; color: string;
}) {
  return (
    <div style={{
      background: '#15171A', border: `1px solid ${color}20`,
      borderRadius: 12, padding: 20,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
        <div style={{
          width: 40, height: 40, borderRadius: 10,
          background: `${color}12`, border: `1px solid ${color}22`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          {icon}
        </div>
        <div>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#F5F2EA' }}>{role}</div>
          <div style={{ fontSize: 11, color: '#6F756F' }}>{permissions.length} разрешений</div>
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {permissions.map(p => (
          <div key={p} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{
              width: 18, height: 18, borderRadius: '50%',
              background: `${color}15`, border: `1px solid ${color}30`,
              display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
            }}>
              <Check size={10} color={color} strokeWidth={3} />
            </div>
            <span style={{ fontSize: 13, color: '#A9A39A' }}>{p}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

const btnPrimary: React.CSSProperties = {
  display: 'flex', alignItems: 'center', gap: 6, padding: '9px 16px',
  background: 'linear-gradient(135deg, #C9A45C, #A07B3A)',
  color: '#0E0F11', border: 'none', borderRadius: 8, fontSize: 13, fontWeight: 700, cursor: 'pointer',
};

const btnSecondary: React.CSSProperties = {
  display: 'flex', alignItems: 'center', gap: 6, padding: '7px 14px',
  background: '#202328', color: '#A9A39A', border: '1px solid #30343B',
  borderRadius: 8, fontSize: 12, fontWeight: 500, cursor: 'pointer',
};
