import base64
import io
import datetime
from django.contrib import messages
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext as _gettext
from django.forms import BoundField
from markupsafe import Markup
from jinja2 import Environment


def qrcode_base64(data, box_size=10, border=4):
    """Generate a QR code and return it as a base64 data URI."""
    import qrcode as qrcode_lib
    qr = qrcode_lib.QRCode(box_size=box_size, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    encoded = base64.b64encode(buf.getvalue()).decode('ascii')
    return f'data:image/png;base64,{encoded}'


def linebreaksbr(text):
    try:
        return Markup(str(text).replace('\n', '<br />'))
    except Exception:
        return text


_NAMESPACE_ALIASES = {
    'document': 'documents',
    'terrarium': 'terrariums',
    'settings': 'app_settings',
}


def url_for(endpoint, **kwargs):
    """Drop-in replacement for Flask's url_for."""
    filename = kwargs.get('filename')
    if endpoint == 'static' and filename:
        return static(filename)
    if endpoint == 'uploaded_file':
        folder = kwargs.get('folder', '')
        fname = kwargs.get('filename', '')
        if folder:
            return f'/uploads/{folder}/{fname}'
        return f'/uploads/{fname}'
    if '.' in endpoint:
        ns, name = endpoint.split('.', 1)
        ns = _NAMESPACE_ALIASES.get(ns, ns)
        django_name = f'{ns}:{name}'
    else:
        django_name = endpoint
    try:
        return reverse(django_name, kwargs={k: v for k, v in kwargs.items() if k != 'filename'})
    except Exception:
        return '#'


class CallableBoundField:
    """Makes Django BoundField callable like WTForms fields.

    Usage in template: {{ form.email(placeholder="x", class="y") }}
    """

    def __init__(self, bound_field):
        self._field = bound_field

    def __call__(self, **kwargs):
        return Markup(self._field.as_widget(attrs=kwargs))

    def __getattr__(self, name):
        attr = getattr(self._field, name)
        if isinstance(attr, BoundField):
            return CallableBoundField(attr)
        return attr

    def __str__(self):
        return str(self._field)

    def __html__(self):
        return self.__str__()


def _custom_getattr(obj, attribute):
    """Override Jinja2 attribute lookup to wrap BoundFields and handle csrf_token."""
    # Intercept csrf_token on Django forms (handled by middleware, not a field)
    if attribute == 'csrf_token':
        from django.forms import BaseForm
        if isinstance(obj, BaseForm):
            return Markup('')

    result = getattr(obj, attribute, Undefined)
    if result is Undefined:
        return Undefined
    if isinstance(result, BoundField):
        return CallableBoundField(result)
    return result


class Undefined:
    """Sentinel for missing attributes."""


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': static,
        'url': reverse,
        'url_for': url_for,
        'get_messages': messages.get_messages,
        'now': datetime.datetime.now,
        'qrcode': qrcode_base64,
        '_': _gettext,
        'gettext': _gettext,
    })
    def dateformat(value, format='medium'):
        """Replacement for Flask-Babel's dateformat filter."""
        if value is None:
            return ''
        fmt_map = {
            'short':  '%d.%m.%y',
            'medium': '%d.%m.%Y',
            'long':   '%d. %B %Y',
            'full':   '%A, %d. %B %Y',
        }
        fmt = fmt_map.get(format, format)
        try:
            return value.strftime(fmt)
        except Exception:
            return str(value)

    env.filters['linebreaksbr'] = linebreaksbr
    env.filters['dateformat'] = dateformat

    # Patch attribute lookup so BoundFields are automatically callable
    original_getattr = env.getattr

    def patched_getattr(obj, attribute):
        from django.forms import BaseForm
        if isinstance(obj, BaseForm) and attribute == 'csrf_token':
            return Markup('')  # replaced by csrf_input(request) in templates
        result = original_getattr(obj, attribute)
        if isinstance(result, BoundField):
            return CallableBoundField(result)
        return result

    env.getattr = patched_getattr

    return env
