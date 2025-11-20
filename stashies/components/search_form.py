import dash_bootstrap_components as dbc


SEARCH_BAR = dbc.Row(
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
                        dbc.Button("Submit", id="search-button", color="primary"),
                        width="auto",
                    ),
                ],
                justify="center",
            ),
        ),
    ],
    className="justify-content-center align-items-center",
)
'''
A search bar component built with Dash Bootstrap Components that provides filtering and search functionality with multiple input controls.

Component Structure:
- Main container: dbc.Row with center alignment
  - Contains a dbc.Form for form functionality
    - Inner dbc.Row with multiple columns containing input groups
      - Category selection dropdown
      - Search query input field  
      - Sort options dropdown
      - Submit button

Input Controls and Their IDs:

category-select (Select dropdown)
  - Purpose: Allows users to filter searches by content category
  - Options:
    * Yarns - Search through yarn database
    * Yarn Companies - Search yarn manufacturers/brands  
    * Personal Stash - Search user's personal yarn collection
    * Projects - Search knitting/crochet projects
    * Patterns - Search knitting/crochet patterns

search-query (Text Input)
  - Purpose: Main search input field for entering text queries
  - Placeholder: "Flux Capacitor" (example search term)

search-sort (Select dropdown) 
  - Purpose: Controls how search results are sorted
  - Options:
    * Best Match - Default relevance-based sorting
    * Highest Rating - Sort by user ratings/score
    * Most Projects - Sort by number of associated projects

search-button (Button)
  - Purpose: Triggers the search operation with selected parameters
  - Style: Primary colored submit button

'''
