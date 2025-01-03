from celery import shared_task
from django.contrib.auth import get_user_model
from fcm_django.models import FCMDevice

from notification.send_notification import send_message_notification
from purchase_request.models import PurchaseRequest
import logging

from src.utils import check_and_send_push_notification

logger = logging.getLogger(__name__)

User = get_user_model()


@shared_task
def deactivate_purchase_request(request_id):
    request = PurchaseRequest.objects.get(pk=request_id)
    request.deactivate()
    return 'Request deactivated'


@shared_task
def create_new_offer_notification(user_id, request_id):
    req = PurchaseRequest.objects.get(pk=request_id)
    body = f"Проверьте свое предложение: {req.get_title_for_purchase_request}"
    title = "У вас новое предложение. Проверьте свои заявки"
    return check_and_send_push_notification(title, user_id, body)
