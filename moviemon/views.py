from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from moviemon.controls_form import ControlsForm


def title(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form_result = ControlsForm(request.POST)
        if form_result.is_valid():
            button = form_result.cleaned_data['button']
            match button:
                case 'A':
                    # game.load_default_settings()
                    return redirect('worldmap')
                case 'B':
                    return redirect('load')
                case _:
                    return redirect('title')

    context = {
        'title': 'Title Screen',
        'messages': ['log1', 'log2'],
        'buttons_active': {'A', 'B'},
    }

    return render(request, 'moviemon/title.html', context)


def worldmap(request: HttpRequest) -> HttpResponse:

    return render(request, 'moviemon/title.html', {})
