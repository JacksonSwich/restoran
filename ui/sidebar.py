"""Боковая панель навигации."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ui.styles import *
from ui.widgets import make_manrope_label, make_label

ADMIN_ITEMS = [
    ("dashboard", "Главная", "📊"),
    ("tables", "Столики", "🪑"),
    ("orders", "Заказы", "📋"),
    ("menu", "Меню", "📖"),
    ("customers", "Клиенты", "👥"),
    ("payments", "Оплаты", "💳"),
    ("reports", "Отчеты", "📈"),
    ("settings", "Настройки", "⚙️"),
]

WAITER_ITEMS = [
    ("waiter-workspace", "Рабочее место", "🏠"),
    ("tables", "Столики", "🪑"),
    ("new-order", "Новый заказ", "➕"),
    ("orders", "Заказы", "📋"),
    ("menu", "Меню", "📖"),
    ("payments", "Оплата", "💳"),
]


class Sidebar(QWidget):
    navigate_signal = pyqtSignal(str)

    def __init__(self, role: str = "admin", parent=None):
        super().__init__(parent)
        self._role = role
        self._current = "dashboard"
        self._buttons: dict[str, QPushButton] = {}
        self.setFixedWidth(220)
        self.setStyleSheet(f"""
            background: {BG_SECONDARY};
            border-right: 1px solid {BORDER};
        """)
        self._setup_ui()

    def set_role(self, role: str):
        self._role = role
        self._rebuild_nav()

    def set_current(self, screen: str):
        self._current = screen
        self._update_active()

    def _setup_ui(self):
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        # Лого
        logo = QWidget()
        logo.setFixedHeight(72)
        logo.setStyleSheet(f"border-bottom: 1px solid {BORDER};")
        ll = QHBoxLayout(logo)
        ll.setContentsMargins(20, 20, 20, 20)
        ll.setSpacing(10)

        icon = QLabel("🍽")
        icon.setStyleSheet(f"""
            font-size: 18px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {GOLD}, stop:1 {GOLD_DARK});
            border-radius: 8px;
            padding: 8px;
            min-width: 20px;
            min-height: 20px;
            max-width: 20px;
            max-height: 20px;
        """)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ll.addWidget(icon)

        brand = QVBoxLayout()
        brand.setSpacing(0)
        t = make_manrope_label("GastroHub", 16, QFont.Weight.ExtraBold)
        t.setStyleSheet(t.styleSheet() + "; letter-spacing: -0.02em;")
        brand.addWidget(t)
        st = make_label("POS система", 10, TEXT_MUTED)
        st.setStyleSheet(f"color: {TEXT_MUTED}; letter-spacing: 0.04em;")
        brand.addWidget(st)
        ll.addLayout(brand)
        ll.addStretch()
        self._layout.addWidget(logo)

        # Индикатор роли
        self._role_indicator = QWidget()
        self._role_indicator.setFixedHeight(48)
        self._layout.addWidget(self._role_indicator)
        self._update_role_indicator()

        # Навигация
        self._nav_container = QWidget()
        self._nav_layout = QVBoxLayout(self._nav_container)
        self._nav_layout.setContentsMargins(10, 8, 10, 8)
        self._nav_layout.setSpacing(2)
        self._build_nav()
        self._layout.addWidget(self._nav_container, 1)

        # Нижняя часть
        bottom = QWidget()
        bottom.setFixedHeight(64)
        bottom.setStyleSheet(f"border-top: 1px solid {BORDER};")
        bl = QHBoxLayout(bottom)
        bl.setContentsMargins(16, 12, 16, 12)
        bl.setSpacing(10)

        avatar = QLabel("АД" if self._role == "admin" else "ОФ")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFixedSize(32, 32)
        avatar.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {BG_ELEVATED}, stop:1 {BORDER});
            border: 2px solid {BORDER};
            border-radius: 16px;
            font-size: 12px;
            font-weight: 700;
            color: {GOLD};
        """)
        bl.addWidget(avatar)

        user_info = QVBoxLayout()
        user_info.setSpacing(0)
        uname = make_label("Алексей Д." if self._role == "admin" else "Максим В.",
                           13, TEXT_PRIMARY, QFont.Weight.DemiBold)
        user_info.addWidget(uname)
        urole = make_label("Администратор" if self._role == "admin" else "Официант",
                           11, TEXT_MUTED)
        user_info.addWidget(urole)
        bl.addLayout(user_info)
        bl.addStretch()

        self._layout.addWidget(bottom)

    def _update_role_indicator(self):
        role = self._role
        color = GOLD if role == "admin" else SUCCESS
        self._role_indicator.setStyleSheet(f"""
            background: rgba({','.join(str(int(color[i:i+2], 16)) for i in (1, 3, 5))}, 0.08);
            border: 1px solid rgba({','.join(str(int(color[i:i+2], 16)) for i in (1, 3, 5))}, 0.2);
            border-radius: 8px;
            margin: 12px 16px;
        """)
        rl = QVBoxLayout(self._role_indicator)
        rl.setContentsMargins(12, 8, 12, 8)
        rl.setSpacing(1)
        rl.addWidget(make_label("РОЛЬ", 10, TEXT_MUTED))
        role_lbl = make_label(
            "Администратор" if role == "admin" else "Официант",
            13, color, QFont.Weight.DemiBold
        )
        rl.addWidget(role_lbl)

    def _build_nav(self):
        items = ADMIN_ITEMS if self._role == "admin" else WAITER_ITEMS
        for screen_id, label, icon in items:
            btn = QPushButton(f"  {icon}  {label}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(38)
            btn.clicked.connect(lambda checked, s=screen_id: self.navigate_signal.emit(s))
            self._buttons[screen_id] = btn
            self._nav_layout.addWidget(btn)
        self._nav_layout.addStretch()
        self._update_active()

    def _rebuild_nav(self):
        for btn in self._buttons.values():
            btn.deleteLater()
        self._buttons.clear()
        # Remove existing items from nav_layout
        while self._nav_layout.count():
            item = self._nav_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._build_nav()

    def _update_active(self):
        for screen_id, btn in self._buttons.items():
            active = screen_id == self._current
            if active:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: rgba(201, 164, 92, 0.12);
                        color: {GOLD};
                        border: none;
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: 600;
                        text-align: left;
                        padding: 10px 12px;
                        border-left: 3px solid {GOLD};
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        color: {TEXT_SECONDARY};
                        border: none;
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: 400;
                        text-align: left;
                        padding: 10px 12px;
                    }}
                    QPushButton:hover {{
                        background: rgba(255, 255, 255, 0.04);
                        color: {TEXT_PRIMARY};
                    }}
                """)
