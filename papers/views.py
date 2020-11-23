from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from papers import forms, models

# Create your views here.


def paper_list(request):
    papers = models.Paper.objects.all()

    return render(
        request,
        "papers/paper_list.html",
        {
            "paper_list": papers,
        },
    )


def paper_detail(request, pk):
    paper = models.Paper.objects.get(pk=pk)

    return render(
        request,
        "papers/paper_detail.html",
        {
            "paper": paper,
        },
    )


def paper_translation_detail(request, pk, language_code):
    paper = models.Paper.objects.get(pk=pk)
    translation = paper.translation_set.get(language_code=language_code)

    amendmend_list = models.Amendmend.objects.filter(
        paper=paper, language_code=language_code, state="public"
    )

    return render(
        request,
        "papers/paper_translation_detail.html",
        {
            "paper": paper,
            "translation": translation,
            "amendmend_list": amendmend_list,
        },
    )


def paper_edit(request, pk, language_code):
    paper = models.Paper.objects.get(pk=pk)
    translation = paper.translation_set.get(language_code=language_code)

    form = forms.AmendmendForm(translation=translation)

    if request.POST:
        form = forms.AmendmendForm(request.POST, translation=translation)

        if form.is_valid():
            content = form.cleaned_data["content"]
            author_name = form.cleaned_data["author"]
            reason = form.cleaned_data["reason"]

            author = models.Author.objects.create(name=author_name)

            amendmend = models.Amendmend.objects.create(
                paper=paper,
                language_code=language_code,
                author=author,
                content=content,
                state="draft",
                reason=reason,
            )

            return redirect("amendmend-detail", amendmend.pk)

    return render(
        request,
        "papers/paper_edit_view.html",
        {
            "paper": paper,
            "form": form,
            "translation": translation,
        },
    )


def paper_create(request):
    form = forms.PaperCreateForm()

    if request.POST:
        form = forms.PaperCreateForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            language_code = form.cleaned_data["language_code"]
            state = form.cleaned_data["state"]

            paper = models.Paper.objects.create(
                amendmend_deadline=timezone.now(),
                working_title=title,
                state=state,
            )
            translation = models.PaperTranslation.objects.create(
                paper=paper,
                language_code=language_code,
                title=title,
                content=content,
            )
            return render(
                request,
                "papers/paper_create_success.html",
                {
                    "paper": paper,
                    "translation": translation,
                },
            )

    return render(request, "papers/paper_create.html", {"form": form})


def amendmend_detail(request, pk):
    amendmend = models.Amendmend.objects.get(pk=pk)
    form = forms.CommentForm()

    if request.method == "POST":
        amendmend.state = "public"
        amendmend.save()
        form = forms.CommentForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data["name"]
            body = form.cleaned_data["comment"]
            comment = models.Comment.objects.create(
                amendment=models.Amendmend.objects.get(pk=pk),
                name=name,
                body=body,
            )
            return redirect("amendmend-detail", amendmend.pk)

    return render(
        request, "papers/amendmend_detail.html", {"amendmend": amendmend, "form": form}
    )


def amendmend_edit(request, pk):
    amendmend = models.Amendmend.objects.get(pk=pk)

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
        request,
        "papers/amendmend_edit.html",
        {
            "form": form,
            "amendmend": amendmend,
        },
    )


def paper_update(request, pk):
    pass


def paper_create_translation(request, pk):
    pass


def translation_update(request, pk, language_code):
    paper = models.Paper.objects.get(pk=pk)

    translation, created = paper.translation_set.get_or_create(
        language_code=language_code,
        defaults={
            "title": paper.working_title,
            "content": "...",
        },
    )
    if request.method == "POST":
        form = forms.TranslationForm(request.POST, instance=translation)
        if form.is_valid():
            form.save()

    form = forms.TranslationForm(instance=translation)

    return render(
        request,
        "papers/translation_update.html",
        {
            "form": form,
            "paper": paper,
        },
    )


@login_required
def members_profile(request):
    return render(request, "registration/profile.html")
