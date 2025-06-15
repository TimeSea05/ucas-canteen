from django.contrib import admin

from .models import Dish, Orders, Comments, DishPreference


# 在admin中注册绑定
class DishAdmin(admin.ModelAdmin):
    list_per_page = 10
    search_fields = ['dish_name']
    list_display = ['dish_id', 'dish_name', 'shop', 'dish_price', 'dish_active']


class OrdersAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['order_id', 'dish', 'customer', 'order_price', 'order_status', 'order_time']


class CommentsAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['comment_id', 'order', 'comment_score', 'comment_time']


class DishPreferenceAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['preference_id', 'customer', 'dish', 'preference_type', 'created_at']
    list_filter = ['preference_type']
    search_fields = ['customer__customer_name', 'dish__dish_name']


admin.site.register(Dish, DishAdmin)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(Comments, CommentsAdmin)
admin.site.register(DishPreference, DishPreferenceAdmin)