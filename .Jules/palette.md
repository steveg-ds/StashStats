## 2026-06-11 - [Dash Bootstrap Components Accessibility]
**Learning:** `dash_bootstrap_components.Button` does not support `aria_label` or `aria-label` as a direct keyword argument. It also does not support general wildcard attributes.
**Action:** Use the `title` attribute for tooltips and basic accessibility on `dbc.Button`, or wrap it in an `html.Div` with `aria-label` if more complex screen reader support is needed. Standard `html.Img` supports `alt` correctly.
