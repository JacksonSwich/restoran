"""Все экраны приложения."""

import json
import os
from datetime import datetime
from functools import partial

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QScrollArea, QGridLayout, QStackedWidget,
    QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QMessageBox, QDialog,
    QDialogButtonBox, QFormLayout, QGroupBox, QCheckBox,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor

from ui.styles import *
from ui.widgets import (
    make_label, make_manrope_label, PrimaryButton, SecondaryButton,
    DangerButton, StatusBadge, SearchInput, FilterTab, Card,
    StatCard, DataTable, SectionHeader, hex_to_rgb,
    ORDER_STATUS_CONFIG, TABLE_STATUS_CONFIG, PAYMENT_STATUS_CONFIG,
)
from database.queries import *

# Module-level variable for passing order_id to OrderDetailsScreen
_order_details_pending_id: int | None = None
# Module-level variable for passing selected customer to NewOrderScreen
_selected_customer_for_order: dict | None = None


def _navigate_to_order(navigate_fn, order_id):
    """Set the pending order ID and navigate to order details."""
    global _order_details_pending_id
    _order_details_pending_id = order_id
    if navigate_fn:
        navigate_fn("order-details")


# ─── Aдминистративный дашборд ──────────────────────────────────

class AdminDashboard(QWidget):
    def __init__(self, on_navigate=None):
        super().__init__()
        self._navigate = on_navigate
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        self._built = False
        self._loading_widget = None
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._show_loading()
        QTimer.singleShot(0, self._build_content)

    def _show_loading(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(28, 28, 28, 28)
        l.addWidget(make_manrope_label("Главная", 24, QFont.Weight.ExtraBold))
        l.addWidget(make_label("Загрузка данных...", 13, TEXT_MUTED))
        l.addStretch()
        self._loading_widget = w
        self._main_layout.addWidget(w)

    def _build_content(self):
        if self._built:
            return
        self._built = True
        if self._loading_widget:
            self._main_layout.removeWidget(self._loading_widget)
            self._loading_widget.deleteLater()
            self._loading_widget = None

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(24)

        # Header
        today_str = datetime.now().strftime("%d %B %Y").lstrip("0")
        month_names = ["января", "февраля", "марта", "апреля", "мая", "июня",
                       "июля", "августа", "сентября", "октября", "ноября", "декабря"]
        now = datetime.now()
        date_str = f"{now.day} {month_names[now.month-1]} {now.year}"
        header = QVBoxLayout()
        header.addWidget(make_manrope_label("Главная", 24, QFont.Weight.ExtraBold))
        header.addWidget(make_label(f"Операционная сводка · {date_str}", 13, TEXT_MUTED))
        layout.addLayout(header)

        # Stats
        stats_grid = QHBoxLayout()
        stats_grid.setSpacing(16)

        try:
            active_orders = get_active_orders()
            paid_orders = get_orders_by_status("paid")
            all_tables = get_all_tables()
            all_orders = get_all_orders()
            occupied_count = sum(1 for t in all_tables if t["status"] == "occupied")
            total_tables = len(all_tables)
            today_total = sum(float(o.get("final_amount", 0) or 0) for o in paid_orders)
            today_orders = len(paid_orders)
            avg_check = today_total / today_orders if today_orders > 0 else 0
        except:
            active_orders = []
            paid_orders = []
            occupied_count = 0
            total_tables = 0
            today_total = 0
            today_orders = 0
            avg_check = 0

        stats = [
            ("Выручка за день", f"{today_total:,.0f} ₽".replace(",", " "), "за сегодня", GOLD),
            ("Количество заказов", str(today_orders), "сегодня", INFO),
            ("Средний чек", f"{avg_check:,.0f} ₽".replace(",", " "), "", WARNING),
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

        # Revenue chart
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

        rev_days = []
        if rev_data:
            for r in rev_data[:7]:
                day_name = str(r.get("payment_date", ""))
                rev = float(r.get("total", 0))
                orders = int(r.get("order_count", 0))
                rev_days.append((day_name, rev, orders))
            max_orders = max((d[2] for d in rev_days), default=1) or 1
        else:
            max_orders = 1

        for day, rev_val, cnt in rev_days if rev_days else []:
            row = QHBoxLayout()
            row.addWidget(make_label(str(day)[:3], 13, TEXT_PRIMARY, QFont.Weight.Medium))
            row.addWidget(make_label(f"{rev_val:,.0f} ₽".replace(",", " "), 13, GOLD, QFont.Weight.Bold))
            row.addWidget(make_label(str(cnt), 13, TEXT_SECONDARY))
            rl.addLayout(row)
            bar_row = QHBoxLayout()
            bar_row.setSpacing(6)
            bar = QFrame()
            bar.setFixedHeight(4)
            pct = (cnt * 100 // max_orders) if max_orders else 0
            bar.setStyleSheet(f"""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {GOLD}, stop:1 rgba(201,164,92,0.2));
                border-radius: 2px;
                max-width: {pct}%;
            """)
            bar_row.addWidget(bar)
            rl.addLayout(bar_row)

        if not rev_days:
            rl.addWidget(make_label("Нет данных за последние дни", 13, TEXT_MUTED))

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

        if pop_dishes:
            max_cnt = max((int(d.get("order_count", 0)) for d in pop_dishes), default=1) or 1
            for d in pop_dishes:
                name = d.get("name", "—")
                cnt = int(d.get("order_count", 0))
                pct = cnt * 100 // max_cnt
                pl.addWidget(make_label(f"{name} · {cnt} заказов", 13, TEXT_PRIMARY))
                bar_row = QHBoxLayout()
                bar_row.setSpacing(6)
                bar = QFrame()
                bar.setFixedHeight(4)
                bar.setStyleSheet(f"""
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {GOLD}, stop:1 rgba(201,164,92,0.2));
                    border-radius: 2px;
                    max-width: {pct}%;
                """)
                bar_row.addWidget(bar)
                pl.addLayout(bar_row)
        else:
            pl.addWidget(make_label("Нет данных о популярности блюд", 13, TEXT_MUTED))

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
        tl.addWidget(table)
        layout.addWidget(table_card)

        scroll.setWidget(content)
        self._main_layout.addWidget(scroll)


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
    created = order.get("created_at", "")
    elapsed_str = "только что"
    if created and created != "":
        try:
            created_dt = created if isinstance(created, datetime) else datetime.strptime(str(created)[:19], "%Y-%m-%d %H:%M:%S")
            delta = datetime.now() - created_dt
            mins = int(delta.total_seconds() // 60)
            if mins < 1:
                elapsed_str = "только что"
            elif mins < 60:
                elapsed_str = f"~{mins} мин назад"
            elif mins < 1440:
                elapsed_str = f"~{mins // 60} ч назад"
            else:
                elapsed_str = f"~{mins // 1440} дн назад"
        except:
            elapsed_str = str(created)[:10] if created else "—"
    elapsed.addWidget(make_label(elapsed_str, 12, TEXT_MUTED))
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
        self._built = False
        self._loading_widget = None
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._show_loading()
        QTimer.singleShot(0, self._build_content)

    def _show_loading(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(28, 28, 28, 28)
        l.addWidget(make_manrope_label("Рабочее место", 24, QFont.Weight.ExtraBold))
        l.addWidget(make_label("Загрузка данных...", 13, TEXT_MUTED))
        l.addStretch()
        self._loading_widget = w
        self._main_layout.addWidget(w)

    def _build_content(self):
        if self._built:
            return
        self._built = True
        if self._loading_widget:
            self._main_layout.removeWidget(self._loading_widget)
            self._loading_widget.deleteLater()
            self._loading_widget = None

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
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
        hour_now = datetime.now().hour
        if 5 <= hour_now < 12:
            greeting = "Доброе утро"
        elif 12 <= hour_now < 17:
            greeting = "Добрый день"
        elif 17 <= hour_now < 22:
            greeting = "Добрый вечер"
        else:
            greeting = "Доброй ночи"
        month_names = ["января", "февраля", "марта", "апреля", "мая", "июня",
                       "июля", "августа", "сентября", "октября", "ноября", "декабря"]
        now = datetime.now()
        date_str = f"{now.day} {month_names[now.month-1]} {now.year}"
        hleft.addWidget(make_label(f"{greeting} · {date_str}", 13, TEXT_MUTED))
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

        # Summary cards
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
                QFrame {{
                    background: {BG_CARD};
                    border: 1px solid {BORDER};
                    border-radius: 14px;
                }}
                QFrame:hover {{
                    border: 1px solid rgba({','.join(map(str, hex_to_rgb(color)))}, 0.4);
                }}
            """)
            cl = QHBoxLayout(card)
            cl.setContentsMargins(20, 20, 20, 20)
            cl.setSpacing(16)

            icon_frame = QFrame()
            icon_frame.setFixedSize(48, 48)
            icon_frame.setStyleSheet(f"""
                QFrame {{
                    background: rgba({','.join(map(str, hex_to_rgb(color)))}, 0.1);
                    border-radius: 14px;
                }}
            """)
            il = QVBoxLayout(icon_frame)
            il.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ilbl = QLabel(icon_text)
            ilbl.setStyleSheet(f"font-size: 22px; background: transparent; border: none;")
            il.addWidget(ilbl)
            cl.addWidget(icon_frame)

            vl = QVBoxLayout()
            vl.setSpacing(2)
            vl.addWidget(make_manrope_label(value, 28, QFont.Weight.ExtraBold, TEXT_PRIMARY))
            vl.addWidget(make_label(label, 12, TEXT_SECONDARY))
            cl.addLayout(vl)
            cl.addStretch()
            summary.addWidget(card)
        layout.addLayout(summary)

        # Ready orders section
        if ready_orders:
            ready_header = QHBoxLayout()
            ready_header.addWidget(make_manrope_label("Готовы к подаче", 16, QFont.Weight.Bold))
            count_badge = QFrame()
            count_badge.setFixedHeight(22)
            count_badge.setStyleSheet(f"""
                QFrame {{
                    background: rgba(63,166,107,0.12);
                    border-radius: 11px;
                    padding: 0 10px;
                }}
            """)
            cbl = QHBoxLayout(count_badge)
            cbl.setContentsMargins(10, 0, 10, 0)
            cbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cbl.addWidget(make_label(str(len(ready_orders)), 12, SUCCESS, QFont.Weight.Bold))
            ready_header.addWidget(count_badge)
            ready_header.addStretch()
            layout.addLayout(ready_header)

            orders_grid = QHBoxLayout()
            orders_grid.setSpacing(14)
            for o in ready_orders[:6]:
                orders_grid.addWidget(_make_order_card(
                    o, highlight=True,
                    on_open=lambda oid=o["id"]: self._navigate("order-details", oid)
                ))
            layout.addLayout(orders_grid)

        # Active orders
        active_section = QHBoxLayout()
        active_section.addWidget(make_manrope_label("Активные заказы", 16, QFont.Weight.Bold))
        count_badge2 = QFrame()
        count_badge2.setFixedHeight(22)
        count_badge2.setStyleSheet(f"""
            QFrame {{
                background: {BG_ELEVATED};
                border-radius: 11px;
            }}
        """)
        cbl2 = QHBoxLayout(count_badge2)
        cbl2.setContentsMargins(10, 0, 10, 0)
        cbl2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cbl2.addWidget(make_label(str(len(working_orders)), 12, TEXT_MUTED, QFont.Weight.Bold))
        active_section.addWidget(count_badge2)
        active_section.addStretch()
        layout.addLayout(active_section)

        if working_orders:
            orders_grid2 = QHBoxLayout()
            orders_grid2.setSpacing(14)
            for o in working_orders[:6]:
                orders_grid2.addWidget(_make_order_card(
                    o, highlight=False,
                    on_open=lambda oid=o["id"]: self._navigate("order-details", oid)
                ))
            layout.addLayout(orders_grid2)
        else:
            empty_frame = QFrame()
            empty_frame.setStyleSheet(f"""
                QFrame {{
                    background: {BG_CARD};
                    border: 1px dashed rgba(111, 117, 111, 0.3);
                    border-radius: 12px;
                }}
            """)
            empty_frame.setMinimumHeight(140)
            el = QVBoxLayout(empty_frame)
            el.setAlignment(Qt.AlignmentFlag.AlignCenter)
            el.setSpacing(12)
            empty_icon = QLabel("📋")
            empty_icon.setStyleSheet("font-size: 40px; background: transparent; border: none;")
            empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            el.addWidget(empty_icon)
            el.addWidget(make_manrope_label("Нет активных заказов", 15, QFont.Weight.DemiBold, TEXT_SECONDARY))
            if self._navigate:
                create_first_btn = QPushButton("➕ Создать первый заказ")
                create_first_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                create_first_btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        color: {GOLD};
                        border: 1px solid rgba(201,164,92,0.3);
                        border-radius: 8px;
                        font-size: 13px;
                        font-weight: 600;
                        padding: 8px 18px;
                    }}
                    QPushButton:hover {{
                        background: rgba(201,164,92,0.08);
                        border-color: {GOLD};
                    }}
                """)
                create_first_btn.clicked.connect(lambda: self._navigate("new-order"))
                btn_container = QHBoxLayout()
                btn_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
                btn_container.addWidget(create_first_btn)
                el.addLayout(btn_container)
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

        def _table_pluralize(n: int) -> str:
            if n % 10 == 1 and n % 100 != 11:
                return "место"
            if 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
                return "места"
            return "мест"

        for t in tables[:10]:
            cfg = TABLE_STATUS_CONFIG.get(t["status"], {})
            color = cfg.get("color", DISABLED)
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: rgba({','.join(map(str, hex_to_rgb(color)))}, 0.06);
                    border: 1px solid rgba({','.join(map(str, hex_to_rgb(color)))}, 0.2);
                    border-radius: 12px;
                }}
                QFrame:hover {{
                    border: 1px solid {GOLD};
                }}
            """)
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            if self._navigate:
                card.mousePressEvent = lambda ev, nav=self._navigate: nav("tables") if ev.button() == Qt.MouseButton.LeftButton else None
            cl = QVBoxLayout(card)
            cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.setSpacing(6)

            # Table icon
            table_icon = QLabel("⊞")
            table_icon.setStyleSheet(f"font-size: 22px; color: {TEXT_MUTED}; background: transparent; border: none;")
            table_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(table_icon)

            # Table number — no border
            num_lbl = make_manrope_label(str(t["table_number"]), 24, QFont.Weight.ExtraBold, TEXT_PRIMARY)
            cl.addWidget(num_lbl)

            # Seats — no border, fixed pluralization
            seats = t['seats_count']
            cl.addWidget(make_label(
                f"{seats} {_table_pluralize(seats)}", 11, TEXT_MUTED
            ))

            # Status badge at bottom
            badge_frame = QFrame()
            badge_frame.setStyleSheet(f"""
                QFrame {{
                    background: rgba({','.join(map(str, hex_to_rgb(color)))}, 0.12);
                    border: none;
                    border-radius: 10px;
                    padding: 4px 12px;
                }}
            """)
            bl = QHBoxLayout(badge_frame)
            bl.setContentsMargins(10, 3, 10, 3)
            bl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            bl.addWidget(make_label(cfg.get("label", ""), 10, color, QFont.Weight.Bold))
            cl.addWidget(badge_frame)
            tables_grid.addWidget(card)
        layout.addLayout(tables_grid)

        scroll.setWidget(content)
        self._main_layout.addWidget(scroll)


# ─── Столики ────────────────────────────────────────────────────

class TableEditDialog(QDialog):
    """Диалог редактирования столика (номер, места, зона)."""
    def __init__(self, table: dict | None = None, parent=None):
        super().__init__(parent)
        self._table = table
        is_new = table is None
        self.setWindowTitle("Добавить столик" if is_new else "Изменить столик")
        self.setModal(True)
        self.setMinimumSize(380, 250)

        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        self._number_spin = QSpinBox()
        self._number_spin.setMinimum(1)
        self._number_spin.setMaximum(999)
        if not is_new:
            self._number_spin.setValue(table.get("table_number", 1))
        layout.addRow("Номер столика:", self._number_spin)

        self._seats_spin = QSpinBox()
        self._seats_spin.setMinimum(1)
        self._seats_spin.setMaximum(50)
        if not is_new:
            self._seats_spin.setValue(table.get("seats_count", 4))
        layout.addRow("Количество мест:", self._seats_spin)

        self._zone_combo = QComboBox()
        # Load zones from file or use defaults
        try:
            zones_file = os.path.join(os.path.dirname(__file__), "..", "restaurant_zones.json")
            if os.path.exists(zones_file):
                with open(zones_file, encoding="utf-8") as zf:
                    zone_data = json.load(zf)
                if zone_data:
                    self._zone_combo.addItems(zone_data)
                else:
                    self._zone_combo.addItems(["Основной зал", "VIP-зона", "Терраса"])
            else:
                self._zone_combo.addItems(["Основной зал", "VIP-зона", "Терраса"])
        except:
            self._zone_combo.addItems(["Основной зал", "VIP-зона", "Терраса"])
        if not is_new and table.get("zone"):
            idx = self._zone_combo.findText(table["zone"])
            if idx >= 0:
                self._zone_combo.setCurrentIndex(idx)
        layout.addRow("Зона:", self._zone_combo)

        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.button(QDialogButtonBox.StandardButton.Ok).setText(
            "Добавить" if is_new else "Сохранить"
        )
        btn_box.accepted.connect(self._on_accept)
        btn_box.rejected.connect(self.reject)
        layout.addRow(btn_box)

    def _on_accept(self):
        if self._number_spin.value() < 1:
            QMessageBox.warning(self, "Ошибка", "Некорректный номер столика")
            return
        self.accept()

    def get_result(self) -> dict:
        return {
            "table_number": self._number_spin.value(),
            "seats": self._seats_spin.value(),
            "zone": self._zone_combo.currentText(),
        }


class TableStatusDialog(QDialog):
    """Диалог изменения статуса столика."""
    def __init__(self, current_status: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Изменить статус столика")
        self.setModal(True)
        self.setMinimumSize(320, 200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        layout.addWidget(make_label("Выберите новый статус:", 14, TEXT_PRIMARY))

        self._status_combo = QComboBox()
        statuses = [
            ("free", "Свободен"),
            ("occupied", "Занят"),
            ("reserved", "Забронирован"),
            ("out_of_service", "Недоступен"),
        ]
        for val, label in statuses:
            self._status_combo.addItem(label, val)
        for i, (val, _) in enumerate(statuses):
            if val == current_status:
                self._status_combo.setCurrentIndex(i)
                break
        layout.addWidget(self._status_combo)

        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.button(QDialogButtonBox.StandardButton.Ok).setText("Изменить")
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def get_selected_status(self) -> str:
        return self._status_combo.currentData()



class TableBulkStatusDialog(QDialog):
    """Dialog for changing table status with table selector and status selector."""

    def __init__(self, tables: list[dict], preselected_table_id: int | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Изменить статус столика")
        self.setModal(True)
        self.setMinimumSize(380, 260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        # Table selector
        layout.addWidget(make_label("Выберите столик:", 14, TEXT_PRIMARY))
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
        for t in tables:
            label = f"Столик №{t['table_number']} ({t.get('zone', '')}) — {t.get('status', '')}"
            self._table_combo.addItem(label, t["id"])
        if preselected_table_id is not None:
            for i in range(self._table_combo.count()):
                if self._table_combo.itemData(i) == preselected_table_id:
                    self._table_combo.setCurrentIndex(i)
                    break
        layout.addWidget(self._table_combo)

        # Status selector
        layout.addWidget(make_label("Новый статус:", 14, TEXT_PRIMARY))
        self._status_combo = QComboBox()
        statuses = [
            ("free", "Свободен"),
            ("occupied", "Занят"),
            ("reserved", "Забронирован"),
            ("out_of_service", "Недоступен"),
        ]
        for val, label in statuses:
            self._status_combo.addItem(label, val)
        self._status_combo.setStyleSheet(f"""
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
        layout.addWidget(self._status_combo)

        layout.addStretch()

        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.button(QDialogButtonBox.StandardButton.Ok).setText("Подтвердить")
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def get_result(self) -> tuple[int, str]:
        return self._table_combo.currentData(), self._status_combo.currentData()

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
        scroll.setFrameShape(QFrame.Shape.NoFrame)
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

    @staticmethod
    def _clear_layout(layout):
        """Recursively clear all items from a layout, deleting widgets."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                sub = item.layout()
                if sub:
                    TablesScreen._clear_layout(sub)

    def _refresh(self):
        # Clear layout — рекурсивно удаляем виджеты и вложенные лэйауты
        self._clear_layout(self._layout)

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
            status_header_btn = SecondaryButton("✏️ Изменить статус")
            status_header_btn.clicked.connect(self._on_bulk_status_change)
            header.addWidget(status_header_btn)
            add_table_btn = PrimaryButton("➕ Добавить столик")
            add_table_btn.clicked.connect(self._on_add_table)
            header.addWidget(add_table_btn)
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

    def _on_edit_table(self, table_id: int):
        """Open dialog to edit table properties (number, seats, zone)."""
        try:
            tables = get_all_tables()
            table = next((t for t in tables if t["id"] == table_id), None)
            if not table:
                QMessageBox.warning(self, "Ошибка", "Столик не найден")
                return
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            return
        dlg = TableEditDialog(table=table, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            result = dlg.get_result()
            try:
                update_table(
                    table_id,
                    table_number=result["table_number"],
                    seats_count=result["seats"],
                    zone=result["zone"],
                )
                self._refresh()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить столик:\n{e}")

    def _on_change_table_status(self, table_id: int, current_status: str):
        """Open dialog to change table status."""
        dlg = TableStatusDialog(current_status, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_status = dlg.get_selected_status()
            if new_status and new_status != current_status:
                try:
                    update_table_status(table_id, new_status)
                    self._refresh()
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось изменить статус:\n{e}")

    def _on_add_table(self):
        """Open dialog to create a new table."""
        dlg = TableEditDialog(table=None, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            result = dlg.get_result()
            try:
                create_table(result["table_number"], result["seats"], result["zone"])
                self._refresh()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать столик:\n{e}")

    def _on_bulk_status_change(self):
        """Show dialog with table selector and status selector."""
        try:
            tables = get_all_tables()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить столики:\n{e}")
            return
        dlg = TableBulkStatusDialog(tables, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            table_id, new_status = dlg.get_result()
            try:
                update_table_status(table_id, new_status)
                self._refresh()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось изменить статус:\n{e}")

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
        card.setFixedSize(280, 260)

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
            edit_btn = SecondaryButton("✏️ Изменить")
            edit_btn.clicked.connect(lambda checked, tid=t["id"]: self._on_edit_table(tid))
            actions.addWidget(edit_btn)
            status_btn = SecondaryButton("⚙️ Статус")
            status_btn.clicked.connect(lambda checked, tid=t["id"], st=t["status"]: self._on_change_table_status(tid, st))
            actions.addWidget(status_btn)
        elif self._role == "waiter" and t["status"] == "occupied" and self._navigate:
            btn = SecondaryButton("Открыть заказ")
            btn.clicked.connect(lambda nav=self._navigate, oid=t.get("order_id"): _navigate_to_order(nav, oid) if nav and oid else None)
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
        self._active_category = ""
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        self._setup_ui()

    def showEvent(self, event):
        super().showEvent(event)
        global _selected_customer_for_order
        if _selected_customer_for_order is not None:
            name = _selected_customer_for_order.get("full_name", "")
            self._customer_input.setText(name)
            self._customer_name = name
            _selected_customer_for_order = None

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

        try:
            db_categories = [c["name"] for c in get_all_categories()]
        except:
            db_categories = []
        categories = db_categories if db_categories else ["Все блюда"]
        if not self._active_category and categories:
            self._active_category = categories[0]
        for cat in categories:
            btn = QPushButton(cat)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            active = cat == self._active_category
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: none;
                    border-bottom: 2px solid {GOLD if active else 'transparent'};
                    color: {GOLD if active else TEXT_SECONDARY};
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
        self._dishes_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._dishes_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
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
        self._cart_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._cart_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
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
        bg = BG_CARD if available else '#1A1D21'
        bd = BORDER if available else '#252932'
        card.setStyleSheet(f"""
            background: {bg};
            border: 1px solid {bd};
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
        # Clear discount layout
        while self._discount_layout.count():
            item = self._discount_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if text.strip():
            # Show discount input
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

class AddDishDialog(QDialog):
    """Диалог добавления блюда в заказ."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить блюдо")
        self.setModal(True)
        self.setMinimumSize(420, 320)
        self._dishes_map: dict = {}

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        try:
            dishes = get_available_dishes()
            if not dishes:
                dishes = get_all_dishes()
        except Exception:
            dishes = []

        self._dishes_map = {d["id"]: d for d in dishes}

        # Dish combo
        layout.addWidget(make_label("Блюдо:", 13, TEXT_PRIMARY))
        self._dish_combo = QComboBox()
        self._dish_combo.addItem("— Выберите блюдо —", None)
        for d in dishes:
            label = f"{d['name']} — {float(d['price']):,.0f} ₽".replace(",", " ")
            self._dish_combo.addItem(label, d["id"])
        layout.addWidget(self._dish_combo)

        # Quantity
        qty_row = QHBoxLayout()
        qty_row.addWidget(make_label("Количество:", 13, TEXT_PRIMARY))
        self._qty_spin = QSpinBox()
        self._qty_spin.setMinimum(1)
        self._qty_spin.setMaximum(99)
        self._qty_spin.setValue(1)
        self._qty_spin.setFixedWidth(80)
        qty_row.addWidget(self._qty_spin)
        qty_row.addStretch()
        layout.addLayout(qty_row)

        # Comment
        layout.addWidget(make_label("Комментарий:", 13, TEXT_PRIMARY))
        self._comment_edit = QLineEdit()
        self._comment_edit.setPlaceholderText("Опционально")
        layout.addWidget(self._comment_edit)

        layout.addStretch()

        # Buttons
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.button(QDialogButtonBox.StandardButton.Ok).setText("Добавить")
        btn_box.accepted.connect(self._on_accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _on_accept(self):
        if self._dish_combo.currentData() is None:
            QMessageBox.warning(self, "Ошибка", "Выберите блюдо")
            return
        self.accept()

    def get_result(self) -> dict:
        dish_id = self._dish_combo.currentData()
        dish = self._dishes_map.get(dish_id, {})
        return {
            "dish_id": dish_id,
            "quantity": self._qty_spin.value(),
            "price": float(dish.get("price", 0)),
            "comment": self._comment_edit.text().strip(),
        }


class StatusDialog(QDialog):
    """Диалог выбора нового статуса заказа."""

    def __init__(self, statuses: list[tuple[str, str]], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Изменить статус")
        self.setModal(True)
        self.setMinimumSize(300, 140)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        layout.addWidget(make_label("Новый статус:", 13, TEXT_PRIMARY))
        self._combo = QComboBox()
        for key, label in statuses:
            self._combo.addItem(label, key)
        layout.addWidget(self._combo)

        layout.addStretch()

        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.button(QDialogButtonBox.StandardButton.Ok).setText("Подтвердить")
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def get_selected_status(self) -> str | None:
        return self._combo.currentData()


class OrderDetailsScreen(QWidget):
    """Детальный просмотр заказа с управлением."""

    def __init__(self, role: str = "admin", on_navigate=None):
        super().__init__()
        self._role = role
        self._navigate = on_navigate
        self._current_order_id: int | None = None
        self._current_order: dict | None = None
        self._content_widget: QWidget | None = None
        self._outer_layout: QVBoxLayout | None = None
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        self._setup_ui()

    def _setup_ui(self):
        """Create the scroll skeleton and back button (persistent)."""
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        outer = QWidget()
        self._outer_layout = QVBoxLayout(outer)
        self._outer_layout.setContentsMargins(28, 28, 28, 28)
        self._outer_layout.setSpacing(20)

        # Back button (stays across order loads)
        if self._navigate:
            back_btn = QPushButton("← Назад к заказам")
            back_btn.setStyleSheet(f"""
                background: none; border: none;
                color: {TEXT_SECONDARY}; font-size: 13px;
                text-align: left;
            """)
            back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            back_btn.clicked.connect(lambda: self._navigate("orders"))
            self._outer_layout.addWidget(back_btn)

        scroll.setWidget(outer)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Initial load
        self._refresh()

    def load_order(self, order_id: int):
        """Public method to load a specific order by ID."""
        self._current_order_id = order_id
        self._refresh()

    def showEvent(self, event):
        """Refresh data when the screen becomes visible (handles navigation)."""
        super().showEvent(event)
        global _order_details_pending_id
        if _order_details_pending_id is not None:
            self._current_order_id = _order_details_pending_id
            _order_details_pending_id = None
        self._refresh()

    # ─── Core loading / refresh ──────────────────────────────────

    def _refresh(self):
        """Reload order data and rebuild the entire content area."""
        global _order_details_pending_id

        # Consume pending order ID if one exists
        if _order_details_pending_id is not None:
            self._current_order_id = _order_details_pending_id
            _order_details_pending_id = None

        # Remove old content widget
        if self._content_widget is not None:
            self._outer_layout.removeWidget(self._content_widget)
            self._content_widget.deleteLater()
            self._content_widget = None

        self._content_widget = QWidget()
        cl = QVBoxLayout(self._content_widget)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(20)

        # Determine which order to load
        self._current_order = None
        order_id = self._current_order_id
        if order_id is not None:
            try:
                self._current_order = get_order_by_id(order_id)
            except Exception:
                pass

        if self._current_order is None:
            # Fallback: first available order
            try:
                orders = get_all_orders()
                if orders:
                    self._current_order = orders[0]
            except Exception:
                pass

        order = self._current_order
        self._current_order_id = order["id"] if order else None

        if not order:
            cl.addWidget(make_label("Нет заказов для просмотра", 14, TEXT_MUTED))
            self._outer_layout.addWidget(self._content_widget)
            return

        # ─── Header ──────────────────────────────────────────
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
        header.addWidget(StatusBadge(cfg))
        header_widget = QWidget()
        header_widget.setLayout(header)
        cl.addWidget(header_widget)

        # ─── Body: left column + right sidebar ────────────────
        content_row = QHBoxLayout()
        content_row.setSpacing(20)

        left_col = QVBoxLayout()
        left_col.setSpacing(16)

        # ── Items table ──
        try:
            items = get_order_items(order["id"])
        except Exception:
            items = []

        table_card = Card()
        tl = QVBoxLayout(table_card)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.addWidget(SectionHeader("Состав заказа"))
        tl.addWidget(make_label("", 1))

        table = DataTable(["Блюдо", "Кол-во", "Цена", "Сумма", "Комментарий"])
        table.setRowCount(len(items))
        for i, item in enumerate(items):
            table.setItem(i, 0, QTableWidgetItem(item.get("dish_name", "—")))
            table.setItem(i, 1, QTableWidgetItem(str(item["quantity"])))
            table.setItem(i, 2, QTableWidgetItem(
                f"{float(item['price_at_order']):,.0f} ₽".replace(",", " ")
            ))
            table.setItem(i, 3, QTableWidgetItem(
                f"{float(item['item_total']):,.0f} ₽".replace(",", " ")
            ))
            table.setItem(i, 4, QTableWidgetItem(item.get("comment", "—") or "—"))
        tl.addWidget(table)
        left_col.addWidget(table_card)

        # ── Totals ──
        total_card = Card()
        total_l = QVBoxLayout(total_card)
        total_l.setContentsMargins(24, 20, 24, 20)
        total_l.setSpacing(8)
        total_l.addWidget(make_label(
            f"Сумма: {float(order['total_amount']):,.0f} ₽".replace(",", " "),
            14, TEXT_SECONDARY
        ))
        if float(order.get("discount_amount", 0)) > 0:
            total_l.addWidget(make_label(
                f"Скидка: −{float(order['discount_amount']):,.0f} ₽".replace(",", " "),
                14, SUCCESS
            ))
        total_l.addWidget(make_manrope_label(
            f"Итого: {float(order['final_amount']):,.0f} ₽".replace(",", " "),
            18, QFont.Weight.ExtraBold, GOLD
        ))
        left_col.addWidget(total_card)

        # ── Action buttons (role- and status-aware) ──
        actions = QHBoxLayout()
        actions.setSpacing(10)

        status = order.get("status", "")
        is_terminal = status in ("paid", "cancelled")

        if self._role == "waiter":
            if not is_terminal:
                # "Добавить блюдо"
                add_btn = PrimaryButton("Добавить блюдо")
                add_btn.clicked.connect(self._on_add_dish)
                actions.addWidget(add_btn)

                # "Изменить статус" (only if there is a next status)
                if self._get_next_statuses(status):
                    status_btn = SecondaryButton("Изменить статус")
                    status_btn.clicked.connect(self._on_change_status)
                    actions.addWidget(status_btn)

                # "Перейти к оплате" (ready / served)
                if status in ("ready", "served"):
                    pay_btn = PrimaryButton("✅ Перейти к оплате")
                    pay_btn.setStyleSheet(f"""
                        QPushButton {{
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #3FA66B, stop:1 #2D8A55);
                            border: none; border-radius: 8px;
                            color: white; font-size: 13px; font-weight: 600;
                            padding: 10px 20px;
                        }}
                        QPushButton:hover {{
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #4BBF7A, stop:1 #3A9E62);
                        }}
                    """)
                    pay_btn.clicked.connect(self._on_pay_order)
                    actions.addWidget(pay_btn)

                # "Отменить заказ"
                cancel_btn = DangerButton("Отменить заказ")
                cancel_btn.clicked.connect(self._on_cancel_order)
                actions.addWidget(cancel_btn)
            else:
                label_text = "Оплачен" if status == "paid" else "Отменён"
                actions.addWidget(make_label(label_text, 13, TEXT_MUTED))

        elif self._role == "admin":
            edit_btn = SecondaryButton("Редактировать заказ")
            edit_btn.clicked.connect(self._on_edit_order)
            actions.addWidget(edit_btn)

            payment_btn = SecondaryButton("Просмотреть оплату")
            payment_btn.clicked.connect(self._on_view_payment)
            actions.addWidget(payment_btn)

            history_btn = SecondaryButton("История изменений")
            history_btn.clicked.connect(self._on_view_history)
            actions.addWidget(history_btn)

            if not is_terminal:
                cancel_btn = DangerButton("Отменить заказ")
                cancel_btn.clicked.connect(self._on_cancel_order)
                actions.addWidget(cancel_btn)

        left_col.addLayout(actions)
        content_row.addLayout(left_col, 1)

        # ─── Right column: timeline + info ─────────────────────
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

            if current:
                dot_color = GOLD
                dot_bg = f"rgba({','.join(map(str, hex_to_rgb(GOLD)))},0.15)"
                dot_border = GOLD
            elif done:
                dot_color = SUCCESS
                dot_bg = f"rgba({','.join(map(str, hex_to_rgb(SUCCESS)))},0.1)"
                dot_border = SUCCESS
            else:
                dot_color = TEXT_MUTED
                dot_bg = "transparent"
                dot_border = BORDER

            dot = QLabel("●" if done else "○")
            dot.setStyleSheet(
                f"font-size: 14px; color: {dot_color};"
                f"background: {dot_bg};"
                f"border: 2px solid {dot_border};"
                f"border-radius: 14px; padding: 4px;"
            )
            step.addWidget(dot)

            lbl = make_label(
                label, 13,
                GOLD if current else (TEXT_PRIMARY if done else TEXT_MUTED),
                QFont.Weight.Bold if current else QFont.Weight.Normal
            )
            step.addWidget(lbl)
            step.addStretch()
            tml.addLayout(step)

            if i < len(status_order) - 1:
                line = QFrame()
                line.setFixedWidth(2)
                line.setFixedHeight(20)
                line_color = f"{SUCCESS}44" if done and i < current_idx else BORDER
                line.setStyleSheet(f"background: {line_color}; margin-left: 10px;")
                tml.addWidget(line, alignment=Qt.AlignmentFlag.AlignLeft)

        # Cancelled state step after the normal flow
        if status == "cancelled":
            step = QHBoxLayout()
            step.setSpacing(14)
            dot = QLabel("✕")
            dot.setStyleSheet(
                f"font-size: 14px; color: {ERROR};"
                f"border: 2px solid {ERROR};"
                f"border-radius: 14px; padding: 4px;"
            )
            step.addWidget(dot)
            step.addWidget(make_label("Отменён", 13, ERROR, QFont.Weight.Bold))
            step.addStretch()
            tml.addLayout(step)

        right_col.addWidget(timeline_card)

        # Info card
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

        # Closed-at info for terminal statuses
        if status in ("paid", "cancelled") and order.get("closed_at"):
            label_text = "Оплачен" if status == "paid" else "Отменён"
            right_col.addWidget(make_label(
                f"{label_text}: {order['closed_at']}", 12, TEXT_MUTED
            ))

        content_row.addLayout(right_col)

        content_row_widget = QWidget()
        content_row_widget.setLayout(content_row)
        cl.addWidget(content_row_widget)

        self._outer_layout.addWidget(self._content_widget)

    # ─── Status helpers ─────────────────────────────────────────

    @staticmethod
    def _get_next_statuses(current_status: str) -> list[tuple[str, str]]:
        """Return valid next status transitions."""
        transitions = {
            "new": [("cooking", "Готовится")],
            "cooking": [("ready", "Готов")],
            "ready": [("served", "Подан")],
            "served": [("paid", "Оплачен")],
            "paid": [],
            "cancelled": [],
        }
        return transitions.get(current_status, [])

    # ─── Action handlers ─────────────────────────────────────────

    def _on_add_dish(self):
        """Show dish selector dialog and add the chosen dish to the order."""
        if self._current_order_id is None:
            return
        dlg = AddDishDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            result = dlg.get_result()
            try:
                add_order_item(
                    self._current_order_id,
                    result["dish_id"],
                    result["quantity"],
                    result["price"],
                    result["comment"],
                )
                self._refresh()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить блюдо:\n{e}")

    def _on_change_status(self):
        """Show status selector dialog and update the order status."""
        if self._current_order_id is None or self._current_order is None:
            return
        next_statuses = self._get_next_statuses(self._current_order["status"])
        if not next_statuses:
            QMessageBox.information(self, "Инфо", "Нет доступных статусов для изменения")
            return
        dlg = StatusDialog(next_statuses, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_status = dlg.get_selected_status()
            if new_status:
                try:
                    update_order_status(self._current_order_id, new_status)
                    self._refresh()
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось изменить статус:\n{e}")

    def _on_pay_order(self):
        """Open payment dialog. On confirmation create payment and mark order paid."""
        if self._current_order_id is None or self._current_order is None:
            return
        order = self._current_order
        method = PaymentDialog.get_payment(
            order_id=order["id"],
            table_number=order.get("table_number", "?"),
            subtotal=float(order["total_amount"]),
            discount=float(order.get("discount_amount", 0)),
            final_amount=float(order["final_amount"]),
            parent=self,
        )
        if method:
            try:
                create_payment(order["id"], float(order["final_amount"]), method)
                update_order_status(order["id"], "paid")
                QMessageBox.information(
                    self, "Оплачено",
                    f"Заказ #{order['id']} оплачен ({method})"
                )
                if self._navigate:
                    self._navigate("orders")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось провести оплату:\n{e}")

    def _on_cancel_order(self):
        """Confirm and cancel the order."""
        if self._current_order_id is None:
            return
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите отменить заказ #{self._current_order_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                cancel_order(self._current_order_id)
                if self._navigate:
                    self._navigate("orders")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось отменить заказ:\n{e}")

    # ─── Placeholder handlers (admin) ────────────────────────────

    def _on_edit_order(self):
        if self._current_order is None:
            return
        dlg = OrderEditDialog(self._current_order, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._refresh()

    def _on_view_payment(self):
        if self._current_order is None:
            return
        dlg = PaymentViewDialog(self._current_order, self)
        dlg.exec()

    def _on_view_history(self):
        dlg = OrderHistoryDialog(self)
        dlg.exec()


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
                open_btn.clicked.connect(lambda checked, nav=self._navigate, oid=o["id"]: _navigate_to_order(nav, oid))
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
                pay_btn.clicked.connect(lambda checked, od=o: self._on_pay_order(od))
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
            open_btn.clicked.connect(lambda nav=self._navigate: _navigate_to_order(nav, self._selected_order_id) if self._selected_order_id else None)
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

    def _on_pay_order(self, order: dict):
        """Open payment dialog and process payment for the given order."""
        method = PaymentDialog.get_payment(
            order_id=order["id"],
            table_number=order.get("table_number", "?"),
            subtotal=float(order["total_amount"]),
            discount=float(order.get("discount_amount", 0)),
            final_amount=float(order["final_amount"]),
            parent=self,
        )
        if method:
            try:
                create_payment(order["id"], float(order["final_amount"]), method)
                update_order_status(order["id"], "paid")
                QMessageBox.information(
                    self, "Оплачено",
                    f"Заказ #{order['id']} оплачен ({method})"
                )
                self._setup_ui()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось провести оплату:\n{e}")


# ─── Меню ───────────────────────────────────────────────────────

class DishEditDialog(QDialog):
    """Диалог добавления/редактирования блюда в меню."""
    def __init__(self, dish: dict | None = None, parent=None):
        super().__init__(parent)
        self._dish = dish
        is_new = dish is None
        self.setWindowTitle("Добавить блюдо" if is_new else "Редактировать блюдо")
        self.setModal(True)
        self.setMinimumSize(450, 400)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        # Name
        layout.addWidget(make_label("Название блюда:", 13, TEXT_PRIMARY))
        self._name_edit = QLineEdit()
        if not is_new:
            self._name_edit.setText(dish.get("name", ""))
        layout.addWidget(self._name_edit)

        # Category
        layout.addWidget(make_label("Категория:", 13, TEXT_PRIMARY))
        self._cat_combo = QComboBox()
        try:
            cats = get_all_categories()
            for c in cats:
                self._cat_combo.addItem(c["name"], c["id"])
        except:
            pass
        if not is_new and dish.get("category_id"):
            idx = self._cat_combo.findData(dish["category_id"])
            if idx >= 0:
                self._cat_combo.setCurrentIndex(idx)
        layout.addWidget(self._cat_combo)

        # Price
        layout.addWidget(make_label("Цена (₽):", 13, TEXT_PRIMARY))
        self._price_spin = QDoubleSpinBox()
        self._price_spin.setMinimum(0)
        self._price_spin.setMaximum(999999)
        self._price_spin.setDecimals(2)
        if not is_new:
            self._price_spin.setValue(float(dish.get("price", 0)))
        layout.addWidget(self._price_spin)

        # Weight
        layout.addWidget(make_label("Вес (г):", 13, TEXT_PRIMARY))
        self._weight_edit = QLineEdit()
        if not is_new:
            self._weight_edit.setText(str(dish.get("weight", "")))
        layout.addWidget(self._weight_edit)

        # Cooking time
        layout.addWidget(make_label("Время приготовления (мин):", 13, TEXT_PRIMARY))
        self._cook_spin = QSpinBox()
        self._cook_spin.setMinimum(0)
        self._cook_spin.setMaximum(999)
        if not is_new:
            self._cook_spin.setValue(int(dish.get("cooking_time_minutes", 0) or 0))
        layout.addWidget(self._cook_spin)

        # Description
        layout.addWidget(make_label("Описание:", 13, TEXT_PRIMARY))
        self._desc_edit = QTextEdit()
        self._desc_edit.setMaximumHeight(80)
        if not is_new:
            self._desc_edit.setPlainText(dish.get("description", ""))
        layout.addWidget(self._desc_edit)

        # Is available
        self._avail_check = QCheckBox("Блюдо доступно")
        self._avail_check.setChecked(dish.get("is_available", True) if not is_new else True)
        self._avail_check.setStyleSheet(f"""
            QCheckBox {{ color: {TEXT_PRIMARY}; font-size: 13px; spacing: 8px; }}
            QCheckBox::indicator {{ width: 18px; height: 18px; }}
        """)
        layout.addWidget(self._avail_check)

        layout.addStretch()

        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.button(QDialogButtonBox.StandardButton.Ok).setText(
            "Добавить" if is_new else "Сохранить"
        )
        btn_box.accepted.connect(self._on_accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _on_accept(self):
        if not self._name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название блюда")
            return
        if self._price_spin.value() <= 0:
            QMessageBox.warning(self, "Ошибка", "Цена должна быть больше 0")
            return
        self.accept()

    def get_result(self) -> dict:
        return {
            "category_id": self._cat_combo.currentData(),
            "name": self._name_edit.text().strip(),
            "description": self._desc_edit.toPlainText().strip(),
            "price": self._price_spin.value(),
            "weight": self._weight_edit.text().strip(),
            "cooking_time_minutes": self._cook_spin.value(),
            "is_available": self._avail_check.isChecked(),
        }


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
            add_dish_btn = PrimaryButton("➕ Добавить блюдо")
            add_dish_btn.clicked.connect(self._on_add_dish)
            header.addWidget(add_dish_btn)
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
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        grid_widget = QWidget()
        self._grid = QGridLayout(grid_widget)
        self._grid.setSpacing(14)
        scroll.setWidget(grid_widget)
        rl.addWidget(scroll, 1)

        self._refresh_grid()
        main_layout.addWidget(right, 1)

    def _on_add_dish(self):
        """Open dialog to create a new dish."""
        dlg = DishEditDialog(dish=None, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            result = dlg.get_result()
            try:
                create_dish(
                    result["category_id"], result["name"],
                    result["description"], result["price"],
                    result["weight"], result["cooking_time_minutes"],
                )
                self._refresh_grid()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить блюдо:\n{e}")

    def _on_edit_dish(self, dish: dict):
        """Open dialog to edit an existing dish."""
        dlg = DishEditDialog(dish=dish, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            result = dlg.get_result()
            try:
                update_dish(dish["id"], **result)
                self._refresh_grid()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить блюдо:\n{e}")

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
        bg = BG_CARD if available else '#1A1D21'
        bd = BORDER if available else '#252932'
        card.setStyleSheet(f"""
            background: {bg};
            border: 1px solid {bd};
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
            edit_btn.clicked.connect(lambda checked, d=dish: self._on_edit_dish(d))
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

class CustomerEditDialog(QDialog):
    """Диалог создания/редактирования клиента."""
    def __init__(self, customer: dict | None = None, parent=None):
        super().__init__(parent)
        self._customer = customer
        is_new = customer is None
        self.setWindowTitle("Создать клиента" if is_new else "Редактировать клиента")
        self.setModal(True)
        self.setMinimumSize(400, 350)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        layout.addWidget(make_label("Имя:", 13, TEXT_PRIMARY))
        self._name_edit = QLineEdit()
        if not is_new:
            self._name_edit.setText(customer.get("full_name", ""))
        layout.addWidget(self._name_edit)

        layout.addWidget(make_label("Телефон:", 13, TEXT_PRIMARY))
        self._phone_edit = QLineEdit()
        if not is_new:
            self._phone_edit.setText(customer.get("phone", ""))
        layout.addWidget(self._phone_edit)

        layout.addWidget(make_label("Email:", 13, TEXT_PRIMARY))
        self._email_edit = QLineEdit()
        if not is_new:
            self._email_edit.setText(customer.get("email", ""))
        layout.addWidget(self._email_edit)

        layout.addWidget(make_label("Скидка (%):", 13, TEXT_PRIMARY))
        self._discount_spin = QSpinBox()
        self._discount_spin.setMinimum(0)
        self._discount_spin.setMaximum(50)
        if not is_new:
            self._discount_spin.setValue(int(customer.get("discount_percent", 0) or 0))
        layout.addWidget(self._discount_spin)

        layout.addStretch()

        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.button(QDialogButtonBox.StandardButton.Ok).setText(
            "Создать" if is_new else "Сохранить"
        )
        btn_box.accepted.connect(self._on_accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _on_accept(self):
        if not self._name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите имя клиента")
            return
        self.accept()

    def get_result(self) -> dict:
        return {
            "full_name": self._name_edit.text().strip(),
            "phone": self._phone_edit.text().strip(),
            "email": self._email_edit.text().strip(),
            "discount_percent": self._discount_spin.value(),
        }


# ─── Helper functions for CustomersScreen ──────────────────────────

AVATAR_PALETTE = [
    "#C9A45C", "#3FA66B", "#4A7BD0", "#D98A35", "#9B6CDD",
    "#E06060", "#5CB8C9", "#C97B5C", "#7BC96C", "#C96CB8",
    "#5CA0C9", "#C96C6C", "#6CC9A4", "#A06CC9", "#C9A46C",
    "#6C8CC9", "#C9A46C", "#4A9BD0", "#D07A4A", "#7A6CC9",
]


def _avatar_color(name: str) -> str:
    """Deterministic pastel color from customer name."""
    idx = abs(hash(name or "")) % len(AVATAR_PALETTE)
    return AVATAR_PALETTE[idx]


def _pluralize(count: int, forms: tuple[str, str, str]) -> str:
    """Russian pluralization: 1 клиент, 2 клиента, 5 клиентов."""
    if count % 10 == 1 and count % 100 != 11:
        return forms[0]
    if 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
        return forms[1]
    return forms[2]


MONTHS_RU = ["янв", "фев", "мар", "апр", "мая", "июн",
             "июл", "авг", "сен", "окт", "ноя", "дек"]


def _format_date(iso_date) -> str:
    """Convert ISO date → '19 июн 2025'."""
    if not iso_date:
        return "—"
    try:
        if isinstance(iso_date, str):
            dt = datetime.fromisoformat(iso_date)
        else:
            dt = iso_date
        return f"{dt.day} {MONTHS_RU[dt.month - 1]} {dt.year}"
    except Exception:
        return str(iso_date)


class CustomersScreen(QWidget):
    def __init__(self, role: str = "admin", on_navigate=None):
        super().__init__()
        self._role = role
        self._on_navigate = on_navigate
        self._search = ""
        self._page_size = 10
        self._visible_count = self._page_size
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        self._setup_ui()

    def _setup_ui(self):
        """Создаёт структуру экрана (однократно)."""
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._content = QWidget()
        self._layout = QVBoxLayout(self._content)
        self._layout.setContentsMargins(28, 28, 28, 28)
        self._layout.setSpacing(20)

        self._refresh()

        scroll.setWidget(self._content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    @staticmethod
    def _clear_layout(layout):
        """Recursively clear all items from a layout."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                sub = item.layout()
                if sub:
                    CustomersScreen._clear_layout(sub)

    def _refresh(self):
        """Перестраивает содержимое внутри существующего scroll-а."""
        self._clear_layout(self._layout)
        if self._role == "waiter":
            self._build_waiter_view(self._layout)
        else:
            self._build_admin_view(self._layout)

    # ─── Admin view ───────────────────────────────────────────

    def _build_admin_view(self, layout: QVBoxLayout):
        try:
            all_customers = get_all_customers()
            if self._search:
                all_customers = find_customers(self._search)
        except Exception:
            all_customers = []

        visible = all_customers[:self._visible_count]
        has_more = len(all_customers) > self._visible_count

        # ── Header ──
        header = QHBoxLayout()
        hleft = QVBoxLayout()
        hleft.addWidget(make_manrope_label("Клиенты", 24, QFont.Weight.ExtraBold))
        plural = _pluralize(len(all_customers), ("клиент", "клиента", "клиентов"))
        hleft.addWidget(make_label(f"{len(all_customers)} {plural} в базе", 13, TEXT_MUTED))
        header.addLayout(hleft)
        header.addStretch()
        add_btn = PrimaryButton("➕ Добавить клиента")
        add_btn.clicked.connect(self._on_create_customer)
        header.addWidget(add_btn)
        layout.addLayout(header)

        # ── Search ──
        search = SearchInput("🔍 Поиск по имени, телефону или email")
        search.setMaximumWidth(400)
        search.textChanged.connect(lambda t: self._set_search(t))
        layout.addWidget(search)

        # ── Empty state ──
        if not all_customers:
            empty = QFrame()
            empty.setStyleSheet(f"""
                QFrame {{ background: {BG_CARD}; border: 1px solid {BORDER};
                          border-radius: 12px; }}
            """)
            empty.setMinimumHeight(200)
            el = QVBoxLayout(empty)
            el.setAlignment(Qt.AlignmentFlag.AlignCenter)
            el.addWidget(make_label("👥", 40, TEXT_MUTED))
            el.addWidget(make_manrope_label(
                "Нет клиентов" if not self._search else "Ничего не найдено",
                16, QFont.Weight.DemiBold, TEXT_SECONDARY,
            ))
            el.addWidget(make_label(
                "Добавьте первого клиента" if not self._search
                else "Попробуйте изменить запрос",
                13, TEXT_MUTED,
            ))
            layout.addWidget(empty)
            return

        # ── Table ──
        columns = ["Имя", "Телефон", "Email", "Скидка", "Заказов",
                    "Сумма", "Посл. визит", ""]
        table = DataTable(columns)
        table.setRowCount(len(visible))
        table.horizontalHeader().setStretchLastSection(False)

        # Column sizing — все колонки интерактивные (пользователь может менять ширину)
        hh = table.horizontalHeader()
        for col in range(table.columnCount()):
            hh.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)

        # Увеличенная ширина колонок
        for col, w in {0: 220, 1: 160, 2: 220, 3: 90, 4: 85, 5: 160, 6: 150, 7: 130}.items():
            table.setColumnWidth(col, w)

        for i, c in enumerate(visible):
            # ── Name with avatar ──
            name = c.get("full_name", "—")
            initial = name[0] if name and name != "—" else "?"
            color = _avatar_color(name)

            name_widget = QWidget()
            name_widget.setStyleSheet("background: transparent;")
            nl = QHBoxLayout(name_widget)
            nl.setContentsMargins(0, 0, 0, 0)
            nl.setSpacing(10)

            avatar = QLabel(initial)
            avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            avatar.setFixedSize(36, 36)
            avatar.setStyleSheet(f"""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color}, stop:1 #00000000);
                border: 2px solid {color}55;
                border-radius: 18px;
                font-size: 13px;
                font-weight: 700;
                color: #FFFFFF;
            """)
            nl.addWidget(avatar)
            nl.addWidget(make_label(name, 14, TEXT_PRIMARY, QFont.Weight.DemiBold))
            nl.addStretch()
            table.setCellWidget(i, 0, name_widget)

            # ── Phone ──
            item = QTableWidgetItem(c.get("phone", "—"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
            table.setItem(i, 1, item)

            # ── Email ──
            item = QTableWidgetItem(c.get("email", "—"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
            table.setItem(i, 2, item)

            # ── Discount badge ──
            disc_widget = QWidget()
            disc_widget.setStyleSheet("background: transparent;")
            dl = QHBoxLayout(disc_widget)
            dl.setContentsMargins(0, 0, 0, 0)
            disc = float(c.get("discount_percent", 0) or 0)
            if disc > 0:
                badge = QLabel(f"−{disc:.0f}%")
                badge.setStyleSheet(f"""
                    background: rgba(201,164,92,0.12);
                    border: 1px solid rgba(201,164,92,0.25);
                    border-radius: 6px;
                    color: {GOLD};
                    font-size: 12px;
                    font-weight: 700;
                    padding: 2px 8px;
                """)
                dl.addWidget(badge)
            else:
                dash = QLabel("—")
                dash.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 13px; background: transparent; border: none; padding: 0;")
                dl.addWidget(dash)
            dl.addStretch()
            table.setCellWidget(i, 3, disc_widget)

            # ── Orders count ──
            oc = str(int(c.get("orders_count", 0) or 0))
            item = QTableWidgetItem(oc)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            table.setItem(i, 4, item)

            # ── Total amount (monospace) ──
            total = float(c.get("total_amount", 0) or 0)
            amt_widget = QWidget()
            amt_widget.setStyleSheet("background: transparent;")
            amt_layout = QHBoxLayout(amt_widget)
            amt_layout.setContentsMargins(0, 0, 0, 0)
            amt_layout.setSpacing(2)

            amt_lbl = QLabel(f"{total:,.0f}".replace(",", " "))
            amt_lbl.setStyleSheet(f"""
                font-size: 13px; font-weight: 600; color: {TEXT_PRIMARY};
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                background: transparent;
            """)
            amt_layout.addWidget(amt_lbl)

            currency_lbl = QLabel("₽")
            currency_lbl.setStyleSheet(f"""
                font-size: 10px; color: {TEXT_MUTED};
                font-weight: 400; background: transparent;
            """)
            currency_lbl.setAlignment(Qt.AlignmentFlag.AlignBottom)
            amt_layout.addWidget(currency_lbl)
            amt_layout.addStretch()
            table.setCellWidget(i, 5, amt_widget)

            # ── Last visit ──
            item = QTableWidgetItem(_format_date(c.get("last_order_date")))
            item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
            table.setItem(i, 6, item)

            # ── Action buttons ──
            actions = QWidget()
            actions.setStyleSheet("background: transparent;")
            al = QHBoxLayout(actions)
            al.setContentsMargins(0, 0, 0, 0)
            al.setSpacing(4)

            for btn_data in (
                ("◉", "Открыть профиль", INFO, self._on_view_customer_history),
                ("✎", "Редактировать", GOLD, self._on_edit_customer),
                ("✕", "Удалить", ERROR, self._on_delete_customer),
            ):
                icon, tip, hover_color, handler = btn_data
                btn = QPushButton(icon)
                btn.setFixedSize(28, 28)
                btn.setToolTip(tip)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        border: 1px solid {BORDER};
                        border-radius: 6px;
                        color: {TEXT_SECONDARY};
                        font-size: 12px;
                    }}
                    QPushButton:hover {{
                        background: rgba({','.join(map(str, hex_to_rgb(hover_color)))}, 0.1);
                        border-color: {hover_color};
                        color: {hover_color};
                    }}
                """)
                r, g, b = hex_to_rgb(hover_color)
                btn.clicked.connect(lambda checked, cust=c, h=handler: h(cust))
                al.addWidget(btn)

            table.setCellWidget(i, 7, actions)

        layout.addWidget(table)

        # ── Pagination ──
        if has_more:
            remaining = len(all_customers) - self._visible_count
            more_btn = QPushButton(f"Показать ещё  ({remaining})")
            more_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            more_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {BG_CARD};
                    color: {GOLD};
                    border: 1px solid {BORDER};
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 600;
                    padding: 10px;
                }}
                QPushButton:hover {{
                    background: rgba(201,164,92,0.08);
                    border-color: rgba(201,164,92,0.3);
                }}
            """)
            more_btn.clicked.connect(self._on_show_more)
            layout.addWidget(more_btn)

        # ── Stats summary ──
        total_orders = sum(int(c.get("orders_count", 0) or 0) for c in all_customers)
        total_revenue = sum(float(c.get("total_amount", 0) or 0) for c in all_customers)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)

        for val, label_text, lbl_color in (
            (str(total_orders), _pluralize(total_orders, ("заказ", "заказа", "заказов")), GOLD),
            (f"{total_revenue:,.0f} ₽".replace(",", " "), "выручка", SUCCESS),
        ):
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{ background: {BG_CARD}; border: 1px solid {BORDER};
                          border-radius: 10px; }}
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 12, 16, 12)
            cl.setSpacing(2)
            cl.addWidget(make_label(val, 20, lbl_color, QFont.Weight.ExtraBold))
            cl.addWidget(make_label(label_text, 11, TEXT_MUTED))
            stats_row.addWidget(card)

        stats_row.addStretch()
        layout.addLayout(stats_row)

    # ─── Waiter view ───────────────────────────────────────────

    def _build_waiter_view(self, layout: QVBoxLayout):
        layout.addWidget(make_manrope_label("Клиенты", 24, QFont.Weight.ExtraBold))
        layout.addWidget(make_label("Поиск и выбор клиента для заказа", 13, TEXT_MUTED))

        search = QLineEdit()
        search.setPlaceholderText("\U0001F50D Найти клиента по имени или телефону")
        search.setStyleSheet(f"""
            QLineEdit {{
                background: {BG_CARD}; color: {TEXT_PRIMARY};
                border: 1px solid {BORDER}; border-radius: 8px;
                padding: 12px 12px 12px 40px; font-size: 14px;
                max-width: 480px;
            }}
        """)
        search.textChanged.connect(lambda t: self._set_search(t))
        layout.addWidget(search)

        create_btn = PrimaryButton("\U0001F464 Создать клиента")
        create_btn.clicked.connect(self._on_create_customer)
        hdr_actions = QHBoxLayout()
        hdr_actions.addWidget(create_btn)
        hdr_actions.addStretch()
        layout.addLayout(hdr_actions)

        try:
            customers = get_all_customers() if not self._search else find_customers(self._search)
        except Exception:
            customers = []

        if not customers:
            empty = QFrame()
            empty.setStyleSheet(f"""
                QFrame {{ background: {BG_CARD}; border: 1px solid {BORDER};
                          border-radius: 12px; }}
            """)
            empty.setMinimumHeight(160)
            el = QVBoxLayout(empty)
            el.setAlignment(Qt.AlignmentFlag.AlignCenter)
            el.addWidget(make_label("👥", 36, TEXT_MUTED))
            el.addWidget(make_label(
                "Нет клиентов" if not self._search else "Ничего не найдено",
                14, TEXT_SECONDARY,
            ))
            layout.addWidget(empty)
            return

        for c in customers[:self._visible_count]:
            card = Card()
            cl = QHBoxLayout(card)
            cl.setContentsMargins(16, 14, 16, 14)
            cl.setSpacing(14)

            name = c.get("full_name", "—")
            initial = name[0] if name and name != "—" else "?"
            color = _avatar_color(name)

            avatar = QLabel(initial)
            avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            avatar.setFixedSize(40, 40)
            avatar.setStyleSheet(f"""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color}, stop:1 #00000000);
                border: 2px solid {color}55;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 700;
                color: #FFFFFF;
            """)
            cl.addWidget(avatar)

            vi = QVBoxLayout()
            vi.setSpacing(2)
            vi.addWidget(make_label(name, 14, TEXT_PRIMARY, QFont.Weight.DemiBold))
            vi.addWidget(make_label(c.get("phone", ""), 12, TEXT_SECONDARY))
            cl.addLayout(vi)
            cl.addStretch()

            disc = float(c.get("discount_percent", 0) or 0)
            if disc > 0:
                badge = QLabel(f"−{disc:.0f}%")
                badge.setStyleSheet(f"""
                    background: rgba(201,164,92,0.1);
                    border: 1px solid rgba(201,164,92,0.2);
                    border-radius: 20px;
                    color: {GOLD}; font-size: 12px; font-weight: 600;
                    padding: 3px 10px;
                """)
                cl.addWidget(badge)

            select_btn = SecondaryButton("Выбрать клиента")
            select_btn.clicked.connect(lambda checked, cust=c: self._on_select_customer(cust))
            cl.addWidget(select_btn)

            layout.addWidget(card)

        # Waiter pagination
        if len(customers) > self._visible_count:
            remaining = len(customers) - self._visible_count
            more_btn = QPushButton(f"Показать ещё ({remaining})")
            more_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            more_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {BG_CARD}; color: {GOLD};
                    border: 1px solid {BORDER}; border-radius: 8px;
                    font-size: 13px; font-weight: 600; padding: 10px;
                }}
                QPushButton:hover {{
                    background: rgba(201,164,92,0.08);
                    border-color: rgba(201,164,92,0.3);
                }}
            """)
            more_btn.clicked.connect(self._on_show_more)
            layout.addWidget(more_btn)

    # ─── Search ────────────────────────────────────────────────

    def _set_search(self, text: str):
        self._search = text.strip()
        self._visible_count = self._page_size
        self._refresh()

    def _on_show_more(self):
        self._visible_count += self._page_size
        self._refresh()

    # ─── CRUD handlers ─────────────────────────────────────────

    def _on_create_customer(self):
        dlg = CustomerEditDialog(customer=None, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            result = dlg.get_result()
            try:
                create_customer(
                    result["full_name"], result["phone"], result["email"],
                    result["discount_percent"],
                )
                QMessageBox.information(self, "Готово",
                    f"Клиент {result['full_name']} создан")
                self._refresh()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                    f"Не удалось создать клиента:\n{e}")

    def _on_select_customer(self, customer: dict):
        global _selected_customer_for_order
        _selected_customer_for_order = customer
        name = customer.get("full_name", "—")
        QMessageBox.information(self, "Клиент выбран",
            f"Выбран клиент: {name}")
        if self._on_navigate:
            self._on_navigate("new-order")

    def _on_edit_customer(self, customer: dict):
        dlg = CustomerEditDialog(customer=customer, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            result = dlg.get_result()
            try:
                update_customer(customer["id"], **result)
                QMessageBox.information(self, "Готово",
                    f"Клиент {result['full_name']} обновлён")
                self._refresh()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                    f"Не удалось обновить клиента:\n{e}")

    def _on_delete_customer(self, customer: dict):
        name = customer.get("full_name", "—")
        reply = QMessageBox.question(
            self, "Удаление клиента",
            f"Вы уверены, что хотите удалить клиента «{name}»?\n"
            "История заказов клиента будет сохранена.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                delete_customer(customer["id"])
                self._refresh()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                    f"Не удалось удалить клиента:\n{e}")

    def _on_view_customer_history(self, customer: dict):
        cust_id = customer.get("id")
        name = customer.get("full_name", "—")
        try:
            all_orders = get_all_orders()
            orders = [o for o in all_orders if o.get("customer_id") == cust_id]
        except Exception:
            orders = []

        dlg = QDialog(self)
        dlg.setWindowTitle(f"Заказы клиента — {name}")
        dlg.setModal(True)
        dlg.setMinimumSize(700, 400)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        layout.addWidget(make_manrope_label(
            f"Заказы клиента: {name}", 16, QFont.Weight.DemiBold))
        layout.addWidget(make_label(
            f"Всего заказов: {len(orders)}", 13, TEXT_MUTED))

        if orders:
            table = DataTable(["№ заказа", "Дата", "Статус", "Сумма", "Итого"])
            table.setRowCount(len(orders))
            for i, o in enumerate(orders):
                table.setItem(i, 0, QTableWidgetItem(f"#{o['id']}"))
                table.setItem(i, 1, QTableWidgetItem(str(o.get("created_at", ""))))
                cfg = ORDER_STATUS_CONFIG.get(o["status"], {})
                table.setItem(i, 2, QTableWidgetItem(cfg.get("label", o["status"])))
                table.setItem(i, 3, QTableWidgetItem(
                    f"{float(o['total_amount']):,.0f} ₽".replace(",", " ")))
                table.setItem(i, 4, QTableWidgetItem(
                    f"{float(o['final_amount']):,.0f} ₽".replace(",", " ")))
            layout.addWidget(table)
        else:
            layout.addWidget(make_label("У клиента нет заказов", 14, TEXT_MUTED))

        layout.addStretch()

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn_box.rejected.connect(dlg.reject)
        layout.addWidget(btn_box)

        dlg.exec()


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
        scroll.setFrameShape(QFrame.Shape.NoFrame)
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
        self._period = "Неделя"
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(24)

        # Header
        month_names = ["января", "февраля", "марта", "апреля", "мая", "июня",
                       "июля", "августа", "сентября", "октября", "ноября", "декабря"]
        now_dt = datetime.now()
        date_str = f"{now_dt.day} {month_names[now_dt.month-1]} {now_dt.year}"
        header = QHBoxLayout()
        header.addWidget(make_manrope_label("Отчеты", 24, QFont.Weight.ExtraBold))
        header.addWidget(make_label(f"Аналитика · {date_str}", 13, TEXT_MUTED))
        header.addStretch()
        period_btns = QHBoxLayout()
        period_btns.setSpacing(8)
        self._period_btns = []
        for i, p in enumerate(["Сегодня", "Неделя", "Месяц"]):
            btn = FilterTab(p, self._period == p)
            btn.clicked.connect(lambda checked, pp=p: self._set_period(pp))
            period_btns.addWidget(btn)
            self._period_btns.append(btn)
        header.addLayout(period_btns)
        layout.addLayout(header)

        # Stats — загружаем реальные данные
        try:
            all_orders = get_all_orders()
            paid_orders = [o for o in all_orders if o.get("status") == "paid"]
            all_tables = get_all_tables()
            rev_data = get_daily_revenue()
            pop_dishes = get_popular_dishes()
        except:
            all_orders = []
            paid_orders = []
            all_tables = []
            rev_data = []
            pop_dishes = []

        today_total = sum(float(o.get("final_amount", 0) or 0) for o in paid_orders)
        today_orders = len(paid_orders)
        avg_check = today_total / today_orders if today_orders > 0 else 0
        top_dish_name = pop_dishes[0].get("name", "—") if pop_dishes else "—"
        top_dish_cnt = pop_dishes[0].get("order_count", 0) if pop_dishes else 0
        week_total = sum(float(r.get("total", 0)) for r in rev_data[:7])
        week_order_count = sum(int(r.get("order_count", 0)) for r in rev_data[:7])

        stats = QHBoxLayout()
        stats.setSpacing(14)
        stat_items = [
            ("Выручка за день", f"{today_total:,.0f} ₽".replace(",", " "), "", GOLD),
            ("Выручка за неделю", f"{week_total:,.0f} ₽".replace(",", " "), "", GOLD),
            ("Заказов сегодня", str(today_orders), "", INFO),
            ("Средний чек", f"{avg_check:,.0f} ₽".replace(",", " "), "", WARNING),
        ]
        if top_dish_name != "—":
            stat_items.append(("Топ блюдо", top_dish_name, f"{top_dish_cnt} заказов", "#9B6CDD"))
        stat_items.append(("Всего столиков", str(len(all_tables)), "", SUCCESS))
        for label, value, sub, color in stat_items:
            stats.addWidget(StatCard(label, value, sub, color))
        layout.addLayout(stats)

        # Charts
        charts_row = QHBoxLayout()
        charts_row.setSpacing(20)

        rev_card = Card()
        rl = QVBoxLayout(rev_card)
        rl.setContentsMargins(24, 24, 24, 24)
        rl.addWidget(SectionHeader("Продажи по дням", "Выручка за неделю"))
        rl.addSpacing(16)
        if rev_data:
            max_rev = max((float(r.get("total", 0)) for r in rev_data[:7]), default=1)
            for r in rev_data[:7]:
                day = str(r.get("payment_date", ""))[:3]
                rev_val = float(r.get("total", 0))
                pct = int(rev_val * 100 / max_rev) if max_rev else 0
                row = QHBoxLayout()
                row.addWidget(make_label(day, 13, TEXT_PRIMARY))
                row.addStretch()
                row.addWidget(make_label(f"{rev_val:,.0f} ₽".replace(",", " "), 13, GOLD, QFont.Weight.Bold))
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
        else:
            rl.addWidget(make_label("Нет данных о продажах", 13, TEXT_MUTED))
        charts_row.addWidget(rev_card, 1)

        # Status distribution
        status_counts = {}
        for o in all_orders:
            s = o.get("status", "unknown")
            status_counts[s] = status_counts.get(s, 0) + 1
        statuses_for_report = [
            ("paid", "Оплачен", EMERALD),
            ("served", "Подан", "#9B6CDD"),
            ("ready", "Готов", SUCCESS),
            ("cooking", "Готовится", WARNING),
            ("cancelled", "Отменен", ERROR),
        ]
        stats_card = Card()
        sl = QVBoxLayout(stats_card)
        sl.setContentsMargins(24, 24, 24, 24)
        sl.addWidget(SectionHeader("Заказы по статусу", "Распределение"))
        sl.addSpacing(16)
        for key, label, color in statuses_for_report:
            count = status_counts.get(key, 0)
            row = QHBoxLayout()
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 12px; border: none; padding: 0; margin: 0;")
            row.addWidget(dot)
            row.addWidget(make_label(label, 13, TEXT_SECONDARY))
            row.addStretch()
            row.addWidget(make_label(str(count), 13, TEXT_PRIMARY, QFont.Weight.Bold))
            sl.addLayout(row)
        charts_row.addWidget(stats_card, 1)

        layout.addLayout(charts_row)

        # Bottom row
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(20)

        # Popular dishes
        pop_card = Card()
        pl = QVBoxLayout(pop_card)
        pl.setContentsMargins(24, 24, 24, 24)
        pl.addWidget(SectionHeader("Популярные блюда", "По заказам"))
        pl.addSpacing(16)
        if pop_dishes:
            max_cnt = max((int(d.get("order_count", 0)) for d in pop_dishes), default=1) or 1
            for d in pop_dishes:
                name = d.get("name", "—")
                cnt = int(d.get("order_count", 0))
                pct = cnt * 100 // max_cnt
                pl.addWidget(make_label(name, 13, TEXT_PRIMARY))
                bar_row = QHBoxLayout()
                bar_row.setSpacing(8)
                bar = QFrame()
                bar.setFixedHeight(6)
                bar.setStyleSheet(f"""
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {GOLD}, stop:1 rgba(201,164,92,0.2));
                    border-radius: 3px;
                    max-width: {pct}%;
                """)
                bar_row.addWidget(bar)
                bar_row.addWidget(make_label(f"{cnt} заказов", 11, TEXT_MUTED))
                pl.addLayout(bar_row)
        else:
            pl.addWidget(make_label("Нет данных", 13, TEXT_MUTED))
        bottom_row.addWidget(pop_card, 2)

        # Payment method distribution
        pay_card = Card()
        pyl = QVBoxLayout(pay_card)
        pyl.setContentsMargins(24, 24, 24, 24)
        pyl.addWidget(SectionHeader("Способы оплаты", "Распределение"))
        pyl.addSpacing(16)
        try:
            payments = get_all_payments()
            method_counts = {}
            for p in payments:
                m = p.get("payment_method", "unknown")
                method_counts[m] = method_counts.get(m, 0) + float(p.get("amount", 0))
            total_pay = sum(method_counts.values()) or 1
            for method, amount in sorted(method_counts.items(), key=lambda x: -x[1]):
                pct = int(amount * 100 / total_pay) if total_pay else 0
                pyl.addWidget(make_label(method, 13, TEXT_PRIMARY))
                bar = QFrame()
                bar.setFixedHeight(6)
                bar.setStyleSheet(f"""
                    background: {GOLD};
                    border-radius: 3px;
                    max-width: {pct}%;
                """)
                pyl.addWidget(bar)
                pyl.addWidget(make_label(
                    f"{amount:,.0f} ₽ · {pct}%".replace(",", " "), 11, TEXT_MUTED))
        except:
            pyl.addWidget(make_label("Нет данных об оплатах", 13, TEXT_MUTED))
        bottom_row.addWidget(pay_card, 1)
        layout.addLayout(bottom_row)

        # Revenue table
        rev_table_card = Card()
        rtl = QVBoxLayout(rev_table_card)
        rtl.setContentsMargins(0, 0, 0, 0)
        rtl.addWidget(SectionHeader("Выручка по дням"))
        table = DataTable(["День", "Заказов", "Выручка", "Средний чек"])
        if rev_data:
            table.setRowCount(min(len(rev_data), 7))
            for i, r in enumerate(rev_data[:7]):
                day = str(r.get("payment_date", ""))[:10]
                cnt = int(r.get("order_count", 0))
                rev_val = float(r.get("total", 0))
                avg = int(rev_val / cnt) if cnt else 0
                table.setItem(i, 0, QTableWidgetItem(day))
                table.setItem(i, 1, QTableWidgetItem(str(cnt)))
                table.setItem(i, 2, QTableWidgetItem(f"{rev_val:,.0f} ₽".replace(",", " ")))
                table.setItem(i, 3, QTableWidgetItem(f"{avg:,} ₽".replace(",", " ")))
        rtl.addWidget(table)
        layout.addWidget(rev_table_card)

        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _set_period(self, period: str):
        """Switch report period and refresh."""
        self._period = period
        for btn in getattr(self, "_period_btns", []):
            btn.set_active(btn.text().strip() == period)


# ─── Настройки ──────────────────────────────────────────────────

class SettingsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self._current_section = 0
        self._nav_btns: list[QPushButton] = []
        self._settings_file = os.path.join(os.path.dirname(__file__), "..", "restaurant_settings.json")
        self._zones_file = os.path.join(os.path.dirname(__file__), "..", "restaurant_zones.json")
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        self._settings = self._load_settings()
        self._zones = self._load_zones()
        self._setup_ui()

    def _load_settings(self) -> dict:
        defaults = {
            "name": "GastroHub",
            "phone": "+7 (495) 123-45-67",
            "address": "Москва, ул. Тверская, 24",
            "email": "info@gastrohub.ru",
            "payment_methods": {"Наличные": True, "Банковская карта": True, "Онлайн-оплата": True},
        }
        try:
            with open(self._settings_file, encoding="utf-8") as f:
                data = json.load(f)
                defaults.update(data)
        except:
            pass
        return defaults

    def _save_settings_to_file(self):
        try:
            with open(self._settings_file, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
        except:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить настройки")

    def _load_zones(self) -> list:
        try:
            with open(self._zones_file, encoding="utf-8") as f:
                return json.load(f)
        except:
            return ["Основной зал", "VIP-зона", "Терраса"]

    def _save_zones(self):
        try:
            with open(self._zones_file, "w", encoding="utf-8") as f:
                json.dump(self._zones, f, indent=2, ensure_ascii=False)
        except:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить зоны")

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
            active = i == self._current_section
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left; padding: 10px 12px;
                    border-radius: 8px; border: none;
                    background: {'rgba(201,164,92,0.1)' if active else 'transparent'};
                    color: {GOLD if active else TEXT_SECONDARY};
                    font-size: 13px;
                    font-weight: {'600' if active else '400'};
                    border-left: 3px solid {GOLD if active else 'transparent'};
                }}
                QPushButton:hover {{
                    background: rgba(255,255,255,0.03);
                }}
            """)
            btn.clicked.connect(lambda checked, sec=i: self._set_section(sec))
            self._nav_btns.append(btn)
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

        # Name field
        nv = QVBoxLayout()
        nv.addWidget(make_label("Название", 11, TEXT_MUTED))
        self._restaurant_name_edit = QLineEdit(self._settings.get("name", "GastroHub"))
        self._restaurant_name_edit.setStyleSheet(f"""
            background: {BG_SECONDARY}; color: {TEXT_PRIMARY};
            border: 1px solid {BORDER}; border-radius: 8px;
            padding: 10px 14px; font-size: 13px;
        """)
        nv.addWidget(self._restaurant_name_edit)
        left_col.addLayout(nv)

        # Phone field
        pv = QVBoxLayout()
        pv.addWidget(make_label("Телефон", 11, TEXT_MUTED))
        self._restaurant_phone_edit = QLineEdit(self._settings.get("phone", "+7 (495) 123-45-67"))
        self._restaurant_phone_edit.setStyleSheet(f"""
            background: {BG_SECONDARY}; color: {TEXT_PRIMARY};
            border: 1px solid {BORDER}; border-radius: 8px;
            padding: 10px 14px; font-size: 13px;
        """)
        pv.addWidget(self._restaurant_phone_edit)
        left_col.addLayout(pv)

        right_col = QVBoxLayout()
        right_col.setSpacing(16)

        # Address field
        av = QVBoxLayout()
        av.addWidget(make_label("Адрес", 11, TEXT_MUTED))
        self._restaurant_address_edit = QLineEdit(self._settings.get("address", "Москва, ул. Тверская, 24"))
        self._restaurant_address_edit.setStyleSheet(f"""
            background: {BG_SECONDARY}; color: {TEXT_PRIMARY};
            border: 1px solid {BORDER}; border-radius: 8px;
            padding: 10px 14px; font-size: 13px;
        """)
        av.addWidget(self._restaurant_address_edit)
        right_col.addLayout(av)

        # Email field
        ev = QVBoxLayout()
        ev.addWidget(make_label("Email", 11, TEXT_MUTED))
        self._restaurant_email_edit = QLineEdit(self._settings.get("email", "info@gastrohub.ru"))
        self._restaurant_email_edit.setStyleSheet(f"""
            background: {BG_SECONDARY}; color: {TEXT_PRIMARY};
            border: 1px solid {BORDER}; border-radius: 8px;
            padding: 10px 14px; font-size: 13px;
        """)
        ev.addWidget(self._restaurant_email_edit)
        right_col.addLayout(ev)

        fields_grid.addLayout(left_col)
        fields_grid.addLayout(right_col)
        pl.addLayout(fields_grid)
        pl.addSpacing(16)
        save_btn = PrimaryButton("Сохранить изменения")
        save_btn.clicked.connect(self._on_save_settings)
        pl.addWidget(save_btn)
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
            dot.setStyleSheet(f"color: {color}; font-size: 10px; border: none; padding: 0; margin: 0;")
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
        add_zone_btn = PrimaryButton("Добавить зону")
        add_zone_btn.clicked.connect(self._on_add_zone)
        zone_header.addWidget(add_zone_btn)
        zl.addLayout(zone_header)
        zl.addSpacing(12)
        self._zone_rows: list[QFrame] = []
        for zone in self._zones:
            row = QFrame()
            row.setStyleSheet(f"""
                background: {BG_SECONDARY};
                border: 1px solid {BORDER}; border-radius: 8px;
            """)
            rl2 = QHBoxLayout(row)
            rl2.setContentsMargins(16, 12, 16, 12)
            rl2.addWidget(make_label(f"📍 {zone}", 14, TEXT_PRIMARY))
            rl2.addStretch()
            edit_btn = SecondaryButton("Редактировать")
            edit_btn.clicked.connect(lambda checked, z=zone: self._on_edit_zone(z))
            rl2.addWidget(edit_btn)
            del_btn = DangerButton("✕")
            del_btn.setFixedSize(32, 32)
            del_btn.clicked.connect(lambda checked, z=zone: self._on_delete_zone(z))
            rl2.addWidget(del_btn)
            zl.addWidget(row)
            self._zone_rows.append(row)
        rl.addWidget(zones_card)

        # Payment methods
        paym_card = Card()
        pml2 = QVBoxLayout(paym_card)
        pml2.setContentsMargins(24, 24, 24, 24)
        pml2.addWidget(make_manrope_label("Способы оплаты", 15, QFont.Weight.DemiBold))
        pml2.addSpacing(12)
        self._payment_toggles: dict[str, QFrame] = {}
        payment_methods = self._settings.get("payment_methods", {})
        for method, enabled in payment_methods.items():
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
            toggle.setCursor(Qt.CursorShape.PointingHandCursor)
            toggle.mousePressEvent = lambda ev, m=method: self._toggle_payment(m)
            toggle_dot = QFrame(toggle)
            toggle_dot.setFixedSize(16, 16)
            toggle_dot.move(22 if enabled else 4, 3)
            bg = SUCCESS if enabled else DISABLED
            border = SUCCESS if enabled else BORDER
            toggle.setStyleSheet(f"""
                background: rgba({','.join(map(str, hex_to_rgb(bg)))}, 0.2);
                border: 1px solid {border};
                border-radius: 12px;
            """)
            toggle_dot.setStyleSheet(f"""
                background: {bg};
                border-radius: 8px;
            """)
            rl3.addWidget(toggle)
            self._payment_toggles[method] = toggle
            pml2.addWidget(row)
        rl.addWidget(paym_card)

        main_layout.addWidget(right, 1)

    def _set_section(self, section_idx: int):
        """Switch settings section — update nav styles and scroll to content."""
        self._current_section = section_idx
        for i, btn in enumerate(self._nav_btns):
            active = i == section_idx
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left; padding: 10px 12px;
                    border-radius: 8px; border: none;
                    background: {'rgba(201,164,92,0.1)' if active else 'transparent'};
                    color: {GOLD if active else TEXT_SECONDARY};
                    font-size: 13px;
                    font-weight: {'600' if active else '400'};
                    border-left: 3px solid {GOLD if active else 'transparent'};
                }}
                QPushButton:hover {{
                    background: rgba(255,255,255,0.03);
                }}
            """)

    def _on_save_settings(self):
        """Save settings to JSON file."""
        self._settings["name"] = self._restaurant_name_edit.text()
        self._settings["phone"] = self._restaurant_phone_edit.text()
        self._settings["address"] = self._restaurant_address_edit.text()
        self._settings["email"] = self._restaurant_email_edit.text()
        self._save_settings_to_file()
        QMessageBox.information(self, "Настройки", "Изменения сохранены")

    def _on_add_zone(self):
        """Add a new zone via input dialog."""
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Добавить зону", "Название зоны:")
        if ok and name.strip():
            self._zones.append(name.strip())
            self._save_zones()
            QMessageBox.information(self, "Зоны", f"Зона «{name.strip()}» добавлена")

    def _on_edit_zone(self, zone: str):
        """Edit zone name."""
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Изменить зону", "Название зоны:", text=zone)
        if ok and name.strip():
            idx = self._zones.index(zone)
            self._zones[idx] = name.strip()
            self._save_zones()
            QMessageBox.information(self, "Зоны", f"Зона переименована в «{name.strip()}»")

    def _on_delete_zone(self, zone: str):
        """Delete a zone with confirmation."""
        reply = QMessageBox.question(
            self, "Удалить зону",
            f"Вы уверены, что хотите удалить зону «{zone}»?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._zones.remove(zone)
            self._save_zones()

    def _toggle_payment(self, method: str):
        """Toggle payment method enabled state."""
        methods = self._settings.get("payment_methods", {})
        if method in methods:
            methods[method] = not methods[method]
            self._save_settings_to_file()


# ─── Order Edit Dialog ──────────────────────────────────────────

class OrderEditDialog(QDialog):
    """Dialog for editing an existing order (table, customer, comment)."""
    def __init__(self, order: dict, parent=None):
        super().__init__(parent)
        self._order = order
        self.setWindowTitle(f"Редактирование заказа #{order['id']}")
        self.setModal(True)
        self.setMinimumSize(420, 300)
        self.setStyleSheet(f"background: {BG_PRIMARY}; color: {TEXT_PRIMARY};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(make_manrope_label(f"Заказ #{order['id']}", 18, QFont.Weight.ExtraBold))

        # Table
        from database.queries import get_all_tables
        tables = get_all_tables()
        self._table_combo = QComboBox()
        for t in tables:
            label = f"Столик №{t['table_number']} ({t.get('zone', '')})"
            self._table_combo.addItem(label, t["id"])
            if t["id"] == order.get("table_id"):
                self._table_combo.setCurrentIndex(self._table_combo.count() - 1)
        layout.addWidget(make_label("Столик:", 12, TEXT_MUTED))
        layout.addWidget(self._table_combo)

        # Customer
        from database.queries import get_all_customers
        customers = get_all_customers()
        self._customer_combo = QComboBox()
        self._customer_combo.addItem("Без клиента", None)
        for c in customers:
            self._customer_combo.addItem(c["full_name"], c["id"])
            if c["id"] == order.get("customer_id"):
                self._customer_combo.setCurrentIndex(self._customer_combo.count() - 1)
        layout.addWidget(make_label("Клиент:", 12, TEXT_MUTED))
        layout.addWidget(self._customer_combo)

        # Comment
        layout.addWidget(make_label("Комментарий:", 12, TEXT_MUTED))
        self._comment_edit = QTextEdit()
        self._comment_edit.setPlainText(order.get("comment", ""))
        self._comment_edit.setMaximumHeight(80)
        self._comment_edit.setStyleSheet(f"""
            background: {BG_SECONDARY}; color: {TEXT_PRIMARY};
            border: 1px solid {BORDER}; border-radius: 8px;
            padding: 8px; font-size: 13px;
        """)
        layout.addWidget(self._comment_edit)

        # Buttons
        btn_row = QHBoxLayout()
        cancel_btn = SecondaryButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        save_btn = PrimaryButton("Сохранить")
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _on_save(self):
        table_id = self._table_combo.currentData()
        customer_id = self._customer_combo.currentData()
        comment = self._comment_edit.toPlainText().strip()
        from database.queries import update_order
        update_order(
            self._order["id"],
            table_id=table_id,
            customer_id=customer_id,
            comment=comment,
        )
        QMessageBox.information(self, "Готово", "Заказ обновлен")
        self.accept()


# ─── PaymentView Dialog ─────────────────────────────────────────

class PaymentViewDialog(QDialog):
    """Dialog to view payment details for an order."""
    def __init__(self, order: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Оплата заказа #{order['id']}")
        self.setModal(True)
        self.setMinimumSize(480, 350)
        self.setStyleSheet(f"background: {BG_PRIMARY}; color: {TEXT_PRIMARY};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(make_manrope_label(f"Оплата заказа #{order['id']}", 18, QFont.Weight.ExtraBold))

        order_cfg = ORDER_STATUS_CONFIG.get(order["status"], {})
        layout.addWidget(StatusBadge(order_cfg))

        # Order info
        info_card = Card()
        il = QVBoxLayout(info_card)
        il.setSpacing(8)
        il.addWidget(make_label(f"Столик №{order.get('table_number', '?')}", 13, TEXT_SECONDARY))
        il.addWidget(make_label(f"Клиент: {order.get('customer_name', '—')}", 13, TEXT_SECONDARY))
        total = float(order.get("final_amount", order.get("total_amount", 0)))
        il.addWidget(make_manrope_label(f"Сумма: {total:,.0f} ₽".replace(",", " "), 20, QFont.Weight.ExtraBold, GOLD))
        layout.addWidget(info_card)

        from database.queries import get_payments_by_order
        payments = get_payments_by_order(order["id"])

        if payments:
            layout.addWidget(make_manrope_label("Проведенные платежи", 15, QFont.Weight.DemiBold))
            for p in payments:
                p_card = QFrame()
                p_card.setStyleSheet(f"""
                    background: {BG_CARD}; border: 1px solid {BORDER};
                    border-radius: 8px;
                """)
                pl = QHBoxLayout(p_card)
                pl.setContentsMargins(16, 12, 16, 12)
                pl.addWidget(make_label(p.get("payment_method", "—"), 13, TEXT_PRIMARY))
                pl.addWidget(make_label(
                    f"{float(p['amount']):,.0f} ₽".replace(",", " "), 13, GOLD, QFont.Weight.Bold
                ))
                pl.addStretch()
                pl.addWidget(make_label(str(p.get("paid_at", "")), 11, TEXT_MUTED))
                layout.addWidget(p_card)
        else:
            empty = QFrame()
            empty.setStyleSheet(f"background: {BG_CARD}; border: 1px dashed {BORDER}; border-radius: 8px;")
            el = QVBoxLayout(empty)
            el.setAlignment(Qt.AlignmentFlag.AlignCenter)
            el.addWidget(make_label("Платежей не найдено", 13, TEXT_MUTED))
            layout.addWidget(empty)

        layout.addStretch()
        close_btn = PrimaryButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


# ─── OrderHistory Dialog ────────────────────────────────────────

class OrderHistoryDialog(QDialog):
    """Dialog showing full order history."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("История заказов")
        self.setModal(True)
        self.setMinimumSize(700, 500)
        self.setStyleSheet(f"background: {BG_PRIMARY}; color: {TEXT_PRIMARY};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(make_manrope_label("История заказов", 20, QFont.Weight.ExtraBold))
        layout.addWidget(make_label("Все заказы за все время", 13, TEXT_MUTED))

        from database.queries import get_all_orders
        orders = get_all_orders()

        table = DataTable(["№", "Столик", "Клиент", "Статус", "Сумма", "Дата"])
        if orders:
            table.setRowCount(len(orders))
            for i, o in enumerate(orders):
                table.setItem(i, 0, QTableWidgetItem(f"#{o['id']}"))
                table.setItem(i, 1, QTableWidgetItem(f"Столик №{o.get('table_number', '?')}"))
                table.setItem(i, 2, QTableWidgetItem(o.get("customer_name", "—") or "—"))
                cfg = ORDER_STATUS_CONFIG.get(o["status"], {})
                table.setItem(i, 3, QTableWidgetItem(cfg.get("label", o["status"])))
                table.setItem(i, 4, QTableWidgetItem(
                    f"{float(o.get('final_amount', 0)):,.0f} ₽".replace(",", " ")
                ))
                table.setItem(i, 5, QTableWidgetItem(str(o.get("created_at", ""))))
        else:
            table.setRowCount(1)
            table.setItem(0, 0, QTableWidgetItem("Нет заказов"))
        layout.addWidget(table)

        close_btn = PrimaryButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


# ─── Notifications Dialog ───────────────────────────────────────

class NotificationsDialog(QDialog):
    """Dialog showing notifications and alerts."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Уведомления")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self.setStyleSheet(f"background: {BG_PRIMARY}; color: {TEXT_PRIMARY};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(make_manrope_label("Уведомления", 20, QFont.Weight.ExtraBold))
        layout.addWidget(make_label("Системные оповещения и события", 13, TEXT_MUTED))

        # Active orders notification
        try:
            active = get_active_orders()
            ready_count = sum(1 for o in active if o["status"] == "ready")
            new_count = sum(1 for o in active if o["status"] == "new")
        except:
            ready_count = 0
            new_count = 0

        notifications = []

        if ready_count > 0:
            notifications.append(("✅", "Готовые заказы", f"{ready_count} заказов готовы к подаче", SUCCESS))
        if new_count > 0:
            notifications.append(("🆕", "Новые заказы", f"{new_count} новых заказов ожидают", INFO))

        notifications.append(("ℹ️", "Система", "Все системы работают в штатном режиме", TEXT_SECONDARY))

        for icon, title, desc, color in notifications:
            card = QFrame()
            card.setStyleSheet(f"""
                background: rgba({','.join(map(str, hex_to_rgb(color)))}, 0.04);
                border: 1px solid rgba({','.join(map(str, hex_to_rgb(color)))}, 0.15);
                border-radius: 10px;
            """)
            cl = QHBoxLayout(card)
            cl.setContentsMargins(16, 14, 16, 14)
            cl.setSpacing(12)
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 20px; background: transparent;")
            cl.addWidget(icon_lbl)
            tl = QVBoxLayout()
            tl.addWidget(make_label(title, 14, TEXT_PRIMARY, QFont.Weight.Medium))
            tl.addWidget(make_label(desc, 12, TEXT_MUTED))
            cl.addLayout(tl)
            cl.addStretch()
            layout.addWidget(card)

        layout.addStretch()
        close_btn = PrimaryButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
