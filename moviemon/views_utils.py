from typing import Type

from django.http import QueryDict

from moviemon.controls_form import ControlsForm


def pressed_button(request_post: Type[QueryDict]) -> str:
    form_result = ControlsForm(request_post)
    if form_result.is_valid():
        return form_result.cleaned_data['button']
