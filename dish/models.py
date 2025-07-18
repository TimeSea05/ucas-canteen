# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from canteen.models import Shop
from customer.models import Customer
from django.utils.text import slugify
from django.shortcuts import redirect
from django.urls import reverse


class Dish(models.Model):
    dish_id = models.AutoField(primary_key=True, verbose_name='菜品编号')
    shop = models.ForeignKey(Shop, models.CASCADE, verbose_name='窗口')
    dish_name = models.CharField(max_length=20, verbose_name='菜品名称')
    dish_detail = models.CharField(max_length=200, blank=True, null=True, verbose_name='菜品描述')
    dish_price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="菜品价格")
    dish_photo = models.ImageField(upload_to='images/dish', null=True, blank=True, verbose_name='菜品照片')
    dish_active = models.IntegerField(choices = [(1, '销售中'),(0, '售罄')], verbose_name='菜品状态')
    
    # 营养信息字段
    calories = models.IntegerField(default=0, verbose_name='热量(千卡)')
    protein = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='蛋白质(克)')
    fat = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='脂肪(克)')
    carbohydrates = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='碳水化合物(克)')
    taste_choices = [
        ('清淡', '清淡'),
        ('适中', '适中'),
        ('重口味', '重口味')
    ]
    taste = models.CharField(max_length=10, choices=taste_choices, default='适中', verbose_name='口味')
    is_spicy = models.BooleanField(default=False, verbose_name='是否辣')

    class Meta:
        ordering = ['dish_id']
        db_table = 'dish'
        verbose_name = "菜品信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.dish_name

    def get_order_url(self):
        return reverse("dish:get_order", kwargs={'dish_id': self.dish_id})
        
    def get_comments_url(self):
        return reverse("dish:dish_comments", kwargs={'dish_id': self.dish_id})


class Orders(models.Model):
    order_id = models.AutoField(primary_key=True, verbose_name='订单编号')
    dish = models.ForeignKey(Dish, models.CASCADE, verbose_name='菜品')
    customer = models.ForeignKey(Customer, models.CASCADE, verbose_name='顾客')
    order_price = models.DecimalField(max_digits=5, decimal_places=2,  blank=True, null=True, verbose_name="订单价格")
    order_status = models.IntegerField(choices=[(0, '已下单'), (1, '已发货'), (2, '已送达'), (3, '已评价')], default=0, verbose_name='订单状态')
    order_time = models.DateTimeField(auto_now_add=True, verbose_name='下单时间')

    class Meta:
        ordering = ['-order_time']
        db_table = 'orders'
        verbose_name = "订单信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.order_id)


class Comments(models.Model):
    comment_id = models.AutoField(primary_key=True, verbose_name='评价编号')
    order = models.ForeignKey(Orders, models.CASCADE, verbose_name='订单编号')
    comment_score = models.SmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=5, verbose_name='评分')
    comment_detail = models.CharField(max_length=200, blank=True, null=True, verbose_name='评价内容')
    comment_time = models.DateTimeField(auto_now_add=True, verbose_name='评价时间')

    class Meta:
        ordering = ['-comment_time']
        db_table = 'comments'
        verbose_name = "评价信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.comment_id)


class DishPreference(models.Model):
    PREFERENCE_CHOICES = [
        ('favorite', '收藏'),
        ('blocked', '拉黑'),
    ]
    
    preference_id = models.AutoField(primary_key=True, verbose_name='偏好编号')
    customer = models.ForeignKey(Customer, models.CASCADE, verbose_name='顾客')
    dish = models.ForeignKey(Dish, models.CASCADE, verbose_name='菜品')
    preference_type = models.CharField(max_length=10, choices=PREFERENCE_CHOICES, verbose_name='偏好类型')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        ordering = ['-created_at']
        db_table = 'dish_preference'
        verbose_name = "菜品偏好"
        verbose_name_plural = verbose_name
        unique_together = ['customer', 'dish', 'preference_type']

    def __str__(self):
        return f"{self.customer.customer_name} - {self.dish.dish_name} - {self.get_preference_type_display()}"
