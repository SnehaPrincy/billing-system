# Register your models here.
from django.contrib import admin

from .models import (
    Customer,
    Denomination,
    Product,
    Purchase,
    PurchaseDenomination,
    PurchaseItem,
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "product_id",
        "name",
        "stock",
        "unit_price",
        "tax_percentage",
        "created_at",
    )
    search_fields = (
        "product_id",
        "name",
    )
    list_filter = (
        "tax_percentage",
    )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "created_at",
    )
    search_fields = ("email",)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "total_amount",
        "paid_amount",
        "balance_amount",
        "created_at",
    )
    search_fields = (
        "customer__email",
    )
    list_filter = (
        "created_at",
    )


@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = (
        "product_name",
        "quantity",
        "unit_price",
        "tax_percentage",
        "total_price",
    )
    search_fields = (
        "product_name",
    )


@admin.register(Denomination)
class DenominationAdmin(admin.ModelAdmin):
    list_display = ("value",)


@admin.register(PurchaseDenomination)
class PurchaseDenominationAdmin(admin.ModelAdmin):
    list_display = (
        "purchase",
        "denomination",
        "available_count",
        "dispensed_count",
    )