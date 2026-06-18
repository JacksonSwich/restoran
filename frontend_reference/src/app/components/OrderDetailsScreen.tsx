import { ArrowLeft, CheckCircle, Circle, Clock } from 'lucide-react';
import { orders, Role } from '../data/mockData';
import { StatusBadge } from './StatusBadge';

const statusTimeline = [
  { key: 'new', label: 'Новый' },
  { key: 'cooking', label: 'Готовится' },
  { key: 'ready', label: 'Готов' },
  { key: 'served', label: 'Подан' },
  { key: 'paid', label: 'Оплачен' },
];

const statusOrder = ['new', 'cooking', 'ready', 'served', 'paid'];

export function OrderDetailsScreen({ role, onNavigate }: { role: Role; onNavigate: (s: string) => void }) {
  const order = orders[0]; // Show order #12 as detail view

  const currentStatusIdx = statusOrder.indexOf(order.status);

  return (
    <div style={{ padding: 28, display: 'flex', flexDirection: 'column', gap: 20, overflowY: 'auto', height: '100%' }}>
      {/* Back + header */}
      <div>
        <button
          onClick={() => onNavigate('orders')}
          style={{
            display: 'flex', alignItems: 'center', gap: 6, background: 'none', border: 'none',
            color: '#A9A39A', fontSize: 13, cursor: 'pointer', marginBottom: 16, padding: 0,
          }}
        >
          <ArrowLeft size={16} /> Назад к заказам
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 4 }}>
              <h1 style={{ fontFamily: 'Manrope', fontSize: 26, fontWeight: 800, color: '#F5F2EA' }}>
                Заказ #{order.id}
              </h1>
              <StatusBadge type="order" status={order.status} />
            </div>
            <p style={{ fontSize: 13, color: '#A9A39A' }}>
              Столик №{order.tableNumber} · {order.customer} · Создан: {order.createdAt}
            </p>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 20 }}>
        {/* Main */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* Items table */}
          <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 12, overflow: 'hidden' }}>
            <div style={{ padding: '16px 20px', borderBottom: '1px solid #30343B' }}>
              <h3 style={{ fontSize: 14, fontWeight: 600, color: '#F5F2EA' }}>Состав заказа</h3>
            </div>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: '#1A1D21' }}>
                  {['Блюдо', 'Кол-во', 'Цена', 'Сумма', 'Комментарий'].map(col => (
                    <th key={col} style={{
                      padding: '10px 16px', textAlign: 'left', fontSize: 11,
                      color: '#6F756F', fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase',
                    }}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {order.items.map((item, i) => (
                  <tr key={i} style={{ borderTop: '1px solid #30343B22' }}>
                    <td style={{ padding: '14px 16px', fontSize: 14, fontWeight: 500, color: '#F5F2EA' }}>{item.dishName}</td>
                    <td style={{ padding: '14px 16px', fontSize: 14, color: '#A9A39A', textAlign: 'center' }}>{item.quantity}</td>
                    <td style={{ padding: '14px 16px', fontSize: 13, color: '#A9A39A' }}>{item.price.toLocaleString('ru-RU')} ₽</td>
                    <td style={{ padding: '14px 16px', fontSize: 14, fontWeight: 700, color: '#C9A45C' }}>
                      {(item.price * item.quantity).toLocaleString('ru-RU')} ₽
                    </td>
                    <td style={{ padding: '14px 16px', fontSize: 12, color: '#6F756F', fontStyle: 'italic' }}>
                      {item.comment || '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Total */}
          <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 12, padding: '20px 24px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 14, color: '#A9A39A' }}>
                <span>Сумма</span>
                <span>{order.total.toLocaleString('ru-RU')} ₽</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 14, color: '#3FA66B' }}>
                <span>Скидка (5%)</span>
                <span>−{order.discount.toLocaleString('ru-RU')} ₽</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 18, fontWeight: 800, fontFamily: 'Manrope', color: '#F5F2EA', paddingTop: 8, borderTop: '1px solid #30343B' }}>
                <span>Итого</span>
                <span style={{ color: '#C9A45C' }}>{(order.total - order.discount).toLocaleString('ru-RU')} ₽</span>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            {role === 'waiter' ? (
              <>
                <button style={btnPrimary}>Добавить блюдо</button>
                <button style={btnSecondary}>Изменить статус</button>
                <button style={{ ...btnSecondary, color: '#3FA66B', borderColor: 'rgba(63,166,107,0.3)' }}>
                  Перейти к оплате
                </button>
                <button style={btnDanger}>Отменить заказ</button>
              </>
            ) : (
              <>
                <button style={btnSecondary}>Редактировать заказ</button>
                <button style={btnSecondary}>Просмотреть оплату</button>
                <button style={btnSecondary}>История изменений</button>
                <button style={btnDanger}>Отменить заказ</button>
              </>
            )}
          </div>
        </div>

        {/* Right panel: timeline */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 12, padding: '20px' }}>
            <h3 style={{ fontSize: 14, fontWeight: 600, color: '#F5F2EA', marginBottom: 20 }}>Статус заказа</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
              {statusTimeline.map((s, i) => {
                const done = i <= currentStatusIdx;
                const current = i === currentStatusIdx;
                const isLast = i === statusTimeline.length - 1;
                return (
                  <div key={s.key} style={{ display: 'flex', gap: 14 }}>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                      <div style={{
                        width: 28, height: 28, borderRadius: '50%',
                        background: done ? (current ? 'rgba(201,164,92,0.15)' : 'rgba(63,166,107,0.1)') : '#252932',
                        border: `2px solid ${done ? (current ? '#C9A45C' : '#3FA66B') : '#30343B'}`,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        flexShrink: 0,
                      }}>
                        {done ? (
                          current ? <Clock size={12} color="#C9A45C" /> : <CheckCircle size={12} color="#3FA66B" />
                        ) : (
                          <Circle size={12} color="#30343B" />
                        )}
                      </div>
                      {!isLast && (
                        <div style={{
                          width: 2, height: 28,
                          background: done && i < currentStatusIdx ? '#3FA66B44' : '#30343B',
                          margin: '2px 0',
                        }} />
                      )}
                    </div>
                    <div style={{ paddingBottom: isLast ? 0 : 14, paddingTop: 4 }}>
                      <div style={{
                        fontSize: 13, fontWeight: current ? 700 : 500,
                        color: current ? '#C9A45C' : done ? '#F5F2EA' : '#6F756F',
                      }}>
                        {s.label}
                      </div>
                      {current && (
                        <div style={{ fontSize: 11, color: '#6F756F', marginTop: 2 }}>{order.createdAt}</div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Info card */}
          <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 12, padding: '18px 20px' }}>
            <h3 style={{ fontSize: 14, fontWeight: 600, color: '#F5F2EA', marginBottom: 14 }}>Информация</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {[
                ['Клиент', order.customer],
                ['Столик', `№${order.tableNumber}`],
                ['Создан', order.createdAt],
                ['Позиций', `${order.items.reduce((s, i) => s + i.quantity, 0)} блюд`],
              ].map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 12, color: '#6F756F' }}>{k}</span>
                  <span style={{ fontSize: 13, fontWeight: 500, color: '#A9A39A' }}>{v}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
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
  display: 'flex', alignItems: 'center', gap: 6, padding: '10px 18px',
  background: '#252932', color: '#A9A39A', border: '1px solid #30343B',
  borderRadius: 8, fontSize: 13, fontWeight: 500, cursor: 'pointer',
};

const btnDanger: React.CSSProperties = {
  display: 'flex', alignItems: 'center', gap: 6, padding: '10px 18px',
  background: 'rgba(201,76,76,0.08)', color: '#C94C4C',
  border: '1px solid rgba(201,76,76,0.25)', borderRadius: 8, fontSize: 13, fontWeight: 600, cursor: 'pointer',
};
