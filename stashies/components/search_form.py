import dash_bootstrap_components as dbc


class SearchBar:
    def layout(self) -> dbc.Row:
        return dbc.Row(
            [
                dbc.Form(
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.InputGroup(
                                    [
                                        dbc.InputGroupText("Category"),
                                        dbc.Select(
                                            id="category-select",
                                            options=[
                                                {
                                                    "label": "Yarns",
                                                    "value": "yarns",
                                                },
                                                {
                                                    "label": "Yarn Companies",
                                                    "value": "yarn_companies",
                                                },
                                                {
                                                    "label": "Personal Stash",
                                                    "value": "personal_stash",
                                                },
                                                {
                                                    "label": "Projects",
                                                    "value": "projects",
                                                },
                                                {
                                                    "label": "Patterns",
                                                    "value": "patterns",
                                                },
                                            ],
                                            value="yarns",
                                            placeholder="Select Category",
                                        ),
                                    ]
                                ),
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    dbc.InputGroup(
                                        [
                                            dbc.InputGroupText("Search"),
                                            dbc.Input(
                                                placeholder="Flux Capacitor",
                                                id="search-query",
                                            ),
                                        ]
                                    ),
                                ],
                                width="auto",
                            ),
                            dbc.Col(
                                dbc.InputGroup(
                                    [
                                        dbc.InputGroupText("Sort By"),
                                        dbc.Select(
                                            id="search-sort",
                                            options=[
                                                {
                                                    "label": "Best Match",
                                                    "value": "best_match",
                                                },
                                                {
                                                    "label": "Highest Rating",
                                                    "value": "high_rating",
                                                },
                                                {
                                                    "label": "Most Projects",
                                                    "value": "most_projects",
                                                },
                                            ],
                                            value="best_match",
                                            placeholder="Best Match",
                                        ),
                                    ]
                                ),
                                width="auto",
                            ),
                            dbc.Col(
                                dbc.Button("Submit", color="primary"), width="auto"
                            ),
                        ],
                        justify="center",
                    ),
                )
            ],
            className="justify-content-center align-items-center",
        )
