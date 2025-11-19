from dash import html
import dash_bootstrap_components as dbc


class SearchResults:
    def layout(self) -> dbc.Row:
        return dbc.Row(
            [
                dbc.Accordion(
                    [
                        dbc.AccordionItem(
                            [
                                html.P("This is the content of the first section"),
                                dbc.Button("Click here"),
                            ],
                            title="Item 1",
                        ),
                        dbc.AccordionItem(
                            [
                                html.P("This is the content of the second section"),
                                dbc.Button("Don't click me!", color="danger"),
                            ],
                            title="Item 2",
                        ),
                        dbc.AccordionItem(
                            "This is the content of the third section",
                            title="Item 3",
                        ),
                    ],
                )
            ],
            className="justify-content-center align-items-center",
        )
