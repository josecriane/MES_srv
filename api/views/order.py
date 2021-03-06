from django.contrib.auth.models import User, AnonymousUser

from rest_framework import viewsets
from rest_framework.reverse import reverse
from rest_framework.response import Response

from api.models import Device, Order, OrderType
from api.serializers import OrderSerializer, OrderTypeSerializer, DeviceOrderSerializer
from api.permissions import IsOwner

from gcm_connection.message import Message

from utils.hash import generate_sha256 

class OrderViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsOwner,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def create(self, request):
        order = request.data
        user = request.user
        is_ok = True
        devices = []
        for device_id in order.get("devices"):
            device = Device.objects.get(id=device_id)
            ok_serializer, serializer = self._single_create(user, device, order)
            is_ok = is_ok and ok_serializer
            devices.append(device)
            if not is_ok:
                break

        if is_ok:
            order = serializer.save()
            for device in devices:
                device_order = DeviceOrderSerializer(data={'order':order.id,'device':str(device.id)});
                if device.configured and device_order.is_valid(): 
                    Message(device.tokenGCM, serializer.data).send_message()
                    device_order.save()
            return Response({'result':'ok'})
        else:
            return Response(status=400)

    def _single_create(self, user, device, order):
        if user.id == device.owner.id:
            order["owner"] = user.id
            serializer = OrderSerializer(data=order)
            print serializer
            print serializer.is_valid()
            if serializer.is_valid():
                return True, serializer
            else:
                return False, None
        else:
            return False, None

    def list(self, request):
        try:
            owner_elements = Order.objects.filter(owner=request.user.id)
        except:
            owner_elements = []

        page = self.paginate_queryset(owner_elements)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(owner_elements, many=True)
        return Response(serializer.data)

class OrderTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrderType.objects.all()
    serializer_class = OrderTypeSerializer