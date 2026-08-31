from django.contrib import messages
from django.shortcuts import redirect, render , get_object_or_404
from .models import Purchase , Denomination
from .forms import (
    BillingForm,
    BillingItemFormSet,
    DenominationFormSet,
)
from .services import (
    BillingError,
    create_purchase,
)
from django_q.tasks import async_task

def billing_page(request):
    """
    Display the billing form and process new purchases.
    """

    if request.method == "POST":
        billing_form = BillingForm(request.POST)
        item_formset = BillingItemFormSet(
            request.POST,
            prefix="items",
        )
        denomination_formset = DenominationFormSet(
            request.POST,
            prefix="denominations",
        )

        if (
            billing_form.is_valid()
            and item_formset.is_valid()
            and denomination_formset.is_valid()
        ):
            items = [
                {
                    "product_id": form.cleaned_data["product"].id,
                    "quantity": form.cleaned_data["quantity"],
                }
                for form in item_formset
                if form.cleaned_data
            ]

            denominations = [
                {
                    "value": (
                        form.cleaned_data["denomination"].value
                    ),
                    "available_count": (
                        form.cleaned_data["available_count"]
                    ),
                }
                for form in denomination_formset
                if form.cleaned_data
            ]

            try:
                purchase = create_purchase(
                    customer_email=(
                        billing_form.cleaned_data[
                            "customer_email"
                        ]
                    ),
                    items=items,
                    paid_amount=(
                        billing_form.cleaned_data[
                            "paid_amount"
                        ]
                    ),
                    denominations=denominations,
                )

            except BillingError as exc:
                messages.error(request, str(exc))

            else:
                async_task(
                    "billing.tasks.send_invoice_email",
                    str(purchase.id),
                )

                return redirect(
                    "billing:invoice",
                    purchase_id=purchase.id,
                )

    else:
        billing_form = BillingForm()

        item_formset = BillingItemFormSet(
            prefix="items",
        )

        denomination_formset = DenominationFormSet(
            prefix="denominations",
            initial=[
                {
                    "denomination": denomination.id,
                    "available_count": 0,
                }
                for denomination in Denomination.objects.order_by("-value")
            ],
        )

    
    return render(
        request,
        "billing/billing_form.html",
        {
            "billing_form": billing_form,
            "item_formset": item_formset,
            "denomination_formset": denomination_formset,
        },
    )


def invoice(request, purchase_id):
    purchase = get_object_or_404(
        Purchase.objects
        .select_related("customer")
        .prefetch_related(
            "items__product",
            "denominations__denomination",
        ),
        id=purchase_id,
    )

    return render(
        request,
        "billing/invoice.html",
        {
            "purchase": purchase,
        },
    )

def customer_purchases(request):
    """
    Display previous purchases for a customer.
    """

    customer_email = request.GET.get("email", "").strip()

    purchases = Purchase.objects.none()

    if customer_email:
        purchases = (
            Purchase.objects
            .select_related("customer")
            .filter(customer__email__iexact=customer_email)
        )

    return render(
        request,
        "billing/customer_purchases.html",
        {
            "customer_email": customer_email,
            "purchases": purchases,
        },
    )


def purchase_detail(request, purchase_id):
    """
    Display details of a previous purchase.
    """

    purchase = get_object_or_404(
        Purchase.objects
        .select_related("customer")
        .prefetch_related(
            "items__product",
            "denominations__denomination",
        ),
        id=purchase_id,
    )

    return render(
        request,
        "billing/purchase_detail.html",
        {
            "purchase": purchase,
        },
    )