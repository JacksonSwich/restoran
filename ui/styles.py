"""Цветовая схема и QSS-стили проекта."""

# ─── Цветовая палитра ──────────────────────────────────────────
BG_PRIMARY = "#0E0F11"
BG_SECONDARY = "#15171A"
BG_CARD = "#202328"
BG_ELEVATED = "#252932"
BORDER = "#30343B"

TEXT_PRIMARY = "#F5F2EA"
TEXT_SECONDARY = "#A9A39A"
TEXT_MUTED = "#6F756F"

GOLD = "#C9A45C"
GOLD_DARK = "#A07B3A"
EMERALD = "#1F6F50"
SUCCESS = "#3FA66B"
WARNING = "#D98A35"
INFO = "#4A7BD0"
ERROR = "#C94C4C"
DISABLED = "#5C6068"

# ─── Внутренние константы QSS (сокращают дублирование) ─────────
_GOLD_HOVER = "rgba(201, 164, 92, 0.25)"
_GOLD_FOCUS = "rgba(201, 164, 92, 0.5)"


# ─── Кнопки ─────────────────────────────────────────────────────

BTN_PRIMARY_QSS = f"""
    QPushButton {{
        font-family: 'Inter', 'Manrope', sans-serif;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {GOLD}, stop:1 {GOLD_DARK});
        color: {BG_PRIMARY};
        border: none;
        border-radius: 8px;
        font-weight: 700;
        font-size: 13px;
        padding: 9px 16px;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #D6B46A, stop:1 {GOLD});
    }}
    QPushButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {GOLD_DARK}, stop:1 #8A6630);
        padding-top: 10px;
        padding-bottom: 8px;
    }}
    QPushButton:disabled {{
        background: {DISABLED};
        color: {TEXT_MUTED};
    }}
"""

BTN_PRIMARY_QSS_HOVER = f"""
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #D6B46A, stop:1 {GOLD});
    }}
"""

BTN_PRIMARY_QSS_PRESSED = f"""
    QPushButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {GOLD_DARK}, stop:1 #8A6630);
        padding-top: 10px;
        padding-bottom: 8px;
    }}
"""

BTN_PRIMARY_QSS_DISABLED = f"""
    QPushButton:disabled {{
        background: {DISABLED};
        color: {TEXT_MUTED};
    }}
"""

BTN_SECONDARY_QSS = f"""
    QPushButton {{
        font-family: 'Inter', 'Manrope', sans-serif;
        background: {BG_ELEVATED};
        color: {TEXT_SECONDARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        font-weight: 500;
        font-size: 13px;
        padding: 9px 16px;
    }}
    QPushButton:hover {{
        background: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {_GOLD_HOVER};
    }}
    QPushButton:pressed {{
        background: {BG_SECONDARY};
        color: {TEXT_PRIMARY};
        border: 1px solid {_GOLD_FOCUS};
        padding-top: 10px;
        padding-bottom: 8px;
    }}
    QPushButton:disabled {{
        background: {BG_SECONDARY};
        color: {DISABLED};
        border: 1px solid transparent;
    }}
"""

BTN_SECONDARY_QSS_HOVER = f"""
    QPushButton:hover {{
        background: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {_GOLD_HOVER};
    }}
"""

BTN_SECONDARY_QSS_PRESSED = f"""
    QPushButton:pressed {{
        background: {BG_SECONDARY};
        color: {TEXT_PRIMARY};
        border: 1px solid {_GOLD_FOCUS};
        padding-top: 10px;
        padding-bottom: 8px;
    }}
"""

BTN_SECONDARY_QSS_DISABLED = f"""
    QPushButton:disabled {{
        background: {BG_SECONDARY};
        color: {DISABLED};
        border: 1px solid transparent;
    }}
"""

BTN_DANGER_QSS = f"""
    QPushButton {{
        font-family: 'Inter', 'Manrope', sans-serif;
        background: rgba(201, 76, 76, 0.08);
        color: {ERROR};
        border: 1px solid rgba(201, 76, 76, 0.25);
        border-radius: 8px;
        font-weight: 600;
        font-size: 13px;
        padding: 9px 16px;
    }}
    QPushButton:hover {{
        background: rgba(201, 76, 76, 0.15);
        border: 1px solid rgba(201, 76, 76, 0.40);
    }}
    QPushButton:pressed {{
        background: rgba(201, 76, 76, 0.25);
        border: 1px solid {ERROR};
        padding-top: 10px;
        padding-bottom: 8px;
    }}
    QPushButton:disabled {{
        background: transparent;
        color: {DISABLED};
        border: 1px solid {DISABLED};
    }}
"""

BTN_DANGER_QSS_HOVER = f"""
    QPushButton:hover {{
        background: rgba(201, 76, 76, 0.15);
        border: 1px solid rgba(201, 76, 76, 0.40);
    }}
"""

BTN_DANGER_QSS_PRESSED = f"""
    QPushButton:pressed {{
        background: rgba(201, 76, 76, 0.25);
        border: 1px solid {ERROR};
        padding-top: 10px;
        padding-bottom: 8px;
    }}
"""

BTN_DANGER_QSS_DISABLED = f"""
    QPushButton:disabled {{
        background: transparent;
        color: {DISABLED};
        border: 1px solid {DISABLED};
    }}
"""

DISABLED_BTN = f"""
    QPushButton:disabled {{
        background: {DISABLED};
        color: {TEXT_MUTED};
        border: 1px solid transparent;
        border-radius: 8px;
    }}
"""


# ─── Поля ввода ─────────────────────────────────────────────────
INPUT_QSS = f"""
    background: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
"""


# ─── Выпадающие списки ──────────────────────────────────────────
COMBOBOX_QSS = f"""
    QComboBox {{
        font-family: 'Inter', 'Manrope', sans-serif;
        background: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 9px 12px;
        font-size: 13px;
    }}
    QComboBox:hover {{
        border: 1px solid {_GOLD_HOVER};
    }}
    QComboBox:focus {{
        border: 1px solid {_GOLD_FOCUS};
    }}
    QComboBox:disabled {{
        background: {BG_SECONDARY};
        color: {TEXT_MUTED};
    }}
    QComboBox::drop-down {{
        border: none;
        padding-right: 8px;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid {TEXT_SECONDARY};
        margin-right: 6px;
    }}
    QComboBox QAbstractItemView {{
        background: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        selection-background-color: rgba(201, 164, 92, 0.15);
        outline: none;
        padding: 4px;
    }}
    QComboBox QAbstractItemView::item {{
        padding: 8px 12px;
        border-radius: 4px;
    }}
    QComboBox QAbstractItemView::item:hover {{
        background: rgba(255, 255, 255, 0.04);
    }}
    QComboBox QAbstractItemView::item:pressed {{
        background: rgba(201, 164, 92, 0.20);
    }}
"""


# ─── Таблицы ────────────────────────────────────────────────────
TABLE_QSS = f"""
    QTableWidget {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
        gridline-color: transparent;
        font-size: 13px;
    }}
    QTableWidget::item {{
        padding: 10px 16px;
        color: {TEXT_PRIMARY};
        border-bottom: 1px solid rgba(48, 52, 59, 0.13);
    }}
    QTableWidget::item:selected {{
        background: rgba(201, 164, 92, 0.1);
        color: {GOLD};
    }}
"""


# ─── Скроллбары ─────────────────────────────────────────────────
SCROLLBAR_QSS = f"""
    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER};
        border-radius: 3px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {GOLD};
    }}
    QScrollBar::handle:vertical:pressed {{
        background: {GOLD_DARK};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background: transparent;
        height: 6px;
        margin: 0;
    }}
    QScrollBar::handle:horizontal {{
        background: {BORDER};
        border-radius: 3px;
        min-width: 30px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {GOLD};
    }}
    QScrollBar::handle:horizontal:pressed {{
        background: {GOLD_DARK};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}
"""


# ─── Общий стиль приложения ────────────────────────────────────
APP_QSS = f"""
    QMainWindow, QDialog, QMessageBox, QInputDialog {{
        background: {BG_PRIMARY};
        color: {TEXT_PRIMARY};
    }}

    QPushButton, QLabel, QComboBox {{
        font-family: 'Inter', 'Manrope', sans-serif;
    }}

    QLabel, QInputDialog QLabel, QMessageBox QLabel {{
        color: {TEXT_PRIMARY};
        font-size: 13px;
    }}

    /* Строковые поля ввода */
    QLineEdit, QInputDialog QLineEdit {{
        {INPUT_QSS}
    }}
    QLineEdit:hover, QInputDialog QLineEdit:hover {{
        border: 1px solid {_GOLD_HOVER};
    }}
    QLineEdit:focus, QInputDialog QLineEdit:focus {{
        border: 1px solid {_GOLD_FOCUS};
    }}
    QLineEdit:disabled, QInputDialog QLineEdit:disabled {{
        background: {BG_SECONDARY};
        color: {TEXT_MUTED};
    }}

    /* Многострочные поля */
    QTextEdit, QPlainTextEdit {{
        background: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 8px;
        font-size: 13px;
    }}
    QTextEdit:hover, QPlainTextEdit:hover {{
        border: 1px solid {_GOLD_HOVER};
    }}
    QTextEdit:focus, QPlainTextEdit:focus {{
        border: 1px solid {_GOLD_FOCUS};
    }}
    QTextEdit:disabled, QPlainTextEdit:disabled {{
        background: {BG_SECONDARY};
        color: {TEXT_MUTED};
    }}

    /* Спиннеры */
    QSpinBox, QDoubleSpinBox {{
        background: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 5px 8px;
        font-size: 13px;
    }}
    QSpinBox:hover, QDoubleSpinBox:hover {{
        border: 1px solid {_GOLD_HOVER};
    }}
    QSpinBox:focus, QDoubleSpinBox:focus {{
        border: 1px solid {_GOLD_FOCUS};
    }}
    QSpinBox:disabled, QDoubleSpinBox:disabled {{
        background: {BG_SECONDARY};
        color: {TEXT_MUTED};
    }}
    QSpinBox::up-button, QDoubleSpinBox::up-button {{
        background: {BG_ELEVATED};
        border: none;
        border-left: 1px solid {BORDER};
        border-top-right-radius: 8px;
        width: 20px;
    }}
    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
        background: {BG_CARD};
    }}
    QSpinBox::up-button:pressed, QDoubleSpinBox::up-button:pressed {{
        background: {BG_SECONDARY};
    }}
    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        background: {BG_ELEVATED};
        border: none;
        border-left: 1px solid {BORDER};
        border-bottom-right-radius: 8px;
        width: 20px;
    }}
    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
        background: {BG_CARD};
    }}
    QSpinBox::down-button:pressed, QDoubleSpinBox::down-button:pressed {{
        background: {BG_SECONDARY};
    }}
    QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 5px solid {TEXT_SECONDARY};
    }}
    QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {TEXT_SECONDARY};
    }}

    /* Таблицы */
    {TABLE_QSS}

    /* Заголовки таблиц */
    QHeaderView::section {{
        background: #1A1D21;
        color: {TEXT_MUTED};
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        padding: 10px 16px;
        border: none;
        border-bottom: 1px solid {BORDER};
    }}
    QHeaderView::section:first {{
        border-top-left-radius: 12px;
    }}
    QHeaderView::section:last {{
        border-top-right-radius: 12px;
    }}
    QHeaderView::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {GOLD};
    }}
    QHeaderView::up-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 5px solid {GOLD};
    }}

    /* Чекбоксы / Радио */
    QCheckBox, QRadioButton {{
        color: {TEXT_PRIMARY};
        font-size: 13px;
        spacing: 8px;
    }}
    QCheckBox::indicator, QRadioButton::indicator {{
        width: 18px;
        height: 18px;
    }}
    QCheckBox:disabled, QRadioButton:disabled {{
        color: {TEXT_MUTED};
    }}

    /* Группы */
    QGroupBox {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 10px;
        margin-top: 14px;
        padding: 16px 12px 12px 12px;
        font-size: 13px;
        color: {TEXT_PRIMARY};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 2px 10px;
        color: {GOLD};
        font-weight: 600;
    }}

    /* Прогресс-бар */
    QProgressBar {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 6px;
        text-align: center;
        font-size: 11px;
        color: {TEXT_PRIMARY};
        height: 18px;
    }}
    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {GOLD}, stop:1 {GOLD_DARK});
        border-radius: 5px;
    }}

    /* Подсказки */
    QToolTip {{
        background: {BG_ELEVATED};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 12px;
    }}

    /* Меню */
    QMenu {{
        background: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 6px;
    }}
    QMenu::item {{
        padding: 8px 32px 8px 16px;
        border-radius: 6px;
    }}
    QMenu::item:selected {{
        background: rgba(201, 164, 92, 0.12);
        color: {GOLD};
    }}
    QMenu::item:pressed {{
        background: rgba(201, 164, 92, 0.18);
    }}
    QMenu::separator {{
        height: 1px;
        background: {BORDER};
        margin: 4px 8px;
    }}

    /* Кнопки диалогов */
    QDialog QPushButton, QMessageBox QPushButton {{
        background: {BG_ELEVATED};
        color: {TEXT_SECONDARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        font-size: 13px;
        padding: 8px 16px;
        min-height: 20px;
    }}
    QDialog QPushButton:hover, QMessageBox QPushButton:hover {{
        background: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {_GOLD_HOVER};
    }}
    QDialog QPushButton:pressed, QMessageBox QPushButton:pressed {{
        background: {BG_SECONDARY};
        padding-top: 9px;
        padding-bottom: 7px;
    }}
    QDialog QPushButton:disabled, QMessageBox QPushButton:disabled {{
        background: {BG_SECONDARY};
        color: {DISABLED};
        border: 1px solid transparent;
    }}
    QMessageBox QPushButton {{
        min-width: 80px;
        padding: 8px 20px;
    }}

    /* Вкладки */
    QTabWidget::pane {{
        background: {BG_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
    }}
    QTabBar::tab {{
        background: {BG_SECONDARY};
        color: {TEXT_SECONDARY};
        border: 1px solid {BORDER};
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 8px 16px;
        font-size: 13px;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{
        background: {BG_CARD};
        color: {GOLD};
        font-weight: 600;
    }}
    QTabBar::tab:hover:!selected {{
        background: {BG_ELEVATED};
    }}

    QAbstractItemView {{
        outline: none;
    }}

    {SCROLLBAR_QSS}
"""
