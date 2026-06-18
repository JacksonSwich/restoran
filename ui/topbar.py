"""Верхняя панель с поиском, датой, ролью и действиями."""

from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFrame,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from ui.styles import *
from ui.widgets import make_label, hex_to_rgb


class TopBar(QWidget):
    """Верхняя панель приложения."""

    def __init__(self, role: str = "admin", parent=None):
        super().__init__(parent)
        self._role = role
        self.setFixedHeight(64)
        self.setStyleSheet(f"""
            background: {BG_SECONDARY};
            border-bottom: 1px solid {BORDER};
        """)
        self._setup_ui()

        # Обновление времени
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
        layout.setSpacing(16)

        # Поиск
        self._search = QLineEdit()
        self._search.setPlaceholderText("Поиск заказа, столика, клиента или блюда")
        self._search.setStyleSheet(f"""
            QLineEdit {{
                background: {BG_PRIMARY};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 8px 12px 8px 36px;
                font-size: 13px;
                max-width: 420px;
                min-width: 280px;
            }}
        """)
        self._search.setMaximumWidth(420)
        self._search.setMinimumHeight(34)
        layout.addWidget(self._search)

        layout.addStretch(1)

        # Дата/время
        self._time_lbl = make_label("", 13, TEXT_SECONDARY)
        layout.addWidget(self._time_lbl)

        # Бейдж роли
        self._role_badge = QLabel()
        layout.addWidget(self._role_badge)
        self._update_role_badge()

        # Уведомления
        notif_btn = QPushButton("🔔")
        notif_btn.setFixedSize(36, 36)
        notif_btn.setStyleSheet(f"""
            QPushButton {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {BG_ELEVATED};
            }}
        """)
        notif_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # Red notification dot (overlay)
        notif_wrapper = QWidget()
        notif_wrapper.setFixedSize(36, 36)
        notif_layout = QVBoxLayout(notif_wrapper)
        notif_layout.setContentsMargins(0, 0, 0, 0)
        notif_dot = QLabel()
        notif_dot.setFixedSize(8, 8)
        notif_dot.setStyleSheet(f"""
            background: {GOLD};
            border: 2px solid {BG_SECONDARY};
            border-radius: 4px;
        """)
        notif_layout.addWidget(notif_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        notif_dot.move(22, 6)
        notif_dot.setParent(notif_wrapper)
        layout.addWidget(notif_wrapper)

        # Кнопка действия
        self._action_btn = QPushButton()
        self._action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
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
                opacity: 0.85;
            }}
        """)
        self._action_btn.setMinimumHeight(34)
        self._update_action_btn()
        layout.addWidget(self._action_btn)

        # Аватар
        avatar = QLabel("АД" if self._role == "admin" else "ОФ")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFixedSize(34, 34)
        avatar.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {BG_ELEVATED}, stop:1 {BORDER});
            border: 2px solid rgba(201, 164, 92, 0.27);
            border-radius: 17px;
            font-size: 12px;
            font-weight: 700;
            color: {GOLD};
        """)
        layout.addWidget(avatar)

        # Выход
        logout_btn = QPushButton("🚪")
        logout_btn.setFixedSize(34, 34)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {BORDER};
                border-radius: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                border-color: rgba(201, 76, 76, 0.27);
            }}
        """)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(logout_btn)

    def _update_time(self):
        now = datetime.now()
        months = ["января", "февраля", "марта", "апреля", "мая", "июня",
                   "июля", "августа", "сентября", "октября", "ноября", "декабря"]
        days = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
        fmt = f"{days[now.weekday()]}, {now.day} {months[now.month-1]} · {now.hour:02d}:{now.minute:02d}"
        self._time_lbl.setText(fmt)

    def _update_role_badge(self):
        color = GOLD if self._role == "admin" else SUCCESS
        self._role_badge.setText(f"Роль: {'Администратор' if self._role == 'admin' else 'Официант'}")
        self._role_badge.setStyleSheet(f"""
            padding: 5px 12px;
            background: rgba({','.join(map(str, hex_to_rgb(color)))}, 0.1);
            border: 1px solid rgba({','.join(map(str, hex_to_rgb(color)))}, 0.25);
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            color: {color};
        """)

    def _update_action_btn(self):
        if self._role == "admin":
            self._action_btn.setText("📄 Создать отчет")
        else:
            self._action_btn.setText("➕ Создать заказ")
