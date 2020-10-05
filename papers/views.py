from django.shortcuts import render, redirect
from django.utils import timezone

from papers import models, forms

# Create your views here.


def paper_list(request):
    papers = models.Paper.objects.all()

    return render(request, 'papers/paper_list.html', {
        'paper_list': papers,
    })


def paper_detail(request, pk):
    paper = models.Paper.objects.get(pk=pk)

    return render(request, 'papers/paper_detail.html', {
        'paper': paper,
    })


def paper_translation_detail(request, pk, language_code):
    paper = models.Paper.objects.get(pk=pk)
    translation = paper.translation_set.get(language_code=language_code)

    return render(request, 'papers/paper_translation_detail.html', {
        'paper': paper,
        'translation': translation,
    })


def paper_create(request):
    form = forms.PaperCreateForm()

    if request.POST:
        form = forms.PaperCreateForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            language_code = form.cleaned_data['language_code']
            state = form.cleaned_data['state']

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
            return render(request, 'papers/paper_create_success.html', {
                'paper': paper,
                'translation': translation,
            })

    return render(request, 'papers/paper_create.html', {
        'form': form
    })


def paper_update(request, pk):
    pass


def paper_create_translation(request, pk):
    pass


def paper_update_translation(request, pk, language_code):
    pass
