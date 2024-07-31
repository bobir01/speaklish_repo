from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers
from .models import SpeaklishOrder, PaymentCallbackUrl


class SpeaklishOrderCreateSerializer(ModelSerializer):
    fake = serializers.BooleanField(default=False)

    class Meta:
        model = SpeaklishOrder
        fields = ['user_id', 'price', 'session_quantity', 'fake', 'currency']
        kwargs = {
            'price': {'required': True},
            'session_quantity': {'required': True},
            'user_id': {'required': True, 'help_text': 'User ID from the system or telegram user id'},
            'currency': {'required': True, 'default': 'UZS'},
        }


class SpeaklishOrderOutputSerializer(ModelSerializer):
    url = serializers.URLField(read_only=True)
    amount = serializers.IntegerField()

    class Meta:
        model = SpeaklishOrder
        fields = ('order_id', 'amount', 'session_quantity', 'price', 'url')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['amount'] = instance.price * instance.session_quantity
        return ret


class PaymentCallbackUrlSerializer(ModelSerializer):
    class Meta:
        model = PaymentCallbackUrl
        fields = '__all__'


#### payze serializers


class OrderSerializer(serializers.Serializer):
    OrderId = serializers.CharField()
    AdvanceContactId = serializers.CharField(allow_null=True)
    OrderItems = serializers.ListField(child=serializers.DictField(allow_null=True))
    UzRegulatoryOrderDetails = serializers.DictField(child=serializers.CharField(allow_null=True), allow_null=True)
    BillingAddress = serializers.DictField(child=serializers.CharField(allow_null=True), allow_null=True)
    ShippingAddress = serializers.DictField(child=serializers.CharField(allow_null=True), allow_null=True)


class ExtraAttributesSerializer(serializers.Serializer):
    Key = serializers.CharField(allow_null=True)
    Value = serializers.CharField(allow_null=True)
    Description = serializers.CharField(allow_null=True)


class RefundSerializer(serializers.Serializer):
    RefundId = serializers.CharField(allow_null=True)
    Status = serializers.CharField(allow_null=True)
    Refundable = serializers.BooleanField(allow_null=True)
    Amount = serializers.FloatField(allow_null=True)
    RequestedAmount = serializers.FloatField(allow_null=True)
    RejectReason = serializers.CharField(allow_null=True)
    RefundDate = serializers.CharField(allow_null=True)
    RefundDateIso = serializers.CharField(allow_null=True)
    Revisions = serializers.ListField(child=serializers.DictField(allow_null=True), allow_null=True)


class MetadataSerializer(serializers.Serializer):
    Channel = serializers.CharField(allow_null=True)
    Order = OrderSerializer()
    ExtraAttributes = serializers.ListField(child=ExtraAttributesSerializer())


class PazyeJustPaySerializer(serializers.Serializer):
    Source = serializers.CharField()
    IdempotencyKey = serializers.CharField()
    PaymentId = serializers.CharField(allow_null=True)
    Type = serializers.CharField(allow_null=True)
    Sandbox = serializers.BooleanField(allow_null=True)
    PaymentStatus = serializers.CharField()
    Amount = serializers.FloatField()
    FinalAmount = serializers.FloatField(allow_null=True)
    Currency = serializers.CharField()
    RRN = serializers.CharField(allow_null=True)
    Commission = serializers.CharField(allow_null=True)
    Preauthorized = serializers.BooleanField(allow_null=True)
    CanBeCaptured = serializers.BooleanField(allow_null=True)
    CreateDate = serializers.IntegerField(allow_null=True)
    CreateDateIso = serializers.DateTimeField(allow_null=True)
    CaptureDate = serializers.IntegerField(allow_null=True)
    CaptureDateIso = serializers.DateTimeField(allow_null=True)
    BlockDate = serializers.CharField(allow_null=True)
    BlockDateIso = serializers.CharField(allow_null=True)
    Token = serializers.CharField(allow_null=True)
    CardMask = serializers.CharField(allow_null=True)
    CardOrigination = serializers.CharField(allow_null=True)
    CardOwnerEntityType = serializers.CharField(allow_null=True)
    CardBrand = serializers.CharField(allow_null=True)
    CardCountry = serializers.CharField(allow_null=True)
    CardHolder = serializers.CharField(allow_null=True)
    ExpirationDate = serializers.CharField(allow_null=True)
    SecureCardId = serializers.CharField(allow_null=True)
    RejectionReason = serializers.CharField(allow_null=True)
    Refund = RefundSerializer()
    Splits = serializers.CharField(allow_null=True)
    Metadata = MetadataSerializer()
    Payer = serializers.DictField(child=serializers.CharField(allow_null=True), allow_null=True)


