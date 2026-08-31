from django.urls import path

from . import views


app_name = "billing"


urlpatterns = [
    path(
        "",
        views.billing_page,
        name="billing",
    ),
    path(
        "invoice/<uuid:purchase_id>/",
        views.invoice,
        name="invoice",
    ),
    path(
        "purchases/",
        views.customer_purchases,
        name="customer_purchases",
    ),

    path(
        "purchases/<uuid:purchase_id>/",
        views.purchase_detail,
        name="purchase_detail",
    ),
]