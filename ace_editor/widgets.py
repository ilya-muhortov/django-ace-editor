
import json
from django import forms
from django.utils.safestring import mark_safe


class AceEditorWidget(forms.Textarea):

    editor_default_options = {
        'fontSize': '14px',
        'minLines': 10,
        'maxLines': 'Infinity',
        'enableBasicAutocompletion': 'true'
    }

    def __init__(
        self,
        mode=None,
        hide_label=True,
        editor_options=None,
        read_only=False,
        use_wrap_mode=False,
        fold=False,
        *args, **kwargs
    ):
        self.mode = mode
        self.hide_label = hide_label
        self.read_only = read_only
        self.use_wrap_mode = use_wrap_mode
        self.editor_options = editor_options or dict()
        self.fold = fold
        super().__init__(*args, **kwargs)

    @property
    def media(self):
        js = [
            'ace/src/ace.js'
        ]

        if self.mode:
            js.append('ace/src/mode-%s.js' % self.mode)

        css = {'screen': ['ace/css/style.css', 'ace/css/textmate.css']}
        return forms.Media(js=js, css=css)

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or dict()
        id_name = attrs['id'].replace('-', '_')
        textarea = super().render(name, value, attrs, renderer)
        editor_options = dict(self.editor_default_options, **self.editor_options)

        return mark_safe(f'''
            {textarea}
            <div id="{attrs['id']}_editor" class="ace-editor"></div>
            <script>
            var textarea_{id_name} = django.jQuery("#{attrs['id']}").hide();
            var editor_{id_name} = ace.edit("{attrs['id']}_editor");
            editor_{id_name}.setTheme("ace/theme/textmate");
            editor_{id_name}.session.setMode("ace/mode/{self.mode}");
            editor_{id_name}.setShowPrintMargin(false);
            editor_{id_name}.setOptions(
                {json.dumps(editor_options)}
            );
            {f'editor_{id_name}.setReadOnly(true);' if self.read_only else ''}
            {f'editor_{id_name}.getSession().setUseWrapMode(true);' if self.use_wrap_mode else ''}
            editor_{id_name}.getSession().setValue(textarea_{id_name}.val());
            editor_{id_name}.getSession().on('change', function(){{
              textarea_{id_name}.val(editor_{id_name}.getSession().getValue());
            }});
            {f'editor_{id_name}.getSession().foldAll(1, editor_{id_name}.getSession().doc.getAllLines().length);' 
                if self.fold else ''
            }
            </script> 
            <style>
            .field-{name} {{
                margin: 0 -40px 0 -40px;
                padding: 20px 20px 20px 0;
            }}
            label[for="{attrs['id']}"] {{
                margin-top: -7px;
                margin-left: 50px;
                display: {'none' if self.hide_label else 'block'};
            }}
            .field-{name} .help {{
                margin-left: 30px !important;
            }}
            </style>
        ''')


class AceJSONWidget(AceEditorWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, mode='json', **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        if value:
            try:
                value = json.dumps(json.loads(value), indent=4, ensure_ascii=False)
            except json.JSONDecodeError:
                pass

        return super().render(name, value, attrs, renderer)


class AceCSSWidget(AceEditorWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, mode='css', **kwargs)


class AceXMLWidget(AceEditorWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, mode='xml', **kwargs)
