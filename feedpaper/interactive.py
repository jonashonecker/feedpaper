from __future__ import annotations

from feedpaper.exclusions import normalize_titles


def choose_excludes(feed_titles, current_excluded):
    """Show a checkbox list of blogs and return the titles to exclude.

    Currently-excluded blogs are pre-checked. Returns the selected titles as a
    list, or ``None`` if the user cancels.
    """
    import questionary

    current = normalize_titles(current_excluded)
    if not feed_titles:
        print("No subscribed blogs found.")
        return []

    choices = [
        questionary.Choice(title=t, checked=t.strip().lower() in current)
        for t in feed_titles
    ]
    return questionary.checkbox(
        "Select blogs to exclude (space to toggle, enter to save):",
        choices=choices,
    ).ask()
