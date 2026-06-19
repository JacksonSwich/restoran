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

# ─── Кнопки (возвращаем QSS-строку) ────────────────────────────

BTN_PRIMARY_QSS = f"""
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {GOLD}, stop:1 {GOLD_DARK});
    color: {BG_PRIMARY};
    border: none;
    border-radius: 8px;
    font-weight: 700;
    font-size: 13px;
    padding: 9px 16px;
"""

BTN_PRIMARY_QSS_HOVER = f"""
    {BTN_PRIMARY_QSS}
    opacity: 0.85;
"""

BTN_SECONDARY_QSS = f"""
    background: {BG_ELEVATED};
    color: {TEXT_SECONDARY};
    border: 1px solid {BORDER};
    border-radius: 8px;
    font-weight: 500;
    font-size: 13px;
    padding: 9px 16px;
"""

BTN_DANGER_QSS = f"""
    background: rgba(201, 76, 76, 0.08);
    color: {ERROR};
    border: 1px solid rgba(201, 76, 76, 0.25);
    border-radius: 8px;
    font-weight: 600;
    font-size: 13px;
    padding: 9px 16px;
"""

INPUT_QSS = f"""
    background: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
"""

COMBOBOX_QSS = f"""
    QComboBox {{
        background: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 9px 12px;
        font-size: 13px;
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
"""

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
"""

SCROLLBAR_QSS = f"""
    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER};
        border-radius: 3px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {GOLD};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background: transparent;
        height: 6px;
    }}
    QScrollBar::handle:horizontal {{
        background: {BORDER};
        border-radius: 3px;
        min-width: 30px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {GOLD};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}
"""

APP_QSS = f"""
    QMainWindow, QDialog, QMessageBox, QInputDialog {{
        background: {BG_PRIMARY};
        color: {TEXT_PRIMARY};
    }}
    QPushButton {{
        font-family: 'Inter', 'Manrope', sans-serif;
    }}
    QLabel {{
        font-family: 'Inter', 'Manrope', sans-serif;
    }}
    QLineEdit {{
        {INPUT_QSS}
    }}
    QLineEdit:focus {{
        border: 1px solid rgba(201, 164, 92, 0.5);
    }}
    QTextEdit, QPlainTextEdit {{
        background: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 8px;
        font-size: 13px;
    }}
    QTextEdit:focus, QPlainTextEdit:focus {{
        border: 1px solid rgba(201, 164, 92, 0.5);
    }}
    QSpinBox, QDoubleSpinBox {{
        background: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 5px 8px;
        font-size: 13px;
    }}
    QSpinBox:focus, QDoubleSpinBox:focus {{
        border: 1px solid rgba(201, 164, 92, 0.5);
    }}
    QSpinBox::up-button, QDoubleSpinBox::up-button {{
        background: {BG_ELEVATED};
        border: none;
        border-left: 1px solid {BORDER};
        border-top-right-radius: 8px;
        width: 20px;
    }}
    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        background: {BG_ELEVATED};
        border: none;
        border-left: 1px solid {BORDER};
        border-bottom-right-radius: 8px;
        width: 20px;
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
    QTableWidget {{
        {TABLE_QSS}
    }}
    QTableWidget::item:selected {{
        background: rgba(201, 164, 92, 0.1);
        color: {GOLD};
    }}
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
    QCheckBox, QRadioButton {{
        color: {TEXT_PRIMARY};
        font-size: 13px;
        spacing: 8px;
    }}
    QCheckBox::indicator, QRadioButton::indicator {{
        width: 18px;
        height: 18px;
    }}
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
    QToolTip {{
        background: {BG_ELEVATED};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 12px;
    }}
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
    QMenu::separator {{
        height: 1px;
        background: {BORDER};
        margin: 4px 8px;
    }}
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
    QDialog QPushButton {{
        background: {BG_ELEVATED};
        color: {TEXT_SECONDARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        font-size: 13px;
        padding: 8px 16px;
        min-height: 20px;
    }}
    QDialog QPushButton:hover {{
        background: {BG_CARD};
        color: {TEXT_PRIMARY};
    }}
    QInputDialog QLineEdit {{
        background: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
    }}
    QInputDialog QLabel {{
        color: {TEXT_PRIMARY};
        font-size: 13px;
    }}
    QMessageBox QLabel {{
        color: {TEXT_PRIMARY};
        font-size: 13px;
    }}
    QMessageBox QPushButton {{
        background: {BG_ELEVATED};
        color: {TEXT_SECONDARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        font-size: 13px;
        padding: 8px 20px;
        min-height: 20px;
        min-width: 80px;
    }}
    QMessageBox QPushButton:hover {{
        background: {BG_CARD};
        color: {TEXT_PRIMARY};
    }}
    QAbstractItemView {{
        outline: none;
    }}
    {SCROLLBAR_QSS}
"""
