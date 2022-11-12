from django.urls import path
from .import views
app_name="sale"
urlpatterns=[
    path("",views.index_view,name="index"),
    path("create/",views.create_view,name="create"),
    path("load/subcategories/",views.load_subcategories,name='load-subcategories'),
    path("create-brand/",views.create_brand_view,name="create-brand"),

    path("update/<slug>/",views.update_view,name='update'),
    path("delete/", views.delete_view, name="delete"),


    path("wish/", views.user_wishlist_view, name="wish"),
    path("wishlist/", views.wishlist_product_view, name="wishlist"),


    path("add/basket/", views.add_basket_view, name="add-basket"),
    path("basket/", views.basket_list_view, name="basket"),
   

    path("class/list/",views.ProductListView.as_view(),name="class/list")

]