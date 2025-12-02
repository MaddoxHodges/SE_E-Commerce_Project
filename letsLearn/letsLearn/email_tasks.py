from django.utils import timezone
from django.core.mail import send_mail
from .models import RSSSubscriber, Product

def send_rss_updates():
    now = timezone.now()
    subscribers = RSSSubscriber.objects.all()

    for s in subscribers:
        last = s.last_sent or (now - timezone.timedelta(days=365))

        new_products = Product.objects.filter(
            created_at__gt=last,
            status="active",
        ).order_by("created_at")

        if not new_products.exists():
            continue

        body_lines = ["Here are new products since your last update:", ""]
        for p in new_products:
            price = f"${p.price_cents / 100:.2f}"
            body_lines.append(f"{p.title} — {price}")

        body = "\n".join(body_lines)

        send_mail(
            subject="New products in the marketplace",
            message=body,
            from_email="yourgmail@gmail.com",   # same as EMAIL_HOST_USER
            recipient_list=[s.email],
            fail_silently=False,
        )

        s.last_sent = now
        s.save()
