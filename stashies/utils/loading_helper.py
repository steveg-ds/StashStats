"""Loading indicator helper utility for Dash components."""

from dash import dcc
import dash_bootstrap_components as dbc


def wrap_with_loading(component):
    """Wrap a Dash component with a loading indicator.
    
    Args:
        component: A Dash component to wrap with a loading indicator
        
    Returns:
        dcc.Loading: Component wrapped with Spinner that shows after 500ms delay
    """
    return dcc.Loading(
        children=component,
        type="default",
        style={"display": "none"},
        delay_show=500,
    )


class LoadingHelper:
    """Helper class wrapper for loading indicator functions."""

    @staticmethod
    def wrap_with_loading(component):
        return wrap_with_loading(component)