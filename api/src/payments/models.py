from django.db import models
from django.contrib.auth import get_user_model


class SpeaklishOrder(models.Model):
    order_id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField()
    price = models.FloatField()
    currency = models.CharField(max_length=3,
                                choices=[('USD', 'USD'),
                                         ('UZS', 'UZS')],
                                default='UZS')
    session_quantity = models.IntegerField()
    status = models.CharField(max_length=10,
                              choices=[('pending', 'pending'),
                                       ('paid', 'paid'),
                                       ('cancelled', 'cancelled')], )
    organization = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def generate_order_id():
        return SpeaklishOrder.objects.count() + 1


class PaymentCallbackUrl(models.Model):
    callback_url = models.URLField()
    organization = models.ForeignKey('school_api.SchoolProfile', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.callback_url


class PayzeTransactions(models.Model):
    order_id = models.CharField(max_length=100)
    transaction_id = models.CharField(max_length=100)
    user_id = models.BigIntegerField()
    amount = models.FloatField()
    currency = models.CharField(max_length=3,
                                choices=[('USD', 'USD'),
                                         ('UZS', 'UZS')],
                                default='UZS')
    status = models.CharField(max_length=10,
                              choices=[('pending', 'pending'),
                                       ('paid', 'paid'),
                                       ('cancelled', 'cancelled')], )
    webhook_response = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
