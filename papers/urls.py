from django.urls import path

from papers import views

urlpatterns = [
    path('', views.paper_list, name="paper-list"),
    path('paper/create/', views.paper_create, name="paper-create"),
    path('paper/<int:pk>/', views.paper_detail, name="paper-detail"),
    path('paper/<int:pk>/<str:language_code>/', views.paper_translation_detail, name="paper-translation-detail"),
    path('paper/<int:pk>/<str:language_code>/edit/', views.paper_edit, name="paper-translation-edit"),
    path('amendmends/<int:pk>/', views.amendmend_detail, name="amendmend-detail"),
    path('amendmends/<int:pk>/edit/', views.amendmend_edit, name="amendmend-edit"),
]
