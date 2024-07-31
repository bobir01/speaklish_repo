import logging
from typing import Literal

from payze.client import Payze
from payze.param import PayzeOPS
from payze.param import request as payze_req
from django.conf import settings
from httpx import Client

from api.utils.logger import logged

auth_key = settings.PAYZE_KEY
secret = settings.PAYZE_SECRET

ops = PayzeOPS(
    url="https://payze.io",
    auth_token=f"{auth_key}:{secret}",
    hooks=payze_req.Hooks(
        web_hook_gateway="https://api.speaklish.uz/payments/payze/webhook/success/",
        error_redirect_gateway="https://api.speaklish.uz/payments/payze/webhook/error/",
        success_redirect_gateway="https://api.speaklish.uz/payments/payze/webhook/redirect/",
    ),
    timeout=30,
)
payze_client = Payze(ops=ops)


def get_order_url(order_id: str, amount: float, currency: Literal['UZS', 'USD'] = "USD") -> str:
    global payze_client
    metadata = payze_req.Metadata(
        order=payze_req.Order(order_id),
    )

    req_params = payze_req.JustPay(
        amount=amount,
        metadata=metadata,
        idempotency_key=order_id,
        currency=currency,
    )
    logged(f"req_params: {req_params}", 'info')
    try:
        resp = payze_client.just_pay(
            req_params=req_params,
            reason="for_speaklish",
        )
    except Exception as e:
        logged(f"error: {e}", 'error')
        return payze_client.just_pay(
            req_params=req_params,
            reason="for_speaklish",
        ).data.payment.payment_url

    return resp.data.payment.payment_url


http_client = Client(auth=settings.PAYZE_KEY + ':' + settings.PAYZE_SECRET)


def get_payze_order_url(order_id: str, amount: float, currency: Literal['UZS', 'USD'] = "USD") -> str:


    return get_order_url(order_id, amount, currency)