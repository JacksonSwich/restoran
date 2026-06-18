import { OrderStatus, TableStatus, PaymentStatus } from '../data/mockData';

const orderStatusConfig: Record<OrderStatus, { label: string; color: string; bg: string }> = {
  new: { label: 'Новый', color: '#4A7BD0', bg: 'rgba(74,123,208,0.12)' },
  cooking: { label: 'Готовится', color: '#D98A35', bg: 'rgba(217,138,53,0.12)' },
  ready: { label: 'Готов', color: '#3FA66B', bg: 'rgba(63,166,107,0.12)' },
  served: { label: 'Подан', color: '#9B6CDD', bg: 'rgba(155,108,221,0.12)' },
  paid: { label: 'Оплачен', color: '#1F6F50', bg: 'rgba(31,111,80,0.15)' },
  cancelled: { label: 'Отменен', color: '#C94C4C', bg: 'rgba(201,76,76,0.12)' },
};

const tableStatusConfig: Record<TableStatus, { label: string; color: string; bg: string }> = {
  free: { label: 'Свободен', color: '#3FA66B', bg: 'rgba(63,166,107,0.12)' },
  occupied: { label: 'Занят', color: '#D98A35', bg: 'rgba(217,138,53,0.12)' },
  reserved: { label: 'Забронирован', color: '#4A7BD0', bg: 'rgba(74,123,208,0.12)' },
  unavailable: { label: 'Недоступен', color: '#5C6068', bg: 'rgba(92,96,104,0.15)' },
};

const paymentStatusConfig: Record<PaymentStatus, { label: string; color: string; bg: string }> = {
  pending: { label: 'Ожидает', color: '#D98A35', bg: 'rgba(217,138,53,0.12)' },
  paid: { label: 'Оплачено', color: '#3FA66B', bg: 'rgba(63,166,107,0.12)' },
  refund: { label: 'Возврат', color: '#9B6CDD', bg: 'rgba(155,108,221,0.12)' },
  cancelled: { label: 'Отменено', color: '#C94C4C', bg: 'rgba(201,76,76,0.12)' },
};

interface Props {
  type: 'order' | 'table' | 'payment';
  status: string;
  size?: 'sm' | 'md';
}

export function StatusBadge({ type, status, size = 'md' }: Props) {
  let config: { label: string; color: string; bg: string } | undefined;

  if (type === 'order') config = orderStatusConfig[status as OrderStatus];
  else if (type === 'table') config = tableStatusConfig[status as TableStatus];
  else if (type === 'payment') config = paymentStatusConfig[status as PaymentStatus];

  if (!config) return null;

  const padding = size === 'sm' ? '2px 8px' : '4px 12px';
  const fontSize = size === 'sm' ? '11px' : '12px';

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding,
        borderRadius: '20px',
        fontSize,
        fontWeight: 600,
        letterSpacing: '0.02em',
        color: config.color,
        background: config.bg,
        border: `1px solid ${config.color}22`,
        whiteSpace: 'nowrap',
      }}
    >
      <span
        style={{
          width: 6,
          height: 6,
          borderRadius: '50%',
          background: config.color,
          marginRight: 6,
          flexShrink: 0,
        }}
      />
      {config.label}
    </span>
  );
}
