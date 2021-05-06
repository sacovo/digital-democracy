"""
Paper views
"""
import io

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404
from django.http.response import FileResponse, HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
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


def paper_amendmentlist(request, paper_pk):
    amendment_list = models.Amendment.objects.filter(paper_id=paper_pk)
    if request.method == "POST":
        for amendment in amendment_list:
            value = request.POST.get(str(amendment.pk), "")
            if value:
                amendment.state = value
                amendment.save()

    return render(
        request,
        "papers/amendment_list.html",
        {"amendment_list": amendment_list, "paper_pk": paper_pk},
    )


def selected_amendments_view(request, paper_pk, language_code):
    translation = models.PaperTranslation.objects.get(
        paper_id=paper_pk, language_code=language_code
    )
    form = forms.AmendmentSelect(translation=translation)

    return render(
        request,
        "papers/select_amendments.html",
        {"form": form, "translation": translation},
    )


def finalize_view(request, paper_pk, language_code):
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


@login_required
def recommendation_create(request, amendment_pk):
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


@login_required
def recommendation_update(request, pk):
    recommendation = models.Recommendation.objects.get(pk=pk)
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
            paper = models.Paper.objects.create(
                amendment_deadline=timezone.now(), working_title=title
            )
            paper.authors.add(author)
            models.PaperTranslation.objects.create(
                paper=paper, language_code=language_code, title=title, content=content
            )

            return redirect("paper-detail", paper.pk)

    return render(request, "papers/paper_create.html", {"form": form})


@login_required
def paper_update(request, paper_pk):
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

    if request.method == "POST":
        amendment.state = "public"
        amendment.save()
        form = forms.CommentForm(request.POST)

        if form.is_valid():
            body = form.cleaned_data["comment"]

            author, _ = models.Author.objects.get_or_create(user=request.user)

            models.Comment.objects.create(
                amendment=models.Amendment.objects.get(pk=amendment_pk),
                body=body,
                author=author,
            )

            return redirect("amendment-detail", amendment.pk)

    comments = models.Comment.objects.filter(
        Q(amendment=amendment) | Q(amendment__in=amendment.translations.all())
    )

    if "retracted" in request.POST:
        amendment.state = "retracted"
        amendment.save()
        form = forms.CommentForm(request.POST)  # needed?

    return render(
        request,
        "papers/amendment_detail.html",
        {"amendment": amendment, "form": form, "comments": comments},
    )


@login_required
def amendment_edit(request, amendment_pk):
    """
    Edit an existing amendment
    """
    amendment = models.Amendment.objects.get(pk=amendment_pk)

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
        member = models.User.objects.get(id=user_id)
    else:
        member = request.user
    if hasattr(member, "author"):
        author = member.author
        comments = author.comment_set.all()
        papers = author.paper_set.all()
        amendments = author.amendment_set.all()
    else:
        comments = models.Comment.objects.none()
        papers = models.Paper.objects.none()
        amendments = models.Amendment.objects.none()

    return render(
        request,
        "registration/profile.html",
        {"papers": papers, "comments": comments, "amendments": amendments},
    )


@login_required
def support_amendment(request, amendment_pk):
    """
    Adds the requesting user to the list of supporters
    """
    if request.method == "POST":
        amendment = models.Amendment.objects.get(pk=amendment_pk)
        user = request.user

        if amendment.supporters.filter(pk=user.pk):
            amendment.supporters.remove(user.pk)

        else:
            amendment.supporters.add(user.pk)

    return redirect("amendment-detail", amendment.pk)


@login_required
def amendment_list(request, paper_pk, tag, language_code):
    """
    List of all papers
    """
    paper = models.Paper.objects.get(pk=paper_pk)
    amendments = models.Amendment.objects.filter(
        tags__name=tag, language_code=language_code, paper=paper
    )

    return render(
        request, "papers/amendments_by_tag.html", {"amendment_list": amendments}
    )


@permission_required("auth.add_user")
def upload_users(request):
    upload_form = forms.UserUploadForm()

    if request.method == "POST":
        upload_form = forms.UserUploadForm(request.POST, request.FILES)

        if upload_form.is_valid():
            csv_file = upload_form.cleaned_data["csv_file"].file
            try:
                imported_users = utils.import_users_from_csv(csv_file)
                messages.success(request, _(f"{imported_users} were imported!"))

                return redirect("admin:auth_user_changelist")
            except Exception as e:
                return render(
                    request,
                    "members/user_upload.html",
                    {"form": upload_form, "error": e},
                )

    return render(request, "members/user_upload.html", {"form": upload_form})


def search_result(request):
    if request.method == "GET":
        searched = request.GET["searched"]
        result_papers = models.Paper.objects.filter(working_title__icontains=searched)
        result_amendments = models.Amendment.objects.filter(title__icontains=searched)
        return render(
            request,
            "papers/search_result.html",
            {
                "searched": searched,
                "result_papers": result_papers,
                "result_amendments": result_amendments,
            },
        )
    else:
        return render(request, "papers/search_result.html")
