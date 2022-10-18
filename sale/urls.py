from django.urls import path
from .import views
app_name="sale"
urlpatterns=[
    path("",views.index_view,name="index"),
    path("create/",views.create_view,name="create")

    
]