from django.urls import path
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from . import views

urlpatterns = [
    path("", LoginView.as_view(template_name='registration/login.html'), name="login"),
    path("home/", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),

    # Auth
    path("register/", views.register, name="register"),
    path("profile/", views.user_profile, name="user_profile"),
    path("create-account/", views.create_additional_account, name="create_additional_account"),

    # Products
    path("products/", views.product_list, name="product_list"),
    path("api/search-suggestions/", views.product_search_suggestions, name="product_search_suggestions"),

    # Reservations CRUD
    path("reservations/", views.reservation_list, name="reservation_list"),
    path("reservations/create/", views.reservation_create, name="reservation_create"),
    path("reservations/<int:pk>/edit/", views.reservation_update, name="reservation_update"),
    path("reservations/<int:pk>/delete/", views.reservation_delete, name="reservation_delete"),

    # Journal CRUD
    path("journal/", views.journal_list, name="journal_list"),
    path("journal/create/", views.journal_create, name="journal_create"),
    path("journal/<int:pk>/edit/", views.journal_update, name="journal_update"),
    path("journal/<int:pk>/delete/", views.journal_delete, name="journal_delete"),

    # Articles CRUD (admin-only create/edit)
    path("articles/", views.article_list, name="article_list"),
    path("articles/create/", views.article_create, name="article_create"),
    path("articles/<int:pk>/edit/", views.article_update, name="article_update"),
    path("articles/<int:pk>/delete/", views.article_delete, name="article_delete"),

    # Feedback forum
    path("feedback/", views.feedback_list_create, name="feedback"),
    
    # Management - Order Management (Changed from admin to avoid Django admin conflict)
    path("management/orders/", views.admin_order_list, name="admin_order_list"),
    path("management/orders/<int:pk>/edit/", views.admin_order_update, name="admin_order_update"),
    path("management/orders/<int:pk>/tracking/", views.admin_order_tracking_update, name="admin_order_tracking_update"),
    
    # Management - Payment Management
    path("management/payments/", views.admin_payment_list, name="admin_payment_list"),
    path("management/payments/create/<int:order_id>/", views.admin_payment_create, name="admin_payment_create"),
    path("management/payments/<int:pk>/edit/", views.admin_payment_update, name="admin_payment_update"),
    
    # Management - All Reservations
    path("management/reservations/", views.admin_reservation_list, name="admin_reservation_list"),
    
    # Management - Stock Management
    path("management/stock/", views.admin_stock_management, name="admin_stock_management"),
    path("management/stock/<int:product_id>/update/", views.admin_update_stock, name="admin_update_stock"),
    
    # Orders
    path("orders/", views.order_list, name="order_list"),
    path("orders/<int:pk>/edit/", views.order_update, name="order_update"),
    path("orders/<int:pk>/delete/", views.order_delete, name="order_delete"),
    path("orders/<int:pk>/add-item/", views.add_order_item, name="add_order_item"),
    path("orders/<int:pk>/remove-item/<int:item_id>/", views.remove_order_item, name="remove_order_item"),
    path("orders/<int:pk>/tracking/", views.order_tracking, name="order_tracking"),
    
    # Tracking Guide
    path("tracking-guide/", views.tracking_guide, name="tracking_guide"),
    
    # User History
    path("history/", views.user_history, name="user_history"),
    path("history/<int:pk>/delete/", views.delete_user_history, name="delete_user_history"),
    path("history/clear/", views.clear_user_history, name="clear_user_history"),
    
    # Cart
    path("cart/", views.cart_view, name="cart_view"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:item_id>/", views.update_cart_item, name="update_cart_item"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
    
    # Map
    path("map/", views.map_view, name="map"),
    
    # Admin Invoices
    path("management/invoices/", views.admin_invoice_list, name="admin_invoice_list"),
    path("management/invoices/<int:pk>/", views.admin_invoice_detail, name="admin_invoice_detail"),
    path("management/orders/<int:order_id>/generate-invoice/", views.admin_generate_invoice, name="admin_generate_invoice"),
]