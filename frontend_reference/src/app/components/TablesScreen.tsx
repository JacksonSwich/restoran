import { useState } from 'react';
import { Plus, Settings2, Edit3, Users } from 'lucide-react';
import { tables, TableStatus, Role } from '../data/mockData';
import { StatusBadge } from './StatusBadge';

type ZoneFilter = 'all' | 'Основной зал' | 'VIP-зона' | 'Терраса';

const statusFilters: { id: TableStatus | 'all'; label: string }[] = [
  { id: 'all', label: 'Все' },
  { id: 'free', label: 'Свободные' },
  { id: 'occupied', label: 'Занятые' },
  { id: 'reserved', label: 'Забронированные' },
  { id: 'unavailable', label: 'Недоступные' },
];

const zoneFilters: { id: ZoneFilter; label: string }[] = [
  { id: 'all', label: 'Все зоны' },
  { id: 'Основной зал', label: 'Основной зал' },
  { id: 'VIP-зона', label: 'VIP-зона' },
  { id: 'Терраса', label: 'Терраса' },
];

export function TablesScreen({ role, onNavigate }: { role: Role; onNavigate: (s: string) => void }) {
  const [statusFilter, setStatusFilter] = useState<TableStatus | 'all'>('all');
  const [zoneFilter, setZoneFilter] = useState<ZoneFilter>('all');

  const filtered = tables.filter(t => {
    if (statusFilter !== 'all' && t.status !== statusFilter) return false;
    if (zoneFilter !== 'all' && t.zone !== zoneFilter) return false;
    return true;
  });

  return (
    <div style={{ padding: 28, display: 'flex', flexDirection: 'column', gap: 20, overflowY: 'auto', height: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontFamily: 'Manrope', fontSize: 24, fontWeight: 800, color: '#F5F2EA', marginBottom: 4 }}>Столики</h1>
          <p style={{ fontSize: 13, color: '#6F756F' }}>{tables.length} столиков · {tables.filter(t => t.status === 'occupied').length} занято</p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          {role === 'admin' ? (
            <>
              <button style={btnSecondary}><Edit3 size={14} /> Изменить статус</button>
              <button style={btnPrimary}><Plus size={14} /> Добавить столик</button>
            </>
          ) : (
            <button onClick={() => onNavigate('new-order')} style={btnPrimary}><Plus size={14} /> Создать заказ</button>
          )}
        </div>
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <FilterTabs
          items={statusFilters}
          active={statusFilter}
          onChange={(v) => setStatusFilter(v as TableStatus | 'all')}
        />
        <FilterTabs
          items={zoneFilters}
          active={zoneFilter}
          onChange={(v) => setZoneFilter(v as ZoneFilter)}
          color="#4A7BD0"
        />
      </div>

      {/* Table grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
        {filtered.map(table => (
          <TableCard key={table.id} table={table} role={role} onNavigate={onNavigate} />
        ))}
        {filtered.length === 0 && (
          <div style={{
            gridColumn: '1/-1', padding: 64, textAlign: 'center',
            color: '#6F756F', fontSize: 14,
            background: '#202328', border: '1px dashed #30343B', borderRadius: 12,
          }}>
            Нет столиков по выбранным фильтрам
          </div>
        )}
      </div>
    </div>
  );
}

function TableCard({ table, role, onNavigate }: { table: any; role: Role; onNavigate: (s: string) => void }) {
  const colorMap: Record<string, string> = {
    free: '#3FA66B',
    occupied: '#D98A35',
    reserved: '#4A7BD0',
    unavailable: '#5C6068',
  };
  const color = colorMap[table.status];

  return (
    <div
      style={{
        background: '#202328',
        border: `1px solid ${table.status === 'free' ? 'rgba(63,166,107,0.2)' : table.status === 'occupied' ? 'rgba(217,138,53,0.2)' : '#30343B'}`,
        borderRadius: 14,
        padding: 20,
        position: 'relative',
        overflow: 'hidden',
        transition: 'transform 0.15s, box-shadow 0.15s',
        cursor: table.status === 'unavailable' ? 'default' : 'pointer',
        opacity: table.status === 'unavailable' ? 0.5 : 1,
      }}
      onMouseEnter={(e) => {
        if (table.status !== 'unavailable') {
          (e.currentTarget as HTMLDivElement).style.transform = 'translateY(-2px)';
          (e.currentTarget as HTMLDivElement).style.boxShadow = '0 8px 24px rgba(0,0,0,0.3)';
        }
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLDivElement).style.transform = 'translateY(0)';
        (e.currentTarget as HTMLDivElement).style.boxShadow = 'none';
      }}
    >
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, height: 3,
        background: `linear-gradient(90deg, ${color}, ${color}88)`,
      }} />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
        <div>
          <div style={{ fontFamily: 'Manrope', fontSize: 20, fontWeight: 800, color: '#F5F2EA', lineHeight: 1 }}>
            Столик №{table.number}
          </div>
          <div style={{ fontSize: 12, color: '#6F756F', marginTop: 3 }}>{table.zone}</div>
        </div>
        <StatusBadge type="table" status={table.status} size="sm" />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 14, color: '#A9A39A', fontSize: 13 }}>
        <Users size={14} />
        {table.seats} {table.seats === 1 ? 'место' : table.seats < 5 ? 'места' : 'мест'}
      </div>

      {table.status === 'occupied' && table.orderId && (
        <div style={{
          background: 'rgba(217,138,53,0.08)', border: '1px solid rgba(217,138,53,0.15)',
          borderRadius: 8, padding: '10px 12px', marginBottom: 12,
        }}>
          <div style={{ fontSize: 11, color: '#6F756F', marginBottom: 2 }}>Активный заказ</div>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#C9A45C' }}>#{table.orderId}</div>
          <div style={{ fontSize: 13, color: '#D98A35', marginTop: 2 }}>{table.amount?.toLocaleString('ru-RU')} ₽</div>
        </div>
      )}

      <div style={{ display: 'flex', gap: 8 }}>
        {role === 'waiter' && table.status === 'free' && (
          <button
            onClick={() => onNavigate('new-order')}
            style={{ ...btnPrimary, fontSize: 12, padding: '7px 12px', flex: 1 }}
          >
            Создать заказ
          </button>
        )}
        {role === 'admin' && (
          <>
            <button style={{ ...btnSecondary, fontSize: 11, padding: '6px 10px', flex: 1 }}>
              <Edit3 size={12} /> Изменить
            </button>
            <button style={{
              ...btnSecondary, fontSize: 11, padding: '6px 10px',
              background: 'transparent', border: '1px solid #30343B', borderRadius: 8,
              color: '#A9A39A', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4,
            }}>
              <Settings2 size={12} /> Статус
            </button>
          </>
        )}
        {role === 'waiter' && table.status === 'occupied' && (
          <button
            onClick={() => onNavigate('order-details')}
            style={{ ...btnSecondary, fontSize: 12, padding: '7px 12px', flex: 1 }}
          >
            Открыть заказ
          </button>
        )}
      </div>
    </div>
  );
}

function FilterTabs({ items, active, onChange, color = '#C9A45C' }: {
  items: { id: string; label: string }[];
  active: string;
  onChange: (v: string) => void;
  color?: string;
}) {
  return (
    <div style={{ display: 'flex', gap: 6 }}>
      {items.map(item => (
        <button
          key={item.id}
          onClick={() => onChange(item.id)}
          style={{
            padding: '7px 14px',
            background: active === item.id ? `${color}15` : '#202328',
            border: `1px solid ${active === item.id ? `${color}44` : '#30343B'}`,
            borderRadius: 8,
            color: active === item.id ? color : '#A9A39A',
            fontSize: 13,
            fontWeight: active === item.id ? 600 : 400,
            cursor: 'pointer',
            transition: 'all 0.15s',
          }}
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}

const btnPrimary: React.CSSProperties = {
  display: 'flex', alignItems: 'center', gap: 6, padding: '9px 16px',
  background: 'linear-gradient(135deg, #C9A45C, #A07B3A)',
  color: '#0E0F11', border: 'none', borderRadius: 8,
  fontSize: 13, fontWeight: 700, cursor: 'pointer',
};

const btnSecondary: React.CSSProperties = {
  display: 'flex', alignItems: 'center', gap: 6, padding: '9px 16px',
  background: '#252932', color: '#A9A39A', border: '1px solid #30343B',
  borderRadius: 8, fontSize: 13, fontWeight: 500, cursor: 'pointer',
};
