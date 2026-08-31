from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP

from django.db import transaction

from .models import (
    Customer,
    Denomination,
    Product,
    Purchase,
    PurchaseDenomination,
    PurchaseItem,
)


MONEY_QUANTIZER = Decimal("0.01")


class BillingError(Exception):
    """Base exception for billing-related errors."""


class InsufficientStockError(BillingError):
    """Raised when requested quantity exceeds available stock."""


class InsufficientPaymentError(BillingError):
    """Raised when customer payment is less than the payable amount."""


class InsufficientDenominationsError(BillingError):
    """Raised when exact change cannot be provided."""


def money(value: Decimal) -> Decimal:
    """
    Normalize a Decimal monetary value to two decimal places.
    """
    return value.quantize(
        MONEY_QUANTIZER,
        rounding=ROUND_HALF_UP,
    )


def calculate_item(
    unit_price: Decimal,
    quantity: int,
    tax_percentage: Decimal,
) -> dict:
    """
    Calculate pricing information for a single purchase item.
    """

    purchase_price = money(
        unit_price * quantity
    )

    tax_amount = money(
        purchase_price * tax_percentage / Decimal("100")
    )

    total_price = money(
        purchase_price + tax_amount
    )

    return {
        "purchase_price": purchase_price,
        "tax_amount": tax_amount,
        "total_price": total_price,
    }


def calculate_bill(items: list[dict]) -> dict:
    """
    Calculate totals for the complete bill.

    The final payable amount is rounded down to the
    nearest whole currency unit as specified in the
    provided assessment example.
    """

    total_without_tax = money(
        sum(
            (item["purchase_price"] for item in items),
            Decimal("0.00"),
        )
    )

    total_tax = money(
        sum(
            (item["tax_amount"] for item in items),
            Decimal("0.00"),
        )
    )

    total_amount = money(
        total_without_tax + total_tax
    )

    rounded_amount = total_amount.quantize(
        Decimal("1"),
        rounding=ROUND_DOWN,
    )

    return {
        "total_without_tax": total_without_tax,
        "total_tax": total_tax,
        "total_amount": total_amount,
        "rounded_amount": rounded_amount,
    }


def calculate_change(
    change_amount: Decimal,
    denominations: list[dict],
) -> dict:
    """
    Calculate exact change while respecting available
    denomination counts.
    """

    change_amount = money(change_amount)

    if change_amount < Decimal("0.00"):
        raise BillingError(
            "Change amount cannot be negative."
        )

    target = int(change_amount)

    if target == 0:
        return {}

    dp = [None] * (target + 1)
    dp[0] = {}

    for denomination in sorted(
        denominations,
        key=lambda item: item["value"],
        reverse=True,
    ):
        value = denomination["value"]
        available_count = denomination["available_count"]

        if value <= 0 or available_count <= 0:
            continue

        for _ in range(available_count):
            for amount in range(
                target,
                value - 1,
                -1,
            ):
                previous = dp[amount - value]

                if previous is None:
                    continue

                if dp[amount] is None:
                    combination = previous.copy()

                    combination[value] = (
                        combination.get(value, 0) + 1
                    )

                    dp[amount] = combination

    if dp[target] is None:
        raise InsufficientDenominationsError(
            "Exact change cannot be provided "
            "with the available denominations."
        )

    return dp[target]


@transaction.atomic
def create_purchase(
    *,
    customer_email: str,
    items: list[dict],
    paid_amount: Decimal,
    denominations: list[dict],
) -> Purchase:
    """
    Create a complete purchase atomically.

    The operation:
    1. Creates or retrieves the customer.
    2. Locks requested product rows.
    3. Validates stock.
    4. Calculates item prices and tax.
    5. Calculates the complete bill.
    6. Validates payment.
    7. Calculates change.
    8. Creates the Purchase.
    9. Creates PurchaseItems.
    10. Updates product stock.
    11. Stores denomination usage.
    """

    if not items:
        raise BillingError(
            "At least one product is required."
        )

    paid_amount = money(paid_amount)

    if paid_amount < Decimal("0.00"):
        raise BillingError(
            "Paid amount cannot be negative."
        )

    # -------------------------------------------------
    # Customer
    # -------------------------------------------------

    customer, _ = Customer.objects.get_or_create(
        email=customer_email,
    )

    # -------------------------------------------------
    # Product IDs
    # -------------------------------------------------

    product_ids = [
        item["product_id"]
        for item in items
    ]

    if len(product_ids) != len(set(product_ids)):
        raise BillingError(
            "The same product cannot be added more than once."
        )

    # -------------------------------------------------
    # Lock products for concurrent purchases
    # -------------------------------------------------

    locked_products = (
        Product.objects
        .select_for_update()
        .filter(id__in=product_ids)
    )

    products_by_id = {
        product.id: product
        for product in locked_products
    }

    if len(products_by_id) != len(product_ids):
        raise BillingError(
            "One or more selected products do not exist."
        )

    # -------------------------------------------------
    # Calculate purchase items
    # -------------------------------------------------

    calculated_items = []

    for item in items:
        product_id = item["product_id"]
        quantity = item["quantity"]

        product = products_by_id[product_id]

        if quantity <= 0:
            raise BillingError(
                "Product quantity must be greater than zero."
            )

        if quantity > product.stock:
            raise InsufficientStockError(
                f"Insufficient stock for "
                f"{product.product_id}. "
                f"Available: {product.stock}, "
                f"Requested: {quantity}."
            )

        calculation = calculate_item(
            unit_price=product.unit_price,
            quantity=quantity,
            tax_percentage=product.tax_percentage,
        )

        calculated_items.append(
            {
                "product": product,
                "quantity": quantity,
                "calculation": calculation,
            }
        )

    # -------------------------------------------------
    # Bill calculation
    # -------------------------------------------------

    bill = calculate_bill(
        [
            item["calculation"]
            for item in calculated_items
        ]
    )

    # -------------------------------------------------
    # Payment validation
    # -------------------------------------------------

    if paid_amount < bill["rounded_amount"]:
        raise InsufficientPaymentError(
            f"Insufficient payment. "
            f"Amount payable: "
            f"{bill['rounded_amount']:.2f}, "
            f"amount received: "
            f"{paid_amount:.2f}."
        )

    change_amount = money(
        paid_amount - bill["rounded_amount"]
    )

    # -------------------------------------------------
    # Change calculation
    # -------------------------------------------------

    dispensed_denominations = calculate_change(
        change_amount,
        denominations,
    )

    # -------------------------------------------------
    # Create purchase
    # -------------------------------------------------

    purchase = Purchase.objects.create(
        customer=customer,
        total_without_tax=bill["total_without_tax"],
        total_tax=bill["total_tax"],
        total_amount=bill["total_amount"],
        rounded_amount=bill["rounded_amount"],
        paid_amount=paid_amount,
        balance_amount=change_amount,
    )

    # -------------------------------------------------
    # Create purchase items + update stock
    # -------------------------------------------------

    for item in calculated_items:
        product = item["product"]
        quantity = item["quantity"]
        calculation = item["calculation"]

        PurchaseItem.objects.create(
            purchase=purchase,
            product=product,
            product_name=product.name,
            unit_price=product.unit_price,
            quantity=quantity,
            tax_percentage=product.tax_percentage,
            tax_amount=calculation["tax_amount"],
            purchase_price=calculation["purchase_price"],
            total_price=calculation["total_price"],
        )

        product.stock -= quantity
        product.save(
            update_fields=[
                "stock",
                "updated_at",
            ]
        )

    # -------------------------------------------------
    # Store denomination information
    # -------------------------------------------------

    denomination_objects = Denomination.objects.filter(
        value__in=[
            denomination["value"]
            for denomination in denominations
        ]
    )

    denomination_by_value = {
        denomination.value: denomination
        for denomination in denomination_objects
    }

    for denomination in denominations:
        value = denomination["value"]
        available_count = denomination["available_count"]

        denomination_object = denomination_by_value.get(
            value
        )

        if denomination_object is None:
            raise BillingError(
                f"Invalid denomination: {value}"
            )

        PurchaseDenomination.objects.create(
            purchase=purchase,
            denomination=denomination_object,
            available_count=available_count,
            dispensed_count=dispensed_denominations.get(
                value,
                0,
            ),
        )

    return purchase