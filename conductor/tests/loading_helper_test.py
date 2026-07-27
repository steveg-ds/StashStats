import pytest
from dash import dcc, html
from conductor.utils.loading_helper import wrap_with_loading

# Test wrapper preserves component ID
def test_wrap_with_loading_preserves_id():
    component = html.Div(id='test-spinner', children=[html.H3('Loading...')])
    wrapped = wrap_with_loading(component)
    assert wrapped.children[0].id == 'test-spinner', 'ID not preserved in wrapper'

# Test wrapper structure
def test_loader_structure():
    component = html.Button('click me', id='test-button')
    wrapped = wrap_with_loading(component)
    assert isinstance(wrapped, dcc.Loading)
    assert wrapped.children_spinner.type == 'div', 'Spinner not in wrapper'