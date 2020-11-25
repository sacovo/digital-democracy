"""
Paper views
"""
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import timezone

from papers import forms, models

# Create your views here.


@login_required
def paper_list(request):
    """
    List of all papers
    """
    papers = models.Paper.objects.all()

    return render(request, "papers/paper_list.html", {"paper_list": papers})


@login_required
def paper_detail(request, paper_pk):
    """
    Detail view of paper
    """
    paper = models.Paper.objects.get(pk=paper_pk)

    return render(request, "papers/paper_detail.html", {"paper": paper})


@login_required
def paper_edit(request, paper_pk, language_code):
    """
    View to create a new amendmen
    """
    paper = models.Paper.objects.get(pk=paper_pk)
    translation = paper.translation_set.get(language_code=language_code)

    form = forms.AmendmendForm(translation=translation)

    if request.POST:
        form = forms.AmendmendForm(request.POST, translation=translation)

        if form.is_valid():
            author, _ = models.Author.objects.get_or_create(user=request.user)

            amendmend = form.create_amendmend(translation, author)
            return redirect("amendmend-detail", amendmend.pk)

    return render(
        request,
        "papers/paper_edit_view.html",
        {"paper": paper, "form": form, "translation": translation},
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
            state = form.cleaned_data["state"]

            paper = models.Paper.objects.create(
                amendmend_deadline=timezone.now(), working_title=title, state=state
            )

            models.PaperTranslation.objects.create(
                paper=paper, language_code=language_code, title=title, content=content
            )

            return redirect("paper-detail", paper.pk)

    return render(request, "papers/paper_create.html", {"form": form})


@login_required
def amendmend_detail(request, amendment_pk):
    """
    Detail view of paper
    """
    amendmend = models.Amendmend.objects.get(pk=amendment_pk)
    form = forms.CommentForm()

    if request.method == "POST":
        amendmend.state = "public"
        amendmend.save()
        form = forms.CommentForm(request.POST)

        if form.is_valid():
            body = form.cleaned_data["comment"]

            author, _ = models.Author.objects.get_or_create(user=request.user)

            models.Comment.objects.create(
                amendment=models.Amendmend.objects.get(pk=amendment_pk),
                body=body,
                author=author,
            )

            return redirect("amendmend-detail", amendmend.pk)

    return render(
        request, "papers/amendmend_detail.html", {"amendmend": amendmend, "form": form}
    )


@login_required
def amendmend_edit(request, amendment_pk):
    """
    Edit an existing amendment
    """
    amendmend = models.Amendmend.objects.get(pk=amendment_pk)

    form = forms.AmendmendForm(amendmend=amendmend)

    if request.method == "POST":
        form = forms.AmendmendForm(request.POST)

        if form.is_valid():
            content = form.cleaned_data.get("content")
            reason = form.cleaned_data.get("reason")

            amendmend.content = content
            amendmend.reason = reason
            amendmend.save()

            return redirect("amendmend-detail", amendmend.pk)

    return render(
        request, "papers/amendmend_edit.html", {"form": form, "amendmend": amendmend}
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
    if request.method == "POST":
        form = forms.TranslationForm(request.POST, instance=translation)
        if form.is_valid():
            form.save()

    form = forms.TranslationForm(instance=translation)

    return render(
        request, "papers/translation_update.html", {"form": form, "paper": paper}
    )


def add_amendment_translation(request, amendment_pk, language_code):
    """
    Shows a form to create a translation in the given language code.
    If POST data is received validate the form and create the translation.
    """
    original = models.Amendmend.objects.get(pk=amendment_pk)

    if original.has_translation_for_language(language_code):
        return redirect("amendmend-edit", amendment_pk)

    if not original.paper.has_translation_for_language(language_code):
        raise Http404("translation for this language not found")

    translation = original.paper.translation_for(language_code)

    form = forms.AmendmendForm(translation=translation)

    if request.method == "POST":
        form = forms.AmendmendForm(request.POST, translation=translation)

        if form.is_valid():
            amendmend = form.create_amendmend(
                translation=translation, author=original.author
            )
            original.add_translation(amendmend)
            return redirect("amendmend-detail", amendmend.pk)

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

    return redirect("amendmend-detail", comment.amendment.pk)


@login_required
def members_profile(request):
    """
    Profile page
    """
    return render(request, "registration/profile.html")


@login_required
def support_amendment(request, amendment_pk):
    """
    Adds the requesting user to the list of supporters
    """
    if request.method == "POST":
        amendment = models.Amendmend.objects.get(pk=amendment_pk)
        user = request.user

        if amendment.supporters.filter(pk=user.pk):
            amendment.supporters.remove(user.pk)

        else:
            amendment.supporters.add(user.pk)

    return redirect("amendmend-detail", amendment.pk)


@login_required
def newsfeed(request):
    """
    Display a newsfeed with recent activity
    """
    return render(request, "papers/newsfeed.html")


@login_required
def amendment_list(request, paper_pk, tag, language_code):
    """
    List of all papers
    """
    paper = models.Paper.objects.get(pk=paper_pk)
    amendments = models.Amendmend.objects.filter(
        tags__name=tag, language_code=language_code, paper=paper
    )

    return render(
        request, "papers/amendments_by_tag.html", {"amendment_list": amendments}
    )
