from decimal import Decimal

from django import forms
from django.forms import BaseFormSet, formset_factory

from .models import Denomination, Product


class BillingForm(forms.Form):
    customer_email = forms.EmailField(
        label="Customer Email",
        max_length=254,
    )

    paid_amount = forms.DecimalField(
        label="Paid Amount",
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.00"),
    )


class BillingItemForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.none(),
        label="Product",
    )

    quantity = forms.IntegerField(
        label="Quantity",
        min_value=1,
        max_value=100000,
        initial=1,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["product"].queryset = (
            Product.objects
            .filter(stock__gt=0)
            .order_by("name")
        )


class BaseBillingItemFormSet(BaseFormSet):
    """
    Validates the collection of products in a bill.
    """

    def clean(self):
        super().clean()

        if any(self.errors):
            return

        products = []

        for form in self.forms:
            if not form.cleaned_data:
                continue

            if form.cleaned_data.get("DELETE"):
                continue

            product = form.cleaned_data.get("product")

            if product is None:
                continue

            if product in products:
                raise forms.ValidationError(
                    "The same product cannot be added more than once."
                )

            products.append(product)


BillingItemFormSet = formset_factory(
    BillingItemForm,
    formset=BaseBillingItemFormSet,
    extra=1,
    min_num=1,
    validate_min=True,
)


class DenominationForm(forms.Form):
    denomination = forms.ModelChoiceField(
        queryset=Denomination.objects.none(),
        label="Denomination",
    )

    available_count = forms.IntegerField(
        label="Available Count",
        min_value=0,
        max_value=1000000,
        initial=0,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["denomination"].queryset = (
            Denomination.objects
            .order_by("-value")
        )


DenominationFormSet = formset_factory(
    DenominationForm,
    extra=0,
)