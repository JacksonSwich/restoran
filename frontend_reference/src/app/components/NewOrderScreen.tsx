import { useState } from 'react';
import { Plus, Minus, Trash2, ShoppingCart, X, Search, Clock, Scale } from 'lucide-react';
import { dishes, tables } from '../data/mockData';

interface CartItem {
  dishId: number;
  dishName: string;
  price: number;
  quantity: number;
  comment: string;
}

const categories = ['Салаты', 'Супы', 'Горячие блюда', 'Напитки', 'Десерты', 'Закуски'];

export function NewOrderScreen({ onNavigate }: { onNavigate: (s: string) => void }) {
  const [activeCategory, setActiveCategory] = useState('Горячие блюда');
  const [cart, setCart] = useState<CartItem[]>([]);
  const [selectedTable, setSelectedTable] = useState(tables[3]);
  const [customer, setCustomer] = useState('');
  const [discount, setDiscount] = useState(0);
  const [dishSearch, setDishSearch] = useState('');

  const filteredDishes = dishes.filter(d => {
    if (d.category !== activeCategory) return false;
    if (dishSearch && !d.name.toLowerCase().includes(dishSearch.toLowerCase())) return false;
    return true;
  });

  const addToCart = (dish: typeof dishes[0]) => {
    if (!dish.available) return;
    setCart(prev => {
      const existing = prev.find(i => i.dishId === dish.id);
      if (existing) {
        return prev.map(i => i.dishId === dish.id ? { ...i, quantity: i.quantity + 1 } : i);
      }
      return [...prev, { dishId: dish.id, dishName: dish.name, price: dish.price, quantity: 1, comment: '' }];
    });
  };

  const updateQty = (dishId: number, delta: number) => {
    setCart(prev => prev.map(i => i.dishId === dishId ? { ...i, quantity: Math.max(1, i.quantity + delta) } : i));
  };

  const removeItem = (dishId: number) => {
    setCart(prev => prev.filter(i => i.dishId !== dishId));
  };

  const subtotal = cart.reduce((s, i) => s + i.price * i.quantity, 0);
  const discountAmt = Math.round(subtotal * discount / 100);
  const total = subtotal - discountAmt;

  const freeTables = tables.filter(t => t.status === 'free');

  return (
    <div style={{ display: 'flex', height: '100%', overflow: 'hidden' }}>
      {/* Left panel */}
      <div style={{
        width: 220, flexShrink: 0, background: '#15171A', borderRight: '1px solid #30343B',
        display: 'flex', flexDirection: 'column', padding: 20, gap: 16, overflowY: 'auto',
      }}>
        <div>
          <h2 style={{ fontSize: 15, fontWeight: 700, color: '#F5F2EA', marginBottom: 12 }}>Столик</h2>
          <select
            value={selectedTable.id}
            onChange={(e) => {
              const t = tables.find(t => t.id === Number(e.target.value));
              if (t) setSelectedTable(t);
            }}
            style={{
              width: '100%', background: '#202328', border: '1px solid #30343B',
              borderRadius: 8, padding: '9px 12px', color: '#F5F2EA', fontSize: 13,
            }}
          >
            {freeTables.map(t => (
              <option key={t.id} value={t.id}>
                Столик №{t.number} ({t.zone})
              </option>
            ))}
          </select>
          <div style={{ marginTop: 10, background: '#202328', border: '1px solid #30343B', borderRadius: 8, padding: '12px' }}>
            <div style={{ fontSize: 18, fontFamily: 'Manrope', fontWeight: 800, color: '#C9A45C' }}>Столик №{selectedTable.number}</div>
            <div style={{ fontSize: 12, color: '#A9A39A', marginTop: 2 }}>{selectedTable.zone}</div>
            <div style={{ fontSize: 12, color: '#6F756F', marginTop: 2 }}>{selectedTable.seats} мест</div>
          </div>
        </div>

        <div>
          <h2 style={{ fontSize: 15, fontWeight: 700, color: '#F5F2EA', marginBottom: 10 }}>Клиент</h2>
          <div style={{ position: 'relative', marginBottom: 8 }}>
            <Search size={14} color="#6F756F" style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              placeholder="Добавить клиента"
              value={customer}
              onChange={(e) => setCustomer(e.target.value)}
              style={{
                width: '100%', background: '#202328', border: '1px solid #30343B',
                borderRadius: 8, padding: '8px 10px 8px 32px', color: '#F5F2EA', fontSize: 13, boxSizing: 'border-box',
              }}
            />
          </div>
          {customer && (
            <div>
              <label style={{ fontSize: 11, color: '#6F756F', display: 'block', marginBottom: 4 }}>Скидка (%)</label>
              <input
                type="number"
                min={0} max={30}
                value={discount}
                onChange={(e) => setDiscount(Number(e.target.value))}
                style={{
                  width: '100%', background: '#202328', border: '1px solid #30343B',
                  borderRadius: 8, padding: '8px 12px', color: '#C9A45C', fontSize: 14, fontWeight: 700, boxSizing: 'border-box',
                }}
              />
            </div>
          )}
        </div>
      </div>

      {/* Center: menu */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Category tabs */}
        <div style={{ borderBottom: '1px solid #30343B', padding: '0 20px', display: 'flex', gap: 0, background: '#15171A' }}>
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              style={{
                padding: '14px 16px', background: 'transparent', border: 'none',
                borderBottom: `2px solid ${activeCategory === cat ? '#C9A45C' : 'transparent'}`,
                color: activeCategory === cat ? '#C9A45C' : '#A9A39A',
                fontSize: 13, fontWeight: activeCategory === cat ? 600 : 400, cursor: 'pointer',
                transition: 'all 0.15s', whiteSpace: 'nowrap',
              }}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Search */}
        <div style={{ padding: '14px 20px 0', borderBottom: '1px solid #30343B22' }}>
          <div style={{ position: 'relative', maxWidth: 280 }}>
            <Search size={14} color="#6F756F" style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              placeholder="Найти блюдо"
              value={dishSearch}
              onChange={(e) => setDishSearch(e.target.value)}
              style={{
                width: '100%', background: '#202328', border: '1px solid #30343B',
                borderRadius: 8, padding: '8px 10px 8px 32px', color: '#F5F2EA', fontSize: 13, boxSizing: 'border-box',
              }}
            />
          </div>
        </div>

        {/* Dishes grid */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '16px 20px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12 }}>
            {filteredDishes.map(dish => (
              <DishCard key={dish.id} dish={dish} onAdd={() => addToCart(dish)} />
            ))}
          </div>
        </div>
      </div>

      {/* Right: cart */}
      <div style={{
        width: 300, flexShrink: 0, background: '#15171A', borderLeft: '1px solid #30343B',
        display: 'flex', flexDirection: 'column',
      }}>
        <div style={{ padding: '18px 20px', borderBottom: '1px solid #30343B', display: 'flex', alignItems: 'center', gap: 8 }}>
          <ShoppingCart size={18} color="#C9A45C" />
          <h2 style={{ fontSize: 15, fontWeight: 700, color: '#F5F2EA' }}>Заказ</h2>
          <span style={{
            marginLeft: 'auto', padding: '2px 8px',
            background: 'rgba(201,164,92,0.12)', borderRadius: 20,
            fontSize: 12, fontWeight: 700, color: '#C9A45C',
          }}>
            {cart.reduce((s, i) => s + i.quantity, 0)} позиций
          </span>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: 8 }}>
          {cart.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: '#6F756F', fontSize: 13 }}>
              <ShoppingCart size={32} color="#30343B" style={{ margin: '0 auto 12px' }} />
              <p>Добавьте блюда из меню</p>
            </div>
          ) : (
            cart.map(item => (
              <div key={item.dishId} style={{
                background: '#202328', border: '1px solid #30343B', borderRadius: 10, padding: '12px 12px',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                  <span style={{ fontSize: 13, fontWeight: 500, color: '#F5F2EA', flex: 1, marginRight: 8, lineHeight: 1.3 }}>
                    {item.dishName}
                  </span>
                  <button onClick={() => removeItem(item.dishId)} style={{ color: '#C94C4C', background: 'none', border: 'none', cursor: 'pointer', padding: 0, flexShrink: 0 }}>
                    <X size={14} />
                  </button>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <button onClick={() => updateQty(item.dishId, -1)} style={qtyBtn}>
                      <Minus size={10} />
                    </button>
                    <span style={{ fontSize: 14, fontWeight: 700, color: '#F5F2EA', minWidth: 20, textAlign: 'center' }}>
                      {item.quantity}
                    </span>
                    <button onClick={() => updateQty(item.dishId, 1)} style={{ ...qtyBtn, background: 'rgba(201,164,92,0.12)', color: '#C9A45C' }}>
                      <Plus size={10} />
                    </button>
                  </div>
                  <span style={{ fontSize: 14, fontWeight: 700, color: '#C9A45C' }}>
                    {(item.price * item.quantity).toLocaleString('ru-RU')} ₽
                  </span>
                </div>
                <input
                  type="text"
                  placeholder="Комментарий"
                  value={item.comment}
                  onChange={(e) => setCart(prev => prev.map(i => i.dishId === item.dishId ? { ...i, comment: e.target.value } : i))}
                  style={{
                    marginTop: 8, width: '100%', background: '#15171A', border: '1px solid #30343B',
                    borderRadius: 6, padding: '5px 8px', color: '#A9A39A', fontSize: 11, boxSizing: 'border-box',
                  }}
                />
              </div>
            ))
          )}
        </div>

        {/* Total */}
        <div style={{ padding: '16px 20px', borderTop: '1px solid #30343B' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, color: '#A9A39A' }}>
              <span>Сумма</span>
              <span>{subtotal.toLocaleString('ru-RU')} ₽</span>
            </div>
            {discountAmt > 0 && (
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, color: '#3FA66B' }}>
                <span>Скидка {discount}%</span>
                <span>−{discountAmt.toLocaleString('ru-RU')} ₽</span>
              </div>
            )}
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 17, fontWeight: 800, fontFamily: 'Manrope', color: '#F5F2EA', paddingTop: 6, borderTop: '1px solid #30343B' }}>
              <span>Итого к оплате</span>
              <span style={{ color: '#C9A45C' }}>{total.toLocaleString('ru-RU')} ₽</span>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <button
              onClick={() => onNavigate('orders')}
              disabled={cart.length === 0}
              style={{
                padding: '12px', background: cart.length === 0 ? '#252932' : 'linear-gradient(135deg, #C9A45C, #A07B3A)',
                color: cart.length === 0 ? '#5C6068' : '#0E0F11', border: 'none', borderRadius: 8,
                fontSize: 14, fontWeight: 700, cursor: cart.length === 0 ? 'not-allowed' : 'pointer',
              }}
            >
              Создать заказ
            </button>
            <button
              onClick={() => setCart([])}
              style={{
                padding: '10px', background: 'transparent', border: '1px solid #30343B', borderRadius: 8,
                color: '#A9A39A', fontSize: 13, cursor: 'pointer',
              }}
            >
              Очистить
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function DishCard({ dish, onAdd }: { dish: typeof dishes[0]; onAdd: () => void }) {
  return (
    <div
      style={{
        background: dish.available ? '#202328' : '#1A1D21',
        border: `1px solid ${dish.available ? '#30343B' : '#252932'}`,
        borderRadius: 12, padding: '16px',
        opacity: dish.available ? 1 : 0.55,
        position: 'relative', overflow: 'hidden',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 6 }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 14, fontWeight: 600, color: '#F5F2EA', marginBottom: 4, lineHeight: 1.3 }}>{dish.name}</div>
          <div style={{ fontSize: 11, color: '#6F756F', lineHeight: 1.4 }}>{dish.description}</div>
        </div>
        {!dish.available && (
          <span style={{
            padding: '2px 8px', background: 'rgba(92,96,104,0.2)', borderRadius: 20,
            fontSize: 10, fontWeight: 600, color: '#5C6068', whiteSpace: 'nowrap', marginLeft: 8,
          }}>
            Недоступно
          </span>
        )}
      </div>

      <div style={{ display: 'flex', gap: 10, marginBottom: 10, marginTop: 8 }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 3, fontSize: 11, color: '#6F756F' }}>
          <Scale size={11} /> {dish.weight}
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 3, fontSize: 11, color: '#6F756F' }}>
          <Clock size={11} /> {dish.cookingTime}
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: 16, fontFamily: 'Manrope', fontWeight: 800, color: '#C9A45C' }}>
          {dish.price.toLocaleString('ru-RU')} ₽
        </span>
        <button
          onClick={onAdd}
          disabled={!dish.available}
          style={{
            display: 'flex', alignItems: 'center', gap: 5, padding: '6px 12px',
            background: dish.available ? 'rgba(201,164,92,0.12)' : 'transparent',
            border: `1px solid ${dish.available ? 'rgba(201,164,92,0.25)' : '#30343B'}`,
            borderRadius: 8, color: dish.available ? '#C9A45C' : '#5C6068',
            fontSize: 12, fontWeight: 600, cursor: dish.available ? 'pointer' : 'not-allowed',
          }}
        >
          <Plus size={12} />
          Добавить
        </button>
      </div>
    </div>
  );
}

const qtyBtn: React.CSSProperties = {
  width: 24, height: 24, borderRadius: 6, background: '#252932', border: '1px solid #30343B',
  display: 'flex', alignItems: 'center', justifyContent: 'center',
  cursor: 'pointer', color: '#A9A39A',
};
