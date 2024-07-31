import base64
from django.conf import settings
from payments.serializers import PazyeJustPaySerializer

# Create your views here.
import json
from paycomuz import Paycom
from payments.models import SpeaklishOrder, PaymentCallbackUrl, PayzeTransactions
from payments.serializers import SpeaklishOrderCreateSerializer, SpeaklishOrderOutputSerializer
from payments.payze_utils import get_order_url
from api.utils.logger import logged

from payments.paycom import MerchantAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework.views import APIView
from httpx import Client
from redis import Redis
from dataclasses import dataclass
from drf_yasg.utils import swagger_auto_schema


@dataclass
class PaymeTransaction:
    amount: float
    order_key: int


class CheckOrder(Paycom):
    redis = Redis(host=settings.AZURE_REDIS_HOST, port=settings.AZURE_REDIS_PORT,
                  password=settings.AZURE_REDIS_PASSWORD, ssl=True, decode_responses=True)

    def check_order(self, amount, account, *args, **kwargs):
        order_id = account['order_id']
        try:
            order = SpeaklishOrder.objects.get(order_id=order_id)
            logged(f'Checking order {order.order_id} with amount {amount}', 'info')
            if (order.price * order.session_quantity * 100) != amount:
                return self.INVALID_AMOUNT
            return self.ORDER_FOUND
        except SpeaklishOrder.DoesNotExist:
            return self.ORDER_NOT_FOND

    def successfully_payment(self, account, transaction, *args, **kwargs):
        order = SpeaklishOrder.objects.get(order_id=transaction.order_key)
        order.status = 'paid'
        order.save()
        msg = {
            'en': "Payment was successfully completed and now You have {0} sessions for unlimited time ✅"
                  f"\n\nThank You for choosing us! 🙂 \n@SpeaklishBot"
        }

        ### send notification to user
        user_id = order.user_id

        inc_success: int = self.redis.incrby(f'premium:{user_id}', order.session_quantity)
        if inc_success == -1:
            self.redis.set(f'premium:{user_id}', order.session_quantity)
            inc_success = order.session_quantity
        logged(f'{user_id} paid for {transaction.amount} ')

        client = Client()
        try:
            response = client.post(
                'https://api.telegram.org/bot{0}/sendMessage'.format(settings.TELEGRAM_BOT_TOKEN),
                data={
                    'chat_id': order.user_id,
                    'text': msg['en'].format(inc_success)
                }
            )
            response.raise_for_status()
        except Exception as e:
            logged(f'Error while sending success payment message to {order.user_id}, {e}', 'error')

        try:
            callback_url = PaymentCallbackUrl.objects.filter(organization__school__username__exact=order.organization)

            logged(f'Callback url for {order.organization} is {callback_url}', 'info')
            if callback_url.exists():
                callback_url = callback_url.first()

                response = client.post(
                    callback_url.callback_url,
                    params={
                        'order_id': order.order_id,
                        'user_id': order.user_id,
                        'amount': int(order.price * order.session_quantity),
                        'session_counts': order.session_quantity,
                        # 'status': 'paid'
                    }
                )

                response.raise_for_status()
                logged(f'Callback to {callback_url.callback_url} was successful', 'info')

        except Exception as e:
            logged(e, 'error')

    def cancel_payment(self, account, transaction, *args, **kwargs):
        order = SpeaklishOrder.objects.get(order_id=transaction.order_key)
        order.status = 'cancelled'
        order.save()
        logged(f'Order {order.order_id} was cancelled', 'info')


class PaymeView(MerchantAPIView):
    VALIDATE_CLASS = CheckOrder


class PaymeGenerateLinkView(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [BasicAuthentication, ]
    serializer_class = SpeaklishOrderCreateSerializer
    PAYME_ID = settings.PAYCOM_SETTINGS['KASSA_ID']
    PAYME_ACCOUNT = 'order_id'

    @swagger_auto_schema(request_body=SpeaklishOrderCreateSerializer,
                         responses={200: SpeaklishOrderOutputSerializer})
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user_id = data.get('user_id')
        price = data.get('price')
        currency = data.get('currency', 'UZS')
        session_quantity = data.get('session_quantity')
        organization = request.user.username
        fake = data.get('fake', False)
        if not all([user_id, price, session_quantity]):
            return Response({'error': 'user_id, price, session_quantity are required'}, status=400)
        overlap_by = 10_700
        order = SpeaklishOrder.objects.create(
            order_id=SpeaklishOrder.generate_order_id() + overlap_by,
            user_id=user_id,
            price=price,
            currency=currency,
            session_quantity=session_quantity,
            status='pending',
            organization=organization
        )
        PAYME_URL = 'https://checkout.paycom.uz'
        if fake:
            PAYME_URL = 'https://checkout.test.paycom.uz'
        GENERATED_PAY_LINK: str = "{payme_url}/{encode_params}"
        PARAMS: str = 'm={payme_id};ac.{payme_account}={order_id};a={amount};c={callback}'

        PARAMS = PARAMS.format(
            payme_id=self.PAYME_ID,
            payme_account=self.PAYME_ACCOUNT,
            order_id=order.order_id,
            amount=order.price * order.session_quantity * 100,
            callback=''
        )

        encode_params = base64.b64encode(PARAMS.encode("utf-8"))
        url = GENERATED_PAY_LINK.format(
            payme_url=PAYME_URL,
            encode_params=str(encode_params, 'utf-8')
        )
        res = {'order_id': order.order_id, 'amount': order.price * order.session_quantity,
               'session_quantity': order.session_quantity, 'price': order.price, 'url': url}
        return Response(res)


class PayzeWebHookgate(APIView):
    permission_classes = []
    authentication_classes = []
    serializer_class = PazyeJustPaySerializer

    def post(self, request):
        logged(request.data, 'info')
        # data = webhook.JustPaySerializer.model_validate_json(request.data)
        serializer = PazyeJustPaySerializer(data=request.data)
        if not serializer.is_valid():
            logged(serializer.errors, 'error')
            return Response({
                "is_webhook_accepted": False,
            })

        data = serializer.validated_data

        order_id = data['Metadata']['Order']['OrderId']
        payment_status = data['PaymentStatus']
        if payment_status == 'Captured':
            amount = data['FinalAmount']
            try:
                order = SpeaklishOrder.objects.get(order_id=order_id)
                order.status = 'paid'
                order.save()
                PayzeTransactions(
                    order_id=order_id,
                    transaction_id=data['IdempotencyKey'],
                    user_id=order.user_id,
                    amount=amount,
                    currency=data['Currency'],
                    status='paid',
                    webhook_response=data
                ).save()
            except SpeaklishOrder.DoesNotExist:
                PayzeTransactions(
                    order_id=order_id,
                    transaction_id=data['IdempotencyKey'],
                    user_id=1,
                    amount=amount,
                    currency=data['Currency'],
                    status='paid',
                    webhook_response=data
                ).save()
                return Response({
                    "is_webhook_accepted": True,
                })

            payze_trans = PaymeTransaction(amount=amount, order_key=int(order_id))
            CheckOrder().successfully_payment(
                account=1,
                transaction=payze_trans,
            )
        if payment_status == 'Draft':
            try:
                order = SpeaklishOrder.objects.get(order_id=int(order_id))
                order.status = 'opened'
                order.save()
            except SpeaklishOrder.DoesNotExist:
                PayzeTransactions(
                    order_id=order_id,
                    transaction_id=data['IdempotencyKey'],
                    user_id=1,
                    amount=data['Amount'],
                    currency=data['Currency'],
                    status='cancelled',
                    webhook_response=data
                ).save()
                return Response({
                    "is_webhook_accepted": True,
                })

        return Response({
            "is_webhook_accepted": True,
        })


    def get(self, request):
        logged(request.GET, 'info')
        return Response({
            "is_webhook_accepted": True,
        })


class PayzeGenerateLink(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [BasicAuthentication, ]
    PAYME_ID = settings.PAYCOM_SETTINGS['KASSA_ID']
    PAYME_ACCOUNT = 'order_id'
    serializer_class = SpeaklishOrderCreateSerializer

    @swagger_auto_schema(request_body=SpeaklishOrderCreateSerializer,
                         responses={200: SpeaklishOrderOutputSerializer})
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        logged(data, 'info')
        user_id = data.get('user_id')
        price = data.get('price')
        currency = data.get('currency', 'UZS')
        session_quantity = data.get('session_quantity')
        organization = request.user.username
        if not all([user_id, price, session_quantity]):
            return Response({'error': 'user_id, price, session_quantity are required'}, status=400)
        order = SpeaklishOrder.objects.create(
            order_id=SpeaklishOrder.generate_order_id() + 10_700,  # this is for payze overlap to avoid conflicts
            user_id=user_id,
            price=price,
            currency=currency,
            session_quantity=session_quantity,
            status='pending',
            organization=organization
        )
        url = get_order_url(str(order.order_id), currency=currency, amount=price * session_quantity)
        res = {'order_id': order.order_id, 'amount': order.price * order.session_quantity,
               'session_quantity': order.session_quantity, 'price': order.price, 'url': url}
        return Response(res)
