from typing import Any, Callable, Iterable, List, Optional


def find(predicate: Callable, sequence: Iterable) -> Optional[Any]:
    """
    Find the first element in a sequence that matches the predicate.

    ??? Hint "Example Usage:"
        ```python
        member = find(lambda m: m.name == "UserName", guild.members)
        ```
    Args:
        predicate: A callable that returns a boolean value
        sequence: A sequence to be searched

    Returns:
        A match if found, otherwise None

    """
    for el in sequence:
        if predicate(el):
            return el
    return None


def find_all(predicate: Callable, sequence: Iterable) -> List[Any]:
    """
    Find all elements in a sequence that match the predicate.

    ??? Hint "Example Usage:"
        ```python
        members = find_all(lambda m: m.name == "UserName", guild.members)
        ```
    Args:
        predicate: A callable that returns a boolean value
        sequence: A sequence to be searched

    Returns:
        A list of matches

    """
    return [el for el in sequence if predicate(el)]


def get(sequence: Iterable, **kwargs: Any) -> Optional[Any]:
    """
    Find the first element in a sequence that matches all attrs.

    ??? Hint "Example Usage:"
        ```python
        channel = get(guild.channels, nsfw=False, category="General")
        ```

    Args:
        sequence: A sequence to be searched
        kwargs: Keyword arguments to search the sequence for

    Returns:
        A match if found, otherwise None
    """
    if not kwargs:
        return sequence[0]

    for el in sequence:
        if any(not hasattr(el, attr) for attr in kwargs.keys()):
            continue
        if all(getattr(el, attr) == value for attr, value in kwargs.items()):
            return el
    return None


def get_all(sequence: Iterable, **kwargs: Any) -> List[Any]:
    """
    Find all elements in a sequence that match all attrs.

    ??? Hint "Example Usage:"
        ```python
        channels = get_all(guild.channels, nsfw=False, category="General")
        ```

    Args:
        sequence: A sequence to be searched
        kwargs: Keyword arguments to search the sequence for

    Returns:
        A list of matches
    """
    if not kwargs:
        return sequence

    matches = []
    for el in sequence:
        if any(not hasattr(el, attr) for attr in kwargs.keys()):
            continue
        if all(getattr(el, attr) == value for attr, value in kwargs.items()):
            matches.append(el)
    return matches
