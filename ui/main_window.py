"""Главное окно приложения с навигацией."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QMessageBox,
    QDialog, QLabel, QPushButton, QFrame, QScrollArea,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from ui.styles import *
from ui.sidebar import Sidebar
from ui.topbar import TopBar
from ui.login_screen import LoginScreen
from database.queries import (
    get_all_orders, get_all_tables, get_all_customers, get_all_dishes,
)
from ui.widgets import make_label, make_manrope_label, StatusBadge, Card, hex_to_rgb
from ui.screens import (
    AdminDashboard,
    WaiterWorkspace,
    TablesScreen,
    NewOrderScreen,
    OrderDetailsScreen,
    OrdersListScreen,
    MenuScreen,
    CustomersScreen,
    PaymentsScreen,
    ReportsScreen,
    SettingsScreen,
    PaymentDialog,
    ORDER_STATUS_CONFIG, TABLE_STATUS_CONFIG,
)


class MainWindow(QWidget):
    """Главное окно — точка входа в интерфейс."""

    def __init__(self):
        super().__init__()
        self._role: str | None = None
        self._current_screen = "dashboard"
        self._pending_order_id = None
        self.setWindowTitle("GastroHub — Система управления рестораном")
        self.setStyleSheet(f"background: {BG_PRIMARY}; color: {TEXT_PRIMARY};")

        # Сначала показываем логин
        self._stack = QStackedWidget(self)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self._stack)

        # Логин
        self._login = LoginScreen()
        self._login.login_signal.connect(self._on_login)
        self._stack.addWidget(self._login)

        # Основное приложение (создаётся после логина)
        self._app_widget = None

        # Отслеживание изменения размера (ДО resize/maximize, чтобы resizeEvent не упал)
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._on_resize_finished)

        # Размер окна по умолчанию и максимизация
        self.resize(1400, 900)
        self.showMaximized()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._resize_timer.start(100)

    def _on_resize_finished(self):
        """Перестраиваем активный экран при изменении размера, если нужно."""
        if not hasattr(self, '_screen_stack') or self._screen_stack is None:
            return
        screen = self._screen_stack.currentWidget()
        if hasattr(screen, 'on_resize') and callable(screen.on_resize):
            screen.on_resize()

    def _on_login(self, role: str):
        self._role = role
        self._build_app()
        self._stack.setCurrentWidget(self._app_widget)

    def _build_app(self):
        self._app_widget = QWidget()
        app_layout = QHBoxLayout(self._app_widget)
        app_layout.setContentsMargins(0, 0, 0, 0)
        app_layout.setSpacing(0)

        # Sidebar
        self._sidebar = Sidebar(self._role)
        self._sidebar.navigate_signal.connect(self._navigate)
        app_layout.addWidget(self._sidebar)

        # Right side
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self._topbar = TopBar(self._role)
        self._topbar.action_signal.connect(self._on_topbar_action)
        self._topbar.logout_signal.connect(self._on_logout)
        self._topbar.search_signal.connect(self._on_search)
        self._topbar.notifications_signal.connect(self._on_notifications)
        right_layout.addWidget(self._topbar)

        # Screen stack
        self._screen_stack = QStackedWidget()
        right_layout.addWidget(self._screen_stack, 1)

        app_layout.addWidget(right, 1)
        self._stack.addWidget(self._app_widget)

        # Создаём экраны (lazy — только при первом переходе)
        self._screens: dict[str, QWidget] = {}
        self._screen_factories: dict[str, tuple] = {}
        self._create_screen_factories()
        QTimer.singleShot(0, lambda: self._navigate("dashboard" if self._role == "admin" else "waiter-workspace"))

    def _create_screen_factories(self):
        """Store screen constructors — actual screens created lazily on first navigation."""
        self._screen_factories = {
            "dashboard": (AdminDashboard, {"on_navigate": self._navigate}),
            "waiter-workspace": (WaiterWorkspace, {"on_navigate": self._navigate}),
            "tables": (TablesScreen, {"role": self._role, "on_navigate": self._navigate}),
            "new-order": (NewOrderScreen, {"on_navigate": self._navigate}),
            "order-details": (OrderDetailsScreen, {"role": self._role, "on_navigate": self._navigate}),
            "orders": (OrdersListScreen, {"role": self._role, "on_navigate": self._navigate}),
            "menu": (MenuScreen, {"role": self._role}),
            "customers": (CustomersScreen, {"role": self._role, "on_navigate": self._navigate}),
            "payments": (PaymentsScreen, {"role": self._role}),
            "reports": (ReportsScreen, {}),
            "settings": (SettingsScreen, {}),
        }

    def _get_or_create_screen(self, screen_id: str) -> QWidget | None:
        """Return existing screen or create it on first access."""
        if screen_id not in self._screens and screen_id in self._screen_factories:
            cls, kwargs = self._screen_factories[screen_id]
            screen = cls(**kwargs)
            self._screens[screen_id] = screen
            self._screen_stack.addWidget(screen)
        return self._screens.get(screen_id)

    def _on_topbar_action(self, action: str):
        if action == "create-order":
            self._navigate("new-order")
        elif action == "create-report":
            self._navigate("reports")

    def _on_logout(self):
        """Return to the login screen."""
        reply = QMessageBox.question(
            self, "Выход",
            "Вы уверены, что хотите выйти?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._stack.setCurrentWidget(self._login)

    def _on_notifications(self):
        """Show notifications dialog."""
        from ui.screens import NotificationsDialog
        dlg = NotificationsDialog(self)
        dlg.exec()

    def _on_search(self, query: str):
        """Search across orders, tables, customers, and dishes."""
        if not query.strip():
            return
        query_lower = query.strip().lower()

        try:
            orders = get_all_orders()
            tables = get_all_tables()
            customers = get_all_customers()
            dishes = get_all_dishes()
        except:
            QMessageBox.warning(self, "Ошибка", "Не удалось выполнить поиск")
            return

        # Search in each category
        matched_orders = [
            o for o in orders
            if query_lower in str(o["id"]) or query_lower in (o.get("customer_name", "") or "").lower()
        ]
        matched_tables = [
            t for t in tables
            if query_lower in str(t["table_number"]) or query_lower in (t.get("zone", "") or "").lower()
        ]
        matched_customers = [
            c for c in customers
            if query_lower in (c.get("full_name", "") or "").lower()
               or query_lower in (c.get("phone", "") or "")
        ]
        matched_dishes = [
            d for d in dishes
            if query_lower in (d.get("name", "") or "").lower()
               or query_lower in (d.get("description", "") or "").lower()
        ]

        total = len(matched_orders) + len(matched_tables) + len(matched_customers) + len(matched_dishes)
        if total == 0:
            QMessageBox.information(self, "Поиск", f"Ничего не найдено по запросу «{query.strip()}»")
            return

        # Build search results dialog
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Результаты поиска: «{query.strip()}»")
        dlg.setModal(True)
        dlg.setMinimumSize(600, 450)
        dlg.setStyleSheet(f"background: {BG_PRIMARY}; color: {TEXT_PRIMARY};")

        dl = QVBoxLayout(dlg)
        dl.setContentsMargins(24, 24, 24, 24)
        dl.setSpacing(16)

        dl.addWidget(make_manrope_label(
            f"Результаты поиска «{query.strip()}»", 18, QFont.Weight.ExtraBold
        ))
        dl.addWidget(make_label(f"Найдено: {total}", 13, TEXT_MUTED))

        # Results scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        results_layout.setSpacing(8)

        # Orders
        if matched_orders:
            section = QLabel("📋  ЗАКАЗЫ")
            section.setStyleSheet(f"color: {GOLD}; font-size: 12px; font-weight: 700; padding: 4px 0;")
            results_layout.addWidget(section)
            for o in matched_orders[:5]:
                row = QFrame()
                row.setStyleSheet(f"""
                    background: {BG_CARD}; border: 1px solid {BORDER};
                    border-radius: 8px; padding: 8px;
                """)
                rl = QHBoxLayout(row)
                rl.setContentsMargins(12, 8, 12, 8)
                rl.addWidget(make_label(f"#{o['id']}", 13, GOLD, QFont.Weight.Bold))
                rl.addWidget(make_label(f"Столик №{o.get('table_number', '?')}", 12, TEXT_SECONDARY))
                rl.addStretch()
                cfg = ORDER_STATUS_CONFIG.get(o["status"], {})
                rl.addWidget(QLabel(cfg.get("label", o["status"])))
                results_layout.addWidget(row)

        # Tables
        if matched_tables:
            section = QLabel("🪑  СТОЛИКИ")
            section.setStyleSheet(f"color: {SUCCESS}; font-size: 12px; font-weight: 700; padding: 4px 0;")
            results_layout.addWidget(section)
            for t in matched_tables[:5]:
                row = QFrame()
                row.setStyleSheet(f"""
                    background: {BG_CARD}; border: 1px solid {BORDER};
                    border-radius: 8px; padding: 8px;
                """)
                rl = QHBoxLayout(row)
                rl.setContentsMargins(12, 8, 12, 8)
                cfg = TABLE_STATUS_CONFIG.get(t["status"], {})
                rl.addWidget(make_label(f"Столик №{t['table_number']}", 13, TEXT_PRIMARY, QFont.Weight.Medium))
                rl.addWidget(make_label(f"{t.get('zone', '')}", 11, TEXT_MUTED))
                rl.addStretch()
                rl.addWidget(QLabel(cfg.get("label", t["status"])))
                results_layout.addWidget(row)

        # Customers
        if matched_customers:
            section = QLabel("👥  КЛИЕНТЫ")
            section.setStyleSheet(f"color: {INFO}; font-size: 12px; font-weight: 700; padding: 4px 0;")
            results_layout.addWidget(section)
            for c in matched_customers[:5]:
                row = QFrame()
                row.setStyleSheet(f"""
                    background: {BG_CARD}; border: 1px solid {BORDER};
                    border-radius: 8px; padding: 8px;
                """)
                rl = QHBoxLayout(row)
                rl.setContentsMargins(12, 8, 12, 8)
                rl.addWidget(make_label(c.get("full_name", "—"), 13, TEXT_PRIMARY, QFont.Weight.Medium))
                rl.addWidget(make_label(c.get("phone", ""), 12, TEXT_SECONDARY))
                rl.addStretch()
                if float(c.get("discount_percent", 0) or 0) > 0:
                    rl.addWidget(QLabel(f"−{float(c['discount_percent']):.0f}%"))
                results_layout.addWidget(row)

        # Dishes
        if matched_dishes:
            section = QLabel("🍽  БЛЮДА")
            section.setStyleSheet(f"color: {WARNING}; font-size: 12px; font-weight: 700; padding: 4px 0;")
            results_layout.addWidget(section)
            for d in matched_dishes[:5]:
                row = QFrame()
                row.setStyleSheet(f"""
                    background: {BG_CARD}; border: 1px solid {BORDER};
                    border-radius: 8px; padding: 8px;
                """)
                rl = QHBoxLayout(row)
                rl.setContentsMargins(12, 8, 12, 8)
                rl.addWidget(make_label(d["name"], 13, TEXT_PRIMARY, QFont.Weight.Medium))
                rl.addWidget(make_label(d.get("category_name", ""), 11, TEXT_MUTED))
                rl.addStretch()
                rl.addWidget(make_label(
                    f"{float(d['price']):,.0f} ₽".replace(",", " "),
                    13, GOLD, QFont.Weight.Bold
                ))
                results_layout.addWidget(row)

        results_layout.addStretch()
        scroll.setWidget(results_widget)
        dl.addWidget(scroll, 1)

        # Close
        close_btn = QPushButton("Закрыть")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {GOLD}, stop:1 {GOLD_DARK});
                color: {BG_PRIMARY}; border: none; border-radius: 8px;
                font-size: 13px; font-weight: 700; padding: 10px 20px;
            }}
        """)
        close_btn.clicked.connect(dlg.accept)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        dl.addWidget(close_btn)

        dlg.exec()

    def _navigate(self, screen_id: str, order_id=None):
        """Перейти на экран. Если order_id указан, передать его экрану."""
        self._pending_order_id = order_id
        screen = self._get_or_create_screen(screen_id)
        if screen is not None:
            self._current_screen = screen_id
            # Передать order_id детальному экрану заказа
            if isinstance(screen, OrderDetailsScreen) and order_id is not None:
                screen.load_order(order_id)
            self._screen_stack.setCurrentWidget(screen)
            self._sidebar.set_current(screen_id)
