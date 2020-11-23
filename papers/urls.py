"""
Urls
"""
from django.contrib.auth import views as auth_views
from django.urls import path

from papers import views

urlpatterns = [
    path("", views.paper_list, name="paper-list"),
    path("paper/create/", views.paper_create, name="paper-create"),
    path("paper/<int:paper_pk>/", views.paper_detail, name="paper-detail"),
    path(
        "paper/<int:paper_pk>/<str:language_code>/",
        views.paper_translation_detail,
        name="paper-translation-detail",
    ),
    path(
        "paper/<int:paper_pk>/<str:language_code>/create-amendmend/",
        views.paper_edit,
        name="create-amendmend",
    ),
    path(
        "paper/<int:paper_pk>/<str:language_code>/update/",
        views.translation_update,
        name="paper-translation-update",
    ),
    path(
        "amendmends/<int:amendment_pk>/",
        views.amendmend_detail,
        name="amendmend-detail",
    ),
    path(
        "amendmends/<int:amendment_pk>/edit/",
        views.amendmend_edit,
        name="amendmend-edit",
    ),
    path("members/login/", auth_views.LoginView.as_view()),
    path("members/logout/", auth_views.LogoutView.as_view()),
    path("members/profile/", views.members_profile),
    path("comments/<int:comment_pk>/like/", views.like_comment, name="comment_like"),
]
