# -*- coding: utf-8 -*-
from django.forms.widgets import Input
"""
HTML5 Form Inputs
"""
class TextInput(Input):
    input_type = 'text'

class EmailInput(Input):
    input_type = 'email'
    
class URLInput(Input):
    input_type = 'url'

class SearchInput(Input):
    input_type = 'search'

class ColorInput(Input):
    """
    Not supported by any browsers at this time (Jan. 2010).
    """
    input_type = 'color'
    
class NumberInput(Input):
    input_type = 'number'
    
class RangeInput(NumberInput):
    input_type = 'range'
    
class DateInput(Input):
    input_type = 'date'
    
class MonthInput(Input):
    input_type = 'month'

class WeekInput(Input):
    input_type = 'week'

class TimeInput(Input):
    input_type = 'time'

class DateTimeInput(Input):
    input_type = 'datetime'

class DateTimeLocalInput(Input):
    input_type = 'datetime-local'
