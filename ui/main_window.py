"""Главное окно приложения с навигацией."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QMessageBox,
)
from PyQt6.QtCore import Qt

from ui.styles import *
from ui.sidebar import Sidebar
from ui.topbar import TopBar
from ui.login_screen import LoginScreen
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

        # Максимизация
        self.showMaximized()

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
        right_layout.addWidget(self._topbar)

        # Screen stack
        self._screen_stack = QStackedWidget()
        right_layout.addWidget(self._screen_stack, 1)

        app_layout.addWidget(right, 1)
        self._stack.addWidget(self._app_widget)

        # Создаём экраны
        self._screens: dict[str, QWidget] = {}
        self._create_screens()
        self._navigate("dashboard" if self._role == "admin" else "waiter-workspace")

    def _create_screens(self):
        screens_data = {
            "dashboard": (AdminDashboard, {"on_navigate": self._navigate}),
            "waiter-workspace": (WaiterWorkspace, {"on_navigate": self._navigate}),
            "tables": (TablesScreen, {"role": self._role, "on_navigate": self._navigate}),
            "new-order": (NewOrderScreen, {"on_navigate": self._navigate}),
            "order-details": (OrderDetailsScreen, {"role": self._role, "on_navigate": self._navigate}),
            "orders": (OrdersListScreen, {"role": self._role, "on_navigate": self._navigate}),
            "menu": (MenuScreen, {"role": self._role}),
            "customers": (CustomersScreen, {"role": self._role}),
            "payments": (PaymentsScreen, {"role": self._role}),
            "reports": (ReportsScreen, {}),
            "settings": (SettingsScreen, {}),
        }

        for screen_id, (cls, kwargs) in screens_data.items():
            screen = cls(**kwargs)
            self._screens[screen_id] = screen
            self._screen_stack.addWidget(screen)

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

    def _navigate(self, screen_id: str, order_id=None):
        """Перейти на экран. Если order_id указан, передать его экрану."""
        self._pending_order_id = order_id
        if screen_id in self._screens:
            self._current_screen = screen_id
            screen = self._screens[screen_id]
            # Передать order_id детальному экрану заказа
            if isinstance(screen, OrderDetailsScreen) and order_id is not None:
                screen.load_order(order_id)
            self._screen_stack.setCurrentWidget(screen)
            self._sidebar.set_current(screen_id)
