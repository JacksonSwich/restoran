import { TrendingUp, ShoppingBag, Receipt, Star } from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { revenueData, popularDishes, ordersByStatus, revenueByPayment } from '../data/mockData';

function StatCard({ icon, label, value, sub, color }: { icon: React.ReactNode; label: string; value: string; sub?: string; color?: string }) {
  return (
    <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 12, padding: '20px 22px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14 }}>
        <div style={{
          width: 38, height: 38, borderRadius: 10, background: `${color || '#C9A45C'}12`,
          border: `1px solid ${color || '#C9A45C'}22`,
          display: 'flex', alignItems: 'center', justifyContent: 'center', color: color || '#C9A45C',
        }}>
          {icon}
        </div>
      </div>
      <div style={{ fontSize: 26, fontFamily: 'Manrope', fontWeight: 800, color: '#F5F2EA', lineHeight: 1 }}>{value}</div>
      <div style={{ fontSize: 12, color: '#A9A39A', marginTop: 4 }}>{label}</div>
      {sub && <div style={{ fontSize: 11, color: '#3FA66B', marginTop: 3 }}>{sub}</div>}
    </div>
  );
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload?.length) {
    return (
      <div style={{ background: '#252932', border: '1px solid #30343B', borderRadius: 8, padding: '10px 14px' }}>
        <p style={{ color: '#A9A39A', fontSize: 12, marginBottom: 4 }}>{label}</p>
        <p style={{ color: '#C9A45C', fontWeight: 700, fontSize: 14 }}>
          {Number(payload[0].value).toLocaleString('ru-RU')} ₽
        </p>
      </div>
    );
  }
  return null;
};

export function ReportsScreen() {
  return (
    <div style={{ padding: 28, display: 'flex', flexDirection: 'column', gap: 24, overflowY: 'auto', height: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontFamily: 'Manrope', fontSize: 24, fontWeight: 800, color: '#F5F2EA', marginBottom: 4 }}>Отчеты</h1>
          <p style={{ fontSize: 13, color: '#6F756F' }}>Аналитика · 18 июня 2026</p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {['Сегодня', 'Неделя', 'Месяц'].map((p, i) => (
            <button key={p} style={{
              padding: '7px 14px', background: i === 1 ? 'rgba(201,164,92,0.12)' : '#202328',
              border: `1px solid ${i === 1 ? 'rgba(201,164,92,0.35)' : '#30343B'}`,
              borderRadius: 8, color: i === 1 ? '#C9A45C' : '#A9A39A', fontSize: 13, cursor: 'pointer',
            }}>{p}</button>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 14 }}>
        <StatCard icon={<TrendingUp size={17} />} label="Выручка за день" value="127 400 ₽" sub="+14%" color="#C9A45C" />
        <StatCard icon={<TrendingUp size={17} />} label="Выручка за неделю" value="427 100 ₽" sub="+8%" color="#C9A45C" />
        <StatCard icon={<ShoppingBag size={17} />} label="Количество заказов" value="84" color="#4A7BD0" />
        <StatCard icon={<Receipt size={17} />} label="Средний чек" value="1 517 ₽" sub="+5%" color="#D98A35" />
        <StatCard icon={<Star size={17} />} label="Топ блюдо" value="Стейк" sub="124 заказа" color="#9B6CDD" />
        <StatCard icon={<ShoppingBag size={17} />} label="Оплаченных" value="78" sub="из 84" color="#3FA66B" />
      </div>

      {/* Charts row 1 */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        {/* Revenue by day */}
        <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 12, padding: 24 }}>
          <h3 style={{ color: '#F5F2EA', fontSize: 15, fontWeight: 600, marginBottom: 4 }}>Продажи по дням</h3>
          <p style={{ fontSize: 12, color: '#6F756F', marginBottom: 20 }}>Выручка за текущую неделю</p>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={revenueData}>
              <defs>
                <linearGradient id="rev" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#C9A45C" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#C9A45C" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: '#6F756F', fontSize: 12 }} />
              <YAxis hide />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="revenue" stroke="#C9A45C" strokeWidth={2} fill="url(#rev)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Orders by status */}
        <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 12, padding: 24 }}>
          <h3 style={{ color: '#F5F2EA', fontSize: 15, fontWeight: 600, marginBottom: 4 }}>Заказы по статусу</h3>
          <p style={{ fontSize: 12, color: '#6F756F', marginBottom: 20 }}>Распределение за неделю</p>
          <div style={{ display: 'flex', gap: 20, alignItems: 'center' }}>
            <ResponsiveContainer width="60%" height={180}>
              <PieChart>
                <Pie
                  data={ordersByStatus}
                  dataKey="count"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={3}
                >
                  {ordersByStatus.map((s, i) => (
                    <Cell key={i} fill={s.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {ordersByStatus.map(s => (
                <div key={s.status} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{ width: 8, height: 8, borderRadius: '50%', background: s.color, flexShrink: 0 }} />
                  <span style={{ fontSize: 12, color: '#A9A39A', flex: 1 }}>{s.status}</span>
                  <span style={{ fontSize: 12, fontWeight: 700, color: '#F5F2EA' }}>{s.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Charts row 2 */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 20 }}>
        {/* Popular dishes */}
        <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 12, padding: 24 }}>
          <h3 style={{ color: '#F5F2EA', fontSize: 15, fontWeight: 600, marginBottom: 4 }}>Популярные блюда</h3>
          <p style={{ fontSize: 12, color: '#6F756F', marginBottom: 20 }}>Топ по количеству заказов</p>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={popularDishes} layout="vertical">
              <XAxis type="number" hide />
              <YAxis type="category" dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#A9A39A', fontSize: 12 }} width={140} />
              <Tooltip
                contentStyle={{ background: '#252932', border: '1px solid #30343B', borderRadius: 8 }}
                labelStyle={{ color: '#A9A39A' }}
                itemStyle={{ color: '#C9A45C' }}
                formatter={(v: any) => [`${v} заказов`]}
              />
              <Bar dataKey="orders" fill="#C9A45C" radius={[0, 4, 4, 0]} opacity={0.85} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Revenue by payment */}
        <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 12, padding: 24 }}>
          <h3 style={{ color: '#F5F2EA', fontSize: 15, fontWeight: 600, marginBottom: 4 }}>Выручка по оплате</h3>
          <p style={{ fontSize: 12, color: '#6F756F', marginBottom: 20 }}>По способам оплаты</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {revenueByPayment.map((r, i) => (
              <div key={r.method}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <span style={{ fontSize: 13, color: '#F5F2EA' }}>{r.method}</span>
                  <span style={{ fontSize: 13, fontWeight: 700, color: '#C9A45C' }}>{r.amount.toLocaleString('ru-RU')} ₽</span>
                </div>
                <div style={{ height: 6, background: '#30343B', borderRadius: 3 }}>
                  <div style={{
                    height: '100%', borderRadius: 3,
                    background: i === 0 ? '#C9A45C' : i === 1 ? '#3FA66B' : '#4A7BD0',
                    width: `${r.pct}%`,
                  }} />
                </div>
                <div style={{ fontSize: 11, color: '#6F756F', marginTop: 4 }}>{r.pct}% от выручки</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Revenue by day table */}
      <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 12, overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #30343B' }}>
          <h3 style={{ color: '#F5F2EA', fontSize: 15, fontWeight: 600 }}>Выручка по дням</h3>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#1A1D21' }}>
              {['День', 'Заказов', 'Выручка', 'Средний чек'].map(col => (
                <th key={col} style={{ padding: '10px 16px', textAlign: 'left', fontSize: 11, color: '#6F756F', fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase' }}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {revenueData.map((d, i) => (
              <tr key={d.day} style={{ borderTop: '1px solid #30343B22', background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)' }}>
                <td style={{ padding: '12px 16px', fontSize: 13, color: '#F5F2EA', fontWeight: 500 }}>{d.day}</td>
                <td style={{ padding: '12px 16px', fontSize: 13, color: '#A9A39A' }}>{d.orders}</td>
                <td style={{ padding: '12px 16px', fontSize: 14, fontWeight: 700, color: '#C9A45C' }}>{d.revenue.toLocaleString('ru-RU')} ₽</td>
                <td style={{ padding: '12px 16px', fontSize: 13, color: '#A9A39A' }}>{Math.round(d.revenue / d.orders).toLocaleString('ru-RU')} ₽</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
