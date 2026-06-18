import { useState } from 'react';
import { Search, Plus, Edit3, ClipboardList, UserPlus } from 'lucide-react';
import { customers, Role } from '../data/mockData';

export function CustomersScreen({ role }: { role: Role }) {
  const [search, setSearch] = useState('');

  const filtered = customers.filter(c =>
    !search || `${c.name} ${c.phone} ${c.email}`.toLowerCase().includes(search.toLowerCase())
  );

  if (role === 'waiter') {
    return (
      <div style={{ padding: 28, display: 'flex', flexDirection: 'column', gap: 20, overflowY: 'auto', height: '100%' }}>
        <div>
          <h1 style={{ fontFamily: 'Manrope', fontSize: 24, fontWeight: 800, color: '#F5F2EA', marginBottom: 4 }}>Клиенты</h1>
          <p style={{ fontSize: 13, color: '#6F756F' }}>Поиск и выбор клиента</p>
        </div>

        <div style={{ maxWidth: 480 }}>
          <div style={{ position: 'relative', marginBottom: 16 }}>
            <Search size={16} color="#6F756F" style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              placeholder="Найти клиента по имени или телефону"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                width: '100%', background: '#202328', border: '1px solid #30343B',
                borderRadius: 8, padding: '12px 12px 12px 40px', color: '#F5F2EA', fontSize: 14, boxSizing: 'border-box',
              }}
            />
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            <button style={btnPrimary}><UserPlus size={14} /> Создать клиента</button>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {filtered.slice(0, 8).map(c => (
            <div key={c.id} style={{
              background: '#202328', border: '1px solid #30343B', borderRadius: 12,
              padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              cursor: 'pointer',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                <div style={{
                  width: 40, height: 40, borderRadius: '50%', background: '#252932',
                  border: '2px solid #30343B', display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 14, fontWeight: 700, color: '#C9A45C',
                }}>
                  {c.name.charAt(0)}
                </div>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 600, color: '#F5F2EA' }}>{c.name}</div>
                  <div style={{ fontSize: 12, color: '#A9A39A' }}>{c.phone}</div>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                {c.discount > 0 && (
                  <span style={{
                    padding: '3px 10px', background: 'rgba(201,164,92,0.1)',
                    border: '1px solid rgba(201,164,92,0.2)', borderRadius: 20,
                    fontSize: 12, fontWeight: 600, color: '#C9A45C',
                  }}>
                    −{c.discount}%
                  </span>
                )}
                <button style={btnSecondary}>Выбрать клиента</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: 28, display: 'flex', flexDirection: 'column', gap: 20, overflowY: 'auto', height: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontFamily: 'Manrope', fontSize: 24, fontWeight: 800, color: '#F5F2EA', marginBottom: 4 }}>Клиенты</h1>
          <p style={{ fontSize: 13, color: '#6F756F' }}>{customers.length} клиентов в базе</p>
        </div>
        <button style={btnPrimary}><Plus size={14} /> Добавить клиента</button>
      </div>

      {/* Search */}
      <div style={{ position: 'relative', maxWidth: 400 }}>
        <Search size={14} color="#6F756F" style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)' }} />
        <input
          type="text"
          placeholder="Поиск по имени, телефону или email"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            width: '100%', background: '#202328', border: '1px solid #30343B',
            borderRadius: 8, padding: '9px 12px 9px 36px', color: '#F5F2EA', fontSize: 13, boxSizing: 'border-box',
          }}
        />
      </div>

      {/* Table */}
      <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 12, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#1A1D21', borderBottom: '1px solid #30343B' }}>
              {['Имя', 'Телефон', 'Email', 'Скидка', 'Кол-во заказов', 'Общая сумма', 'Последний заказ', ''].map(col => (
                <th key={col} style={{
                  padding: '11px 16px', textAlign: 'left', fontSize: 11,
                  color: '#6F756F', fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase',
                }}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((c, i) => (
              <tr
                key={c.id}
                style={{
                  borderTop: '1px solid #30343B22',
                  background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)',
                }}
                onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(201,164,92,0.03)')}
                onMouseLeave={(e) => (e.currentTarget.style.background = i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)')}
              >
                <td style={{ padding: '13px 16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{
                      width: 32, height: 32, borderRadius: '50%', background: '#252932',
                      border: '2px solid #30343B', display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: 12, fontWeight: 700, color: '#C9A45C', flexShrink: 0,
                    }}>
                      {c.name.charAt(0)}
                    </div>
                    <span style={{ fontSize: 13, fontWeight: 600, color: '#F5F2EA' }}>{c.name}</span>
                  </div>
                </td>
                <td style={{ padding: '13px 16px', fontSize: 13, color: '#A9A39A' }}>{c.phone}</td>
                <td style={{ padding: '13px 16px', fontSize: 13, color: '#A9A39A' }}>{c.email}</td>
                <td style={{ padding: '13px 16px' }}>
                  {c.discount > 0 ? (
                    <span style={{
                      padding: '3px 10px', background: 'rgba(201,164,92,0.1)',
                      border: '1px solid rgba(201,164,92,0.2)', borderRadius: 20,
                      fontSize: 12, fontWeight: 700, color: '#C9A45C',
                    }}>
                      {c.discount}%
                    </span>
                  ) : <span style={{ color: '#6F756F' }}>—</span>}
                </td>
                <td style={{ padding: '13px 16px', fontSize: 14, fontWeight: 700, color: '#F5F2EA', textAlign: 'center' }}>
                  {c.ordersCount}
                </td>
                <td style={{ padding: '13px 16px', fontSize: 13, fontWeight: 600, color: '#C9A45C' }}>
                  {c.totalAmount.toLocaleString('ru-RU')} ₽
                </td>
                <td style={{ padding: '13px 16px', fontSize: 12, color: '#6F756F' }}>{c.lastOrder}</td>
                <td style={{ padding: '13px 16px' }}>
                  <div style={{ display: 'flex', gap: 6 }}>
                    <button style={{ ...iconBtn }}><Edit3 size={13} /></button>
                    <button style={{ ...iconBtn }}><ClipboardList size={13} /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const btnPrimary: React.CSSProperties = {
  display: 'flex', alignItems: 'center', gap: 6, padding: '10px 18px',
  background: 'linear-gradient(135deg, #C9A45C, #A07B3A)',
  color: '#0E0F11', border: 'none', borderRadius: 8, fontSize: 13, fontWeight: 700, cursor: 'pointer',
};

const btnSecondary: React.CSSProperties = {
  display: 'flex', alignItems: 'center', gap: 6, padding: '8px 14px',
  background: '#252932', color: '#A9A39A', border: '1px solid #30343B',
  borderRadius: 8, fontSize: 12, fontWeight: 500, cursor: 'pointer',
};

const iconBtn: React.CSSProperties = {
  width: 30, height: 30, borderRadius: 7, background: '#252932',
  border: '1px solid #30343B', display: 'flex', alignItems: 'center', justifyContent: 'center',
  cursor: 'pointer', color: '#A9A39A',
};
