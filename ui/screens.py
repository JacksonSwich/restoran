"""Все экраны приложения."""

from datetime import datetime
from functools import partial

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QScrollArea, QGridLayout, QStackedWidget,
    QComboBox, QSpinBox, QTextEdit, QMessageBox, QDialog,
    QDialogButtonBox, QFormLayout, QGroupBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from ui.styles import *
from ui.widgets import (
    make_label, make_manrope_label, PrimaryButton, SecondaryButton,
    DangerButton, StatusBadge, SearchInput, FilterTab, Card,
    StatCard, DataTable, SectionHeader, hex_to_rgb,
    ORDER_STATUS_CONFIG, TABLE_STATUS_CONFIG, PAYMENT_STATUS_CONFIG,
)
from database.queries import *

# ─── Aдминистративный дашборд ──────────────────────────────────

class AdminDashboard(QWidget):
    def __init__(self, on_navigate=None):
        super().__init__()
        self._navigate = on_navigate
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(24)

        # Header
        header = QVBoxLayout()
        header.addWidget(make_manrope_label("Главная", 24, QFont.Weight.ExtraBold))
        header.addWidget(make_label("Операционная сводка · 18 июня 2026", 13, TEXT_MUTED))
        layout.addLayout(header)

        # Stats
        stats_grid = QHBoxLayout()
        stats_grid.setSpacing(16)

        # Загружаем данные
        try:
            active_orders = get_active_orders()
            paid_orders = get_orders_by_status("paid")
            all_tables = get_all_tables()
            occupied_count = sum(1 for t in all_tables if t["status"] == "occupied")
            total_tables = len(all_tables)
        except:
            active_orders = []
            paid_orders = []
            occupied_count = 0
            total_tables = 0

        stats = [
            ("Выручка за день", "127 400 ₽", "+14% к вчера", GOLD),
            ("Количество заказов", "84", "сегодня", INFO),
            ("Средний чек", "1 517 ₽", "+5% к вчера", WARNING),
            ("Активные заказы", str(len(active_orders)), "", "#9B6CDD"),
            ("Занятые столики", f"{occupied_count}/{total_tables}", "", WARNING),
            ("Оплаченные заказы", str(len(paid_orders)), "сегодня", SUCCESS),
        ]
        for label, value, sub, color in stats:
            stats_grid.addWidget(StatCard(label, value, sub, color))
        layout.addLayout(stats_grid)

        # Charts row
        charts_row = QHBoxLayout()
        charts_row.setSpacing(20)

        # Revenue chart (simplified as table data)
        rev_card = Card()
        rl = QVBoxLayout(rev_card)
        rl.setContentsMargins(24, 24, 24, 24)
        rl.addWidget(SectionHeader("Выручка по дням", "Последние 7 дней"))
        rl.addSpacing(16)

        rev_headers = QHBoxLayout()
        for h in ["День", "Выручка", "Заказы"]:
            rev_headers.addWidget(make_label(h, 11, TEXT_MUTED, QFont.Weight.DemiBold))
        rl.addLayout(rev_headers)

        try:
            rev_data = get_daily_revenue()
        except:
            rev_data = []

        week_data = [
            ("Пн", "48 200 ₽", 32), ("Вт", "52 100 ₽", 38),
            ("Ср", "61 400 ₽", 45), ("Чт", "58 900 ₽", 41),
            ("Пт", "74 300 ₽", 54), ("Сб", "89 200 ₽", 68),
            ("Вс", "42 800 ₽", 30),
        ]
        for day, rev, cnt in week_data:
            row = QHBoxLayout()
            row.addWidget(make_label(day, 13, TEXT_PRIMARY, QFont.Weight.Medium))
            row.addWidget(make_label(rev, 13, GOLD, QFont.Weight.Bold))
            row.addWidget(make_label(str(cnt), 13, TEXT_SECONDARY))
            rl.addLayout(row)
            # Progress bar
            bar = QFrame()
            bar.setFixedHeight(4)
            pct = cnt * 100 // 68
            bar.setStyleSheet(f"""
                background: {BORDER};
                border-radius: 2px;
            """)
            rl.addWidget(bar)

        charts_row.addWidget(rev_card, 2)

        # Popular dishes
        pop_card = Card()
        pl = QVBoxLayout(pop_card)
        pl.setContentsMargins(24, 24, 24, 24)
        pl.addWidget(SectionHeader("Популярные блюда", "По количеству заказов"))
        pl.addSpacing(16)

        try:
            pop_dishes = get_popular_dishes()
        except:
            pop_dishes = []

        sample_popular = [
            ("Стейк Рибай", 124), ("Паста Карбонара", 98),
            ("Лосось на гриле", 87), ("Цезарь с курицей", 76),
            ("Тирамису", 65),
        ]
        for name, cnt in sample_popular:
            pl.addWidget(make_label(name, 13, TEXT_PRIMARY))
            bar = QFrame()
            bar.setFixedHeight(4)
            pct = cnt * 100 // 124
            bar.setStyleSheet(f"""
                background: {BORDER};
                border-radius: 2px;
            """)
            pl.addWidget(bar)

        charts_row.addWidget(pop_card, 1)
        layout.addLayout(charts_row)

        # Recent orders table
        table_card = Card()
        tl = QVBoxLayout(table_card)
        tl.setContentsMargins(0, 0, 0, 0)

        th = QWidget()
        th.setStyleSheet(f"border-bottom: 1px solid {BORDER};")
        th_layout = QHBoxLayout(th)
        th_layout.setContentsMargins(24, 20, 24, 20)
        th_layout.addWidget(SectionHeader("Последние заказы", "Текущие и недавние заказы"))
        th_layout.addStretch()
        if self._navigate:
            all_btn = SecondaryButton("Все заказы →")
            all_btn.clicked.connect(lambda: self._navigate("orders"))
            th_layout.addWidget(all_btn)
        tl.addWidget(th)

        try:
            orders_data = get_all_orders()
        except:
            orders_data = []

        table = DataTable(["№ заказа", "Столик", "Клиент", "Статус", "Сумма", "Оплата", "Создан"])
        if orders_data:
            table.setRowCount(min(len(orders_data), 10))
            for i, o in enumerate(orders_data[:10]):
                table.setItem(i, 0, QTableWidgetItem(f"#{o['id']}"))
                table.setItem(i, 1, QTableWidgetItem(f"Столик №{o.get('table_number', '?')}"))
                table.setItem(i, 2, QTableWidgetItem(o.get("customer_name", "—") or "—"))
                cfg = ORDER_STATUS_CONFIG.get(o["status"], {})
                table.setItem(i, 3, QTableWidgetItem(cfg.get("label", o["status"])))
                table.setItem(i, 4, QTableWidgetItem(f"{float(o['final_amount']):,.0f} ₽".replace(",", " ")))
                table.setItem(i, 5, QTableWidgetItem("—"))
                table.setItem(i, 6, QTableWidgetItem(str(o.get("created_at", ""))))
        table.setMaximumHeight(400)
        tl.addWidget(table)
        layout.addWidget(table_card)

        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)


# ─── Рабочее место официанта ───────────────────────────────────

def _make_order_card(order: dict, highlight: bool = False, on_open=None) -> QFrame:
    """OrderCard как в React: highlight для готовых заказов."""
    card = QFrame()
    if highlight:
        card.setStyleSheet(f"""
            background: rgba(63,166,107,0.06);
            border: 1px solid rgba(63,166,107,0.25);
            border-radius: 12px;
        """)
    else:
        card.setStyleSheet(f"""
            background: {BG_CARD};
            border: 1px solid {BORDER};
            border-radius: 12px;
        """)
    cl = QVBoxLayout(card)
    cl.setContentsMargins(18, 18, 18, 18)
    cl.setSpacing(8)

    # Highlight top gradient line
    if highlight:
        top_line = QFrame()
        top_line.setFixedHeight(3)
        top_line.setStyleSheet("background: qlinearGradient(x1:0,y1:0,x2:1,y2:0, stop:0 #3FA66B, stop:1 #1F6F50);")
        cl.addWidget(top_line)

    # Header row
    hdr = QHBoxLayout()
    hdr.addWidget(make_manrope_label(f"#{order['id']}", 16, QFont.Weight.ExtraBold, GOLD))
    hdr.addStretch()
    cfg = ORDER_STATUS_CONFIG.get(order["status"], {})
    hdr.addWidget(StatusBadge(cfg))
    cl.addLayout(hdr)

    cl.addWidget(make_label(f"Столик №{order.get('table_number', '?')}", 12, TEXT_SECONDARY))

    # Elapsed time
    elapsed = QHBoxLayout()
    elapsed.addWidget(QLabel("⏱"))
    elapsed.addWidget(make_label("~30 мин назад", 12, TEXT_MUTED))
    cl.addLayout(elapsed)

    # Bottom: amount + open button
    bottom = QHBoxLayout()
    total = float(order.get("final_amount", order.get("total_amount", 0)))
    bottom.addWidget(make_manrope_label(
        f"{total:,.0f} ₽".replace(",", " "),
        16, QFont.Weight.Bold, TEXT_PRIMARY
    ))
    bottom.addStretch()
    if on_open:
        btn_color = "#3FA66B" if highlight else GOLD
        btn = QPushButton("Открыть")
        btn.setStyleSheet(f"""
            background: rgba({','.join(map(str, hex_to_rgb(btn_color)))}, 0.1);
            border: 1px solid rgba({','.join(map(str, hex_to_rgb(btn_color)))}, 0.25);
            border-radius: 8px; color: {btn_color};
            font-size: 12px; font-weight: 600; padding: 6px 12px;
        """)
        btn.clicked.connect(on_open)
        bottom.addWidget(btn)
    cl.addLayout(bottom)
    return card


class WaiterWorkspace(QWidget):
    def __init__(self, on_navigate=None):
        super().__init__()
        self._navigate = on_navigate
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(24)

        try:
            all_tables = get_all_tables()
            free_count = sum(1 for t in all_tables if t["status"] == "free")
            occupied_count = sum(1 for t in all_tables if t["status"] == "occupied")
            active_orders = get_active_orders()
            ready_orders = [o for o in active_orders if o["status"] == "ready"]
            working_orders = [o for o in active_orders if o["status"] in ("new", "cooking")]
        except:
            free_count = occupied_count = ready_count = working_count = 0
            ready_orders = []
            working_orders = []

        # Header
        header = QHBoxLayout()
        hleft = QVBoxLayout()
        hleft.addWidget(make_manrope_label("Рабочее место", 24, QFont.Weight.ExtraBold))
        hleft.addWidget(make_label("Добрый вечер · 18 июня 2026", 13, TEXT_MUTED))
        header.addLayout(hleft)
        header.addStretch()
        new_btn = QPushButton("➕ Создать заказ")
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_btn.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {GOLD}, stop:1 {GOLD_DARK});
            color: {BG_PRIMARY}; border: none; border-radius: 10px;
            font-size: 14px; font-weight: 700; padding: 12px 22px;
        """)
        if self._navigate:
            new_btn.clicked.connect(lambda: self._navigate("new-order"))
        header.addWidget(new_btn)
        layout.addLayout(header)

        # Summary cards (с иконками — как в React)
        summary = QHBoxLayout()
        summary.setSpacing(16)
        for icon_text, label, value, color in [
            ("🪑", "Свободные столики", str(free_count), SUCCESS),
            ("🪑", "Занятые столики", str(occupied_count), WARNING),
            ("✅", "Готовые заказы", str(len(ready_orders)), GOLD),
            ("⏳", "Заказы в работе", str(len(working_orders)), INFO),
        ]:
            card = QFrame()
            card.setStyleSheet(f"""
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            """)
            cl = QHBoxLayout(card)
            cl.setContentsMargins(20, 20, 20, 20)
            cl.setSpacing(16)
            # Icon box
            icon_frame = QFrame()
            icon_frame.setFixedSize(48, 48)
            icon_frame.setStyleSheet(f"""
                background: rgba({','.join(map(str, hex_to_rgb(color)))}, 0.07);
                border: 1px solid rgba({','.join(map(str, hex_to_rgb(color)))}, 0.13);
                border-radius: 12px;
            """)
            il = QVBoxLayout(icon_frame)
            il.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl = QLabel(icon_text)
            lbl.setStyleSheet(f"font-size: 22px; background: transparent;")
            il.addWidget(lbl)
            cl.addWidget(icon_frame)
            # Value + label
            vl = QVBoxLayout()
            vl.addWidget(make_manrope_label(value, 28, QFont.Weight.ExtraBold, TEXT_PRIMARY))
            vl.addWidget(make_label(label, 12, TEXT_SECONDARY))
            cl.addLayout(vl)
            cl.addStretch()
            summary.addWidget(card)
        layout.addLayout(summary)

        # Ready orders section (как в React — с зелёным хайлайтом)
        if ready_orders:
            ready_header = QHBoxLayout()
            ready_header.addWidget(make_manrope_label("Готовы к подаче", 16, QFont.Weight.Bold))
            count_badge = QFrame()
            count_badge.setFixedSize(30, 22)
            count_badge.setStyleSheet(f"""
                background: rgba(63,166,107,0.15);
                border: 1px solid rgba(63,166,107,0.25);
                border-radius: 11px;
            """)
            cbl = QVBoxLayout(count_badge)
            cbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cbl.setContentsMargins(6, 0, 6, 0)
            cbl.addWidget(make_label(str(len(ready_orders)), 12, SUCCESS, QFont.Weight.Bold))
            ready_header.addWidget(count_badge)
            ready_header.addStretch()
            layout.addLayout(ready_header)

            orders_grid = QHBoxLayout()
            orders_grid.setSpacing(14)
            for o in ready_orders[:6]:
                orders_grid.addWidget(_make_order_card(
                    o, highlight=True,
                    on_open=lambda: self._navigate("order-details") if self._navigate else None
                ))
            layout.addLayout(orders_grid)

        # Active orders
        active_section = QHBoxLayout()
        active_section.addWidget(make_manrope_label("Активные заказы", 16, QFont.Weight.Bold))
        count_badge2 = QFrame()
        count_badge2.setFixedSize(30, 22)
        count_badge2.setStyleSheet(f"""
            background: rgba(74,123,208,0.15);
            border: 1px solid rgba(74,123,208,0.25);
            border-radius: 11px;
        """)
        cbl2 = QVBoxLayout(count_badge2)
        cbl2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cbl2.setContentsMargins(6, 0, 6, 0)
        cbl2.addWidget(make_label(str(len(working_orders)), 12, INFO, QFont.Weight.Bold))
        active_section.addWidget(count_badge2)
        active_section.addStretch()
        layout.addLayout(active_section)

        if working_orders:
            orders_grid2 = QHBoxLayout()
            orders_grid2.setSpacing(14)
            for o in working_orders[:6]:
                orders_grid2.addWidget(_make_order_card(
                    o, highlight=False,
                    on_open=lambda: self._navigate("order-details") if self._navigate else None
                ))
            layout.addLayout(orders_grid2)
        else:
            empty_frame = QFrame()
            empty_frame.setStyleSheet(f"""
                background: {BG_CARD};
                border: 1px dashed {BORDER};
                border-radius: 12px;
            """)
            empty_frame.setMinimumHeight(80)
            el = QVBoxLayout(empty_frame)
            el.setAlignment(Qt.AlignmentFlag.AlignCenter)
            el.addWidget(make_label("Нет активных заказов", 14, TEXT_MUTED))
            layout.addWidget(empty_frame)

        # Tables quick view
        tables_header = QHBoxLayout()
        tables_header.addWidget(make_manrope_label("Мои столики", 16, QFont.Weight.Bold))
        tables_header.addStretch()
        if self._navigate:
            all_btn = SecondaryButton("Все столики →")
            all_btn.clicked.connect(lambda: self._navigate("tables"))
            tables_header.addWidget(all_btn)
        layout.addLayout(tables_header)

        tables_grid = QHBoxLayout()
        tables_grid.setSpacing(12)
        try:
            tables = get_all_tables()
        except:
            tables = []

        for t in tables[:10]:
            cfg = TABLE_STATUS_CONFIG.get(t["status"], {})
            color = cfg.get("color", DISABLED)
            card = QFrame()
            card.setStyleSheet(f"""
                background: rgba({','.join(map(str, hex_to_rgb(color)))}, 0.06);
                border: 1px solid rgba({','.join(map(str, hex_to_rgb(color)))}, 0.2);
                border-radius: 10px;
            """)
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            cl = QVBoxLayout(card)
            cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.setSpacing(4)
            cl.addWidget(make_manrope_label(str(t["table_number"]), 20, QFont.Weight.ExtraBold))
            cl.addWidget(make_label(f"{t['seats_count']} мест", 10, TEXT_MUTED))
            cl.addSpacing(2)
            # Small status badge text
            badge_lbl = make_label(cfg.get("label", ""), 9, color, QFont.Weight.Bold)
            badge_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(badge_lbl)
            tables_grid.addWidget(card)
        layout.addLayout(tables_grid)

        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)


# ─── Столики ────────────────────────────────────────────────────

class TablesScreen(QWidget):
    def __init__(self, role: str = "admin", on_navigate=None):
        super().__init__()
        self._role = role
        self._navigate = on_navigate
        self._status_filter = "all"
        self._zone_filter = "all"
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        self._layout = QVBoxLayout(content)
        self._layout.setContentsMargins(28, 28, 28, 28)
        self._layout.setSpacing(20)

        self._refresh()
        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _refresh(self):
        # Clear layout
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        header = QHBoxLayout()
        hleft = QVBoxLayout()
        try:
            tables = get_all_tables()
        except:
            tables = []
        hleft.addWidget(make_manrope_label("Столики", 24, QFont.Weight.ExtraBold))
        hleft.addWidget(make_label(
            f"{len(tables)} столиков · {sum(1 for t in tables if t['status'] == 'occupied')} занято",
            13, TEXT_MUTED
        ))
        header.addLayout(hleft)
        header.addStretch()
        if self._role == "admin":
            header.addWidget(SecondaryButton("✏️ Изменить статус"))
            header.addWidget(PrimaryButton("➕ Добавить столик"))
        elif self._navigate:
            new_btn = PrimaryButton("➕ Создать заказ")
            new_btn.clicked.connect(lambda: self._navigate("new-order"))
            header.addWidget(new_btn)
        self._layout.addLayout(header)

        # Filters
        filters = QHBoxLayout()
        filters.setSpacing(6)
        for f_id, f_label in [
            ("all", "Все"), ("free", "Свободные"), ("occupied", "Занятые"),
            ("reserved", "Забронированные"), ("out_of_service", "Недоступные"),
        ]:
            btn = FilterTab(f_label, self._status_filter == f_id)
            btn.clicked.connect(lambda checked, fid=f_id: self._set_status_filter(fid))
            filters.addWidget(btn)
        self._layout.addLayout(filters)

        zone_filters = QHBoxLayout()
        zone_filters.setSpacing(6)
        for z_id, z_label in [
            ("all", "Все зоны"), ("Основной зал", "Основной зал"),
            ("VIP-зона", "VIP-зона"), ("Терраса", "Терраса"),
        ]:
            btn = FilterTab(z_label, self._zone_filter == z_id, INFO)
            btn.clicked.connect(lambda checked, zid=z_id: self._set_zone_filter(zid))
            zone_filters.addWidget(btn)
        self._layout.addLayout(zone_filters)

        # Table grid
        grid = QGridLayout()
        grid.setSpacing(16)

        filtered = [
            t for t in tables
            if (self._status_filter == "all" or t["status"] == self._status_filter)
            and (self._zone_filter == "all" or t["zone"] == self._zone_filter)
        ]

        for i, t in enumerate(filtered):
            card = self._make_table_card(t)
            grid.addWidget(card, i // 4, i % 4)

        if not filtered:
            empty_lbl = make_label("Нет столиков по выбранным фильтрам", 14, TEXT_MUTED)
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setMinimumHeight(120)
            grid.addWidget(empty_lbl, 0, 0, 1, 4)

        self._layout.addLayout(grid)

    def _set_status_filter(self, fid: str):
        self._status_filter = fid
        self._refresh()

    def _set_zone_filter(self, zid: str):
        self._zone_filter = zid
        self._refresh()

    def _make_table_card(self, t: dict) -> QFrame:
        cfg = TABLE_STATUS_CONFIG.get(t["status"], {})
        color = cfg.get("color", DISABLED)

        _base_bg = BG_CARD
        _hover_bg = BG_ELEVATED
        _base_border = f"rgba({','.join(map(str, hex_to_rgb(color)))}, 0.2)"
        _hover_border = f"rgba({','.join(map(str, hex_to_rgb(color)))}, 0.4)"
        _border_r = "14px"

        class HoverCard(QFrame):
            def enterEvent(self, event):
                self.setStyleSheet(
                    f"background: {_hover_bg};"
                    f"border: 1px solid {_hover_border};"
                    f"border-radius: {_border_r};"
                )

            def leaveEvent(self, event):
                self.setStyleSheet(
                    f"background: {_base_bg};"
                    f"border: 1px solid {_base_border};"
                    f"border-radius: {_border_r};"
                )

        card = HoverCard()
        card.setStyleSheet(f"""
            background: {_base_bg};
            border: 1px solid {_base_border};
            border-radius: {_border_r};
        """)
        card.setMinimumSize(240, 180)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 20, 20, 20)
        cl.setSpacing(8)

        # Top gradient line
        line = QFrame()
        line.setFixedHeight(3)
        line.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {color}, stop:1 {color}88);
            border-radius: 2px;
        """)
        cl.addWidget(line)

        # Header
        hdr = QHBoxLayout()
        hdr.addWidget(make_manrope_label(f"Столик №{t['table_number']}", 20, QFont.Weight.ExtraBold))
        hdr.addStretch()
        badge = StatusBadge(cfg)
        hdr.addWidget(badge)
        cl.addLayout(hdr)

        cl.addWidget(make_label(t.get("zone", ""), 12, TEXT_MUTED))
        cl.addWidget(make_label(
            f"{t['seats_count']} мест",
            13, TEXT_SECONDARY
        ))

        if t["status"] == "occupied":
            info = QFrame()
            info.setStyleSheet(f"""
                background: rgba({','.join(map(str, hex_to_rgb(WARNING)))}, 0.08);
                border: 1px solid rgba({','.join(map(str, hex_to_rgb(WARNING)))}, 0.15);
                border-radius: 8px;
            """)
            il = QVBoxLayout(info)
            il.setContentsMargins(12, 10, 12, 10)
            il.addWidget(make_label("Активный заказ", 11, TEXT_MUTED))
            order_row = QHBoxLayout()
            order_row.addWidget(make_manrope_label(f"#{t.get('order_id', '?')}", 14, QFont.Weight.Bold, GOLD))
            order_row.addStretch()
            order_row.addWidget(make_manrope_label(
                f"{t.get('amount', 0):,.0f} ₽".replace(",", " "),
                14, QFont.Weight.Bold, WARNING
            ))
            il.addLayout(order_row)
            cl.addWidget(info)

        # Actions
        actions = QHBoxLayout()
        if self._role == "waiter" and t["status"] == "free" and self._navigate:
            btn = PrimaryButton("Создать заказ")
            btn.clicked.connect(lambda: self._navigate("new-order"))
            actions.addWidget(btn)
        elif self._role == "admin":
            actions.addWidget(SecondaryButton("✏️ Изменить"))
            actions.addWidget(SecondaryButton("⚙️ Статус"))
        elif self._role == "waiter" and t["status"] == "occupied" and self._navigate:
            btn = SecondaryButton("Открыть заказ")
            btn.clicked.connect(lambda: self._navigate("order-details"))
            actions.addWidget(btn)
        cl.addLayout(actions)

        return card


# ─── Новый заказ ────────────────────────────────────────────────

class NewOrderScreen(QWidget):
    def __init__(self, on_navigate=None):
        super().__init__()
        self._navigate = on_navigate
        self._cart: list[dict] = []
        self._selected_table_id = None
        self._customer_name = ""
        self._discount = 0
        self._active_category = "Горячие блюда"
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left panel - table & customer
        left = QWidget()
        left.setFixedWidth(220)
        left.setStyleSheet(f"background: {BG_SECONDARY}; border-right: 1px solid {BORDER};")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(20, 20, 20, 20)
        ll.setSpacing(16)

        ll.addWidget(make_manrope_label("Столик", 15, QFont.Weight.Bold))

        try:
            free_tables = get_free_tables()
        except:
            free_tables = []

        self._table_combo = QComboBox()
        self._table_combo.setStyleSheet(f"""
            QComboBox {{
                background: {BG_CARD}; color: {TEXT_PRIMARY};
                border: 1px solid {BORDER}; border-radius: 8px;
                padding: 9px 12px; font-size: 13px;
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{
                background: {BG_CARD}; color: {TEXT_PRIMARY};
                border: 1px solid {BORDER}; border-radius: 6px;
                selection-background-color: rgba(201,164,92,0.15);
            }}
        """)
        for t in free_tables:
            self._table_combo.addItem(f"Столик №{t['table_number']} ({t.get('zone','')})", t["id"])
        if free_tables:
            self._selected_table_id = free_tables[0]["id"]
        self._table_combo.currentIndexChanged.connect(self._on_table_changed)
        ll.addWidget(self._table_combo)

        # Table info
        self._table_info = Card()
        ti_layout = QVBoxLayout(self._table_info)
        ti_layout.setContentsMargins(12, 12, 12, 12)
        ti_layout.addWidget(make_manrope_label("Столик №—", 18, QFont.Weight.ExtraBold, GOLD))
        ti_layout.addWidget(make_label("", 12, TEXT_SECONDARY))
        ti_layout.addWidget(make_label("", 12, TEXT_MUTED))
        ll.addWidget(self._table_info)

        ll.addWidget(make_manrope_label("Клиент", 15, QFont.Weight.Bold))
        self._customer_input = QLineEdit()
        self._customer_input.setPlaceholderText("Добавить клиента")
        self._customer_input.setStyleSheet(f"""
            background: {BG_CARD}; color: {TEXT_PRIMARY};
            border: 1px solid {BORDER}; border-radius: 8px;
            padding: 8px 12px; font-size: 13px;
        """)
        self._customer_input.textChanged.connect(self._on_customer_changed)
        ll.addWidget(self._customer_input)

        self._discount_layout = QVBoxLayout()
        ll.addLayout(self._discount_layout)
        ll.addStretch()

        # Center - menu
        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        # Category tabs
        cat_bar = QWidget()
        cat_bar.setStyleSheet(f"background: {BG_SECONDARY}; border-bottom: 1px solid {BORDER};")
        cat_layout = QHBoxLayout(cat_bar)
        cat_layout.setContentsMargins(20, 0, 20, 0)
        cat_layout.setSpacing(0)

        categories = ["Салаты", "Супы", "Горячие блюда", "Напитки", "Десерты", "Закуски"]
        for cat in categories:
            btn = QPushButton(cat)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            active = cat == self._active_category
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: none;
                    border-bottom: 2px solid {'{GOLD}' if active else 'transparent'};
                    color: {'{GOLD}' if active else '{TEXT_SECONDARY}'};
                    font-size: 13px; font-weight: {'600' if active else '400'};
                    padding: 14px 16px;
                }}
                QPushButton:hover {{ color: {TEXT_PRIMARY}; }}
            """)
            btn.clicked.connect(lambda checked, c=cat: self._set_category(c))
            cat_layout.addWidget(btn)
        cat_layout.addStretch()
        center_layout.addWidget(cat_bar)

        # Search
        search_bar = QWidget()
        search_bar.setStyleSheet(f"border-bottom: 1px solid rgba(48, 52, 59, 0.13);")
        s_layout = QHBoxLayout(search_bar)
        s_layout.setContentsMargins(20, 14, 20, 14)
        self._dish_search = QLineEdit()
        self._dish_search.setPlaceholderText("Найти блюдо")
        self._dish_search.setStyleSheet(f"""
            background: {BG_CARD}; color: {TEXT_PRIMARY};
            border: 1px solid {BORDER}; border-radius: 8px;
            padding: 8px 12px; font-size: 13px;
            max-width: 280px;
        """)
        self._dish_search.textChanged.connect(self._refresh_dishes)
        s_layout.addWidget(self._dish_search)
        s_layout.addStretch()
        center_layout.addWidget(search_bar)

        # Dishes grid
        self._dishes_scroll = QScrollArea()
        self._dishes_scroll.setWidgetResizable(True)
        self._dishes_scroll.setStyleSheet("QScrollArea { border: none; }")
        self._dishes_container = QWidget()
        self._dishes_grid = QGridLayout(self._dishes_container)
        self._dishes_grid.setSpacing(12)
        self._dishes_scroll.setWidget(self._dishes_container)
        center_layout.addWidget(self._dishes_scroll, 1)

        # Right - cart
        right = QWidget()
        right.setFixedWidth(300)
        right.setStyleSheet(f"background: {BG_SECONDARY}; border-left: 1px solid {BORDER};")

        self._cart_layout = QVBoxLayout(right)
        self._cart_layout.setContentsMargins(0, 0, 0, 0)

        # Cart header
        cart_hdr = QWidget()
        cart_hdr.setStyleSheet(f"border-bottom: 1px solid {BORDER};")
        ch_layout = QHBoxLayout(cart_hdr)
        ch_layout.setContentsMargins(20, 18, 20, 18)
        ch_layout.addWidget(make_manrope_label("Заказ", 15, QFont.Weight.Bold))
        self._cart_count = make_label("0 позиций", 12, GOLD, QFont.Weight.Bold)
        ch_layout.addWidget(self._cart_count)
        self._cart_layout.addWidget(cart_hdr)

        self._cart_scroll = QScrollArea()
        self._cart_scroll.setWidgetResizable(True)
        self._cart_scroll.setStyleSheet("QScrollArea { border: none; }")
        self._cart_items = QWidget()
        self._cart_items_layout = QVBoxLayout(self._cart_items)
        self._cart_items_layout.setContentsMargins(16, 12, 16, 12)
        self._cart_items_layout.setSpacing(8)
        self._cart_scroll.setWidget(self._cart_items)
        self._cart_layout.addWidget(self._cart_scroll, 1)

        # Cart total
        self._cart_total = QWidget()
        self._cart_total.setStyleSheet(f"border-top: 1px solid {BORDER};")
        ctl = QVBoxLayout(self._cart_total)
        ctl.setContentsMargins(20, 16, 20, 16)
        ctl.setSpacing(6)

        self._subtotal_lbl = make_label("Сумма: 0 ₽", 13, TEXT_SECONDARY)
        ctl.addWidget(self._subtotal_lbl)
        self._discount_lbl = make_label("", 13, SUCCESS)
        ctl.addWidget(self._discount_lbl)
        self._total_lbl = make_manrope_label("Итого к оплате: 0 ₽", 17, QFont.Weight.ExtraBold, GOLD)
        ctl.addWidget(self._total_lbl)
        ctl.addSpacing(8)

        create_btn = PrimaryButton("Создать заказ")
        create_btn.clicked.connect(self._create_order)
        ctl.addWidget(create_btn)
        clear_btn = SecondaryButton("Очистить")
        clear_btn.clicked.connect(self._clear_cart)
        ctl.addWidget(clear_btn)
        self._cart_layout.addWidget(self._cart_total)

        main_layout.addWidget(left)
        main_layout.addWidget(center, 1)
        main_layout.addWidget(right)

        self._refresh_dishes()

    def _set_category(self, cat: str):
        self._active_category = cat
        self._refresh_dishes()

    def _refresh_dishes(self):
        # Clear grid
        while self._dishes_grid.count():
            item = self._dishes_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            all_dishes = get_all_dishes()
        except:
            all_dishes = []

        search_text = self._dish_search.text().lower()
        filtered = [
            d for d in all_dishes
            if d["category_name"] == self._active_category
            and (not search_text or search_text in d["name"].lower())
        ]

        for i, dish in enumerate(filtered):
            card = self._make_dish_card(dish)
            self._dishes_grid.addWidget(card, i // 2, i % 2)

        if not filtered:
            empty = make_label("Нет блюд в этой категории", 13, TEXT_MUTED)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setMinimumHeight(100)
            self._dishes_grid.addWidget(empty, 0, 0, 1, 2)

    def _make_dish_card(self, dish: dict) -> QFrame:
        available = dish.get("is_available", True)
        card = QFrame()
        card.setStyleSheet(f"""
            background: {{BG_CARD if available else '#1A1D21'}};
            border: 1px solid {{BORDER if available else '#252932'}};
            border-radius: 12px;
        """)
        card.setMinimumSize(200, 140)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 16, 16, 16)
        cl.setSpacing(6)

        name_lbl = make_label(dish["name"], 14, TEXT_PRIMARY, QFont.Weight.DemiBold)
        cl.addWidget(name_lbl)

        if dish.get("description"):
            cl.addWidget(make_label(dish["description"], 11, TEXT_MUTED))

        info = QHBoxLayout()
        info.setSpacing(10)
        if dish.get("weight"):
            info.addWidget(make_label(f"⚖ {dish['weight']}", 11, TEXT_MUTED))
        if dish.get("cooking_time_minutes"):
            info.addWidget(make_label(f"⏱ {dish['cooking_time_minutes']} мин", 11, TEXT_MUTED))
        cl.addLayout(info)

        price_row = QHBoxLayout()
        price_row.addWidget(make_manrope_label(
            f"{float(dish['price']):,.0f} ₽".replace(",", " "),
            16, QFont.Weight.ExtraBold, GOLD
        ))
        price_row.addStretch()

        if available:
            add_btn = QPushButton("➕ Добавить")
            add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            add_btn.setStyleSheet(f"""
                background: rgba(201,164,92,0.12);
                border: 1px solid rgba(201,164,92,0.25);
                border-radius: 8px; color: {GOLD};
                font-size: 12px; font-weight: 600; padding: 6px 12px;
            """)
            add_btn.clicked.connect(lambda checked, d=dish: self._add_to_cart(d))
            price_row.addWidget(add_btn)
        cl.addLayout(price_row)

        return card

    def _add_to_cart(self, dish: dict):
        existing = next((i for i in self._cart if i["dish_id"] == dish["id"]), None)
        if existing:
            existing["quantity"] += 1
        else:
            self._cart.append({
                "dish_id": dish["id"],
                "dish_name": dish["name"],
                "price": float(dish["price"]),
                "quantity": 1,
                "comment": "",
            })
        self._update_cart()

    def _update_cart(self):
        # Clear cart items
        while self._cart_items_layout.count():
            item = self._cart_items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        total_qty = sum(i["quantity"] for i in self._cart)
        self._cart_count.setText(f"{total_qty} позиций")

        for item in self._cart:
            card = QFrame()
            card.setStyleSheet(f"""
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 10px;
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(12, 12, 12, 12)
            cl.setSpacing(6)

            name_row = QHBoxLayout()
            name_row.addWidget(make_label(item["dish_name"], 13, TEXT_PRIMARY, QFont.Weight.Medium))
            name_row.addStretch()
            cl.addLayout(name_row)

            qty_row = QHBoxLayout()
            qty_row.setSpacing(6)
            minus_btn = QPushButton("−")
            minus_btn.setFixedSize(24, 24)
            minus_btn.setStyleSheet(f"""
                background: {BG_ELEVATED}; border: 1px solid {BORDER};
                border-radius: 6px; color: {TEXT_SECONDARY};
                font-size: 12px; font-weight: bold;
            """)
            minus_btn.clicked.connect(lambda checked, d=item["dish_id"]: self._update_qty(d, -1))
            qty_row.addWidget(minus_btn)

            qty_lbl = make_label(str(item["quantity"]), 14, TEXT_PRIMARY, QFont.Weight.Bold)
            qty_row.addWidget(qty_lbl)

            plus_btn = QPushButton("+")
            plus_btn.setFixedSize(24, 24)
            plus_btn.setStyleSheet(f"""
                background: rgba(201,164,92,0.12); border: 1px solid rgba(201,164,92,0.25);
                border-radius: 6px; color: {GOLD};
                font-size: 12px; font-weight: bold;
            """)
            plus_btn.clicked.connect(lambda checked, d=item["dish_id"]: self._update_qty(d, 1))
            qty_row.addWidget(plus_btn)

            qty_row.addStretch()
            total = item["price"] * item["quantity"]
            qty_row.addWidget(make_manrope_label(
                f"{total:,.0f} ₽".replace(",", " "),
                14, QFont.Weight.Bold, GOLD
            ))
            cl.addLayout(qty_row)

            # Remove
            remove_btn = QPushButton("✕ Убрать")
            remove_btn.setStyleSheet(f"""
                background: transparent; border: none;
                color: {ERROR}; font-size: 11px;
                text-align: left;
            """)
            remove_btn.clicked.connect(lambda checked, d=item["dish_id"]: self._remove_from_cart(d))
            cl.addWidget(remove_btn)

            # Comment input (как в React)
            comment_input = QLineEdit(item.get("comment", ""))
            comment_input.setPlaceholderText("Комментарий")
            comment_input.setStyleSheet(f"""
                background: {BG_SECONDARY}; color: {TEXT_SECONDARY};
                border: 1px solid {BORDER}; border-radius: 6px;
                padding: 5px 8px; font-size: 11px;
            """)
            comment_input.textChanged.connect(
                lambda text, d=item["dish_id"]: self._update_comment(d, text)
            )
            cl.addWidget(comment_input)

            self._cart_items_layout.addWidget(card)

        self._cart_items_layout.addStretch()
        self._update_totals()

    def _update_qty(self, dish_id: int, delta: int):
        for item in self._cart:
            if item["dish_id"] == dish_id:
                item["quantity"] = max(1, item["quantity"] + delta)
                break
        self._update_cart()

    def _update_comment(self, dish_id: int, text: str):
        for item in self._cart:
            if item["dish_id"] == dish_id:
                item["comment"] = text
                break

    def _remove_from_cart(self, dish_id: int):
        self._cart = [i for i in self._cart if i["dish_id"] != dish_id]
        self._update_cart()

    def _clear_cart(self):
        self._cart.clear()
        self._update_cart()

    def _update_totals(self):
        subtotal = sum(i["price"] * i["quantity"] for i in self._cart)
        self._subtotal_lbl.setText(f"Сумма: {subtotal:,.0f} ₽".replace(",", " "))

        if self._discount > 0:
            discount_amt = round(subtotal * self._discount / 100)
            self._discount_lbl.setText(f"Скидка {self._discount}%: −{discount_amt:,.0f} ₽".replace(",", " "))
            total = subtotal - discount_amt
        else:
            self._discount_lbl.setText("")
            total = subtotal

        self._total_lbl.setText(f"Итого к оплате: {total:,.0f} ₽".replace(",", " "))

    def _on_table_changed(self, idx: int):
        try:
            free_tables = get_free_tables()
            if 0 <= idx < len(free_tables):
                t = free_tables[idx]
                self._selected_table_id = t["id"]
                ti_layout = self._table_info.layout()
                ti_layout.itemAt(0).widget().setText(f"Столик №{t['table_number']}")
                ti_layout.itemAt(1).widget().setText(t.get("zone", ""))
                ti_layout.itemAt(2).widget().setText(f"{t['seats_count']} мест")
        except:
            pass

    def _on_customer_changed(self, text: str):
        self._customer_name = text
        if text.strip():
            # Show discount input
            while self._discount_layout.count():
                item = self._discount_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self._discount_layout.addWidget(make_label("Скидка (%)", 11, TEXT_MUTED))
            self._discount_spin = QSpinBox()
            self._discount_spin.setRange(0, 30)
            self._discount_spin.valueChanged.connect(self._on_discount_changed)
            self._discount_spin.setStyleSheet(f"""
                background: {BG_CARD}; color: {GOLD};
                border: 1px solid {BORDER}; border-radius: 8px;
                padding: 8px; font-size: 14px; font-weight: 700;
            """)
            self._discount_layout.addWidget(self._discount_spin)

    def _on_discount_changed(self, val: int):
        self._discount = val
        self._update_totals()

    def _create_order(self):
        if not self._cart:
            QMessageBox.warning(self, "Ошибка", "Добавьте блюда в заказ")
            return
        if not self._selected_table_id:
            QMessageBox.warning(self, "Ошибка", "Выберите столик")
            return

        try:
            # Find customer by name
            customer_id = None
            if self._customer_name.strip():
                customers = find_customers(self._customer_name.strip())
                if customers:
                    customer_id = customers[0]["id"]

            # Create order
            order_id = create_order(self._selected_table_id, customer_id)

            # Add items
            for item in self._cart:
                add_order_item(
                    order_id, item["dish_id"], item["quantity"],
                    item["price"], item.get("comment", "")
                )

            # Update table status
            update_table_status(self._selected_table_id, "occupied")

            QMessageBox.information(self, "Успешно", f"Заказ #{order_id} создан!")
            self._clear_cart()
            if self._navigate:
                self._navigate("orders")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать заказ: {e}")


# ─── Детали заказа ──────────────────────────────────────────────

class OrderDetailsScreen(QWidget):
    def __init__(self, role: str = "admin", on_navigate=None):
        super().__init__()
        self._role = role
        self._navigate = on_navigate
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(20)

        # Back button
        if self._navigate:
            back_btn = QPushButton("← Назад к заказам")
            back_btn.setStyleSheet(f"""
                background: none; border: none;
                color: {TEXT_SECONDARY}; font-size: 13px;
                text-align: left;
            """)
            back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            back_btn.clicked.connect(lambda: self._navigate("orders"))
            layout.addWidget(back_btn)

        # Загружаем первый активный заказ для примера
        try:
            orders = get_all_orders()
            order = orders[0] if orders else None
        except:
            order = None

        if not order:
            layout.addWidget(make_label("Нет заказов для просмотра", 14, TEXT_MUTED))
            scroll.setWidget(content)
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.addWidget(scroll)
            return

        # Header
        header = QHBoxLayout()
        hleft = QVBoxLayout()
        hleft.addWidget(make_manrope_label(f"Заказ #{order['id']}", 26, QFont.Weight.ExtraBold))
        cfg = ORDER_STATUS_CONFIG.get(order["status"], {})
        hleft.addWidget(make_label(
            f"Столик №{order.get('table_number', '?')} · {order.get('customer_name', '—')} · Создан: {order.get('created_at', '')}",
            13, TEXT_SECONDARY
        ))

        header.addLayout(hleft)
        header.addStretch()
        badge = StatusBadge(cfg)
        header.addWidget(badge)
        layout.addLayout(header)

        # Main + sidebar
        content_row = QHBoxLayout()
        content_row.setSpacing(20)

        # Left - items table
        left_col = QVBoxLayout()
        left_col.setSpacing(16)

        try:
            items = get_order_items(order["id"])
        except:
            items = []

        table_card = Card()
        tl = QVBoxLayout(table_card)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.addWidget(SectionHeader("Состав заказа"))
        tl.addWidget(make_label("", 1))  # separator

        table = DataTable(["Блюдо", "Кол-во", "Цена", "Сумма", "Комментарий"])
        table.setRowCount(len(items))
        for i, item in enumerate(items):
            table.setItem(i, 0, QTableWidgetItem(item.get("dish_name", "—")))
            table.setItem(i, 1, QTableWidgetItem(str(item["quantity"])))
            table.setItem(i, 2, QTableWidgetItem(f"{float(item['price_at_order']):,.0f} ₽".replace(",", " ")))
            table.setItem(i, 3, QTableWidgetItem(f"{float(item['item_total']):,.0f} ₽".replace(",", " ")))
            table.setItem(i, 4, QTableWidgetItem(item.get("comment", "—") or "—"))
        tl.addWidget(table)
        left_col.addWidget(table_card)

        # Total
        total_card = Card()
        total_l = QVBoxLayout(total_card)
        total_l.setContentsMargins(24, 20, 24, 20)
        total_l.setSpacing(8)

        total_l.addWidget(make_label(f"Сумма: {float(order['total_amount']):,.0f} ₽".replace(",", " "), 14, TEXT_SECONDARY))
        if float(order["discount_amount"]) > 0:
            total_l.addWidget(make_label(
                f"Скидка: −{float(order['discount_amount']):,.0f} ₽".replace(",", " "),
                14, SUCCESS
            ))
        total_l.addWidget(make_manrope_label(
            f"Итого: {float(order['final_amount']):,.0f} ₽".replace(",", " "),
            18, QFont.Weight.ExtraBold, GOLD
        ))
        left_col.addWidget(total_card)

        # Actions
        actions = QHBoxLayout()
        actions.setSpacing(10)
        if self._role == "waiter":
            actions.addWidget(PrimaryButton("Добавить блюдо"))
            actions.addWidget(SecondaryButton("Изменить статус"))
            pay_btn = PrimaryButton("✅ Перейти к оплате")
            pay_btn.setStyleSheet(pay_btn.styleSheet().replace(
                f"stop:0 {GOLD}, stop:1 {GOLD_DARK}",
                f"stop:0 {SUCCESS}, stop:1 #2D8A55"
            ))
            actions.addWidget(pay_btn)
            actions.addWidget(DangerButton("Отменить заказ"))
        else:
            actions.addWidget(SecondaryButton("Редактировать заказ"))
            actions.addWidget(SecondaryButton("Просмотреть оплату"))
            actions.addWidget(SecondaryButton("История изменений"))
            actions.addWidget(DangerButton("Отменить заказ"))
        left_col.addLayout(actions)

        content_row.addLayout(left_col, 1)

        # Right panel - timeline & info
        right_col = QVBoxLayout()
        right_col.setSpacing(16)

        # Timeline
        timeline_card = Card()
        tml = QVBoxLayout(timeline_card)
        tml.setContentsMargins(20, 20, 20, 20)
        tml.addWidget(make_manrope_label("Статус заказа", 14, QFont.Weight.DemiBold))
        tml.addSpacing(12)

        status_order = [
            ("new", "Новый"), ("cooking", "Готовится"), ("ready", "Готов"),
            ("served", "Подан"), ("paid", "Оплачен"),
        ]
        current_idx = -1
        for i, (key, _) in enumerate(status_order):
            if key == order.get("status"):
                current_idx = i
                break

        for i, (key, label) in enumerate(status_order):
            step = QHBoxLayout()
            step.setSpacing(14)
            done = i <= current_idx
            current = i == current_idx

            dot = QLabel("●" if done else "○")
            dot.setStyleSheet(f"""
                font-size: 14px;
                color: {GOLD if current else (SUCCESS if done else TEXT_MUTED)};
                background: rgba(201,164,92,0.15) if current else (
                    rgba(63,166,107,0.1) if done else transparent);
                border: 2px solid {'{GOLD}' if current else ('{SUCCESS}' if done else '{BORDER}')};
                border-radius: 14px;
                padding: 4px;
            """)
            step.addWidget(dot)

            lbl = make_label(label, 13,
                             GOLD if current else (TEXT_PRIMARY if done else TEXT_MUTED),
                             QFont.Weight.Bold if current else QFont.Weight.Normal)
            step.addWidget(lbl)
            step.addStretch()
            tml.addLayout(step)

            if i < len(status_order) - 1:
                line = QFrame()
                line.setFixedWidth(2)
                line.setFixedHeight(20)
                line.setStyleSheet(f"""
                    background: {'{SUCCESS}44' if done and i < current_idx else BORDER};
                    margin-left: 10px;
                """)
                tml.addWidget(line, alignment=Qt.AlignmentFlag.AlignLeft)

        right_col.addWidget(timeline_card)

        # Info
        info_card = Card()
        il = QVBoxLayout(info_card)
        il.setContentsMargins(20, 18, 20, 18)
        il.addWidget(make_manrope_label("Информация", 14, QFont.Weight.DemiBold))
        il.addSpacing(14)
        info_data = [
            ("Клиент", order.get("customer_name", "—") or "—"),
            ("Столик", f"№{order.get('table_number', '?')}"),
            ("Создан", str(order.get("created_at", ""))),
            ("Позиций", f"{sum(i.get('quantity', 0) for i in items)} блюд" if items else "0"),
        ]
        for k, v in info_data:
            row = QHBoxLayout()
            row.addWidget(make_label(k, 12, TEXT_MUTED))
            row.addStretch()
            row.addWidget(make_label(v, 13, TEXT_SECONDARY, QFont.Weight.Medium))
            il.addLayout(row)
        right_col.addWidget(info_card)

        content_row.addLayout(right_col)
        layout.addLayout(content_row)

        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)


# ─── Список заказов ─────────────────────────────────────────────

class OrdersListScreen(QWidget):
    def __init__(self, role: str = "admin", on_navigate=None):
        super().__init__()
        self._role = role
        self._navigate = on_navigate
        self._status_filter = "all"
        self._search_text = ""
        self._selected_order_id = None
        self._orders_list = []
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Main list
        list_panel = QWidget()
        list_layout = QVBoxLayout(list_panel)
        list_layout.setContentsMargins(28, 24, 28, 24)
        list_layout.setSpacing(16)

        # Header
        list_layout.addWidget(make_manrope_label("Заказы", 24, QFont.Weight.ExtraBold))

        try:
            self._orders_list = get_all_orders()
            filtered = [
                o for o in self._orders_list
                if (self._status_filter == "all" or o["status"] == self._status_filter)
                and (not self._search_text or
                     self._search_text in str(o["id"]) or
                     self._search_text.lower() in (o.get("customer_name", "") or "").lower())
            ]
        except:
            filtered = []

        list_layout.addWidget(make_label(f"{len(filtered)} заказов", 13, TEXT_MUTED))

        # Filters
        filters = QHBoxLayout()
        filters.setSpacing(6)
        for f_id, f_label in [
            ("all", "Все"), ("new", "Новый"), ("cooking", "Готовится"),
            ("ready", "Готов"), ("served", "Подан"), ("paid", "Оплачен"),
            ("cancelled", "Отменен"),
        ]:
            btn = FilterTab(f_label, self._status_filter == f_id)
            btn.clicked.connect(lambda checked, fid=f_id: self._set_filter(fid))
            filters.addWidget(btn)

        # Search
        search = QLineEdit()
        search.setPlaceholderText("Поиск заказа или клиента")
        search.setStyleSheet(f"""
            background: {BG_CARD}; color: {TEXT_PRIMARY};
            border: 1px solid {BORDER}; border-radius: 8px;
            padding: 7px 12px; font-size: 13px;
            max-width: 220px;
        """)
        search.textChanged.connect(lambda t: self._search(t))
        filters.addWidget(search)
        list_layout.addLayout(filters)

        # Table
        table = DataTable([
            "№ заказа", "Столик", "Клиент", "Статус",
            "Сумма", "Скидка", "Итого", "Создан", "Действие"
        ])
        table.setRowCount(len(filtered))
        for i, o in enumerate(filtered):
            table.setItem(i, 0, QTableWidgetItem(f"#{o['id']}"))
            table.setItem(i, 1, QTableWidgetItem(f"Столик №{o.get('table_number', '?')}"))
            table.setItem(i, 2, QTableWidgetItem(o.get("customer_name", "—") or "—"))
            cfg = ORDER_STATUS_CONFIG.get(o["status"], {})
            table.setItem(i, 3, QTableWidgetItem(cfg.get("label", o["status"])))
            table.setItem(i, 4, QTableWidgetItem(f"{float(o['total_amount']):,.0f} ₽".replace(",", " ")))
            disc = float(o.get("discount_amount", 0))
            table.setItem(i, 5, QTableWidgetItem(
                f"−{disc:,.0f} ₽".replace(",", " ") if disc > 0 else "—"
            ))
            table.setItem(i, 6, QTableWidgetItem(
                f"{float(o['final_amount']):,.0f} ₽".replace(",", " ")
            ))
            table.setItem(i, 7, QTableWidgetItem(str(o.get("created_at", ""))))

            # Action
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(4)
            open_btn = QPushButton("Открыть")
            open_btn.setStyleSheet(f"""
                background: rgba(201,164,92,0.1);
                border: 1px solid rgba(201,164,92,0.2);
                border-radius: 6px;
                color: {GOLD}; font-size: 11px; font-weight: 600;
                padding: 5px 10px;
            """)
            if self._navigate:
                open_btn.clicked.connect(lambda checked, oid=o["id"]: self._navigate("order-details"))
            action_layout.addWidget(open_btn)

            if self._role == "waiter" and o["status"] not in ("paid", "cancelled"):
                pay_btn = QPushButton("Оплатить")
                pay_btn.setStyleSheet(f"""
                    background: rgba(63,166,107,0.1);
                    border: 1px solid rgba(63,166,107,0.2);
                    border-radius: 6px;
                    color: {SUCCESS}; font-size: 11px; font-weight: 600;
                    padding: 5px 10px;
                """)
                action_layout.addWidget(pay_btn)

            table.setCellWidget(i, 8, action_widget)

        # Row click -> select & show preview
        table.clicked.connect(lambda idx: self._select_order(
            filtered[idx.row()]["id"] if idx.row() < len(filtered) else None
        ))

        list_layout.addWidget(table, 1)
        main_layout.addWidget(list_panel, 1)

        # Right preview panel (interactive)
        self._preview_panel = QWidget()
        self._preview_panel.setFixedWidth(300)
        self._preview_panel.setStyleSheet(f"""
            background: {BG_SECONDARY};
            border-left: 1px solid {BORDER};
        """)
        self._preview_layout = QVBoxLayout(self._preview_panel)
        self._preview_layout.setContentsMargins(20, 24, 20, 24)
        self._preview_layout.setSpacing(12)
        self._show_empty_preview()
        main_layout.addWidget(self._preview_panel)

    def _show_empty_preview(self):
        """Default preview placeholder when no order selected."""
        while self._preview_layout.count():
            item = self._preview_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._preview_layout.addWidget(make_manrope_label("Детали заказа", 16, QFont.Weight.Bold))
        self._preview_layout.addSpacing(8)
        lbl = make_label("Нажмите на заказ в таблице\nчтобы увидеть подробности", 13, TEXT_MUTED)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_layout.addWidget(lbl, 1)

    def _show_order_preview(self, order: dict):
        """Show order details in the right preview panel."""
        while self._preview_layout.count():
            item = self._preview_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cfg = ORDER_STATUS_CONFIG.get(order["status"], {})

        # Header
        self._preview_layout.addWidget(make_manrope_label(
            f"Заказ #{order['id']}", 18, QFont.Weight.ExtraBold
        ))
        self._preview_layout.addWidget(StatusBadge(cfg))

        # Info rows
        info_data = [
            ("Столик", f"№{order.get('table_number', '?')}"),
            ("Клиент", order.get("customer_name", "—") or "—"),
            ("Создан", str(order.get("created_at", ""))),
        ]
        for k, v in info_data:
            row = QHBoxLayout()
            row.setSpacing(8)
            row.addWidget(make_label(k, 12, TEXT_MUTED))
            row.addStretch()
            row.addWidget(make_label(v, 13, TEXT_SECONDARY, QFont.Weight.Medium))
            self._preview_layout.addLayout(row)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER};")
        self._preview_layout.addWidget(sep)

        # Items
        try:
            items = get_order_items(order["id"])
        except:
            items = []
        self._preview_layout.addWidget(make_label(f"Позиции ({len(items)})", 12, TEXT_MUTED))

        for item in items[:5]:  # Show top 5
            item_row = QHBoxLayout()
            item_row.setSpacing(8)
            item_row.addWidget(make_label(
                f"×{item['quantity']}", 13, GOLD, QFont.Weight.Bold
            ))
            item_row.addWidget(make_label(
                item.get("dish_name", "—"), 13, TEXT_PRIMARY
            ))
            item_row.addStretch()
            item_row.addWidget(make_label(
                f"{float(item['item_total']):,.0f} ₽".replace(",", " "),
                13, TEXT_SECONDARY
            ))
            self._preview_layout.addLayout(item_row)

        if len(items) > 5:
            self._preview_layout.addWidget(make_label(
                f"и ещё {len(items) - 5} позиций...", 11, TEXT_MUTED
            ))

        self._preview_layout.addStretch()

        # Totals
        total_card = QFrame()
        total_card.setStyleSheet(f"""
            background: {BG_CARD};
            border: 1px solid {BORDER};
            border-radius: 10px;
        """)
        tl = QVBoxLayout(total_card)
        tl.setContentsMargins(16, 14, 16, 14)
        tl.setSpacing(6)
        tl.addWidget(make_label(
            f"Сумма: {float(order['total_amount']):,.0f} ₽".replace(",", " "),
            13, TEXT_SECONDARY
        ))
        if float(order.get("discount_amount", 0)) > 0:
            tl.addWidget(make_label(
                f"Скидка: −{float(order['discount_amount']):,.0f} ₽".replace(",", " "),
                13, SUCCESS
            ))
        tl.addWidget(make_manrope_label(
            f"Итого: {float(order['final_amount']):,.0f} ₽".replace(",", " "),
            16, QFont.Weight.ExtraBold, GOLD
        ))
        self._preview_layout.addWidget(total_card)

        # Action button
        if self._navigate:
            open_btn = PrimaryButton("📄 Открыть заказ")
            open_btn.clicked.connect(lambda: self._navigate("order-details"))
            self._preview_layout.addWidget(open_btn)

    def _select_order(self, order_id):
        self._selected_order_id = order_id
        if order_id is None:
            self._show_empty_preview()
            return
        for o in self._orders_list:
            if o["id"] == order_id:
                self._show_order_preview(o)
                return
        self._show_empty_preview()

    def _set_filter(self, fid: str):
        self._status_filter = fid
        self._setup_ui()

    def _search(self, text: str):
        self._search_text = text
        self._setup_ui()


# ─── Меню ───────────────────────────────────────────────────────

class MenuScreen(QWidget):
    def __init__(self, role: str = "admin"):
        super().__init__()
        self._role = role
        self._category = "Все"
        self._avail_filter = "Все блюда"
        self._search = ""
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left sidebar - categories
        left = QWidget()
        left.setFixedWidth(200)
        left.setStyleSheet(f"""
            background: {BG_SECONDARY};
            border-right: 1px solid {BORDER};
        """)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(14, 24, 14, 24)
        ll.addWidget(make_label("КАТЕГОРИИ", 11, TEXT_MUTED))
        ll.addSpacing(8)

        try:
            all_dishes_list = get_all_dishes()
            cats = ["Все"] + [c["name"] for c in get_all_categories()]
        except:
            cats = ["Все"]

        # Count dishes per category
        cat_counts = {}
        try:
            for d in all_dishes_list:
                cat_name = d.get("category_name", "") or d.get("category", "") or ""
                cat_counts[cat_name] = cat_counts.get(cat_name, 0) + 1
        except:
            pass
        total_ct = sum(cat_counts.values())

        for cat in cats:
            # Category button row: name + count badge
            cat_frame = QFrame()
            cat_frame.setCursor(Qt.CursorShape.PointingHandCursor)
            active = cat == self._category
            cat_frame.setStyleSheet(f"""
                QFrame {{
                    padding: 0px;
                    border-radius: 8px;
                    background: {'rgba(201,164,92,0.1)' if active else 'transparent'};
                }}
            """)
            cat_layout = QHBoxLayout(cat_frame)
            cat_layout.setContentsMargins(12, 9, 12, 9)
            cat_layout.setSpacing(4)

            name_lbl = make_label(cat, 13, GOLD if active else TEXT_SECONDARY,
                                  QFont.Weight.Medium if active else QFont.Weight.Normal)
            cat_layout.addWidget(name_lbl)

            cat_layout.addStretch()

            count = total_ct if cat == "Все" else cat_counts.get(cat, 0)
            count_lbl = make_label(str(count), 11, TEXT_MUTED)
            cat_layout.addWidget(count_lbl)

            # Click event via mouse press
            def _make_handler(c):
                def handler(event):
                    if event.button() == Qt.MouseButton.LeftButton:
                        self._set_category(c)
                return handler
            cat_frame.mousePressEvent = _make_handler(cat)

            ll.addWidget(cat_frame)
        ll.addStretch()
        main_layout.addWidget(left)

        # Right content
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(24, 24, 24, 24)
        rl.setSpacing(16)

        # Header
        header = QHBoxLayout()
        hleft = QVBoxLayout()
        hleft.addWidget(make_manrope_label("Меню", 24, QFont.Weight.ExtraBold))
        try:
            hleft.addWidget(make_label(f"{len(all_dishes_list)} блюд", 13, TEXT_MUTED))
        except:
            pass
        header.addLayout(hleft)
        header.addStretch()
        if self._role == "admin":
            header.addWidget(PrimaryButton("➕ Добавить блюдо"))
        rl.addLayout(header)

        # Filters
        filters = QHBoxLayout()
        filters.setSpacing(8)
        for f in ["Все блюда", "Доступные", "Недоступные"]:
            btn = FilterTab(f, self._avail_filter == f)
            btn.clicked.connect(lambda checked, ff=f: self._set_avail(ff))
            filters.addWidget(btn)

        search = QLineEdit()
        search.setPlaceholderText("🔍 Найти блюдо")
        search.setStyleSheet(f"""
            background: {BG_CARD}; color: {TEXT_PRIMARY};
            border: 1px solid {BORDER}; border-radius: 8px;
            padding: 7px 12px; font-size: 13px;
            max-width: 280px;
        """)
        search.textChanged.connect(lambda t: self._set_search(t))
        filters.addWidget(search)
        filters.addStretch()
        rl.addLayout(filters)

        # Dishes grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        grid_widget = QWidget()
        self._grid = QGridLayout(grid_widget)
        self._grid.setSpacing(14)
        scroll.setWidget(grid_widget)
        rl.addWidget(scroll, 1)

        self._refresh_grid()
        main_layout.addWidget(right, 1)

    def _set_category(self, cat: str):
        self._category = cat
        self._refresh_grid()

    def _set_avail(self, f: str):
        self._avail_filter = f
        self._refresh_grid()

    def _set_search(self, s: str):
        self._search = s.lower()
        self._refresh_grid()

    def _refresh_grid(self):
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            dishes_list = get_all_dishes()
        except:
            dishes_list = []

        filtered = [
            d for d in dishes_list
            if (self._category == "Все" or d.get("category_name") == self._category)
            and (self._avail_filter == "Все блюда" or
                 (self._avail_filter == "Доступные" and d["is_available"]) or
                 (self._avail_filter == "Недоступные" and not d["is_available"]))
            and (not self._search or self._search in d["name"].lower())
        ]

        for i, dish in enumerate(filtered):
            card = self._make_dish_card(dish)
            self._grid.addWidget(card, i // 3, i % 3)

        if not filtered:
            empty = make_label("Нет блюд по выбранным фильтрам", 14, TEXT_MUTED)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setMinimumHeight(120)
            self._grid.addWidget(empty, 0, 0, 1, 3)

    def _make_dish_card(self, dish: dict) -> QFrame:
        available = dish.get("is_available", True)
        card = QFrame()
        card.setStyleSheet(f"""
            background: {BG_CARD if available else '#1A1D21'};
            border: 1px solid {BORDER if available else '#252932'};
            border-radius: 12px;
        """)
        card.setMinimumSize(260, 160)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(18, 18, 18, 18)
        cl.setSpacing(6)

        if not available:
            cl.addWidget(QLabel("Недоступно"), alignment=Qt.AlignmentFlag.AlignRight)

        cl.addWidget(make_label(dish["name"], 14, TEXT_PRIMARY, QFont.Weight.DemiBold))
        cl.addWidget(make_label(dish.get("category_name", ""), 11, TEXT_MUTED))
        if dish.get("description"):
            cl.addWidget(make_label(dish["description"], 12, TEXT_SECONDARY))
        cl.addSpacing(4)

        info = QHBoxLayout()
        info.setSpacing(12)
        if dish.get("weight"):
            info.addWidget(make_label(f"⚖ {dish['weight']}", 12, TEXT_MUTED))
        if dish.get("cooking_time_minutes"):
            info.addWidget(make_label(f"⏱ {dish['cooking_time_minutes']} мин", 12, TEXT_MUTED))
        cl.addLayout(info)

        price_row = QHBoxLayout()
        price_row.addWidget(make_manrope_label(
            f"{float(dish['price']):,.0f} ₽".replace(",", " "),
            18, QFont.Weight.ExtraBold, GOLD
        ))
        price_row.addStretch()

        if self._role == "admin":
            edit_btn = SecondaryButton("✏️ Редактировать")
            price_row.addWidget(edit_btn)
        else:
            status_text = "Доступно" if available else "Недоступно"
            status_color = SUCCESS if available else DISABLED
            badge = QPushButton(status_text)
            badge.setStyleSheet(f"""
                background: rgba({','.join(map(str, hex_to_rgb(status_color)))}, 0.12);
                border: 1px solid rgba({','.join(map(str, hex_to_rgb(status_color)))}, 0.2);
                border-radius: 20px;
                color: {status_color}; font-size: 11px; font-weight: 600;
                padding: 3px 10px;
            """)
            price_row.addWidget(badge)
        cl.addLayout(price_row)

        return card


# ─── Клиенты ────────────────────────────────────────────────────

class CustomersScreen(QWidget):
    def __init__(self, role: str = "admin"):
        super().__init__()
        self._role = role
        self._search = ""
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(20)

        if self._role == "waiter":
            # Simplified waiter view
            layout.addWidget(make_manrope_label("Клиенты", 24, QFont.Weight.ExtraBold))
            layout.addWidget(make_label("Поиск и выбор клиента", 13, TEXT_MUTED))

            search = QLineEdit()
            search.setPlaceholderText("🔍 Найти клиента по имени или телефону")
            search.setStyleSheet(f"""
                background: {BG_CARD}; color: {TEXT_PRIMARY};
                border: 1px solid {BORDER}; border-radius: 8px;
                padding: 12px 12px 12px 40px; font-size: 14px;
                max-width: 480px;
            """)
            search.textChanged.connect(lambda t: self._set_search(t))
            layout.addWidget(search)

            header_actions = QHBoxLayout()
            header_actions.addWidget(PrimaryButton("👤 Создать клиента"))
            header_actions.addStretch()
            layout.addLayout(header_actions)

            try:
                customers = get_all_customers() if not self._search else find_customers(self._search)
            except:
                customers = []

            for c in customers[:8]:
                card = Card()
                cl = QHBoxLayout(card)
                cl.setContentsMargins(16, 16, 16, 16)
                cl.setSpacing(14)

                avatar = QLabel(c["full_name"][0] if c.get("full_name") else "?")
                avatar.setFixedSize(40, 40)
                avatar.setStyleSheet(f"""
                    background: {BG_ELEVATED}; border: 2px solid {BORDER};
                    border-radius: 20px; font-size: 14px; font-weight: 700;
                    color: {GOLD};
                """)
                avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cl.addWidget(avatar)

                vi = QVBoxLayout()
                vi.addWidget(make_label(c.get("full_name", "—"), 14, TEXT_PRIMARY, QFont.Weight.DemiBold))
                vi.addWidget(make_label(c.get("phone", ""), 12, TEXT_SECONDARY))
                cl.addLayout(vi)
                cl.addStretch()

                if float(c.get("discount_percent", 0)) > 0:
                    disc_badge = QPushButton(f"−{float(c['discount_percent']):.0f}%")
                    disc_badge.setStyleSheet(f"""
                        background: rgba(201,164,92,0.1);
                        border: 1px solid rgba(201,164,92,0.2);
                        border-radius: 20px;
                        color: {GOLD}; font-size: 12px; font-weight: 600;
                        padding: 3px 10px;
                    """)
                    cl.addWidget(disc_badge)

                cl.addWidget(SecondaryButton("Выбрать клиента"))
                layout.addWidget(card)
        else:
            # Admin full view
            header = QHBoxLayout()
            hleft = QVBoxLayout()
            try:
                customers = get_all_customers()
            except:
                customers = []
            hleft.addWidget(make_manrope_label("Клиенты", 24, QFont.Weight.ExtraBold))
            hleft.addWidget(make_label(f"{len(customers)} клиентов в базе", 13, TEXT_MUTED))
            header.addLayout(hleft)
            header.addStretch()
            header.addWidget(PrimaryButton("➕ Добавить клиента"))
            layout.addLayout(header)

            search = QLineEdit()
            search.setPlaceholderText("🔍 Поиск по имени, телефону или email")
            search.setStyleSheet(f"""
                background: {BG_CARD}; color: {TEXT_PRIMARY};
                border: 1px solid {BORDER}; border-radius: 8px;
                padding: 9px 12px 9px 36px; font-size: 13px;
                max-width: 400px;
            """)
            search.textChanged.connect(lambda t: self._set_search(t))
            layout.addWidget(search)

            table = DataTable(["Имя", "Телефон", "Email", "Скидка", "Кол-во заказов", "Общая сумма", "Последний заказ", ""])
            table.setRowCount(len(customers))
            for i, c in enumerate(customers):
                # Name with avatar
                name_widget = QWidget()
                nl = QHBoxLayout(name_widget)
                nl.setContentsMargins(0, 0, 0, 0)
                nl.setSpacing(8)
                avatar = QLabel(c["full_name"][0] if c.get("full_name") else "?")
                avatar.setFixedSize(28, 28)
                avatar.setStyleSheet(f"""
                    background: {BG_ELEVATED}; border: 2px solid {BORDER};
                    border-radius: 14px; font-size: 11px; font-weight: 700;
                    color: {GOLD};
                """)
                avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
                nl.addWidget(avatar)
                nl.addWidget(make_label(c.get("full_name", "—"), 13, TEXT_PRIMARY, QFont.Weight.DemiBold))
                table.setCellWidget(i, 0, name_widget)

                table.setItem(i, 1, QTableWidgetItem(c.get("phone", "—")))
                table.setItem(i, 2, QTableWidgetItem(c.get("email", "—")))
                disc = float(c.get("discount_percent", 0) or 0)
                table.setItem(i, 3, QTableWidgetItem(f"{disc:.0f}%" if disc > 0 else "—"))
                orders_count = int(c.get("orders_count", 0) or 0)
                table.setItem(i, 4, QTableWidgetItem(str(orders_count)))
                total_amt = float(c.get("total_amount", 0) or 0)
                table.setItem(i, 5, QTableWidgetItem(
                    f"{total_amt:,.0f} ₽".replace(",", " ")
                ))
                last_order = c.get("last_order_date") or "—"
                table.setItem(i, 6, QTableWidgetItem(str(last_order)))

                action_widget = QWidget()
                al = QHBoxLayout(action_widget)
                al.setContentsMargins(0, 0, 0, 0)
                edit_btn = QPushButton("✏️")
                edit_btn.setFixedSize(30, 30)
                edit_btn.setStyleSheet(f"""
                    background: {BG_ELEVATED}; border: 1px solid {BORDER};
                    border-radius: 7px; color: {TEXT_SECONDARY};
                """)
                al.addWidget(edit_btn)
                hist_btn = QPushButton("📋")
                hist_btn.setFixedSize(30, 30)
                hist_btn.setStyleSheet(f"""
                    background: {BG_ELEVATED}; border: 1px solid {BORDER};
                    border-radius: 7px; color: {TEXT_SECONDARY};
                """)
                al.addWidget(hist_btn)
                table.setCellWidget(i, 7, action_widget)

            layout.addWidget(table)

        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _set_search(self, text: str):
        self._search = text
        self._setup_ui()


# ─── Оплаты ─────────────────────────────────────────────────────

class PaymentDialog(QDialog):
    """Модальное окно оплаты — как в React."""
    def __init__(self, order_id, table_number, subtotal, discount, final_amount, parent=None):
        super().__init__(parent)
        self._selected_method = "card"
        self._order_id = order_id
        self._table_number = table_number
        self._subtotal = subtotal
        self._discount = discount
        self._final_amount = final_amount

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(440, 500)

        # Backdrop
        self.setStyleSheet("""
            QDialog {
                background: rgba(14, 15, 17, 0.85);
            }
        """)

        # Central card
        card = QFrame()
        card.setStyleSheet(f"""
            background: {BG_CARD};
            border: 1px solid {BORDER};
            border-radius: 16px;
        """)
        card.setFixedSize(400, 460)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(28, 28, 28, 24)
        cl.setSpacing(0)

        # Close button
        close_row = QHBoxLayout()
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet(f"""
            background: {BG_ELEVATED}; border: none;
            border-radius: 14px; color: {TEXT_MUTED};
            font-size: 14px;
        """)
        close_btn.clicked.connect(self.reject)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_row.addStretch()
        close_row.addWidget(close_btn)
        cl.addLayout(close_row)

        # Title
        cl.addWidget(make_manrope_label("Принять оплату", 20, QFont.Weight.ExtraBold))
        cl.addSpacing(4)
        cl.addWidget(make_label(
            f"Заказ #{order_id} · Столик №{table_number}",
            14, TEXT_SECONDARY
        ))
        cl.addSpacing(24)

        # Amount breakdown
        cl.addWidget(make_label(f"Сумма:         {subtotal:,.0f} ₽".replace(",", " "), 14, TEXT_SECONDARY))
        cl.addSpacing(4)
        if discount > 0:
            cl.addWidget(make_label(f"Скидка:       −{discount:,.0f} ₽".replace(",", " "), 14, SUCCESS))
            cl.addSpacing(4)
        cl.addWidget(make_manrope_label(
            f"Итого:           {final_amount:,.0f} ₽".replace(",", " "),
            18, QFont.Weight.ExtraBold, GOLD
        ))
        cl.addSpacing(24)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER};")
        cl.addWidget(sep)
        cl.addSpacing(16)

        # Method selector label
        cl.addWidget(make_label("Способ оплаты", 13, TEXT_PRIMARY, QFont.Weight.Medium))
        cl.addSpacing(12)

        # Method grid
        methods_row = QHBoxLayout()
        methods_row.setSpacing(10)

        for m_id, icon, label, color in [
            ("cash", "💵", "Наличные", SUCCESS),
            ("card", "💳", "Карта", GOLD),
            ("online", "📱", "Онлайн", INFO),
        ]:
            m_btn = QPushButton(f"{icon}\n{label}")
            m_btn.setFixedSize(110, 72)
            m_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            selected = self._selected_method == m_id
            m_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {BG_ELEVATED if selected else BG_SECONDARY};
                    border: 2px solid {color if selected else BORDER};
                    border-radius: 12px;
                    font-size: 12px;
                    color: {TEXT_PRIMARY if selected else TEXT_SECONDARY};
                    font-weight: {700 if selected else 400};
                }}
                QPushButton:hover {{
                    border: 2px solid {color};
                    background: {BG_ELEVATED};
                }}
            """)
            def _pick(mid=m_id):
                self._selected_method = mid
                self.rebuild()
            m_btn.clicked.connect(_pick)
            methods_row.addWidget(m_btn)

        self._method_buttons = methods_row
        cl.addLayout(methods_row)
        cl.addSpacing(24)

        # Confirm button
        confirm_btn = QPushButton("✅ Подтвердить оплату")
        confirm_btn.setFixedHeight(44)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {GOLD}, stop:1 {GOLD_DARK});
                border: none; border-radius: 10px;
                color: {BG_PRIMARY}; font-size: 15px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                opacity: 0.85;
            }}
        """)
        confirm_btn.clicked.connect(self.accept)
        cl.addWidget(confirm_btn)

        # Center card in dialog
        dl = QVBoxLayout(self)
        dl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dl.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    def rebuild(self):
        """Refresh method buttons selection state."""
        methods_data = [("cash", "💵", "Наличные", SUCCESS),
                        ("card", "💳", "Карта", GOLD),
                        ("online", "📱", "Онлайн", INFO)]
        for i, (m_id, icon, label, color) in enumerate(methods_data):
            item = self._method_buttons.itemAt(i)
            if item and item.widget():
                btn = item.widget()
                selected = self._selected_method == m_id
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {BG_ELEVATED if selected else BG_SECONDARY};
                        border: 2px solid {color if selected else BORDER};
                        border-radius: 12px;
                        font-size: 12px;
                        color: {TEXT_PRIMARY if selected else TEXT_SECONDARY};
                        font-weight: {700 if selected else 400};
                    }}
                    QPushButton:hover {{
                        border: 2px solid {color};
                        background: {BG_ELEVATED};
                    }}
                """)

    @staticmethod
    def get_payment(order_id, table_number, subtotal, discount, final_amount, parent=None):
        dlg = PaymentDialog(order_id, table_number, subtotal, discount, final_amount, parent)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            return dlg._selected_method
        return None


class PaymentsScreen(QWidget):
    def __init__(self, role: str = "admin"):
        super().__init__()
        self._role = role
        self._method_filter = "all"
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(20)

        try:
            payments = get_all_payments()
            total_revenue = sum(float(p["amount"]) for p in payments if p.get("status") == "paid")
        except:
            payments = []
            total_revenue = 0

        # Header
        header = QHBoxLayout()
        hleft = QVBoxLayout()
        hleft.addWidget(make_manrope_label("Оплаты", 24, QFont.Weight.ExtraBold))
        hleft.addWidget(make_label(
            f"Выручка сегодня: {total_revenue:,.0f} ₽".replace(",", " "),
            13, GOLD, QFont.Weight.Bold
        ))
        header.addLayout(hleft)
        header.addStretch()
        if self._role == "waiter":
            pay_btn = PrimaryButton("💳 Принять оплату")
            pay_btn.clicked.connect(lambda: self._open_payment_modal())
            header.addWidget(pay_btn)
        layout.addLayout(header)

        # Admin filters
        if self._role == "admin":
            filters = QHBoxLayout()
            filters.setSpacing(6)
            for m_id, m_label in [("all", "Все способы"), ("cash", "Наличные"),
                                   ("card", "Карта"), ("online", "Онлайн")]:
                btn = FilterTab(m_label, self._method_filter == m_id)
                btn.clicked.connect(lambda checked, mid=m_id: self._set_method(mid))
                filters.addWidget(btn)
            layout.addLayout(filters)

        # Table
        table = DataTable(["ID оплаты", "№ заказа", "Столик", "Сумма", "Способ оплаты", "Статус", "Дата"])
        filtered = [p for p in payments if self._method_filter == "all" or p.get("payment_method") == self._method_filter]
        table.setRowCount(len(filtered))

        method_map = {"cash": "Наличные", "card": "Карта", "online": "Онлайн"}
        method_icons = {"cash": "💵", "card": "💳", "online": "📱"}

        for i, p in enumerate(filtered):
            table.setItem(i, 0, QTableWidgetItem(str(p.get("id", ""))))
            table.setItem(i, 1, QTableWidgetItem(f"#{p.get('order_id', '?')}"))
            table.setItem(i, 2, QTableWidgetItem(f"Столик №{p.get('table_number', '?')}"))
            table.setItem(i, 3, QTableWidgetItem(
                f"{float(p['amount']):,.0f} ₽".replace(",", " ")
            ))
            method = p.get("payment_method", "")
            table.setItem(i, 4, QTableWidgetItem(
                f"{method_icons.get(method, '')} {method_map.get(method, method)}"
            ))
            cfg = PAYMENT_STATUS_CONFIG.get(p.get("status", ""), {})
            table.setItem(i, 5, QTableWidgetItem(cfg.get("label", p.get("status", ""))))
            table.setItem(i, 6, QTableWidgetItem(str(p.get("paid_at", p.get("created_at", "")))))

        layout.addWidget(table)

        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _set_method(self, mid: str):
        self._method_filter = mid
        self._setup_ui()

    def _open_payment_modal(self, order_id="?", table_number="?", amount=0):
        """Open the payment modal dialog."""
        try:
            orders = get_all_orders()
            active_orders = [o for o in orders if o.get("status") not in ("paid", "cancelled")]
            if active_orders and order_id == "?":
                o = active_orders[0]
                order_id = o.get("id", "?")
                table_number = o.get("table_number", "?")
                amount = float(o.get("final_amount", 0))
        except:
            pass
        method = PaymentDialog.get_payment(
            order_id, table_number, amount, 0, amount, self
        )
        if method:
            method_map = {"cash": "Наличные", "card": "Карта", "online": "Онлайн"}
            QMessageBox.information(self, "Оплата принята",
                f"Оплата заказа #{order_id} принята.\n"
                f"Способ: {method_map.get(method, method)}\n"
                f"Сумма: {amount:,.0f} ₽".replace(",", " "))


# ─── Отчеты ─────────────────────────────────────────────────────

class ReportsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(24)

        # Header
        header = QHBoxLayout()
        header.addWidget(make_manrope_label("Отчеты", 24, QFont.Weight.ExtraBold))
        header.addWidget(make_label("Аналитика · 18 июня 2026", 13, TEXT_MUTED))
        header.addStretch()
        period_btns = QHBoxLayout()
        period_btns.setSpacing(8)
        for i, p in enumerate(["Сегодня", "Неделя", "Месяц"]):
            btn = FilterTab(p, i == 1)
            period_btns.addWidget(btn)
        header.addLayout(period_btns)
        layout.addLayout(header)

        # Stats
        stats = QHBoxLayout()
        stats.setSpacing(14)
        for label, value, sub, color in [
            ("Выручка за день", "127 400 ₽", "+14%", GOLD),
            ("Выручка за неделю", "427 100 ₽", "+8%", GOLD),
            ("Количество заказов", "84", "", INFO),
            ("Средний чек", "1 517 ₽", "+5%", WARNING),
            ("Топ блюдо", "Стейк", "124 заказа", "#9B6CDD"),
            ("Оплаченных", "78", "из 84", SUCCESS),
        ]:
            stats.addWidget(StatCard(label, value, sub, color))
        layout.addLayout(stats)

        # Charts
        charts_row = QHBoxLayout()
        charts_row.setSpacing(20)

        rev_card = Card()
        rl = QVBoxLayout(rev_card)
        rl.setContentsMargins(24, 24, 24, 24)
        rl.addWidget(SectionHeader("Продажи по дням", "Выручка за текущую неделю"))
        rl.addSpacing(16)
        week_data = [
            ("Пн", "48 200", 32, 54), ("Вт", "52 100", 38, 58),
            ("Ср", "61 400", 45, 69), ("Чт", "58 900", 41, 66),
            ("Пт", "74 300", 54, 83), ("Сб", "89 200", 68, 100),
            ("Вс", "42 800", 30, 48),
        ]
        for day, rev, cnt, pct in week_data:
            row = QHBoxLayout()
            row.addWidget(make_label(day, 13, TEXT_PRIMARY))
            row.addStretch()
            row.addWidget(make_label(f"{rev} ₽", 13, GOLD, QFont.Weight.Bold))
            rl.addLayout(row)
            bar_row = QHBoxLayout()
            bar_row.setSpacing(8)
            bar = QFrame()
            bar.setFixedHeight(6)
            bar.setStyleSheet(f"""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {GOLD}, stop:1 rgba(201,164,92,0.3));
                border-radius: 3px;
                max-width: {pct}%;
            """)
            bar_row.addWidget(bar)
            bar_row.addWidget(make_label(f"{pct}%", 11, TEXT_MUTED))
            rl.addLayout(bar_row)
        charts_row.addWidget(rev_card, 1)

        stats_card = Card()
        sl = QVBoxLayout(stats_card)
        sl.setContentsMargins(24, 24, 24, 24)
        sl.addWidget(SectionHeader("Заказы по статусу", "Распределение за неделю"))
        sl.addSpacing(16)
        status_items = [
            ("Оплачен", 312, "#3FA66B"),
            ("Подан", 28, "#9B6CDD"),
            ("Готов", 14, "#3FA66B"),
            ("Готовится", 18, "#D98A35"),
            ("Отменен", 12, "#C94C4C"),
        ]
        for status, count, color in status_items:
            row = QHBoxLayout()
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 12px;")
            row.addWidget(dot)
            row.addWidget(make_label(status, 13, TEXT_SECONDARY))
            row.addStretch()
            row.addWidget(make_label(str(count), 13, TEXT_PRIMARY, QFont.Weight.Bold))
            sl.addLayout(row)
        charts_row.addWidget(stats_card, 1)

        layout.addLayout(charts_row)

        # Popular dishes & payment methods
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(20)

        pop_card = Card()
        pl = QVBoxLayout(pop_card)
        pl.setContentsMargins(24, 24, 24, 24)
        pl.addWidget(SectionHeader("Популярные блюда", "Топ по количеству заказов"))
        pl.addSpacing(16)
        for name, orders_count in [
            ("Стейк Рибай", 124), ("Паста Карбонара", 98),
            ("Лосось на гриле", 87), ("Цезарь с курицей", 76),
            ("Тирамису", 65),
        ]:
            pl.addWidget(make_label(name, 13, TEXT_PRIMARY))
            bar_row = QHBoxLayout()
            bar_row.setSpacing(8)
            bar = QFrame()
            bar.setFixedHeight(6)
            bar.setStyleSheet(f"""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {GOLD}, stop:1 rgba(201,164,92,0.2));
                border-radius: 3px;
                max-width: {orders_count}%;
            """)
            bar_row.addWidget(bar)
            bar_row.addWidget(make_label(f"{orders_count} заказов", 11, TEXT_MUTED))
            pl.addLayout(bar_row)
        bottom_row.addWidget(pop_card, 2)

        pay_card = Card()
        pyl = QVBoxLayout(pay_card)
        pyl.setContentsMargins(24, 24, 24, 24)
        pyl.addWidget(SectionHeader("Выручка по оплате", "По способам оплаты"))
        pyl.addSpacing(16)
        for method, amount, pct, color in [
            ("Карта", "168 400 ₽", 62, GOLD),
            ("Наличные", "64 200 ₽", 24, SUCCESS),
            ("Онлайн", "38 000 ₽", 14, INFO),
        ]:
            pyl.addWidget(make_label(method, 13, TEXT_PRIMARY))
            bar = QFrame()
            bar.setFixedHeight(6)
            bar.setStyleSheet(f"""
                background: {color};
                border-radius: 3px;
                max-width: {pct}%;
            """)
            pyl.addWidget(bar)
            pyl.addWidget(make_label(f"{amount} · {pct}% от выручки", 11, TEXT_MUTED))
        bottom_row.addWidget(pay_card, 1)

        layout.addLayout(bottom_row)

        # Revenue by day table
        rev_table_card = Card()
        rtl = QVBoxLayout(rev_table_card)
        rtl.setContentsMargins(0, 0, 0, 0)
        rtl.addWidget(SectionHeader("Выручка по дням"))
        table = DataTable(["День", "Заказов", "Выручка", "Средний чек"])
        table.setRowCount(len(week_data))
        for i, (day, rev, orders_cnt, _) in enumerate(week_data):
            table.setItem(i, 0, QTableWidgetItem(day))
            table.setItem(i, 1, QTableWidgetItem(str(orders_cnt)))
            table.setItem(i, 2, QTableWidgetItem(f"{rev} ₽"))
            avg = int(float(rev.replace(" ", "")) / orders_cnt) if orders_cnt else 0
            table.setItem(i, 3, QTableWidgetItem(f"{avg:,} ₽".replace(",", " ")))
        rtl.addWidget(table)
        layout.addWidget(rev_table_card)

        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)


# ─── Настройки ──────────────────────────────────────────────────

class SettingsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        left = QWidget()
        left.setFixedWidth(220)
        left.setStyleSheet(f"""
            background: {BG_SECONDARY};
            border-right: 1px solid {BORDER};
        """)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(14, 24, 14, 24)
        ll.addWidget(make_label("НАСТРОЙКИ", 11, TEXT_MUTED))
        ll.addSpacing(10)
        sections = [
            ("🏢", "Профиль ресторана"),
            ("👥", "Пользователи и роли"),
            ("📋", "Статусы заказов"),
            ("📍", "Зоны столиков"),
            ("💳", "Способы оплаты"),
        ]
        for i, (icon, label) in enumerate(sections):
            btn = QPushButton(f"  {icon}  {label}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            active = i == 1
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left; padding: 10px 12px;
                    border-radius: 8px; border: none;
                    background: {'rgba(201,164,92,0.1)' if active else 'transparent'};
                    color: {'{GOLD}' if active else '{TEXT_SECONDARY}'};
                    font-size: 13px;
                    font-weight: {'600' if active else '400'};
                    border-left: 3px solid {'{GOLD}' if active else 'transparent'};
                }}
                QPushButton:hover {{
                    background: rgba(255,255,255,0.03);
                }}
            """)
            ll.addWidget(btn)
        ll.addStretch()
        main_layout.addWidget(left)

        # Content
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(28, 28, 28, 28)
        rl.setSpacing(24)

        rl.addWidget(make_manrope_label("Настройки", 24, QFont.Weight.ExtraBold))
        rl.addWidget(make_label("Управление системой и правами доступа", 13, TEXT_MUTED))

        # Restaurant profile
        profile_card = Card()
        pl = QVBoxLayout(profile_card)
        pl.setContentsMargins(24, 24, 24, 24)
        pl.addWidget(make_manrope_label("Профиль ресторана", 15, QFont.Weight.DemiBold))
        pl.addSpacing(16)

        fields_grid = QHBoxLayout()
        fields_grid.setSpacing(16)
        left_col = QVBoxLayout()
        left_col.setSpacing(16)
        for label, value in [("Название", "GastroHub"), ("Телефон", "+7 (495) 123-45-67")]:
            lv = QVBoxLayout()
            lv.addWidget(make_label(label, 11, TEXT_MUTED))
            inp = QLineEdit(value)
            inp.setStyleSheet(f"""
                background: {BG_SECONDARY}; color: {TEXT_PRIMARY};
                border: 1px solid {BORDER}; border-radius: 8px;
                padding: 10px 14px; font-size: 13px;
            """)
            lv.addWidget(inp)
            left_col.addLayout(lv)

        right_col = QVBoxLayout()
        right_col.setSpacing(16)
        for label, value in [("Адрес", "Москва, ул. Тверская, 24"), ("Email", "info@gastrohub.ru")]:
            lv = QVBoxLayout()
            lv.addWidget(make_label(label, 11, TEXT_MUTED))
            inp = QLineEdit(value)
            inp.setStyleSheet(f"""
                background: {BG_SECONDARY}; color: {TEXT_PRIMARY};
                border: 1px solid {BORDER}; border-radius: 8px;
                padding: 10px 14px; font-size: 13px;
            """)
            lv.addWidget(inp)
            right_col.addLayout(lv)

        fields_grid.addLayout(left_col)
        fields_grid.addLayout(right_col)
        pl.addLayout(fields_grid)
        pl.addSpacing(16)
        pl.addWidget(PrimaryButton("Сохранить изменения"))
        rl.addWidget(profile_card)

        # Role permissions
        perm_card = Card()
        pml = QVBoxLayout(perm_card)
        pml.setContentsMargins(24, 24, 24, 24)
        pml.addWidget(make_manrope_label("Права доступа по ролям", 15, QFont.Weight.DemiBold))
        pml.addWidget(make_label("Настройка разрешений для каждой роли", 12, TEXT_MUTED))
        pml.addSpacing(16)

        roles_row = QHBoxLayout()
        roles_row.setSpacing(20)
        for role_name, perms, color in [
            ("Администратор", [
                "Управление меню", "Управление столиками", "Просмотр отчетов",
                "Управление клиентами", "Просмотр оплат", "Редактирование заказов",
            ], GOLD),
            ("Официант", [
                "Создание заказов", "Добавление блюд", "Изменение статусов",
                "Оплата заказов", "Просмотр меню", "Просмотр столиков",
            ], SUCCESS),
        ]:
            rc = QFrame()
            rc.setStyleSheet(f"""
                background: {BG_SECONDARY};
                border: 1px solid rgba({','.join(map(str, hex_to_rgb(color)))}, 0.13);
                border-radius: 12px;
            """)
            rcl = QVBoxLayout(rc)
            rcl.setContentsMargins(20, 20, 20, 20)
            rcl.setSpacing(8)
            rcl.addWidget(make_manrope_label(role_name, 14, QFont.Weight.Bold))
            rcl.addWidget(make_label(f"{len(perms)} разрешений", 11, TEXT_MUTED))
            rcl.addSpacing(8)
            for perm in perms:
                row = QHBoxLayout()
                row.setSpacing(8)
                check = QLabel("✓")
                check.setStyleSheet(f"""
                    color: {color}; font-size: 10px; font-weight: bold;
                    background: rgba({','.join(map(str, hex_to_rgb(color)))}, 0.08);
                    border: 1px solid rgba({','.join(map(str, hex_to_rgb(color)))}, 0.19);
                    border-radius: 9px; padding: 3px;
                    min-width: 12px; min-height: 12px; max-width: 12px; max-height: 12px;
                """)
                check.setAlignment(Qt.AlignmentFlag.AlignCenter)
                row.addWidget(check)
                row.addWidget(make_label(perm, 13, TEXT_SECONDARY))
                row.addStretch()
                rcl.addLayout(row)
            roles_row.addWidget(rc)
        pml.addLayout(roles_row)
        rl.addWidget(perm_card)

        # Order statuses
        status_card = Card()
        sl = QVBoxLayout(status_card)
        sl.setContentsMargins(24, 24, 24, 24)
        sl.addWidget(make_manrope_label("Статусы заказов", 15, QFont.Weight.DemiBold))
        sl.addSpacing(12)
        status_row = QHBoxLayout()
        status_row.setSpacing(10)
        for key, label, color in [
            ("new", "Новый", INFO), ("cooking", "Готовится", WARNING),
            ("ready", "Готов", SUCCESS), ("served", "Подан", "#9B6CDD"),
            ("paid", "Оплачен", EMERALD), ("cancelled", "Отменен", ERROR),
        ]:
            badge = QFrame()
            badge.setStyleSheet(f"""
                background: rgba({','.join(map(str, hex_to_rgb(color)))}, 0.06);
                border: 1px solid rgba({','.join(map(str, hex_to_rgb(color)))}, 0.19);
                border-radius: 10px;
            """)
            bl = QHBoxLayout(badge)
            bl.setContentsMargins(16, 10, 16, 10)
            bl.setSpacing(8)
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 10px;")
            bl.addWidget(dot)
            bl.addWidget(make_label(label, 13, TEXT_PRIMARY, QFont.Weight.Medium))
            status_row.addWidget(badge)
        status_row.addStretch()
        sl.addLayout(status_row)
        rl.addWidget(status_card)

        # Zones
        zones_card = Card()
        zl = QVBoxLayout(zones_card)
        zl.setContentsMargins(24, 24, 24, 24)
        zone_header = QHBoxLayout()
        zone_header.addWidget(make_manrope_label("Зоны столиков", 15, QFont.Weight.DemiBold))
        zone_header.addStretch()
        zone_header.addWidget(PrimaryButton("Добавить зону"))
        zl.addLayout(zone_header)
        zl.addSpacing(12)
        for zone in ["Основной зал", "VIP-зона", "Терраса"]:
            row = QFrame()
            row.setStyleSheet(f"""
                background: {BG_SECONDARY};
                border: 1px solid {BORDER}; border-radius: 8px;
            """)
            rl2 = QHBoxLayout(row)
            rl2.setContentsMargins(16, 12, 16, 12)
            rl2.addWidget(make_label(f"📍 {zone}", 14, TEXT_PRIMARY))
            rl2.addStretch()
            rl2.addWidget(SecondaryButton("Редактировать"))
            zl.addWidget(row)
        rl.addWidget(zones_card)

        # Payment methods
        paym_card = Card()
        pml2 = QVBoxLayout(paym_card)
        pml2.setContentsMargins(24, 24, 24, 24)
        pml2.addWidget(make_manrope_label("Способы оплаты", 15, QFont.Weight.DemiBold))
        pml2.addSpacing(12)
        for method in ["Наличные", "Банковская карта", "Онлайн-оплата"]:
            row = QFrame()
            row.setStyleSheet(f"""
                background: {BG_SECONDARY};
                border: 1px solid {BORDER}; border-radius: 8px;
            """)
            rl3 = QHBoxLayout(row)
            rl3.setContentsMargins(16, 12, 16, 12)
            rl3.addWidget(make_label(method, 14, TEXT_PRIMARY))
            rl3.addStretch()
            toggle = QFrame()
            toggle.setFixedSize(44, 24)
            toggle.setStyleSheet(f"""
                background: rgba(63,166,107,0.2);
                border: 1px solid {SUCCESS};
                border-radius: 12px;
            """)
            toggle_dot = QFrame()
            toggle_dot.setFixedSize(16, 16)
            toggle_dot.move(22, 3)
            toggle_dot.setStyleSheet(f"""
                background: {SUCCESS};
                border-radius: 8px;
            """)
            rl3.addWidget(toggle)
            pml2.addWidget(row)
        rl.addWidget(paym_card)

        main_layout.addWidget(right, 1)
