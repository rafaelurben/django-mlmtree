from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.urls import reverse, reverse_lazy

from . import views

#######################

app_name = 'mlmtree'

urlpatterns = [
    # Main
    path('', views.home, name="home"),
    path('t/<object_id>/', views.tree_view, name="tree-view"),

    # API
    path('api/t/<tree_id>/p/<int:person_id>/get', 
         views.api_person_get,
         name="api-person-get"),
    path('api/t/<tree_id>/p/<int:person_id>/get/teamcount', 
         views.api_person_get_teamcount,
         name="api-person-get-teamcount"),
    path('api/t/<tree_id>/p/<int:person_id>/createchild',
         views.api_person_createchild,
         name="api-person-createchild"),
    path('api/t/<tree_id>/p/<int:person_id>/update', 
         views.api_person_update,
         name="api-person-update"),
    path('api/t/<tree_id>/p/<int:person_id>/delete',
         views.api_person_delete,
         name="api-person-delete"),

    # Fake static
    # path('manifest.webmanifest', views.manifest, name="manifest"),

    # Login
    path('login/',
         auth_views.LoginView.as_view(
             template_name='mlmtree/login.html',),
         name="login"),

    # Errors

    re_path('^api/.*', views.api_error404, name="api-base"),
    re_path('.*', views.error404),
]
