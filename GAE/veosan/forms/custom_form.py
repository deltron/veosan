# -*- coding: utf-8 -*-

from wtforms import Form, SelectMultipleField, BooleanField
from wtforms import widgets
from cgi import escape

''' 
need to write our own list widget so the <label> doesn't appear after
the checkbox (which shows up on a new line and also makes the click target
much smaller). 

Bottom line: default behavior for checkboxes from WTForms makes no sense

'''
class MultipleCheckboxWidget(object):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
 
        html = []

        for subfield in field:
            if field.default is not None and subfield.data in field.default:
                subfield.checked = True

            html.append(u'<label %s>%s %s</label>' % (widgets.html_params(**kwargs), unicode(subfield), unicode(subfield.label.text)))
        return widgets.HTMLString(u''.join(html))

class CustomCheckboxInput(widgets.Input):
    input_type = 'checkbox'
    
    html_params = staticmethod(widgets.html_params)

    def __call__(self, field, **kwargs):
        if getattr(field, 'checked', field.data):
            kwargs['checked'] = True

        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
            
        label_class = u' '
        if 'class' in kwargs:
            label_class = (u'%s="%s"' % (unicode('class'), escape(unicode(kwargs['class']), quote=True)))

        return widgets.HTMLString(u'<label %s><input %s> %s</label>' % (label_class, widgets.html_params(name=field.name, **kwargs), field.label.text))


# WTF! WTF doesn't come with checkboxes out of the box
class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = MultipleCheckboxWidget()
    option_widget = widgets.CheckboxInput()
    

# Custom boolean field that shows up as :
#   [] Boolean field label
# 
# instead of the default behavior from WTForms which is
#   Boolean field label []
class CustomBooleanField(BooleanField):
    """
    Represents an ``<label><input type="checkbox"> label text</label>``.
    """
    widget = CustomCheckboxInput()

    def _value(self):
        ''' overwrite default value for true from y to True '''
        
        if self.raw_data:
            return unicode(self.raw_data[0])
        else:
            return u'True'

class CustomForm(object):
    def get_form(self, request=None, obj=None):
        class F(Form):
            pass
        
        self._set_fields(F)

        return F(request, obj)

    # override in child
    def _set_fields(self, F):
        pass

