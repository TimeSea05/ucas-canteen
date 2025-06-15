from django.contrib import admin

from .models import Customer


# 在admin中注册绑定
class CustomerAdmin(admin.ModelAdmin):
    list_per_page = 10
    search_fields = ['address__building']
    list_display = ['customer_id', 'customer_name', 'customer_tel', 'create_time']

admin.site.register(Customer, CustomerAdmin)

admin.site.site_header = '校园食堂后台管理系统'
admin.site.site_title = '校园食堂后台管理系统'
