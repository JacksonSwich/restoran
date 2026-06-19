"""Боковая панель навигации."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ui.styles import *
from ui.widgets import make_manrope_label, make_label, hex_to_rgb

ADMIN_ITEMS = [
    ("dashboard", "Главная", "◈"),
    ("tables", "Столики", "⊞"),
    ("orders", "Заказы", "☰"),
    ("menu", "Меню", "⊡"),
    ("customers", "Клиенты", "◎"),
    ("payments", "Оплаты", "◇"),
    ("reports", "Отчеты", "⊟"),
    ("settings", "Настройки", "⚙"),
]

WAITER_ITEMS = [
    ("waiter-workspace", "Рабочее место", "◈"),
    ("tables", "Столики", "⊞"),
    ("new-order", "Новый заказ", "⊕"),
    ("orders", "Заказы", "☰"),
    ("menu", "Меню", "⊡"),
    ("payments", "Оплата", "◇"),
]


class Sidebar(QWidget):
    navigate_signal = pyqtSignal(str)

    def __init__(self, role: str = "admin", parent=None):
        super().__init__(parent)
        self._role = role
        self._current = "dashboard"
        self._buttons: dict[str, QPushButton] = {}
        self.setFixedWidth(220)
        self.setObjectName("sidebar")
        self.setStyleSheet(f"""
            #sidebar {{
                background: {BG_SECONDARY};
                border-right: 1px solid {BORDER};
            }}
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

        # ─── Логотип GastroHub ────────────────────────────────
        logo = QWidget()
        logo.setFixedHeight(64)
        logo.setObjectName("logo")
        logo.setStyleSheet(f"""
            #logo {{
                border-bottom: 1px solid {BORDER};
            }}
        """)
        ll = QHBoxLayout(logo)
        ll.setContentsMargins(18, 16, 18, 16)
        ll.setSpacing(10)

        icon = QLabel("◈")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setFixedSize(32, 32)
        icon.setStyleSheet(f"""
            font-size: 16px;
            color: {BG_PRIMARY};
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {GOLD}, stop:1 {GOLD_DARK});
            border-radius: 8px;
            border: none;
        """)
        ll.addWidget(icon)

        brand = QVBoxLayout()
        brand.setSpacing(0)
        t = make_manrope_label("GastroHub", 15, QFont.Weight.ExtraBold)
        t.setStyleSheet(t.styleSheet() + "; letter-spacing: -0.02em;")
        brand.addWidget(t)
        st = make_label("POS система", 9, TEXT_MUTED)
        st.setStyleSheet(f"color: {TEXT_MUTED}; letter-spacing: 0.06em; background: transparent; border: none; padding: 0; margin: 0;")
        brand.addWidget(st)
        ll.addLayout(brand)
        ll.addStretch()
        self._layout.addWidget(logo)

        # ─── Навигация ────────────────────────────────────────
        self._nav_container = QWidget()
        self._nav_layout = QVBoxLayout(self._nav_container)
        self._nav_layout.setContentsMargins(8, 12, 8, 12)
        self._nav_layout.setSpacing(2)
        self._build_nav()
        self._layout.addWidget(self._nav_container, 1)

        # ─── Профиль (нижняя часть) ───────────────────────────
        bottom = QFrame()
        bottom.setFixedHeight(72)
        bottom.setStyleSheet(f"""
            QFrame {{
                border-top: 1px solid {BORDER};
                background: transparent;
            }}
            QFrame:hover {{
                background: rgba(255, 255, 255, 0.02);
            }}
        """)
        bottom.setCursor(Qt.CursorShape.PointingHandCursor)
        bl = QHBoxLayout(bottom)
        bl.setContentsMargins(16, 14, 16, 14)
        bl.setSpacing(10)

        avatar = QLabel("АД" if self._role == "admin" else "ОФ")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFixedSize(34, 34)
        avatar.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {BG_ELEVATED}, stop:1 {BORDER});
            border: 1.5px solid rgba(201, 164, 92, 0.2);
            border-radius: 17px;
            font-size: 12px;
            font-weight: 700;
            color: {GOLD};
        """)
        bl.addWidget(avatar)

        user_info = QVBoxLayout()
        user_info.setSpacing(1)
        uname = make_label("Алексей Д." if self._role == "admin" else "Максим В.",
                           13, TEXT_PRIMARY, QFont.Weight.DemiBold)
        user_info.addWidget(uname)
        urole = make_label("Администратор" if self._role == "admin" else "Официант",
                           10, TEXT_MUTED)
        urole.setStyleSheet(f"color: {TEXT_MUTED}; letter-spacing: 0.02em; background: transparent; border: none; padding: 0; margin: 0;")
        user_info.addWidget(urole)
        bl.addLayout(user_info)
        bl.addStretch()

        self._layout.addWidget(bottom)

    def _build_nav(self):
        items = ADMIN_ITEMS if self._role == "admin" else WAITER_ITEMS
        for screen_id, label, icon_char in items:
            btn = self._make_nav_btn(screen_id, label, icon_char)
            self._buttons[screen_id] = btn
            self._nav_layout.addWidget(btn)
        self._nav_layout.addStretch()
        self._update_active()

    def _make_nav_btn(self, screen_id: str, label: str, icon_char: str) -> QPushButton:
        btn = QPushButton()
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setMinimumHeight(40)

        # Container with icon + text
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(10)

        icon_lbl = QLabel(icon_char)
        icon_lbl.setFixedWidth(18)
        icon_lbl.setStyleSheet("font-size: 14px; background: transparent; border: none; padding: 0;")
        container_layout.addWidget(icon_lbl)

        text_lbl = QLabel(label)
        text_lbl.setStyleSheet("font-size: 14px; background: transparent; border: none; padding: 0;")
        container_layout.addWidget(text_lbl)
        container_layout.addStretch()

        # QPushButton with styling, using layout to position content
        btn_layout = QHBoxLayout(btn)
        btn_layout.setContentsMargins(14, 0, 12, 0)
        btn_layout.addWidget(container)

        btn.clicked.connect(lambda checked, s=screen_id: self.navigate_signal.emit(s))

        return btn

    def _rebuild_nav(self):
        for btn in self._buttons.values():
            btn.deleteLater()
        self._buttons.clear()
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
                        border-top-right-radius: 8px;
                        border-bottom-right-radius: 8px;
                        border-left: 3px solid {GOLD};
                    }}
                    QPushButton:hover {{
                        background: rgba(201, 164, 92, 0.18);
                    }}
                """)
                self._update_child_labels(btn, True)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        color: {TEXT_SECONDARY};
                        border: none;
                        border-top-right-radius: 8px;
                        border-bottom-right-radius: 8px;
                        border-left: 3px solid transparent;
                    }}
                    QPushButton:hover {{
                        background: rgba(255, 255, 255, 0.04);
                        color: {TEXT_PRIMARY};
                    }}
                """)
                self._update_child_labels(btn, False)

    def _update_child_labels(self, btn: QPushButton, active: bool):
        for child in btn.findChildren(QLabel):
            text = child.text()
            if len(text) <= 2 and text in [it[2] for it in ADMIN_ITEMS + WAITER_ITEMS]:
                # Icon label
                child.setStyleSheet(f"""
                    font-size: 14px; background: transparent; border: none; padding: 0; margin: 0;
                    color: {GOLD if active else TEXT_SECONDARY};
                """)
            elif text in [it[1] for it in ADMIN_ITEMS + WAITER_ITEMS]:
                # Text label
                child.setStyleSheet(f"""
                    font-size: 14px; background: transparent; border: none; padding: 0; margin: 0;
                    font-weight: {600 if active else 400};
                    color: {GOLD if active else TEXT_SECONDARY};
                """)
