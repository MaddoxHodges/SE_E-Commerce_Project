from django.utils import timezone
from django.core.mail import send_mail
from .models import RSSSubscriber
from products.models import Product  # adjust if your Product app is named differently

def send_rss_updates():
    subscribers = RSSSubscriber.objects.all()
    now = timezone.now()

    for s in subscribers:
        last = s.last_sent or (now - timezone.timedelta(days=365))

        # Find new products since last email
        new_products = Product.objects.filter(created_at__gt=last)

        if new_products.exists():
            body = "New Products on BurnLab:\n\n"
            for p in new_products:
                body += f"- {p.title}\n"

            # Send email to subscriber
            send_mail(
                subject="BurnLab Product Updates",
                message=body,
                from_email="burnlabNotifications@gmail.com",  # your Gmail
                recipient_list=[s.email],
                fail_silently=True,
            )

            # Update last sent time
            s.last_sent = now
            s.save()
