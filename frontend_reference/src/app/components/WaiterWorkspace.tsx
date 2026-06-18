import { Clock, ExternalLink, Plus, CheckCircle2, Table2, Loader2 } from 'lucide-react';
import { orders, tables } from '../data/mockData';
import { StatusBadge } from './StatusBadge';

export function WaiterWorkspace({ onNavigate }: { onNavigate: (s: string) => void }) {
  const freeTables = tables.filter(t => t.status === 'free');
  const occupiedTables = tables.filter(t => t.status === 'occupied');
  const readyOrders = orders.filter(o => o.status === 'ready');
  const activeOrders = orders.filter(o => ['new', 'cooking'].includes(o.status));

  const SummaryCard = ({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: string | number; color: string }) => (
    <div style={{
      background: '#202328', border: '1px solid #30343B', borderRadius: 12, padding: '20px 22px',
      display: 'flex', alignItems: 'center', gap: 16,
    }}>
      <div style={{
        width: 48, height: 48, borderRadius: 12,
        background: `${color}12`, border: `1px solid ${color}22`,
        display: 'flex', alignItems: 'center', justifyContent: 'center', color, flexShrink: 0,
      }}>
        {icon}
      </div>
      <div>
        <div style={{ fontSize: 28, fontFamily: 'Manrope', fontWeight: 800, color: '#F5F2EA', lineHeight: 1 }}>{value}</div>
        <div style={{ fontSize: 12, color: '#A9A39A', marginTop: 4 }}>{label}</div>
      </div>
    </div>
  );

  return (
    <div style={{ padding: 28, display: 'flex', flexDirection: 'column', gap: 24, overflowY: 'auto', height: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontFamily: 'Manrope', fontSize: 24, fontWeight: 800, color: '#F5F2EA', marginBottom: 4 }}>
            Рабочее место
          </h1>
          <p style={{ fontSize: 13, color: '#6F756F' }}>Добрый вечер · 18 июня 2026</p>
        </div>
        <button
          onClick={() => onNavigate('new-order')}
          style={{
            display: 'flex', alignItems: 'center', gap: 8, padding: '12px 22px',
            background: 'linear-gradient(135deg, #C9A45C, #A07B3A)', color: '#0E0F11',
            border: 'none', borderRadius: 10, fontSize: 14, fontWeight: 700, cursor: 'pointer',
          }}
        >
          <Plus size={16} />
          Создать заказ
        </button>
      </div>

      {/* Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
        <SummaryCard icon={<Table2 size={22} />} label="Свободные столики" value={freeTables.length} color="#3FA66B" />
        <SummaryCard icon={<Table2 size={22} />} label="Занятые столики" value={occupiedTables.length} color="#D98A35" />
        <SummaryCard icon={<CheckCircle2 size={22} />} label="Готовые заказы" value={readyOrders.length} color="#C9A45C" />
        <SummaryCard icon={<Loader2 size={22} />} label="Заказы в работе" value={activeOrders.length} color="#4A7BD0" />
      </div>

      {/* Ready orders */}
      {readyOrders.length > 0 && (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
            <h2 style={{ fontSize: 16, fontWeight: 700, color: '#F5F2EA' }}>Готовы к подаче</h2>
            <span style={{
              padding: '2px 8px', background: 'rgba(63,166,107,0.15)', borderRadius: 20,
              fontSize: 12, fontWeight: 700, color: '#3FA66B',
            }}>
              {readyOrders.length}
            </span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
            {readyOrders.map(order => (
              <OrderCard key={order.id} order={order} highlight onOpen={() => onNavigate('order-details')} />
            ))}
          </div>
        </div>
      )}

      {/* Active orders */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
          <h2 style={{ fontSize: 16, fontWeight: 700, color: '#F5F2EA' }}>Активные заказы</h2>
          <span style={{
            padding: '2px 8px', background: 'rgba(74,123,208,0.15)', borderRadius: 20,
            fontSize: 12, fontWeight: 700, color: '#4A7BD0',
          }}>
            {activeOrders.length}
          </span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
          {activeOrders.map(order => (
            <OrderCard key={order.id} order={order} onOpen={() => onNavigate('order-details')} />
          ))}
          {activeOrders.length === 0 && (
            <div style={{
              gridColumn: '1/-1', padding: '48px', textAlign: 'center',
              color: '#6F756F', fontSize: 14,
              background: '#202328', border: '1px dashed #30343B', borderRadius: 12,
            }}>
              Нет активных заказов
            </div>
          )}
        </div>
      </div>

      {/* Tables quick view */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
          <h2 style={{ fontSize: 16, fontWeight: 700, color: '#F5F2EA' }}>Мои столики</h2>
          <button
            onClick={() => onNavigate('tables')}
            style={{
              background: 'transparent', border: '1px solid #30343B', borderRadius: 8,
              padding: '6px 14px', color: '#A9A39A', fontSize: 12, cursor: 'pointer',
            }}
          >
            Все столики →
          </button>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 12 }}>
          {tables.slice(0, 10).map(table => (
            <div
              key={table.id}
              onClick={() => onNavigate('tables')}
              style={{
                background: table.status === 'free' ? 'rgba(63,166,107,0.06)' :
                  table.status === 'occupied' ? 'rgba(217,138,53,0.06)' :
                    table.status === 'reserved' ? 'rgba(74,123,208,0.06)' : '#202328',
                border: `1px solid ${table.status === 'free' ? 'rgba(63,166,107,0.2)' :
                  table.status === 'occupied' ? 'rgba(217,138,53,0.2)' :
                    table.status === 'reserved' ? 'rgba(74,123,208,0.2)' : '#30343B'}`,
                borderRadius: 10,
                padding: '14px 12px',
                cursor: 'pointer',
                textAlign: 'center',
                transition: 'transform 0.1s',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.transform = 'scale(1.02)')}
              onMouseLeave={(e) => (e.currentTarget.style.transform = 'scale(1)')}
            >
              <div style={{ fontSize: 20, fontFamily: 'Manrope', fontWeight: 800, color: '#F5F2EA', marginBottom: 2 }}>
                {table.number}
              </div>
              <div style={{ fontSize: 10, color: '#6F756F', marginBottom: 6 }}>{table.seats} мест</div>
              <StatusBadge type="table" status={table.status} size="sm" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function OrderCard({ order, highlight, onOpen }: { order: any; highlight?: boolean; onOpen: () => void }) {
  const elapsed = (() => {
    const [time] = order.createdAt.split(' ')[1].split(':').map(Number);
    return `${20 + Math.floor(Math.random() * 40)} мин`;
  })();

  return (
    <div
      style={{
        background: highlight ? 'rgba(63,166,107,0.06)' : '#202328',
        border: `1px solid ${highlight ? 'rgba(63,166,107,0.25)' : '#30343B'}`,
        borderRadius: 12,
        padding: 18,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {highlight && (
        <div style={{
          position: 'absolute', top: 0, left: 0, right: 0, height: 3,
          background: 'linear-gradient(90deg, #3FA66B, #1F6F50)',
        }} />
      )}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 }}>
        <div>
          <div style={{ fontSize: 16, fontFamily: 'Manrope', fontWeight: 800, color: '#C9A45C' }}>
            #{order.id}
          </div>
          <div style={{ fontSize: 12, color: '#A9A39A' }}>Столик №{order.tableNumber}</div>
        </div>
        <StatusBadge type="order" status={order.status} size="sm" />
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12, color: '#6F756F', fontSize: 12 }}>
        <Clock size={12} />
        {elapsed} назад
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ fontSize: 16, fontWeight: 700, color: '#F5F2EA' }}>
          {(order.total - order.discount).toLocaleString('ru-RU')} ₽
        </div>
        <button
          onClick={onOpen}
          style={{
            display: 'flex', alignItems: 'center', gap: 5, padding: '6px 12px',
            background: highlight ? 'rgba(63,166,107,0.15)' : 'rgba(201,164,92,0.1)',
            border: `1px solid ${highlight ? 'rgba(63,166,107,0.3)' : 'rgba(201,164,92,0.2)'}`,
            borderRadius: 8, color: highlight ? '#3FA66B' : '#C9A45C',
            fontSize: 12, fontWeight: 600, cursor: 'pointer',
          }}
        >
          <ExternalLink size={12} />
          Открыть
        </button>
      </div>
    </div>
  );
}
