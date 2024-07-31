from django.contrib import admin
from paycomuz.models import Transaction
from .models import SpeaklishOrder, PaymentCallbackUrl, PayzeTransactions

# Register your models here.

admin.site.unregister(Transaction)


@admin.register(SpeaklishOrder)
class SpeaklishOrderAdmin(admin.ModelAdmin):
    list_display = (
    'order_id', 'user_id', 'price', 'currency', 'session_quantity', 'status', 'organization', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'user_id')


@admin.register(PaymentCallbackUrl)
class PaymentCallbackUrlAdmin(admin.ModelAdmin):
    list_display = ('callback_url', 'organization', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('organization',)

@admin.register(PayzeTransactions)
class PayzeTransactionsAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'transaction_id', 'user_id', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'transaction_id', 'user_id')