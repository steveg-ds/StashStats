import pytest
from dash import html
import dash_bootstrap_components as dbc
from stashies.utils.loading_helper import LoadingHelper, wrap_with_loading


def test_wrap_with_loading_structure_and_id():
    # Create a test component with specific ID
    test_component = html.Div(id='test-component', children="Test")
    
    # Wrap with loading indicator
    wrapped = LoadingHelper.wrap_with_loading(test_component)
    
    # Verify component structure
    assert wrapped.children is test_component
    assert wrapped.delay_show == 500