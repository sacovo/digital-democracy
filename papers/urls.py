"""
This module links the different views with a url.

Each entry in urlpatterns is a url of the app and served by a view function.
With the <int:paper_pk> syntax we can capture parts of the url and provide them
to the function that is served under the url.

To add new urls you can just add a new entry to the list.

Learn more here: https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""
from django.conf.urls import include
from django.contrib.auth import views as auth_views
from django.urls import path

from papers import views

urlpatterns = [
    path("", views.paper_list, name="paper-list"),
    path("paper/create/", views.paper_create, name="paper-create"),
    path("paper/<int:paper_pk>/", views.paper_detail, name="paper-detail"),
    path("paper/<int:paper_pk>/delete/", views.paper_delete, name="paper-delete"),
    path(
        "paper/<int:paper_pk>/presentation/",
        views.paper_presentation,
        name="paper-presentation",
    ),
    path(
        "paper/<int:paper_pk>/paper_amendmentlist/",
        views.paper_amendmentlist,
        name="paper-amendment-list",
    ),
    path("paper/<int:paper_pk>/update/", views.paper_update, name="paper-update"),
    path(
        "paper/<int:paper_pk>/<str:language_code>/",
        views.paper_detail,
        name="paper-detail-language",
    ),
    path(
        "paper/<int:paper_pk>/<str:language_code>/select-amendments/",
        views.selected_amendments_view,
        name="paper-select-amendments",
    ),
    path(
        "paper/<int:paper_pk>/<str:language_code>/finalize/",
        views.finalize_view,
        name="paper-finalize",
    ),
    path(
        "paper/<int:paper_pk>/<str:language_code>/create-pdf",
        views.paper_detail_create_pdf,
        name="paper-detail-language-create-pdf",
    ),
    path(
        "paper/<int:paper_pk>/<str:language_code>/create-amendment/",
        views.amendment_create,
        name="create-amendment",
    ),
    path(
        "paper/<int:paper_pk>/<str:language_code>/update/",
        views.translation_update,
        name="paper-translation-update",
    ),
    path(
        "translation/<int:translation_pk>/delete/",
        views.translation_delete,
        name="translation-delete",
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
    path(
        "amendments/<int:amendment_pk>/clone/",
        views.amendment_clone,
        name="amendment-clone",
    ),
    path(
        "amendments/<int:recommendation_pk>/recommendation/update/",
        views.recommendation_update,
        name="recommendation-edit",
    ),
    path(
        "amendments/<int:amendment_pk>/recommendation/create/",
        views.recommendation_create,
        name="recommendation-create",
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
        "comments/<int:comment_pk>/delete/", views.comment_delete, name="comment-delete"
    ),
    path(
        "paper-comments/<int:comment_pk>/delete/",
        views.paper_comment_delete,
        name="paper-comment-delete",
    ),
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
    path("search_result", views.search_result, name="search-result"),
    path("i18n/", include("django.conf.urls.i18n")),
]
