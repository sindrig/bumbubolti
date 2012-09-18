from django import forms
from django.forms.widgets import flatatt
from django.utils.encoding import smart_unicode
from django.utils.html import escape
from django.utils.simplejson import JSONEncoder

class JQueryAutoComplete(forms.TextInput):
    def __init__(self, source, options={}, attrs={}):
        self.attrs = {'autocomplete': 'off', 'class': 'autocompleter'}
        self.attrs.update(attrs)
        self.options = JSONEncoder().encode({'source': source})
    
    def render_js(self, classname):
        return u'$(\'.%s\').autocomplete(%s);' % (classname, self.options)

    def render(self, name, value=None, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        if value:
            final_attrs['value'] = escape(smart_unicode(value))

        if not self.attrs.has_key('id'):
            final_attrs['id'] = 'id_%s' % name    
        
        return u'''<input type="text" %(attrs)s/>
        <script type="text/javascript"><!--//
        %(js)s//--></script>
        ''' % {
            'attrs' : flatatt(final_attrs),
            'js' : self.render_js(final_attrs['class']),
        }