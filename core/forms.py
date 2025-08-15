from django import forms
from django.template.loader import render_to_string


class BaseForm(forms.BaseForm):
    def as_div(self):
        html = render_to_string("core/components/forms/as_div.html", {"form": self})
        return html

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            initial_class = field.widget.attrs.get("class", "")

            extra_class = " input w-full"

            has_error = field_name in self.errors

            is_checkbox = isinstance(field.widget, forms.CheckboxInput)
            is_radio = isinstance(field.widget, forms.RadioSelect)
            is_select = isinstance(field.widget, forms.Select)
            is_textarea = isinstance(field.widget, forms.Textarea)

            if has_error:
                extra_class += " input-error"

            if is_checkbox or is_radio:
                # remove w-full and input-error
                extra_class = extra_class.replace(" w-full", "")
                extra_class = extra_class.replace(" input-error", "")

            if is_checkbox:
                extra_class = extra_class.replace("input", "")
                if "checkbox" not in initial_class:
                    extra_class += " toggle"
            elif is_radio:
                extra_class = extra_class.replace("input", "radio")
            elif is_select:
                # select select-error
                extra_class = extra_class.replace("input", "select")
            elif is_textarea:
                # textarea textarea-error
                extra_class = extra_class.replace("input", "textarea")

            field.widget.attrs["class"] = initial_class + extra_class
