# Create your models here.
import uuid

from django.db import models


class Product(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    product_id = models.CharField(
        max_length=50,
        unique=True,
    )
    name = models.CharField(
        max_length=255,
    )
    stock = models.PositiveIntegerField(
        default=0,
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    tax_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.product_id} - {self.name}"


class Customer(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    email = models.EmailField(
        unique=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.email


class Purchase(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="purchases",
    )
    total_without_tax = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    total_tax = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    rounded_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    balance_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Purchase #{self.pk}"


class PurchaseItem(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="purchase_items",
    )
    product_name = models.CharField(
        max_length=255,
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    quantity = models.PositiveIntegerField()
    tax_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    purchase_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class Denomination(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    value = models.PositiveIntegerField(
        unique=True,
    )

    class Meta:
        ordering = ["-value"]

    def __str__(self):
        return str(self.value)


class PurchaseDenomination(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="denominations",
    )
    denomination = models.ForeignKey(
        Denomination,
        on_delete=models.PROTECT,
    )
    available_count = models.PositiveIntegerField(
        default=0,
    )
    dispensed_count = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["purchase", "denomination"],
                name="unique_purchase_denomination",
            ),
        ]

    def __str__(self):
        return f"{self.denomination.value} - {self.available_count}"