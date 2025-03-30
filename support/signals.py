from django.db.models.signals import post_save
from django.dispatch import receiver
from fcm_django.models import FCMDevice
from firebase_admin.messaging import AndroidConfig, AndroidNotification, Message
from firebase_admin.messaging import Notification as FCM_Notification

from support.models import InquiryAnswer, Notice, Notification


@receiver(post_save, sender=Notification)
def create_notification_instance(sender, instance, created, **kwargs):
    if created:
        # You can still use .filter() or any methods that return QuerySet (from the chain)
        devices = FCMDevice.objects.filter(user=instance.user)
        # send_message parameters include: message, dry_run, app
        # (message = messaging.Message( notification = messaging.Notification( title='my app', body='my message here' ), android=messaging.AndroidConfig( priority='high', notification=messaging.AndroidNotification( sound='default' ), ), apns=messaging.APNSConfig( payload=messaging.APNSPayload( aps=messaging.Aps( sound='default' ), ), ), data=data, topic='all', ))
        for device in devices:
            if device.type == "android":
                # print("here")
                device.send_message(
                    Message(
                        # notification=FCM_Notification(
                        #     title=instance.title, body=instance.body
                        # ),
                        android=AndroidConfig(
                            notification=AndroidNotification(
                                title=instance.title,
                                body=instance.body,
                                # sound='default',
                                # default_sound=True,
                                # color="#d234eb",
                                # default_vibrate_timings=True,
                                # default_light_settings=True,
                                # image="https://img.icons8.com/?size=50&id=xZiTPdO57ltQ&format=png&color=000000",
                                # sticky=True,
                                # notification_count=10
                            ),
                            # collapse_key="New",
                            # ttl=2,
                        ),
                        # topic="New",
                        data={
                            "title": instance.title,
                            "body": instance.body,
                            "type": instance.notification_type,
                        },
                    )
                )
            else:
                device.send_message(
                    Message(
                        notification=FCM_Notification(
                            title=instance.title, body=instance.body
                        ),
                        # topic="New",
                        data={
                            "title": instance.title,
                            "body": instance.body,
                            "type": instance.notification_type,
                        },
                    )
                )
        # devices.send_message(
        #     Message(
        #         notification=FCM_Notification(title=instance.title, body=instance.body),
        #         # topic="New",
        #     )
        # )


@receiver(post_save, sender=Notice)
def create_notice_instance(sender, instance, created, **kwargs):
    if created:
        # You can still use .filter() or any methods that return QuerySet (from the chain)
        devices = FCMDevice.objects.all()
        # send_message parameters include: message, dry_run, app
        devices.send_message(
            Message(
                notification=FCM_Notification(
                    title=instance.title, body="You have a new notice"
                ),
                # topic="New",
                data={
                    "title": instance.title,
                    "body": instance.body,
                    "type": "notice",
                },
            )
        )


@receiver(post_save, sender=InquiryAnswer)
def create_inquery_answer_instance(sender, instance, created, **kwargs):
    if created:
        # You can still use .filter() or any methods that return QuerySet (from the chain)
        devices = FCMDevice.objects.filter(user=instance.inquiry.user)
        instance.inquiry.is_answered = True
        instance.inquiry.save(update_fields=["is_answered"])
        # send_message parameters include: message, dry_run, app
        devices.send_message(
            Message(
                notification=FCM_Notification(
                    title="You have got a solution",
                    body="Your inquiry has just been answered. Check Now.",
                ),
                # topic="New",
                data={
                    "title": instance.title,
                    "body": instance.body,
                    "type": "notice",
                },
            )
        )
