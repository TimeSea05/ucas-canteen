# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True, verbose_name='顾客编号')
    customer_name = models.CharField(max_length=20, verbose_name='顾客昵称')
    customer_password = models.CharField(max_length=20, verbose_name='顾客密码')
    customer_tel = models.CharField(max_length=11, verbose_name="顾客电话")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name="送餐地址")

    class Meta:
        ordering = ['customer_id']
        db_table = 'customer'
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.customer_name

