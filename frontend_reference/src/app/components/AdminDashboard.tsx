import { TrendingUp, ShoppingBag, Receipt, Clock, Table2, CheckCircle, ArrowUpRight } from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from 'recharts';
import { orders, revenueData, popularDishes, tables } from '../data/mockData';
import { StatusBadge } from './StatusBadge';

function StatCard({ icon, label, value, sub, color }: {
  icon: React.ReactNode; label: string; value: string; sub?: string; color?: string;
}) {
  return (
    <div
      style={{
        background: '#202328',
        border: '1px solid #30343B',
        borderRadius: 12,
        padding: '20px 20px',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          position: 'absolute',
          top: 0,
          right: 0,
          width: 80,
          height: 80,
          background: `radial-gradient(circle, ${color || '#C9A45C'}08, transparent)`,
        }}
      />
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 12 }}>
        <div
          style={{
            width: 38,
            height: 38,
            borderRadius: 10,
            background: `${color || '#C9A45C'}12`,
            border: `1px solid ${color || '#C9A45C'}22`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: color || '#C9A45C',
          }}
        >
          {icon}
        </div>
        <ArrowUpRight size={14} color="#3FA66B" />
      </div>
      <div style={{ fontSize: 26, fontFamily: 'Manrope', fontWeight: 800, color: '#F5F2EA', lineHeight: 1 }}>
        {value}
      </div>
      <div style={{ fontSize: 12, color: '#A9A39A', marginTop: 4 }}>{label}</div>
      {sub && <div style={{ fontSize: 11, color: '#6F756F', marginTop: 2 }}>{sub}</div>}
    </div>
  );
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload?.length) {
    return (
      <div style={{
        background: '#252932', border: '1px solid #30343B', borderRadius: 8, padding: '10px 14px',
      }}>
        <p style={{ color: '#A9A39A', fontSize: 12, marginBottom: 4 }}>{label}</p>
        <p style={{ color: '#C9A45C', fontWeight: 700, fontSize: 14 }}>
          {Number(payload[0].value).toLocaleString('ru-RU')} ₽
        </p>
      </div>
    );
  }
  return null;
};

export function AdminDashboard({ onNavigate }: { onNavigate: (s: string) => void }) {
  const activeOrders = orders.filter(o => ['new', 'cooking', 'ready', 'served'].includes(o.status));
  const paidOrders = orders.filter(o => o.status === 'paid');
  const occupiedTables = tables.filter(t => t.status === 'occupied');

  return (
    <div style={{ padding: '28px', display: 'flex', flexDirection: 'column', gap: 24, overflowY: 'auto', height: '100%' }}>
      <div>
        <h1 style={{ fontFamily: 'Manrope', fontSize: 24, fontWeight: 800, color: '#F5F2EA', marginBottom: 4 }}>
          Главная
        </h1>
        <p style={{ fontSize: 13, color: '#6F756F' }}>Операционная сводка · 18 июня 2026</p>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 16 }}>
        <StatCard icon={<TrendingUp size={18} />} label="Выручка за день" value="127 400 ₽" sub="+14% к вчера" color="#C9A45C" />
        <StatCard icon={<ShoppingBag size={18} />} label="Количество заказов" value="84" sub="сегодня" color="#4A7BD0" />
        <StatCard icon={<Receipt size={18} />} label="Средний чек" value="1 517 ₽" sub="+5% к вчера" color="#D98A35" />
        <StatCard icon={<Clock size={18} />} label="Активные заказы" value={String(activeOrders.length)} color="#9B6CDD" />
        <StatCard icon={<Table2 size={18} />} label="Занятые столики" value={`${occupiedTables.length}/${tables.length}`} color="#D98A35" />
        <StatCard icon={<CheckCircle size={18} />} label="Оплаченные заказы" value={String(paidOrders.length)} sub="сегодня" color="#3FA66B" />
      </div>

      {/* Charts row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 20 }}>
        {/* Revenue chart */}
        <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 12, padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
            <div>
              <h3 style={{ color: '#F5F2EA', fontSize: 15, fontWeight: 600, marginBottom: 2 }}>Выручка по дням</h3>
              <p style={{ fontSize: 12, color: '#6F756F' }}>Последние 7 дней</p>
            </div>
            <div style={{ fontSize: 11, color: '#C9A45C', fontWeight: 600 }}>↑ 14% к прошлой неделе</div>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={revenueData} margin={{ top: 5, right: 5, bottom: 0, left: 0 }}>
              <defs>
                <linearGradient id="goldGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#C9A45C" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#C9A45C" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: '#6F756F', fontSize: 12 }} />
              <YAxis hide />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="revenue" stroke="#C9A45C" strokeWidth={2} fill="url(#goldGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Popular dishes */}
        <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 12, padding: 24 }}>
          <h3 style={{ color: '#F5F2EA', fontSize: 15, fontWeight: 600, marginBottom: 4 }}>Популярные блюда</h3>
          <p style={{ fontSize: 12, color: '#6F756F', marginBottom: 20 }}>По количеству заказов</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {popularDishes.map((d, i) => (
              <div key={d.name}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <span style={{ fontSize: 13, color: '#F5F2EA', fontWeight: 500 }}>{d.name}</span>
                  <span style={{ fontSize: 13, color: '#C9A45C', fontWeight: 600 }}>{d.orders}</span>
                </div>
                <div style={{ height: 4, background: '#30343B', borderRadius: 2 }}>
                  <div
                    style={{
                      height: '100%',
                      borderRadius: 2,
                      background: i === 0 ? '#C9A45C' : i === 1 ? '#D98A35' : '#A9A39A',
                      width: `${(d.orders / 124) * 100}%`,
                      transition: 'width 0.5s ease',
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent orders table */}
      <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 12, overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '20px 24px', borderBottom: '1px solid #30343B' }}>
          <div>
            <h3 style={{ color: '#F5F2EA', fontSize: 15, fontWeight: 600, marginBottom: 2 }}>Последние заказы</h3>
            <p style={{ fontSize: 12, color: '#6F756F' }}>Текущие и недавние заказы</p>
          </div>
          <button
            onClick={() => onNavigate('orders')}
            style={{
              padding: '7px 14px', background: 'transparent', border: '1px solid #30343B', borderRadius: 8,
              color: '#A9A39A', fontSize: 12, cursor: 'pointer',
            }}
          >
            Все заказы →
          </button>
        </div>

        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#1A1D21' }}>
              {['№ заказа', 'Столик', 'Клиент', 'Статус', 'Сумма', 'Оплата', 'Создан'].map(col => (
                <th key={col} style={{
                  padding: '10px 16px', textAlign: 'left', fontSize: 11,
                  color: '#6F756F', fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase',
                }}>
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {orders.map((order, i) => (
              <tr
                key={order.id}
                style={{
                  borderTop: '1px solid #30343B22',
                  background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)',
                  cursor: 'pointer',
                  transition: 'background 0.1s',
                }}
                onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(201,164,92,0.04)')}
                onMouseLeave={(e) => (e.currentTarget.style.background = i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)')}
              >
                <td style={{ padding: '12px 16px', fontSize: 13, color: '#C9A45C', fontWeight: 600 }}>#{order.id}</td>
                <td style={{ padding: '12px 16px', fontSize: 13, color: '#F5F2EA' }}>Столик №{order.tableNumber}</td>
                <td style={{ padding: '12px 16px', fontSize: 13, color: '#A9A39A' }}>{order.customer}</td>
                <td style={{ padding: '12px 16px' }}>
                  <StatusBadge type="order" status={order.status} size="sm" />
                </td>
                <td style={{ padding: '12px 16px', fontSize: 13, color: '#F5F2EA', fontWeight: 600 }}>
                  {order.total.toLocaleString('ru-RU')} ₽
                </td>
                <td style={{ padding: '12px 16px', fontSize: 12, color: '#A9A39A' }}>
                  {order.paymentMethod === 'cash' ? 'Наличные' : order.paymentMethod === 'card' ? 'Карта' : order.paymentMethod === 'online' ? 'Онлайн' : '—'}
                </td>
                <td style={{ padding: '12px 16px', fontSize: 12, color: '#6F756F' }}>{order.createdAt}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
