"""Экран выбора роли (Login)."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ui.styles import *
from ui.widgets import make_manrope_label, make_label, hex_to_rgb


class LoginScreen(QWidget):
    """Экран выбора роли: Администратор / Официант."""
    login_signal = pyqtSignal(str)  # 'admin' or 'waiter'

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(0)

        # Контейнер
        container = QWidget()
        container.setFixedWidth(880)
        cl = QVBoxLayout(container)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.setSpacing(0)

        # Лого
        logo_row = QHBoxLayout()
        logo_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_row.setSpacing(14)

        logo_icon = QLabel("🍽")
        logo_icon.setStyleSheet(f"""
            font-size: 36px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {GOLD}, stop:1 {GOLD_DARK});
            border-radius: 14px;
            padding: 8px;
            min-width: 48px;
            min-height: 48px;
            max-width: 48px;
            max-height: 48px;
        """)
        logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_row.addWidget(logo_icon)

        brand = QVBoxLayout()
        brand.setSpacing(2)
        title = make_manrope_label("GastroHub", 32, QFont.Weight.ExtraBold)
        title.setStyleSheet(title.styleSheet() + "; letter-spacing: -0.04em;")
        brand.addWidget(title)
        subtitle = make_label("Restaurant Management System", 12, TEXT_MUTED,
                              QFont.Weight.Normal)
        subtitle.setStyleSheet(f"color: {TEXT_MUTED}; letter-spacing: 0.1em;")
        brand.addWidget(subtitle)
        logo_row.addLayout(brand)
        cl.addLayout(logo_row)
        cl.addSpacing(40)

        # Заголовок
        h1 = make_manrope_label("Система управления рестораном", 28,
                                QFont.Weight.Bold)
        cl.addWidget(h1)
        cl.addSpacing(8)

        p = make_label("Выберите роль для входа в систему", 15, TEXT_SECONDARY)
        cl.addWidget(p)
        cl.addSpacing(48)

        # Карточки ролей
        cards_row = QHBoxLayout()
        cards_row.setSpacing(20)
        cards_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        admin_card = self._make_role_card(
            "🛡", "Администратор", "Полный доступ к системе",
            [
                "Управление меню", "Отчеты и аналитика",
                "Управление клиентами", "Просмотр оплат",
                "Редактирование заказов", "Управление столиками",
            ],
            GOLD, "admin"
        )
        cards_row.addWidget(admin_card)

        waiter_card = self._make_role_card(
            "👤", "Официант", "Рабочее место сотрудника",
            [
                "Работа со столиками", "Создание заказов",
                "Добавление блюд", "Изменение статусов",
                "Оплата заказов", "Просмотр меню",
            ],
            SUCCESS, "waiter"
        )
        cards_row.addWidget(waiter_card)

        cl.addLayout(cards_row)
        cl.addSpacing(40)

        footer = make_label("GastroHub POS · Версия 2.4.1 · 2026", 12, TEXT_MUTED)
        cl.addWidget(footer)

        layout.addWidget(container)

    def _make_role_card(self, icon: str, title: str, subtitle: str,
                        features: list[str], accent: str, role: str) -> QFrame:
        card = QFrame()
        card.setFixedSize(370, 420)
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        base_style = f"""
            background: {BG_CARD};
            border: 1px solid {BORDER};
            border-radius: 16px;
        """
        hover_style = f"""
            background: {BG_ELEVATED};
            border: 1px solid {accent}66;
            border-radius: 16px;
        """
        card.setStyleSheet(f"QFrame {{ {base_style} }}")

        # Click + hover via event override
        def mouse_press(self_, event):
            if event.button() == Qt.MouseButton.LeftButton:
                self.login_signal.emit(role)
        card.mousePressEvent = lambda ev: mouse_press(card, ev)

        def enter_ev(self_, event):
            self_.setStyleSheet(f"QFrame {{ {hover_style} }}")
        card.enterEvent = lambda ev: enter_ev(card, ev)

        def leave_ev(self_, event):
            self_.setStyleSheet(f"QFrame {{ {base_style} }}")
        card.leaveEvent = lambda ev: leave_ev(card, ev)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 28, 24, 28)
        layout.setSpacing(0)

        # Иконка
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"""
            font-size: 28px;
            background: rgba({','.join(map(str, hex_to_rgb(accent)))}, 0.07);
            border: 1px solid rgba({','.join(map(str, hex_to_rgb(accent)))}, 0.13);
            border-radius: 14px;
            padding: 12px;
            min-width: 28px;
            min-height: 28px;
            max-width: 52px;
            max-height: 52px;
        """)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_lbl)
        layout.addSpacing(20)

        # Title
        t = make_manrope_label(title, 20, QFont.Weight.Bold)
        layout.addWidget(t)
        layout.addSpacing(4)

        s = make_label(subtitle, 13, TEXT_SECONDARY)
        layout.addWidget(s)
        layout.addSpacing(24)

        # Features
        for f in features:
            row = QHBoxLayout()
            row.setSpacing(8)
            dot = QLabel("✓")
            dot.setStyleSheet(f"""
                color: {accent};
                font-size: 10px;
                font-weight: bold;
                background: rgba({','.join(map(str, hex_to_rgb(accent)))}, 0.08);
                border: 1px solid rgba({','.join(map(str, hex_to_rgb(accent)))}, 0.2);
                border-radius: 9px;
                padding: 3px;
                min-width: 12px;
                min-height: 12px;
                max-width: 12px;
                max-height: 12px;
            """)
            dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row.addWidget(dot)
            row.addWidget(make_label(f, 13, TEXT_SECONDARY))
            row.addStretch()
            layout.addLayout(row)
            layout.addSpacing(6)

        layout.addStretch()

        # Кнопка входа
        btn = QLabel(f"Войти как {title.lower()}")
        btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn.setFixedHeight(40)
        btn.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {accent}, stop:1 {accent}CC);
            color: {BG_PRIMARY};
            border-radius: 10px;
            font-size: 14px;
            font-weight: 700;
            padding: 10px;
        """)
        layout.addWidget(btn)

        return card
