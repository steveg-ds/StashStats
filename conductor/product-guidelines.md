# Product Guidelines: StashStats

## Prose & Code Documentation Style
- **Strict Pythonic**: Maintain explicit, clear, and comprehensive docstrings for all classes, methods, and functions. Code readability and clean docstrings are required.
- Note: External communication rules (like terse caveman-style responses) apply only to agent-human interactions as defined in AGENTS.md, whereas codebase prose, comments, and documentation must remain standard and grammatically correct.

## UI/UX Styling & Branding
- **Bootstrap Darkly**: Build upon the existing dark theme (`dbc.themes.DARKLY`) to maintain consistency in styling, fonts, and colors across all layout elements.
- **Clean Layouts**: Align all components (search, cards, analytics) neatly within responsive grids.

## Interaction & UX Principles
- **Sync Indicators**: Provide clear, visible loading feedback (such as spinners or progress bars) during Ravelry API synchronization and network operations.
- **Modal-based Editing**: Use interactive modals for modifying stash entry quantities, logging usage history, and inputting metadata, ensuring a clean, focused user experience.
