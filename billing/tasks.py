from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from .models import Purchase



def send_invoice_email(purchase_id):
    """
    Send the invoice email for a completed purchase.
    """

    purchase = (
        Purchase.objects
        .select_related("customer")
        .prefetch_related(
            "items__product",
            "denominations__denomination",
        )
        .get(id=purchase_id)
    )

    subject = f"Invoice for Purchase {purchase.id}"

    context = {
        "purchase": purchase,
    }

    html_content = render_to_string(
        "billing/invoice_email.html",
        context,
    )

    text_content = render_to_string(
        "billing/invoice_email.txt",
        context,
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[purchase.customer.email],
    )

    email.attach_alternative(
        html_content,
        "text/html",
    )

    email.send()