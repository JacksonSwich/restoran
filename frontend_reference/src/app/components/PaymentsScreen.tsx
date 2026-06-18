import { useState } from 'react';
import { CheckCircle, X, CreditCard, Banknote, Smartphone } from 'lucide-react';
import { payments, Role, PaymentMethod } from '../data/mockData';
import { StatusBadge } from './StatusBadge';

const methodLabel: Record<PaymentMethod, string> = {
  cash: 'Наличные',
  card: 'Карта',
  online: 'Онлайн',
};

const methodIcon: Record<PaymentMethod, React.ReactNode> = {
  cash: <Banknote size={14} />,
  card: <CreditCard size={14} />,
  online: <Smartphone size={14} />,
};

export function PaymentsScreen({ role }: { role: Role }) {
  const [methodFilter, setMethodFilter] = useState<PaymentMethod | 'all'>('all');
  const [showModal, setShowModal] = useState(false);
  const [selectedMethod, setSelectedMethod] = useState<PaymentMethod>('card');
  const [paymentSuccess, setPaymentSuccess] = useState(false);

  const filtered = payments.filter(p => {
    if (methodFilter !== 'all' && p.method !== methodFilter) return false;
    return true;
  });

  const totalRevenue = payments.filter(p => p.status === 'paid').reduce((s, p) => s + p.amount, 0);

  const handlePayment = () => {
    setShowModal(false);
    setPaymentSuccess(true);
    setTimeout(() => setPaymentSuccess(false), 4000);
  };

  return (
    <div style={{ padding: 28, display: 'flex', flexDirection: 'column', gap: 20, overflowY: 'auto', height: '100%', position: 'relative' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontFamily: 'Manrope', fontSize: 24, fontWeight: 800, color: '#F5F2EA', marginBottom: 4 }}>Оплаты</h1>
          <p style={{ fontSize: 13, color: '#6F756F' }}>
            Выручка сегодня: <span style={{ color: '#C9A45C', fontWeight: 700 }}>{totalRevenue.toLocaleString('ru-RU')} ₽</span>
          </p>
        </div>
        {role === 'waiter' && (
          <button onClick={() => setShowModal(true)} style={btnPrimary}>
            <CreditCard size={14} /> Принять оплату
          </button>
        )}
      </div>

      {/* Filters */}
      {role === 'admin' && (
        <div style={{ display: 'flex', gap: 6 }}>
          {(['all', 'cash', 'card', 'online'] as const).map(m => (
            <button
              key={m}
              onClick={() => setMethodFilter(m)}
              style={{
                padding: '7px 14px', background: methodFilter === m ? 'rgba(201,164,92,0.12)' : '#202328',
                border: `1px solid ${methodFilter === m ? 'rgba(201,164,92,0.35)' : '#30343B'}`,
                borderRadius: 8, color: methodFilter === m ? '#C9A45C' : '#A9A39A',
                fontSize: 13, fontWeight: methodFilter === m ? 600 : 400, cursor: 'pointer',
              }}
            >
              {m === 'all' ? 'Все способы' : methodLabel[m]}
            </button>
          ))}
        </div>
      )}

      {/* Table */}
      <div style={{ background: '#202328', border: '1px solid #30343B', borderRadius: 12, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#1A1D21', borderBottom: '1px solid #30343B' }}>
              {['ID оплаты', '№ заказа', 'Столик', 'Сумма', 'Способ оплаты', 'Статус', 'Дата'].map(col => (
                <th key={col} style={{
                  padding: '11px 16px', textAlign: 'left', fontSize: 11,
                  color: '#6F756F', fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase',
                }}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((pay, i) => (
              <tr
                key={pay.id}
                style={{
                  borderTop: '1px solid #30343B22',
                  background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)',
                }}
                onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(201,164,92,0.03)')}
                onMouseLeave={(e) => (e.currentTarget.style.background = i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)')}
              >
                <td style={{ padding: '13px 16px', fontSize: 12, fontFamily: 'monospace', color: '#A9A39A' }}>{pay.id}</td>
                <td style={{ padding: '13px 16px', fontSize: 14, fontWeight: 700, color: '#C9A45C' }}>#{pay.orderId}</td>
                <td style={{ padding: '13px 16px', fontSize: 13, color: '#F5F2EA' }}>Столик №{pay.tableNumber}</td>
                <td style={{ padding: '13px 16px', fontSize: 15, fontWeight: 800, fontFamily: 'Manrope', color: '#F5F2EA' }}>
                  {pay.amount.toLocaleString('ru-RU')} ₽
                </td>
                <td style={{ padding: '13px 16px' }}>
                  <span style={{
                    display: 'inline-flex', alignItems: 'center', gap: 6,
                    fontSize: 13, color: '#A9A39A',
                  }}>
                    {methodIcon[pay.method]}
                    {methodLabel[pay.method]}
                  </span>
                </td>
                <td style={{ padding: '13px 16px' }}>
                  <StatusBadge type="payment" status={pay.status} size="sm" />
                </td>
                <td style={{ padding: '13px 16px', fontSize: 12, color: '#6F756F' }}>{pay.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Payment Modal */}
      {showModal && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex',
          alignItems: 'center', justifyContent: 'center', zIndex: 100, backdropFilter: 'blur(4px)',
        }}>
          <div style={{
            background: '#202328', border: '1px solid #30343B', borderRadius: 16,
            padding: '32px', width: 400, position: 'relative',
          }}>
            <button
              onClick={() => setShowModal(false)}
              style={{
                position: 'absolute', top: 16, right: 16, background: 'none',
                border: 'none', cursor: 'pointer', color: '#6F756F',
              }}
            >
              <X size={20} />
            </button>
            <h2 style={{ fontFamily: 'Manrope', fontSize: 20, fontWeight: 800, color: '#F5F2EA', marginBottom: 6 }}>
              Принять оплату
            </h2>
            <p style={{ fontSize: 13, color: '#6F756F', marginBottom: 24 }}>Заказ #12 · Столик №2</p>

            <div style={{ background: '#15171A', borderRadius: 12, padding: '16px 20px', marginBottom: 24 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: 13, color: '#A9A39A' }}>
                <span>Сумма</span><span>1 480 ₽</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: 13, color: '#3FA66B' }}>
                <span>Скидка 5%</span><span>−74 ₽</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 20, fontWeight: 800, fontFamily: 'Manrope', color: '#C9A45C', borderTop: '1px solid #30343B', paddingTop: 10 }}>
                <span>Итого к оплате</span><span>1 406 ₽</span>
              </div>
            </div>

            <div style={{ marginBottom: 24 }}>
              <label style={{ fontSize: 12, color: '#6F756F', display: 'block', marginBottom: 10 }}>СПОСОБ ОПЛАТЫ</label>
              <div style={{ display: 'flex', gap: 8 }}>
                {(['cash', 'card', 'online'] as PaymentMethod[]).map(m => (
                  <button
                    key={m}
                    onClick={() => setSelectedMethod(m)}
                    style={{
                      flex: 1, padding: '12px 8px',
                      background: selectedMethod === m ? 'rgba(201,164,92,0.12)' : '#15171A',
                      border: `2px solid ${selectedMethod === m ? '#C9A45C' : '#30343B'}`,
                      borderRadius: 10, cursor: 'pointer',
                      display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6,
                      color: selectedMethod === m ? '#C9A45C' : '#A9A39A', transition: 'all 0.15s',
                    }}
                  >
                    {methodIcon[m]}
                    <span style={{ fontSize: 12, fontWeight: 600 }}>{methodLabel[m]}</span>
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={handlePayment}
              style={{
                width: '100%', padding: '14px',
                background: 'linear-gradient(135deg, #C9A45C, #A07B3A)',
                color: '#0E0F11', border: 'none', borderRadius: 10,
                fontSize: 15, fontWeight: 800, cursor: 'pointer',
              }}
            >
              Подтвердить оплату · 1 406 ₽
            </button>
          </div>
        </div>
      )}

      {/* Success notification */}
      {paymentSuccess && (
        <div style={{
          position: 'fixed', bottom: 28, right: 28, zIndex: 200,
          background: '#202328', border: '1px solid rgba(63,166,107,0.3)',
          borderRadius: 14, padding: '20px 24px',
          boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
          display: 'flex', alignItems: 'center', gap: 14,
        }}>
          <div style={{
            width: 44, height: 44, borderRadius: '50%',
            background: 'rgba(63,166,107,0.12)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <CheckCircle size={24} color="#3FA66B" />
          </div>
          <div>
            <div style={{ fontSize: 15, fontWeight: 700, color: '#3FA66B', marginBottom: 2 }}>Заказ оплачен</div>
            <div style={{ fontSize: 12, color: '#A9A39A' }}>Столик №2 освобожден</div>
          </div>
        </div>
      )}
    </div>
  );
}

const btnPrimary: React.CSSProperties = {
  display: 'flex', alignItems: 'center', gap: 6, padding: '10px 18px',
  background: 'linear-gradient(135deg, #C9A45C, #A07B3A)',
  color: '#0E0F11', border: 'none', borderRadius: 8, fontSize: 13, fontWeight: 700, cursor: 'pointer',
};
