"""Верхняя панель с поиском, датой, ролью и действиями."""

from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFrame,
    QMenu,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QAction

from ui.styles import *
from ui.widgets import make_label, hex_to_rgb


class TopBar(QWidget):
    """Верхняя панель приложения."""
    action_signal = pyqtSignal(str)
    logout_signal = pyqtSignal()
    search_signal = pyqtSignal(str)
    notifications_signal = pyqtSignal()

    def __init__(self, role: str = "admin", parent=None):
        super().__init__(parent)
        self._role = role
        self.setObjectName("topbar")
        self.setFixedHeight(64)
        self.setStyleSheet(f"""
            #topbar {{
                background: {BG_SECONDARY};
                border-bottom: 1px solid {BORDER};
            }}
        """)
        self._setup_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_time)
        self._timer.start(60000)
        self._update_time()

    def set_role(self, role: str):
        self._role = role
        self._update_role_badge()
        self._update_action_btn()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # ─── Поиск с иконкой лупы ──────────────────────────────
        search_container = QFrame()
        search_container.setFixedHeight(36)
        search_container.setMaximumWidth(420)
        search_container.setMinimumWidth(260)
        search_container.setStyleSheet(f"""
            QFrame {{
                background: {BG_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
        """)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(10, 0, 10, 0)
        search_layout.setSpacing(8)

        search_icon = QLabel("⌕")
        search_icon.setStyleSheet(f"""
            color: {TEXT_MUTED}; font-size: 16px; font-weight: 300;
            background: transparent; border: none; padding: 0;
        """)
        search_layout.addWidget(search_icon)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Поиск заказа, столика, клиента или блюда")
        self._search.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                color: {TEXT_PRIMARY};
                border: none;
                font-size: 13px;
                padding: 0;
            }}
            QLineEdit:focus {{
                border: none;
            }}
            QLineEdit::placeholder {{
                color: {TEXT_MUTED};
            }}
        """)
        self._search.returnPressed.connect(lambda: self.search_signal.emit(self._search.text()))
        search_layout.addWidget(self._search, 1)
        layout.addWidget(search_container)

        layout.addStretch(1)

        # ─── Дата/время pill ──────────────────────────────────
        time_frame = QFrame()
        time_frame.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border: 1px solid rgba(48, 52, 59, 0.5);
                border-radius: 20px;
                padding: 4px 12px;
            }}
        """)
        time_layout = QHBoxLayout(time_frame)
        time_layout.setContentsMargins(10, 4, 10, 4)
        time_layout.setSpacing(6)

        clock_icon = QLabel("🕐")
        clock_icon.setStyleSheet("font-size: 12px; background: transparent; border: none; padding: 0;")
        time_layout.addWidget(clock_icon)

        self._time_lbl = make_label("", 12, TEXT_SECONDARY)
        time_layout.addWidget(self._time_lbl)
        layout.addWidget(time_frame)

        layout.addSpacing(4)

        # ─── Бейдж роли ───────────────────────────────────────
        self._role_badge = QFrame()
        self._role_badge.setStyleSheet("background: transparent;")
        role_layout = QHBoxLayout(self._role_badge)
        role_layout.setContentsMargins(12, 4, 12, 4)
        role_layout.setSpacing(6)

        role_dot = QLabel("●")
        role_dot.setStyleSheet("font-size: 8px; background: transparent; border: none; padding: 0;")
        role_layout.addWidget(role_dot)
        self._role_label = make_label("", 12, GOLD, QFont.Weight.Medium)
        role_layout.addWidget(self._role_label)
        self._update_role_badge()
        layout.addWidget(self._role_badge)

        layout.addSpacing(4)

        # ─── Уведомления ──────────────────────────────────────
        notif_container = QFrame()
        notif_container.setFixedSize(36, 36)
        notif_container.setCursor(Qt.CursorShape.PointingHandCursor)
        notif_container.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
            QFrame:hover {{
                background: rgba(255,255,255,0.03);
            }}
        """)
        notif_layout = QVBoxLayout(notif_container)
        notif_layout.setContentsMargins(0, 0, 0, 0)
        notif_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        notif_icon = QLabel("🔔")
        notif_icon.setStyleSheet("font-size: 14px; background: transparent; border: none; padding: 0;")
        notif_layout.addWidget(notif_icon)

        # Red dot (will be positioned absolutely via negative margin)
        notif_dot = QLabel()
        notif_dot.setFixedSize(7, 7)
        notif_dot.setStyleSheet(f"""
            background: {GOLD};
            border: 1.5px solid {BG_SECONDARY};
            border-radius: 4px;
        """)
        notif_dot.setParent(notif_container)
        notif_dot.move(24, 5)

        notif_container.mousePressEvent = lambda ev: self.notifications_signal.emit() if ev.button() == Qt.MouseButton.LeftButton else None
        layout.addWidget(notif_container)

        layout.addSpacing(4)

        # ─── CTA кнопка ───────────────────────────────────────
        self._action_btn = QPushButton()
        self._action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._action_btn.setMinimumHeight(36)
        self._action_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {GOLD}, stop:1 {GOLD_DARK});
                color: {BG_PRIMARY};
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 700;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {GOLD}, stop:1 #B89045);
            }}
        """)
        self._update_action_btn()
        self._action_btn.clicked.connect(self._on_action)
        layout.addWidget(self._action_btn)

        layout.addSpacing(4)

        # ─── Профиль: аватар + имя в блоке с hover+menu ───────
        profile_container = QFrame()
        profile_container.setCursor(Qt.CursorShape.PointingHandCursor)
        profile_container.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border: 1px solid transparent;
                border-radius: 10px;
            }}
            QFrame:hover {{
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(48, 52, 59, 0.5);
            }}
        """)
        profile_layout = QHBoxLayout(profile_container)
        profile_layout.setContentsMargins(6, 4, 10, 4)
        profile_layout.setSpacing(8)

        initials = "АД" if self._role == "admin" else "ОФ"
        profile_avatar = QLabel(initials)
        profile_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        profile_avatar.setFixedSize(28, 28)
        profile_avatar.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {BG_ELEVATED}, stop:1 {BORDER});
            border: 1.5px solid rgba(201, 164, 92, 0.27);
            border-radius: 14px;
            font-size: 10px;
            font-weight: 700;
            color: {GOLD};
        """)
        profile_layout.addWidget(profile_avatar)

        profile_name = make_label(
            "Алексей Д." if self._role == "admin" else "Максим В.",
            13, TEXT_PRIMARY, QFont.Weight.DemiBold
        )
        profile_layout.addWidget(profile_name)

        profile_arrow = QLabel("▼")
        profile_arrow.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 7px; background: transparent; border: none;")
        profile_layout.addWidget(profile_arrow)

        # Profile dropdown menu
        self._profile_menu = QMenu(profile_container)
        self._profile_menu.setStyleSheet(f"""
            QMenu {{
                background: {BG_CARD};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 6px;
            }}
            QMenu::item {{
                padding: 8px 20px 8px 12px;
                border-radius: 6px;
                font-size: 13px;
            }}
            QMenu::item:selected {{
                background: rgba(201,164,92,0.12);
                color: {GOLD};
            }}
            QMenu::separator {{
                height: 1px;
                background: {BORDER};
                margin: 4px 8px;
            }}
        """)

        profile_action = QAction("👤 Профиль", profile_container)
        self._profile_menu.addAction(profile_action)

        settings_action = QAction("⚙ Настройки", profile_container)
        settings_action.triggered.connect(lambda: None)  # placeholder
        self._profile_menu.addAction(settings_action)

        self._profile_menu.addSeparator()

        logout_action = QAction("🚪 Выйти", profile_container)
        logout_action.triggered.connect(self.logout_signal.emit)
        self._profile_menu.addAction(logout_action)

        profile_container.mousePressEvent = lambda ev: self._show_profile_menu(ev, profile_container)
        layout.addWidget(profile_container)

        # ─── Выход (иконка с tooltip) ─────────────────────────
        logout_btn = QPushButton("")
        logout_btn.setFixedSize(36, 36)
        logout_btn.setToolTip("Выйти из системы")
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {BORDER};
                border-radius: 10px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background: rgba(201, 76, 76, 0.08);
                border: 1px solid rgba(201, 76, 76, 0.3);
            }}
        """)
        # Unicode power-off icon as text
        logout_icon = QLabel("⏻")
        logout_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logout_icon.setStyleSheet("font-size: 16px; background: transparent; border: none; color: #A9A39A;")
        # Use a layout to position the icon inside the button
        logout_btn_layout = QHBoxLayout(logout_btn)
        logout_btn_layout.setContentsMargins(0, 0, 0, 0)
        logout_btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logout_btn_layout.addWidget(logout_icon)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self.logout_signal.emit)
        layout.addWidget(logout_btn)

    def _show_profile_menu(self, event, container):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = container.mapToGlobal(event.pos())
            self._profile_menu.exec(pos)

    def _update_time(self):
        now = datetime.now()
        months = ["янв", "фев", "мар", "апр", "мая", "июн",
                   "июл", "авг", "сен", "окт", "ноя", "дек"]
        days = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
        fmt = f"{days[now.weekday()]}, {now.day} {months[now.month-1]} · {now.hour:02d}:{now.minute:02d}"
        self._time_lbl.setText(fmt)

    def _update_role_badge(self):
        color = GOLD if self._role == "admin" else SUCCESS
        role_text = "Администратор" if self._role == "admin" else "Официант"
        self._role_label.setText(role_text)
        self._role_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 500; background: transparent; border: none; padding: 0; margin: 0;")
        self._role_badge.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border: 1px solid rgba({','.join(map(str, hex_to_rgb(color)))}, 0.25);
                border-radius: 20px;
            }}
        """)
        # Update the dot color
        items = self._role_badge.layout()
        if items and items.count() > 0:
            dot = items.itemAt(0)
            if dot and dot.widget():
                dot.widget().setStyleSheet(f"font-size: 8px; color: {color}; background: transparent; border: none; padding: 0;")

    def _on_action(self):
        if self._role == "admin":
            self.action_signal.emit("create-report")
        else:
            self.action_signal.emit("create-order")

    def _update_action_btn(self):
        if self._role == "admin":
            self._action_btn.setText("📄 Создать отчёт")
        else:
            self._action_btn.setText("➕ Создать заказ")
