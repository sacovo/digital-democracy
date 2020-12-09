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
    path("newsfeed/", views.newsfeed, name="newsfeed"),
    path(
        "paper/<int:paper_pk>/<str:language_code>/create-amendment/",
        views.paper_edit,
        name="create-amendment",
    ),
    path(
        "paper/<int:paper_pk>/<str:language_code>/update/",
        views.translation_update,
        name="paper-translation-update",
    ),
    path(
        "amendments/<int:amendment_pk>/",
        views.amendment_detail,
        name="amendment-detail",
    ),
    path(
        "amendments/<int:amendment_pk>/edit/",
        views.amendment_edit,
        name="amendment-edit",
    ),
    path("members/login/", auth_views.LoginView.as_view(), name="login"),
    path("members/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "members/change_password/",
        auth_views.PasswordChangeView.as_view(
            success_url="/members/change_password_done/"
        ),
        name="password_change",
    ),
    path(
        "members/change_password_done/",
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path(
        "members/reset_password/",
        auth_views.PasswordResetView.as_view(
            success_url="/members/reset_password_done/"
        ),
        name="password_reset",
    ),
    path(
        "members/reset_password_done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "members/reset_password_confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "members/reset_password_complete/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("members/profile/", views.members_profile, name="profile"),
    path("members/profile/<int:user_id>", views.members_profile, name="profile"),
    path("members/upload-users/", views.upload_users, name="upload_users"),
    path("comments/<int:comment_pk>/like/", views.like_comment, name="comment_like"),
    path(
        "amendments/<int:amendment_pk>/like/",
        views.support_amendment,
        name="support-amendment",
    ),
    path(
        "amendment/list/<int:paper_pk>/<str:tag>/<str:language_code>/",
        views.amendment_list,
        name="amendment_list",
    ),
    path(
        "amendments/<int:amendment_pk>/translate/<str:language_code>/",
        views.add_amendment_translation,
        name="amendment-add-translation",
    ),
]
