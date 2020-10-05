from django.urls import path

from papers import views

urlpatterns = [
    path('', views.paper_list, name="paper-list"),
    path('paper/create/', views.paper_create, name="paper-create"),
    path('paper/<int:pk>/', views.paper_detail, name="paper-detail"),
    path('paper/<int:pk>/<str:language_code>/', views.paper_translation_detail, name="paper-translation-detail"),
]
