"""
This module has all the views that are served by the application.

Each view returns a http response that then will be displayed in the
browser of the user. A view always gets the request object, that has
information about the request and the user that made it.

Additional arguments are captured by the url routing mechanism and can
be used to get objects from the database through an id.

Usually a view returns a response with html content. This content is rendered
from a file that lies in the templates subfolder. To render the template additional
context can be provided. The render method does this, it need the request as the first
argument, the path to the template (relative to the templates folder) as second and
a dict with the context as third.

To learn more about views you can start here:
    https://docs.djangoproject.com/en/3.2/topics/http/views/
To learn more about templates start here:
    https://docs.djangoproject.com/en/3.2/topics/templates/
"""
import io

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404
from django.http.response import FileResponse, HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from weasyprint import CSS, HTML

from papers import forms, models, utils

# Create your views here.


@login_required
def paper_list(request):
    """
    List of all papers
    """
    papers = models.Paper.objects.all()
    if not request.user.is_staff:
        papers = papers.exclude(state="draft")

    for paper in papers:
        paper.created_at = paper.created_at.date()

    return render(request, "papers/paper_list.html", {"paper_list": papers})


@login_required
def paper_detail(request, paper_pk, language_code=None):
    """
    Detail view of paper
    """
    paper = models.Paper.objects.get(pk=paper_pk)
    form = forms.CommentForm()

    if request.method == "POST":
        form = forms.CommentForm(request.POST)

        if form.is_valid():
            body = form.cleaned_data["comment"]

            author, _ = models.Author.objects.get_or_create(user=request.user)

            models.PaperComment.objects.create(paper=paper, body=body, author=author)
            return redirect("paper-detail", paper.pk)

    return render(
        request,
        "papers/paper_detail.html",
        {
            "form": form,
            "paper": paper,
            "update_allowed": request.user.is_superuser
            or paper.is_author(request.user),
            "language_code": language_code
            or paper.translation_set.first().language_code,
            "create_amendment_allowed": paper.amendment_deadline > timezone.now(),
        },
    )


@staff_member_required
def paper_amendmentlist(request, paper_pk):
    """
    List of all amendments of a paper with checkboxes to accept/reject every amendment.
    If called with post the amendments are modified in the database.
    """
    amendments = models.Amendment.objects.filter(paper_id=paper_pk)
    if request.method == "POST":
        for amendment in amendments:
            value = request.POST.get(str(amendment.pk), "")
            if value:
                amendment.state = value
                amendment.save()

    return render(
        request,
        "papers/amendment_list.html",
        {"amendment_list": amendments, "paper_pk": paper_pk},
    )


@staff_member_required
def selected_amendments_view(request, paper_pk, language_code):
    """
    Render a form to select amendments that should be merged into the final paper.
    """
    translation = models.PaperTranslation.objects.get(
        paper_id=paper_pk, language_code=language_code
    )
    form = forms.AmendmentSelect(translation=translation)

    return render(
        request,
        "papers/select_amendments.html",
        {"form": form, "translation": translation},
    )


@staff_member_required
def translation_delete(request, translation_pk):
    """
    Delete view for a translation.
    """
    translation = models.PaperTranslation.objects.get(pk=translation_pk)

    if translation.paper.translation_set.count() == 1:
        messages.warning(request, _("Cannot delete only translation of this paper"))
        return redirect("paper-detail", translation.paper_id)

    if request.method == "POST":
        paper_pk = translation.paper_id
        translation.delete()
        messages.success(request, _("Successfully deleted translation."))
        return redirect("paper-detail", paper_pk)

    return render(
        request,
        "papers/confirm_deletion.html",
        {
            "translation": translation,
            "name": translation.title + f" ({translation.language_code})",
            "back": reverse(
                "paper-detail-language",
                kwargs={
                    "paper_pk": translation.paper_id,
                    "language_code": translation.language_code,
                },
            ),
        },
    )


@login_required
def comment_delete(request, comment_pk):
    """Deltes the comment, if the user is allowed to do so."""
    comment = models.Comment.objects.get(pk=comment_pk)
    if comment.author.user != request.user:
        messages.warning(request, _("You are not allowed to delete this comment."))
        return redirect("amendment-detail", args=(comment.amendment_id,))

    if request.method == "POST":
        amendment_pk = comment.amendment_id
        comment.delete()
        messages.success(request, _("Successfully deleted comment."))
        return redirect("amendment-detail", amendment_pk)

    return render(
        request,
        "papers/confirm_deletion.html",
        {
            "name": _("your comment"),
            "back": reverse(
                "amendment-detail", kwargs={"amendment_pk": comment.amendment_id}
            ),
        },
    )


@login_required
def paper_comment_delete(request, comment_pk):
    """Deletes a comment if the users is allowed to do so."""
    comment = models.PaperComment.objects.get(pk=comment_pk)
    if comment.author.user != request.user:
        messages.warning(request, _("You are not allowed to delete this comment."))
        return redirect("amendment-detail", args=(comment.amendment_id,))

    if request.method == "POST":
        paper_pk = comment.paper_id
        comment.delete()
        messages.success(request, _("Successfully deleted comment."))
        return redirect("paper-detail", paper_pk)

    return render(
        request,
        "papers/confirm_deletion.html",
        {
            "name": _("your comment"),
            "back": reverse("paper-detail", kwargs={"paper_pk": comment.paper_id}),
        },
    )


@staff_member_required
def paper_delete(request, paper_pk):
    """View to delete the whole paper."""
    paper = models.Paper.objects.get(pk=paper_pk)
    if request.method == "POST":
        paper.delete()
        messages.success(request, _("Successfully deleted paper."))
        return redirect("paper-list")

    return render(
        request,
        "papers/confirm_deletion.html",
        {
            "paper": paper,
            "name": paper.working_title,
            "back": reverse("paper-detail", args=(paper_pk,)),
        },
    )


@staff_member_required
def finalize_view(request, paper_pk, language_code):
    """
    View to see all accepted amendments in a text editor, so that users can
    accept each amendment and make modifications to the text if necessary.
    """
    translation = models.PaperTranslation.objects.get(
        paper_id=paper_pk, language_code=language_code
    )
    form = forms.AmendmentSelect(request.GET, translation=translation)

    if request.method == "POST":
        translation.content = request.POST.get("content")
        translation.save()
        return redirect("paper-detail", translation.paper_id)

    if not form.is_valid():
        return render(
            request,
            "papers/select_amendments.html",
            {"form": form, "translation": translation},
        )

    modified_text = utils.create_modified_text(
        translation.content, form.cleaned_data["merge"]
    )
    modified_text = utils.add_lite_classes(modified_text)
    form = forms.FinalizePaperForm(
        initial={"content": modified_text, "title": translation.title}
    )

    return render(
        request,
        "papers/modified_text.html",
        {"translation": translation, "modified_text": modified_text, "form": form},
    )


@login_required
def paper_detail_create_pdf(request, paper_pk, language_code):
    """
    Create and download a pdf of the paper, if not yet finalized this will also include
    the amendments.
    """
    paper = models.Paper.objects.get(pk=paper_pk).translation_for(language_code)
    amendments = models.Amendment.objects.filter(
        paper_id=paper_pk, language_code=language_code
    )

    filename = "Digital-Democracy-Paper-" + str(paper_pk) + "-" + language_code + ".pdf"
    html = render_to_string(
        "pdf/amendment_pdf_template.html",
        {
            "title": paper.title,
            "content": paper.content,
            "amendments": amendments,
            "paper": paper.paper,
        },
    )
    css = CSS(
        string=render_to_string(
            "pdf/amendment_pdf_template.css",
            {
                "body_font": settings.PDF_BODY_FONT,
                "title_font": settings.PDF_TITLE_FONT,
            },
        )
    )
    pdf = HTML(string=html).write_pdf(stylesheets=[css])
    buffer = io.BytesIO()
    buffer.write(pdf)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=filename)


@login_required
def paper_presentation(request, paper_pk):
    """Download presentation for the paper, with a slide for each amendment"""
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    response["Content-Disposition"] = f'attachment; filename="paper_{paper_pk}.pptx"'
    presentation = utils.generate_powerpoint(models.Paper.objects.get(pk=paper_pk))
    presentation.save(response)

    return response


@login_required
def amendment_create(request, paper_pk, language_code):
    """
    View to create a new amendment
    """
    paper = models.Paper.objects.get(pk=paper_pk)
    translation = paper.translation_set.get(language_code=language_code)

    form = forms.AmendmentForm(translation=translation)

    if request.POST:
        form = forms.AmendmentForm(request.POST, translation=translation)

        if form.is_valid():
            author, _ = models.Author.objects.get_or_create(user=request.user)
            amendment = form.create_amendment(translation, author)

            user = request.user
            amendment.supporters.add(user.pk)

            return redirect("amendment-detail", amendment.pk)

    return render(
        request,
        "papers/paper_edit_view.html",
        {"paper": paper, "form": form, "translation": translation},
    )


@staff_member_required
def recommendation_create(request, amendment_pk):
    """
    Create a recommendation for an amendment.
    Also updates the recommendation for all translations.
    """
    amendment = models.Amendment.objects.get(pk=amendment_pk)
    if hasattr(amendment, "recommendation"):
        return redirect("recommendation-edit", amendment.recommendation.pk)
    form = forms.RecommendationForm()

    if request.method == "POST":
        form = forms.RecommendationForm(request.POST)
        if form.is_valid():
            form.instance.amendment = amendment
            form.save(commit=False)
            form.instance.save(update_translations=True)
            return redirect("amendment-detail", amendment.pk)
    return render(
        request,
        "papers/recommendation_form.html",
        {"form": form, "amendment": amendment},
    )


@staff_member_required
def recommendation_update(request, recommendation_pk):
    """Update the recommendation of the amendment and of all translations."""
    recommendation = models.Recommendation.objects.get(pk=recommendation_pk)
    form = forms.RecommendationForm(instance=recommendation)

    if request.method == "POST":
        form = forms.RecommendationForm(request.POST, instance=recommendation)

        if form.is_valid():
            form.save(commit=False)
            form.instance.save(update_translations=True)
            return redirect("amendment-detail", recommendation.amendment.pk)

    return render(
        request,
        "papers/recommendation_form.html",
        {"form": form, "amendment": recommendation.amendment},
    )


@login_required
def paper_create(request):
    """
    View to create a new paper
    """
    form = forms.PaperCreateForm()

    if request.POST:
        form = forms.PaperCreateForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            language_code = form.cleaned_data["language_code"]
            author, _ = models.Author.objects.get_or_create(user=request.user)
            amendment_deadline = form.cleaned_data["deadline"]
            paper = models.Paper.objects.create(
                amendment_deadline=amendment_deadline, working_title=title
            )
            paper.authors.add(author)
            models.PaperTranslation.objects.create(
                paper=paper, language_code=language_code, title=title, content=content
            )

            return redirect("paper-detail", paper.pk)

    return render(request, "papers/paper_create.html", {"form": form})


@login_required
def paper_update(request, paper_pk):
    """Update the details of the paper."""
    paper = models.Paper.objects.get(pk=paper_pk)

    # Check if user may edit paper
    if not (request.user.is_superuser or paper.is_author(request.user)):
        raise PermissionDenied(_("You are not allowed to edit this paper."))

    form = forms.PaperUpdateForm(instance=paper)

    if request.method == "POST":
        form = forms.PaperUpdateForm(request.POST, instance=paper)

        if form.is_valid():
            form.save()

        return redirect("paper-detail", paper.pk)

    return render(request, "papers/paper_update.html", {"form": form, "paper": paper})


@login_required
def amendment_detail(request, amendment_pk):
    """
    Detail view of paper
    """
    amendment = models.Amendment.objects.get(pk=amendment_pk)
    form = forms.CommentForm()
    author, _ = models.Author.objects.get_or_create(user=request.user)

    if request.method == "POST":

        if request.POST.get("action", None) == "publish" and request.user.is_staff:
            amendment.state = "public"
        elif request.POST.get("action", None) == "review":
            amendment.state = "review"
            utils.notify_amendment(amendment, request)

        amendment.save()

        form = forms.CommentForm(request.POST)

        if form.is_valid():
            body = form.cleaned_data["comment"]
            if "submit-comment" in request.POST:
                models.Comment.objects.create(
                    amendment=models.Amendment.objects.get(pk=amendment_pk),
                    body=body,
                    author=author,
                )
            if "submit-note" in request.POST:
                models.Note.objects.create(
                    amendment=models.Amendment.objects.get(pk=amendment_pk),
                    body=body,
                    author=author,
                )
            return redirect("amendment-detail", amendment.pk)

    comments = models.Comment.objects.filter(
        Q(amendment=amendment) | Q(amendment__in=amendment.translations.all())
    )
    notes = models.Note.objects.filter(
        (Q(amendment=amendment) | Q(amendment__in=amendment.translations.all()))
        & Q(author=author)
    )
    if "retracted" in request.POST and amendment.paper.is_open():
        amendment.state = "retracted"
        amendment.save()
    form = forms.CommentForm(request.POST)  # needed?

    return render(
        request,
        "papers/amendment_detail.html",
        {"amendment": amendment, "form": form, "comments": comments, "notes": notes},
    )


@login_required
def amendment_edit(request, amendment_pk):
    """
    Edit an existing amendment
    """
    amendment = models.Amendment.objects.get(pk=amendment_pk)

    if amendment.author.user != request.user and not request.user.is_staff:
        raise PermissionDenied(_("You are not allowed to edit this amendment."))

    form = forms.AmendmentForm(amendment=amendment)

    if request.method == "POST":
        form = forms.AmendmentForm(request.POST, amendment=amendment)

        if form.is_valid():
            content = form.cleaned_data.get("content")
            reason = form.cleaned_data.get("reason")
            title = form.cleaned_data.get("title")

            amendment.content = content
            amendment.reason = reason
            amendment.title = title
            amendment.save()

            return redirect("amendment-detail", amendment.pk)

    return render(
        request, "papers/amendment_edit.html", {"form": form, "amendment": amendment}
    )


@login_required
def amendment_clone(request, amendment_pk):
    """
    Clone an amendment
    """
    amendment = models.Amendment.objects.get(pk=amendment_pk)
    form = forms.AmendmentForm(amendment=amendment)

    if request.method == "POST":
        form = forms.AmendmentForm(request.POST, amendment=amendment)

        if form.is_valid():
            amendment.pk = None
            content = form.cleaned_data.get("content")
            reason = form.cleaned_data.get("reason")
            title = form.cleaned_data.get("title")

            amendment.content = content
            amendment.reason = reason
            amendment.title = title
            amendment.save()

            return redirect("amendment-detail", amendment.pk)

    return render(
        request,
        "papers/amendment_edit.html",
        {"form": form, "amendment": amendment, "clone": True},
    )


@permission_required("papers.change_translation")
def translation_update(request, paper_pk, language_code):
    """
    Update the translation of a paper
    """
    paper = models.Paper.objects.get(pk=paper_pk)

    translation, _ = paper.translation_set.get_or_create(
        language_code=language_code,
        defaults={"title": paper.working_title, "content": "..."},
    )
    form = forms.TranslationForm(instance=translation)
    if request.method == "POST":
        form = forms.TranslationForm(request.POST, instance=translation)
        if form.is_valid():
            form.save()
            paper.translation_set.exclude(pk=translation.pk).filter(
                needs_update=False
            ).update(needs_update=form.cleaned_data["needs_update"])
            translation.needs_update = False
            translation.save()
            return redirect("paper-detail-language", paper.pk, language_code)

    return render(
        request, "papers/translation_update.html", {"form": form, "paper": paper}
    )


@permission_required("papers.add_translation")
def add_amendment_translation(request, amendment_pk, language_code):
    """
    Shows a form to create a translation in the given language code.
    If POST data is received validate the form and create the translation.
    """
    original = models.Amendment.objects.get(pk=amendment_pk)

    if original.has_translation_for_language(language_code):
        return redirect("amendment-edit", amendment_pk)

    if not original.paper.has_translation_for_language(language_code):
        raise Http404("translation for this language not found")

    translation = original.paper.translation_for(language_code)

    form = forms.AmendmentForm(translation=translation)

    if request.method == "POST":
        form = forms.AmendmentForm(request.POST, translation=translation)

        if form.is_valid():
            amendment = form.create_amendment(
                translation=translation, author=original.author
            )
            original.add_translation(amendment)
            for translated_amendment in original.translations.all():
                translated_amendment.add_translation(amendment)
            return redirect("amendment-detail", amendment.pk)

    return render(
        request,
        "papers/add_amendment_translation.html",
        {"form": form, "translation": translation, "original": original},
    )


@login_required
def like_comment(request, comment_pk):
    """
    Function to like and unlike a comment.
    """
    if request.method == "POST":
        comment = models.Comment.objects.get(pk=comment_pk)
        user = request.user

        if comment.likes.filter(pk=user.pk):
            comment.likes.remove(user.pk)

        else:
            comment.likes.add(user.pk)

    return redirect("amendment-detail", comment.amendment.pk)


@login_required
def members_profile(request, user_id=None):
    """
    Profile page
    If no user id is specified, default to showing the logged in user's profile
    """
    if user_id is not None:
        member = get_user_model().objects.get(id=user_id)
    else:
        member = request.user

    # Get the objects to be displayed in the profile page, by default None
    comments = models.Comment.objects.none()
    papers = models.Paper.objects.none()
    amendments = models.Amendment.objects.none()
    notes = models.Note.objects.none()
    if hasattr(member, "author"):
        author = member.author
        comments = author.comment_set.all()
        papers = author.paper_set.all()
        amendments = author.amendment_set.all()
        # Only display notes if the currently logged in user is viewing their own profile
        if user_id is None or user_id == request.user.id:
            notes = author.note_set.all()

    return render(
        request,
        "registration/profile.html",
        {
            "member": member,
            "papers": papers,
            "comments": comments,
            "amendments": amendments,
            "notes": notes,
        },
    )


@login_required
def support_amendment(request, amendment_pk):
    """
    Adds the requesting user to the list of supporters
    """

    amendment = models.Amendment.objects.get(pk=amendment_pk)

    if request.method == "POST" and amendment.paper.is_open():
        user = request.user

        if amendment.supporters.filter(pk=user.pk):
            amendment.supporters.remove(user.pk)

        else:
            amendment.supporters.add(user.pk)

    return redirect("amendment-detail", amendment.pk)


@login_required
def amendment_list(request, paper_pk, language_code):
    """
    List of all papers
    """
    paper = models.Paper.objects.get(pk=paper_pk)
    amendments = models.Amendment.objects.filter(
        language_code=language_code, paper=paper
    )

    return render(
        request, "papers/amendments_by_tag.html", {"amendment_list": amendments}
    )


@permission_required("auth.add_user")
def upload_users(request):
    """
    Upload a csv with email adresses to create new users.
    """
    upload_form = forms.UserUploadForm()

    if request.method == "POST":
        upload_form = forms.UserUploadForm(request.POST, request.FILES)

        if upload_form.is_valid():
            csv_file = upload_form.cleaned_data["csv_file"].file
            imported_users = utils.import_users_from_csv(csv_file)
            messages.success(request, _(f"{imported_users} were imported!"))

            return redirect("admin:auth_user_changelist")

    return render(request, "members/user_upload.html", {"form": upload_form})


@login_required
def search_result(request):
    """
    Display all amendments that match the search
    """
    if request.method == "GET":
        searched = request.GET["searched"]
        result_papers = models.Paper.objects.filter(working_title__icontains=searched)

        filter_amendments = Q(state="public") | Q(author__user_id=request.user.id)
        result_amendments = models.Amendment.objects.filter(
            title__icontains=searched
        ).filter(filter_amendments)

        filter_paper = (
            Q(paper__state="public")
            | Q(paper__state="final")
            | Q(paper__authors__user=request.user)
        )
        result_trans_body = models.PaperTranslation.objects.filter(
            title__icontains=searched
        ).filter(filter_paper)

        filter_private_notes = Q(author__user_id=request.user.id)
        result_private_notes = models.Note.objects.filter(
            body__icontains=searched
        ).filter(filter_private_notes)

        return render(
            request,
            "papers/search_result.html",
            {
                "searched": searched,
                "result_papers": result_papers,
                "result_amendments": result_amendments,
                "result_trans_body": result_trans_body,
                "result_private_notes": result_private_notes,
            },
        )
    return render(request, "papers/search_result.html")
