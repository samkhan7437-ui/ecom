from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name='ShopHome'),
    path("about/", views.about, name='AboutUs'),
    path("contact/", views.contact, name='ContactUs'),
    path("tracker/", views.tracker, name='TrackingStatus'),
    path("search/", views.search, name='Search'),
    path("products/<int:myid>/", views.productview, name='ProductView'),
    path("productview/", views.productview, name='ProductViewLegacy'),
    path("checkout/", views.checkout, name='Checkout'),
    
    # Operations & Inventory Control
    path("admin-dashboard/", views.admin_dashboard, name='AdminDashboard'),
    path("inventory/", views.admin_dashboard, name='InventoryHub'),
    path("admin-dashboard/add/", views.admin_add_product, name='AdminAddProduct'),
    path("admin-dashboard/edit/<int:product_id>/", views.admin_edit_product, name='AdminEditProduct'),
    path("admin-dashboard/delete/<int:product_id>/", views.admin_delete_product, name='AdminDeleteProduct'),
    path("admin-dashboard/quick-update/", views.admin_quick_update, name='AdminQuickUpdate'),
]
