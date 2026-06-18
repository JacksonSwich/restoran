Create a premium dark modern desktop web application design for a restaurant management system with role-based access for two user roles: Administrator and Waiter.

Project name: “Restaurant Management System — Меню и заказы ресторана”.

The app must support two roles:

1. Administrator — manages the restaurant system, menu, tables, customers, payments, orders, and reports.
2. Waiter — works with tables, creates orders, adds dishes, changes order statuses, and processes payments.

Important:
The prompt is written in English, but all visible UI text in the Figma design must be in Russian.
All buttons, labels, headings, menu items, statuses, table columns, modals, forms, and cards must use Russian language.

Design style:
Premium dark modern restaurant management interface.
The app should look like a high-quality restaurant POS / management dashboard.
Use a dark luxury aesthetic, modern spacing, large readable typography, clean cards, subtle glassmorphism, soft shadows, rounded corners, and restrained gold accents.

No food photos.
Do not use dish images.
Dish cards must be text-based only.

Canvas:
Desktop only.
Design all screens in 1440×1024.
Use a clean 12-column grid.
Make the interface suitable for professional restaurant staff.

Color palette:

* Main background: #0E0F11
* Secondary background: #15171A
* Card background: #202328
* Elevated panel: #252932
* Border color: #30343B
* Primary text: #F5F2EA
* Secondary text: #A9A39A
* Muted text: #6F756F
* Primary accent: premium gold #C9A45C
* Secondary accent: deep emerald #1F6F50
* Success: #3FA66B
* Warning: #D98A35
* Info: #4A7BD0
* Error: #C94C4C
* Disabled: #5C6068

Typography:
Use Inter, Manrope, or SF Pro.
Use strong visual hierarchy.
Table numbers, order totals, and statuses must be large and easy to read.
Buttons must be large enough for quick restaurant workflow.

Role-based logic:
Create two versions of the interface:

1. Administrator interface
2. Waiter interface

The app should have a clear role indicator in the top bar:

* “Роль: Администратор”
* “Роль: Официант”

Also create a small role switch / login concept screen where a user can choose:

* “Войти как администратор”
* “Войти как официант”

The sidebar must change depending on the role.

Administrator sidebar:

1. Главная
2. Столики
3. Заказы
4. Меню
5. Клиенты
6. Оплаты
7. Отчеты
8. Настройки

Waiter sidebar:

1. Столики
2. Новый заказ
3. Заказы
4. Меню
5. Оплата

Top bar for both roles:

* Restaurant name: “GastroHub”
* Search field: “Поиск заказа, столика, клиента или блюда”
* Current date and time
* Current role
* User profile
* Primary action button:

  * for Administrator: “Добавить блюдо” or “Создать отчет”
  * for Waiter: “Создать заказ”

Create the following screens:

1. Login / Role selection screen — “Выбор роли”
   Create a premium dark login-style screen.
   Include:

* app logo or wordmark “GastroHub”
* title: “Система управления рестораном”
* subtitle: “Выберите роль для входа”
* two role cards:

  * “Администратор”
  * “Официант”
    Each role card should briefly show available actions.

Administrator card:

* управление меню;
* отчеты;
* клиенты;
* оплаты;
* заказы;
* столики.

Waiter card:

* работа со столиками;
* создание заказов;
* добавление блюд;
* изменение статусов;
* оплата заказов.

2. Administrator dashboard — “Главная”
   This is the main admin screen.
   Show restaurant analytics and operational control.

Cards at the top:

* “Выручка за день”
* “Количество заказов”
* “Средний чек”
* “Активные заказы”
* “Занятые столики”
* “Оплаченные заказы”

Middle section:

* revenue chart by day;
* popular dishes list;
* active orders overview.

Bottom section:
Table “Последние заказы” with columns:

* № заказа
* Столик
* Клиент
* Статус
* Сумма
* Оплата
* Создан

Use premium dark cards and gold accents.

3. Waiter workspace — “Рабочее место официанта”
   This is the main waiter screen.
   Focus on fast work.

Show:

* free tables;
* occupied tables;
* active orders;
* orders ready to serve;
* quick button “Создать заказ”.

Large cards:

* “Свободные столики”
* “Занятые столики”
* “Готовые заказы”
* “Заказы в работе”

Active order cards must show:

* order number;
* table number;
* status;
* time since creation;
* final amount;
* action button “Открыть”.

4. Tables screen — “Столики”
   This screen is available for both roles.

Create a visual table map using premium dark cards.
Each table card must show:

* “Столик №1”
* seats count: “2 места”, “4 места”, “6 мест”
* zone: “Основной зал”, “VIP-зона”, “Терраса”
* status badge:

  * “Свободен”
  * “Занят”
  * “Забронирован”
  * “Недоступен”
* current order number if occupied;
* current amount if occupied.

Top filters:

* Все
* Свободные
* Занятые
* Забронированные
* Недоступные

Zone filters:

* Основной зал
* VIP-зона
* Терраса

For Waiter:
Show quick action:

* “Создать заказ для столика”

For Administrator:
Show management actions:

* “Добавить столик”
* “Изменить столик”
* “Изменить статус”

5. New order screen — “Новый заказ”
   This screen is primarily for Waiter but can also be available for Administrator.

Layout:

* left panel: selected table and customer;
* center panel: menu categories and dishes;
* right panel: current order cart.

Left panel:

* selected table: “Столик №4”
* zone
* seats count
* customer search: “Добавить клиента”
* discount field if customer selected.

Center panel:
Category tabs:

* Салаты
* Супы
* Горячие блюда
* Напитки
* Десерты
* Закуски

Dish cards without photos.
Each dish card:

* dish name;
* short description;
* price;
* weight;
* preparation time;
* availability status;
* button “Добавить”.

Example dish card:

* “Паста Карбонара”
* “Сливочный соус, бекон, пармезан”
* “560 ₽”
* “300 г”
* “20 мин”
* button “Добавить”

Unavailable dish:

* muted semi-transparent card;
* badge “Недоступно”;
* disabled button.

Right cart panel:
Heading: “Заказ”
Show:

* dish name;
* quantity stepper;
* price;
* item total;
* comment field: “Комментарий”.

Bottom total block:

* “Сумма”
* “Скидка”
* “Итого к оплате”

Buttons:

* “Создать заказ”
* “Очистить”

6. Order details screen — “Детали заказа”
   Available for both roles.

Top section:

* “Заказ №15”
* “Столик №4”
* order status badge
* customer name
* created time

Main table:
Columns:

* Блюдо
* Количество
* Цена
* Сумма
* Комментарий

Example rows:

* “Паста Карбонара” — 2 — 560 ₽ — 1120 ₽ — “Без лука”
* “Капучино” — 2 — 180 ₽ — 360 ₽ — “Один без сахара”

Right side panel:
Order status timeline:

1. Новый
2. Готовится
3. Готов
4. Подан
5. Оплачен

Total block:

* “Сумма: 1480 ₽”
* “Скидка: 74 ₽”
* “Итого: 1406 ₽”

Waiter actions:

* “Добавить блюдо”
* “Изменить статус”
* “Перейти к оплате”
* “Отменить заказ”

Administrator actions:

* “Редактировать заказ”
* “Просмотреть оплату”
* “История изменений”
* “Отменить заказ”

7. Orders list screen — “Заказы”
   Available for both roles.

Top filters:

* Все
* Новый
* Готовится
* Готов
* Подан
* Оплачен
* Отменен

Table columns:

* № заказа
* Столик
* Клиент
* Статус
* Сумма
* Скидка
* Итого
* Создан
* Действие

Use color-coded status badges:

* Новый — blue
* Готовится — orange
* Готов — green
* Подан — purple
* Оплачен — emerald
* Отменен — red

Add right-side preview panel for the selected order.

For Waiter:
Emphasize quick actions:

* “Открыть”
* “Изменить статус”
* “Оплатить”

For Administrator:
Emphasize control actions:

* “Открыть”
* “Редактировать”
* “Просмотреть оплату”
* “Отчет”

8. Menu management screen — “Меню”
   For Administrator:
   This is a full menu management screen.

Left side:
category list:

* Салаты
* Супы
* Горячие блюда
* Напитки
* Десерты
* Закуски

Main area:
text-based dish cards without images.

Each card:

* dish name;
* category;
* description;
* price;
* weight;
* cooking time;
* availability status.

Admin buttons:

* “Добавить блюдо”
* “Редактировать”
* “Скрыть из меню”
* “Удалить”

Add filters:

* “Все блюда”
* “Доступные”
* “Недоступные”

Add search:

* “Найти блюдо”

For Waiter:
Create a simplified menu viewing mode.
Waiter can only view available dishes and add them to an order.
No edit/delete buttons.

9. Customers screen — “Клиенты”
   Mainly for Administrator, simplified for Waiter.

Admin view:
Table columns:

* Имя
* Телефон
* Email
* Скидка
* Количество заказов
* Общая сумма заказов
* Последний заказ

Admin actions:

* “Добавить клиента”
* “Редактировать”
* “История заказов”

Waiter view:
Simplified customer search and selection:

* search input “Найти клиента”
* button “Выбрать клиента”
* button “Создать клиента”

10. Payments screen — “Оплаты”
    Available for both roles.

Table columns:

* ID оплаты
* № заказа
* Столик
* Сумма
* Способ оплаты
* Статус
* Дата оплаты

Payment methods:

* Наличные
* Карта
* Онлайн

Payment statuses:

* Ожидает оплаты
* Оплачено
* Возврат
* Отменено

Waiter flow:
Create payment modal:

* order number;
* table number;
* final amount;
* payment method selector;
* button “Подтвердить оплату”.

After successful payment:
show confirmation:

* “Заказ оплачен”
* “Столик свободен”

Administrator flow:
Add filters:

* by payment method;
* by payment status;
* by date.
  Show total revenue for selected period.

11. Reports screen — “Отчеты”
    Only for Administrator.

Create a premium analytics dashboard.

Cards:

* “Выручка за день”
* “Выручка за неделю”
* “Количество заказов”
* “Средний чек”
* “Самое популярное блюдо”
* “Оплаченные заказы”

Charts:

* sales by day;
* popular dishes;
* orders by status;
* revenue by payment method.

Tables:

* “Популярные блюда”
* “История заказов”
* “Выручка по дням”

Make reports visually premium, clean, and easy to read.

12. Settings screen — “Настройки”
    Only for Administrator.

Sections:

* “Профиль ресторана”
* “Пользователи и роли”
* “Статусы заказов”
* “Зоны столиков”
* “Способы оплаты”

Create a role permissions block:
Administrator permissions:

* управление меню;
* управление столиками;
* просмотр отчетов;
* управление клиентами;
* просмотр оплат;
* редактирование заказов.

Waiter permissions:

* создание заказов;
* добавление блюд;
* изменение статусов;
* оплата заказов;
* просмотр меню;
* просмотр столиков.

UX principles:

* The waiter interface must be fast and operational.
* The administrator interface must be analytical and managerial.
* The role separation must be visually clear.
* Use Russian UI text everywhere.
* Keep the dark premium modern style consistent.
* Avoid unnecessary decoration.
* Do not use food photos.
* Use large buttons, readable cards, status badges, clean tables, and structured panels.

Components to create:

* Role selection card
* Sidebar navigation with role-based items
* Top bar with role indicator
* Table card
* Order card
* Dish card without image
* Status badge
* Quantity stepper
* Payment method selector
* Order total block
* Modal window
* Data table
* Search input
* Filter tabs
* Primary button
* Secondary button
* Danger button
* Analytics card
* Chart card
* Empty state
* Disabled dish card

Final screen list:

1. Выбор роли
2. Главная администратора
3. Рабочее место официанта
4. Столики
5. Новый заказ
6. Детали заказа
7. Заказы
8. Меню
9. Клиенты
10. Оплаты
11. Отчеты
12. Настройки

Final goal:
Create a complete premium dark modern Figma design system and desktop screen set for a restaurant management application with role-based access for Administrator and Waiter.
