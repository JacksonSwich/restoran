import { useState } from 'react';
import { Plus, Edit3, EyeOff, Trash2, Search, Clock, Scale } from 'lucide-react';
import { dishes, Role } from '../data/mockData';

const categories = ['Все', 'Салаты', 'Супы', 'Горячие блюда', 'Напитки', 'Десерты', 'Закуски'];
const availabilityFilters = ['Все блюда', 'Доступные', 'Недоступные'];

export function MenuScreen({ role }: { role: Role }) {
  const [selectedCategory, setSelectedCategory] = useState('Все');
  const [availFilter, setAvailFilter] = useState('Все блюда');
  const [search, setSearch] = useState('');

  const filtered = dishes.filter(d => {
    if (selectedCategory !== 'Все' && d.category !== selectedCategory) return false;
    if (availFilter === 'Доступные' && !d.available) return false;
    if (availFilter === 'Недоступные' && d.available) return false;
    if (search && !d.name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div style={{ display: 'flex', height: '100%', overflow: 'hidden' }}>
      {/* Left sidebar: categories */}
      <div style={{
        width: 200, flexShrink: 0, background: '#15171A', borderRight: '1px solid #30343B',
        padding: '24px 14px', display: 'flex', flexDirection: 'column', gap: 4,
      }}>
        <div style={{ fontSize: 11, color: '#6F756F', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 8, paddingLeft: 8 }}>
          Категории
        </div>
        {categories.map(cat => {
          const count = cat === 'Все' ? dishes.length : dishes.filter(d => d.category === cat).length;
          const active = selectedCategory === cat;
          return (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '9px 12px', borderRadius: 8, border: 'none',
                background: active ? 'rgba(201,164,92,0.1)' : 'transparent',
                color: active ? '#C9A45C' : '#A9A39A',
                fontSize: 13, fontWeight: active ? 600 : 400, cursor: 'pointer', textAlign: 'left',
                borderLeft: `3px solid ${active ? '#C9A45C' : 'transparent'}`,
              }}
            >
              <span>{cat}</span>
              <span style={{ fontSize: 11, color: active ? '#C9A45C' : '#6F756F' }}>{count}</span>
            </button>
          );
        })}
      </div>

      {/* Main area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Header */}
        <div style={{ padding: '24px 24px 0', flexShrink: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <div>
              <h1 style={{ fontFamily: 'Manrope', fontSize: 24, fontWeight: 800, color: '#F5F2EA', marginBottom: 4 }}>Меню</h1>
              <p style={{ fontSize: 13, color: '#6F756F' }}>{filtered.length} блюд</p>
            </div>
            {role === 'admin' && (
              <button style={btnPrimary}>
                <Plus size={14} /> Добавить блюдо
              </button>
            )}
          </div>

          {/* Filters row */}
          <div style={{ display: 'flex', gap: 8, marginBottom: 16, alignItems: 'center' }}>
            <div style={{ display: 'flex', gap: 6 }}>
              {availabilityFilters.map(f => (
                <button
                  key={f}
                  onClick={() => setAvailFilter(f)}
                  style={{
                    padding: '6px 14px', background: availFilter === f ? 'rgba(201,164,92,0.12)' : '#202328',
                    border: `1px solid ${availFilter === f ? 'rgba(201,164,92,0.35)' : '#30343B'}`,
                    borderRadius: 8, color: availFilter === f ? '#C9A45C' : '#A9A39A',
                    fontSize: 12, fontWeight: availFilter === f ? 600 : 400, cursor: 'pointer',
                  }}
                >
                  {f}
                </button>
              ))}
            </div>
            <div style={{ position: 'relative', flex: 1, maxWidth: 280 }}>
              <Search size={14} color="#6F756F" style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)' }} />
              <input
                type="text"
                placeholder="Найти блюдо"
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

        {/* Dishes grid */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '0 24px 24px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
            {filtered.map(dish => (
              <DishCard key={dish.id} dish={dish} role={role} />
            ))}
            {filtered.length === 0 && (
              <div style={{
                gridColumn: '1/-1', padding: 64, textAlign: 'center',
                color: '#6F756F', fontSize: 14, background: '#202328',
                border: '1px dashed #30343B', borderRadius: 12,
              }}>
                Нет блюд по выбранным фильтрам
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function DishCard({ dish, role }: { dish: typeof dishes[0]; role: Role }) {
  return (
    <div style={{
      background: dish.available ? '#202328' : '#1A1D21',
      border: `1px solid ${dish.available ? '#30343B' : '#252932'}`,
      borderRadius: 12, padding: '18px',
      opacity: dish.available ? 1 : 0.65,
      position: 'relative', overflow: 'hidden',
      transition: 'box-shadow 0.15s',
    }}>
      {!dish.available && (
        <div style={{
          position: 'absolute', top: 10, right: 10,
          padding: '3px 8px', background: 'rgba(92,96,104,0.2)', borderRadius: 20,
          fontSize: 10, fontWeight: 700, color: '#5C6068',
        }}>
          Недоступно
        </div>
      )}

      <div style={{ marginBottom: 10 }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: '#F5F2EA', marginBottom: 4, lineHeight: 1.3, paddingRight: dish.available ? 0 : 60 }}>
          {dish.name}
        </div>
        <div style={{ fontSize: 11, color: '#6F756F', lineHeight: 1.5 }}>{dish.category}</div>
      </div>

      <div style={{ fontSize: 12, color: '#A9A39A', marginBottom: 12, lineHeight: 1.5 }}>
        {dish.description}
      </div>

      <div style={{ display: 'flex', gap: 12, marginBottom: 14 }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, color: '#6F756F' }}>
          <Scale size={12} /> {dish.weight}
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, color: '#6F756F' }}>
          <Clock size={12} /> {dish.cookingTime}
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ fontSize: 18, fontFamily: 'Manrope', fontWeight: 800, color: '#C9A45C' }}>
          {dish.price.toLocaleString('ru-RU')} ₽
        </div>
        {role === 'admin' && (
          <div style={{ display: 'flex', gap: 6 }}>
            <button style={iconBtn} title="Редактировать"><Edit3 size={13} /></button>
            <button style={{ ...iconBtn, color: '#D98A35' }} title="Скрыть из меню"><EyeOff size={13} /></button>
            <button style={{ ...iconBtn, color: '#C94C4C' }} title="Удалить"><Trash2 size={13} /></button>
          </div>
        )}
        {role === 'waiter' && (
          <div style={{
            padding: '3px 10px', borderRadius: 20, fontSize: 11, fontWeight: 600,
            background: dish.available ? 'rgba(63,166,107,0.12)' : 'rgba(92,96,104,0.12)',
            color: dish.available ? '#3FA66B' : '#5C6068',
            border: `1px solid ${dish.available ? 'rgba(63,166,107,0.2)' : '#30343B'}`,
          }}>
            {dish.available ? 'Доступно' : 'Недоступно'}
          </div>
        )}
      </div>
    </div>
  );
}

const btnPrimary: React.CSSProperties = {
  display: 'flex', alignItems: 'center', gap: 6, padding: '10px 18px',
  background: 'linear-gradient(135deg, #C9A45C, #A07B3A)',
  color: '#0E0F11', border: 'none', borderRadius: 8, fontSize: 13, fontWeight: 700, cursor: 'pointer',
};

const iconBtn: React.CSSProperties = {
  width: 30, height: 30, borderRadius: 7, background: '#252932',
  border: '1px solid #30343B', display: 'flex', alignItems: 'center', justifyContent: 'center',
  cursor: 'pointer', color: '#A9A39A',
};
