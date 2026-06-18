"""Переиспользуемые виджеты."""

from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from ui.styles import *

# ─── Label с поддержкой Manrope через QFont ────────────────────

def make_label(text: str, size: int = 13, color: str = TEXT_PRIMARY,
               weight: int = QFont.Weight.Normal, family: str = "Inter") -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(f"color: {color}; background: transparent; font-size: {size}px;")
    f = lbl.font()
    f.setPointSize(size)
    f.setWeight(weight)
    f.setFamily(family)
    lbl.setFont(f)
    return lbl


def make_manrope_label(text: str, size: int = 16, weight: int = QFont.Weight.Bold,
                       color: str = TEXT_PRIMARY) -> QLabel:
    return make_label(text, size, color, weight, "Manrope")


# ─── Кнопки ─────────────────────────────────────────────────────

class PrimaryButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(BTN_PRIMARY_QSS)
        self.setMinimumHeight(36)

    def set_enabled(self, enabled: bool):
        self.setEnabled(enabled)
        if enabled:
            self.setStyleSheet(BTN_PRIMARY_QSS)
        else:
            self.setStyleSheet(f"""
                background: {BG_ELEVATED};
                color: {DISABLED};
                border: none;
                border-radius: 8px;
                font-weight: 700;
                font-size: 13px;
                padding: 9px 16px;
            """)


class SecondaryButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(BTN_SECONDARY_QSS)
        self.setMinimumHeight(36)


class DangerButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(BTN_DANGER_QSS)
        self.setMinimumHeight(36)


class GoldButton(QPushButton):
    """Золотая кнопка с градиентом, как в дизайне."""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(BTN_PRIMARY_QSS)
        self.setMinimumHeight(36)


# ─── StatusBadge ────────────────────────────────────────────────

ORDER_STATUS_CONFIG = {
    "new":       {"label": "Новый",      "color": INFO,     "bg": "rgba(74,123,208,0.12)"},
    "cooking":   {"label": "Готовится",  "color": WARNING,  "bg": "rgba(217,138,53,0.12)"},
    "ready":     {"label": "Готов",      "color": SUCCESS,  "bg": "rgba(63,166,107,0.12)"},
    "served":    {"label": "Подан",      "color": "#9B6CDD","bg": "rgba(155,108,221,0.12)"},
    "paid":      {"label": "Оплачен",    "color": EMERALD,  "bg": "rgba(31,111,80,0.15)"},
    "cancelled": {"label": "Отменен",    "color": ERROR,    "bg": "rgba(201,76,76,0.12)"},
}

TABLE_STATUS_CONFIG = {
    "free":          {"label": "Свободен",     "color": SUCCESS, "bg": "rgba(63,166,107,0.12)"},
    "occupied":      {"label": "Занят",        "color": WARNING, "bg": "rgba(217,138,53,0.12)"},
    "reserved":      {"label": "Забронирован", "color": INFO,    "bg": "rgba(74,123,208,0.12)"},
    "out_of_service": {"label": "Недоступен",  "color": DISABLED,"bg": "rgba(92,96,104,0.15)"},
}

PAYMENT_STATUS_CONFIG = {
    "pending":  {"label": "Ожидает",  "color": WARNING, "bg": "rgba(217,138,53,0.12)"},
    "paid":     {"label": "Оплачено", "color": SUCCESS, "bg": "rgba(63,166,107,0.12)"},
    "refunded":  {"label": "Возврат",  "color": "#9B6CDD","bg": "rgba(155,108,221,0.12)"},
    "cancelled":{"label": "Отменено", "color": ERROR,   "bg": "rgba(201,76,76,0.12)"},
}


class StatusBadge(QFrame):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.setFixedHeight(24)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(6)

        dot = QLabel("●")
        dot.setStyleSheet(f"color: {config['color']}; font-size: 8px; background: transparent;")
        dot.setFixedWidth(8)
        layout.addWidget(dot)

        lbl = QLabel(config["label"])
        lbl.setStyleSheet(f"""
            color: {config['color']};
            font-size: 11px;
            font-weight: 600;
            background: transparent;
        """)
        layout.addWidget(lbl)

        self.setStyleSheet(f"""
            StatusBadge {{
                background: {config['bg']};
                border: 1px solid {config['color']}33;
                border-radius: 12px;
            }}
        """)


# ─── SearchInput ────────────────────────────────────────────────

class SearchInput(QLineEdit):
    def __init__(self, placeholder: str = "Поиск...", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet(f"""
            QLineEdit {{
                background: {BG_CARD};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 8px 12px 8px 36px;
                font-size: 13px;
            }}
        """)
        self.setMinimumHeight(36)
        self.setMaximumWidth(300)


# ─── FilterTabs ─────────────────────────────────────────────────

class FilterTab(QPushButton):
    def __init__(self, text: str, active: bool = False, color: str = GOLD, parent=None):
        super().__init__(text, parent)
        self._color = color
        self._active = active
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(32)
        self.update_style()

    def set_active(self, active: bool):
        self._active = active
        self.update_style()

    def update_style(self):
        if self._active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: rgba({','.join(map(str, hex_to_rgb(self._color)))}, 0.12);
                    border: 1px solid rgba({','.join(map(str, hex_to_rgb(self._color)))}, 0.35);
                    border-radius: 8px;
                    color: {self._color};
                    font-size: 13px;
                    font-weight: 600;
                    padding: 7px 14px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {BG_CARD};
                    border: 1px solid {BORDER};
                    border-radius: 8px;
                    color: {TEXT_SECONDARY};
                    font-size: 13px;
                    font-weight: 400;
                    padding: 7px 14px;
                }}
                QPushButton:hover {{
                    background: rgba(255,255,255,0.03);
                }}
            """)


def hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


# ─── Card (контейнер с тёмной карточкой) ───────────────────────

class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            Card {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)


# ─── SectionHeader ──────────────────────────────────────────────

class SectionHeader(QWidget):
    def __init__(self, title: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        title_lbl = make_manrope_label(title, 15, QFont.Weight.DemiBold)
        layout.addWidget(title_lbl)
        if subtitle:
            sub_lbl = make_label(subtitle, 12, TEXT_MUTED)
            layout.addWidget(sub_lbl)


# ─── StatCard (для дашборда) ────────────────────────────────────

class StatCard(QFrame):
    def __init__(self, label: str, value: str, sub: str = "",
                 color: str = GOLD, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            StatCard {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(4)

        val_lbl = make_manrope_label(value, 26, QFont.Weight.ExtraBold, TEXT_PRIMARY)
        layout.addWidget(val_lbl)

        lbl = make_label(label, 12, TEXT_SECONDARY)
        layout.addWidget(lbl)

        if sub:
            sub_lbl = make_label(sub, 11, SUCCESS if "+" in sub else TEXT_MUTED)
            layout.addWidget(sub_lbl)


# ─── DataTable ──────────────────────────────────────────────────

class DataTable(QTableWidget):
    """Стандартная тёмная таблица."""
    def __init__(self, columns: list[str], parent=None):
        super().__init__(parent)
        self._columns = columns
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setStyleSheet(f"""
            QTableWidget {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
                gridline-color: transparent;
                font-size: 13px;
                color: {TEXT_PRIMARY};
            }}
            QTableWidget::item {{
                padding: 10px 16px;
                border-bottom: 1px solid rgba(48, 52, 59, 0.13);
            }}
            QTableWidget::item:selected {{
                background: rgba(201, 164, 92, 0.06);
            }}
            QTableWidget::item:hover {{
                background: rgba(255, 255, 255, 0.02);
            }}
            QHeaderView::section {{
                background: #1A1D21;
                color: {TEXT_MUTED};
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.05em;
                border: none;
                padding: 10px 16px;
                border-bottom: 1px solid {BORDER};
            }}
            QHeaderView::section:first {{
                border-top-left-radius: 12px;
            }}
            QHeaderView::section:last {{
                border-top-right-radius: 12px;
            }}
            QTableWidget::item:alternate {{
                background: rgba(255, 255, 255, 0.01);
            }}
        """)
