from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def title_screen(request: HttpRequest) -> HttpResponse:

    context = {
        'title': 'Title Screen',
        'content': 'moviemon/title_screen.html'
    }

    return render(request, 'moviemon/base.html', context)
