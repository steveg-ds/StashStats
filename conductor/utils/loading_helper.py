from dash import dcc
import dash_bootstrap_components as dbc

def wrap_with_loading(component, delay=500):
    """
    Wraps a Dash component with a loading indicator.
    
    Args:
        component: The Dash component to wrap.
        delay: The delay in milliseconds before showing the loading indicator (default: 500).
    
    Returns:
        A Dash Loading component containing the wrapped component.
    """
    return dcc.Loading(
        children=component,
        children_spinner=dbc.Spinner(),
        delay_show=delay
    )