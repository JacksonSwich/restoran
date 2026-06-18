import { useState } from 'react';
import { Search, ExternalLink, X } from 'lucide-react';
import { orders, OrderStatus, Role } from '../data/mockData';
import { StatusBadge } from './StatusBadge';

const statusFilters: { id: OrderStatus | 'all'; label: string }[] = [
  { id: 'all', label: 'Все' },
  { id: 'new', label: 'Новый' },
  { id: 'cooking', label: 'Готовится' },
  { id: 'ready', label: 'Готов' },
  { id: 'served', label: 'Подан' },
  { id: 'paid', label: 'Оплачен' },
  { id: 'cancelled', label: 'Отменен' },
];

export function OrdersListScreen({ role, onNavigate }: { role: Role; onNavigate: (s: string) => void }) {
  const [statusFilter, setStatusFilter] = useState<OrderStatus | 'all'>('all');
  const [search, setSearch] = useState('');
  const [selectedOrder, setSelectedOrder] = useState<typeof orders[0] | null>(null);

  const filtered = orders.filter(o => {
    if (statusFilter !== 'all' && o.status !== statusFilter) return false;
    if (search && !`${o.id} ${o.customer} ${o.tableNumber}`.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div style={{ display: 'flex', height: '100%', overflow: 'hidden' }}>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <div style={{ padding: '24px 28px 0', flexShrink: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
            <div>
              <h1 style={{ fontFamily: 'Manrope', fontSize: 24, fontWeight: 800, color: '#F5F2EA', marginBottom: 4 }}>Заказы</h1>
              <p style={{ fontSize: 13, color: '#6F756F' }}>{orders.length} заказов за сегодня</p>
            </div>
          </div>

          {/* Filters */}
          <div style={{ display: 'flex', gap: 6, marginBottom: 16, overflowX: 'auto' }}>
            {statusFilters.map(f => (
              <button
                key={f.id}
                onClick={() => setStatusFilter(f.id)}
                style={{
                  padding: '7px 14px',
                  background: statusFilter === f.id ? 'rgba(201,164,92,0.12)' : '#202328',
                  border: `1px solid ${statusFilter === f.id ? 'rgba(201,164,92,0.35)' : '#30343B'}`,
                  borderRadius: 8, color: statusFilter === f.id ? '#C9A45C' : '#A9A39A',
                  fontSize: 13, fontWeight: statusFilter === f.id ? 600 : 400, cursor: 'pointer', whiteSpace: 'nowrap',
                }}
              >
                {f.label}
              </button>
            ))}
            <div style={{ marginLeft: 'auto', position: 'relative', minWidth: 220 }}>
              <Search size={14} color="#6F756F" style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)' }} />
              <input
                type="text"
                placeholder="Поиск заказа или клиента"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                style={{
                  width: '100%', background: '#202328', border: '1px solid #30343B',
                  borderRadius: 8, padding: '7px 10px 7px 32px', color: '#F5F2EA', fontSize: 13, boxSizing: 'border-box',
                }}
              />
            </div>
          </div>
        </div>

        {/* Table */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '0 28px 24px' }}>
          <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 12, overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: '#1A1D21', borderBottom: '1px solid #30343B' }}>
                  {['№ заказа', 'Столик', 'Клиент', 'Статус', 'Сумма', 'Скидка', 'Итого', 'Создан', 'Действие'].map(col => (
                    <th key={col} style={{
                      padding: '11px 16px', textAlign: 'left', fontSize: 11,
                      color: '#6F756F', fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase', whiteSpace: 'nowrap',
                    }}>
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.map((order, i) => (
                  <tr
                    key={order.id}
                    onClick={() => setSelectedOrder(selectedOrder?.id === order.id ? null : order)}
                    style={{
                      borderTop: '1px solid #30343B22',
                      background: selectedOrder?.id === order.id ? 'rgba(201,164,92,0.06)' : i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)',
                      cursor: 'pointer', transition: 'background 0.1s',
                    }}
                    onMouseEnter={(e) => {
                      if (selectedOrder?.id !== order.id) (e.currentTarget.style.background = 'rgba(255,255,255,0.03)');
                    }}
                    onMouseLeave={(e) => {
                      if (selectedOrder?.id !== order.id) (e.currentTarget.style.background = i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)');
                    }}
                  >
                    <td style={{ padding: '13px 16px', fontSize: 14, fontWeight: 700, color: '#C9A45C' }}>#{order.id}</td>
                    <td style={{ padding: '13px 16px', fontSize: 13, color: '#F5F2EA' }}>Столик №{order.tableNumber}</td>
                    <td style={{ padding: '13px 16px', fontSize: 13, color: '#A9A39A' }}>{order.customer}</td>
                    <td style={{ padding: '13px 16px' }}>
                      <StatusBadge type="order" status={order.status} size="sm" />
                    </td>
                    <td style={{ padding: '13px 16px', fontSize: 13, color: '#A9A39A' }}>{order.total.toLocaleString('ru-RU')} ₽</td>
                    <td style={{ padding: '13px 16px', fontSize: 13, color: order.discount > 0 ? '#3FA66B' : '#6F756F' }}>
                      {order.discount > 0 ? `−${order.discount.toLocaleString('ru-RU')} ₽` : '—'}
                    </td>
                    <td style={{ padding: '13px 16px', fontSize: 14, fontWeight: 700, color: '#F5F2EA' }}>
                      {(order.total - order.discount).toLocaleString('ru-RU')} ₽
                    </td>
                    <td style={{ padding: '13px 16px', fontSize: 12, color: '#6F756F' }}>{order.createdAt}</td>
                    <td style={{ padding: '13px 16px' }}>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button
                          onClick={(e) => { e.stopPropagation(); onNavigate('order-details'); }}
                          style={{
                            display: 'flex', alignItems: 'center', gap: 4, padding: '5px 10px',
                            background: 'rgba(201,164,92,0.1)', border: '1px solid rgba(201,164,92,0.2)',
                            borderRadius: 6, color: '#C9A45C', fontSize: 11, fontWeight: 600, cursor: 'pointer',
                          }}
                        >
                          <ExternalLink size={11} /> Открыть
                        </button>
                        {role === 'waiter' && order.status !== 'paid' && order.status !== 'cancelled' && (
                          <button style={{
                            padding: '5px 10px', background: 'rgba(63,166,107,0.1)',
                            border: '1px solid rgba(63,166,107,0.2)', borderRadius: 6,
                            color: '#3FA66B', fontSize: 11, fontWeight: 600, cursor: 'pointer',
                          }}>
                            Оплатить
                          </button>
                        )}
                        {role === 'admin' && (
                          <button style={{
                            padding: '5px 10px', background: '#252932',
                            border: '1px solid #30343B', borderRadius: 6,
                            color: '#A9A39A', fontSize: 11, cursor: 'pointer',
                          }}>
                            Отчет
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filtered.length === 0 && (
              <div style={{ padding: 48, textAlign: 'center', color: '#6F756F', fontSize: 14 }}>
                Нет заказов по выбранным фильтрам
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Preview panel */}
      {selectedOrder && (
        <div style={{
          width: 300, flexShrink: 0, background: '#15171A', borderLeft: '1px solid #30343B',
          display: 'flex', flexDirection: 'column', overflowY: 'auto',
        }}>
          <div style={{ padding: '18px 20px', borderBottom: '1px solid #30343B', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <h3 style={{ fontSize: 15, fontWeight: 700, color: '#F5F2EA' }}>Заказ #{selectedOrder.id}</h3>
            <button onClick={() => setSelectedOrder(null)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#6F756F' }}>
              <X size={16} />
            </button>
          </div>
          <div style={{ padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <StatusBadge type="order" status={selectedOrder.status} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {[
                ['Столик', `№${selectedOrder.tableNumber}`],
                ['Клиент', selectedOrder.customer],
                ['Создан', selectedOrder.createdAt],
              ].map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: 12, color: '#6F756F' }}>{k}</span>
                  <span style={{ fontSize: 13, color: '#A9A39A' }}>{v}</span>
                </div>
              ))}
            </div>

            <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 10, padding: '12px 14px' }}>
              <div style={{ fontSize: 11, color: '#6F756F', marginBottom: 8, letterSpacing: '0.05em', textTransform: 'uppercase' }}>Состав</div>
              {selectedOrder.items.map((item, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <span style={{ fontSize: 12, color: '#A9A39A' }}>{item.dishName} ×{item.quantity}</span>
                  <span style={{ fontSize: 12, fontWeight: 600, color: '#F5F2EA' }}>{(item.price * item.quantity).toLocaleString('ru-RU')} ₽</span>
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, paddingTop: 4 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, color: '#A9A39A' }}>
                <span>Сумма</span>
                <span>{selectedOrder.total.toLocaleString('ru-RU')} ₽</span>
              </div>
              {selectedOrder.discount > 0 && (
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, color: '#3FA66B' }}>
                  <span>Скидка</span>
                  <span>−{selectedOrder.discount.toLocaleString('ru-RU')} ₽</span>
                </div>
              )}
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 16, fontWeight: 800, color: '#C9A45C', paddingTop: 6, borderTop: '1px solid #30343B' }}>
                <span>Итого</span>
                <span>{(selectedOrder.total - selectedOrder.discount).toLocaleString('ru-RU')} ₽</span>
              </div>
            </div>

            <button
              onClick={() => onNavigate('order-details')}
              style={{
                padding: '11px', background: 'linear-gradient(135deg, #C9A45C, #A07B3A)',
                color: '#0E0F11', border: 'none', borderRadius: 8, fontSize: 13, fontWeight: 700, cursor: 'pointer',
              }}
            >
              Открыть полный заказ
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
