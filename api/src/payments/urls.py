from django.urls import path
from django.shortcuts import redirect

from .views import PaymeView, PaymeGenerateLinkView, PayzeWebHookgate, PayzeGenerateLink

urlpatterns = [
    path('payme/', PaymeView.as_view(), name='payme'),
    path('payme/generate_link/', PaymeGenerateLinkView.as_view(), name='generate_link'),
    path('payze/webhook/success/', PayzeWebHookgate.as_view(), name='payze_webhook_success'),
    path('payze/webhook/error/', lambda request: redirect(
        'https://t.me/speaklishbot?start=payze_error'),
                                        name='payze_webhook_error'),
    path('payze/webhook/redirect/', lambda request: redirect(
        'https://t.me/speaklishbot?start=payze_success'),
                                        name='payze_webhook_redirect'),
    path('payze/generate_link/', PayzeGenerateLink.as_view(), name='payze_generate_link'),

]