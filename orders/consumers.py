import json
from channels.generic.websocket import AsyncWebsocketConsumer


class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.order_group = f'order_{self.order_id}'

        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
            return

        from orders.models import Order
        try:
            order = await Order.objects.aget(id=self.order_id)
        except Order.DoesNotExist:
            await self.close()
            return

        if not user.is_staff and order.user_id != user.id:
            await self.close()
            return

        await self.channel_layer.group_add(self.order_group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.order_group, self.channel_name)

    async def order_status_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'order_status_update',
            'order_id': event['order_id'],
            'status': event['status'],
            'tracking_number': event.get('tracking_number', ''),
        }))
