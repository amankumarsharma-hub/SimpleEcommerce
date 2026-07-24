from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('cart/', views.cart, name='cart'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),


    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('increase/<int:product_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("wishlist/add/<int:id>/", views.add_to_wishlist, name="add_to_wishlist"),
    path("my-orders/", views.my_orders, name="my_orders"),
    path("payment/", views.payment, name="payment"),
    path("payment/success/", views.payment_success, name="payment_success"),
    path("payment/failed/", views.payment_failed, name="payment_failed"),
    path("product/<int:id>/", views.product_detail, name="product_detail"),
    path("admin-dashboard/",views.admin_dashboard,name="admin_dashboard"),
    path("invoice/<int:order_id>/",views.download_invoice,name="download_invoice"),
    
]