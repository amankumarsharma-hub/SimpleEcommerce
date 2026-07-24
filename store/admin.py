from django.contrib import admin
from .models import Product, Order, Category
from .models import Wishlist
from .models import Review
from .models import Coupon

admin.site.register(Coupon)


admin.site.register(Product)

admin.site.register(Category)
admin.site.register(Wishlist)
admin.site.register(Review)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "email",
        "total_amount",
        "status",
        "created_at",
    )

    list_filter = ("status",)
    search_fields = ("customer_name", "email")