"""Main module for the project."""


def hello_world(name: str = "World") -> str:
    """
    Return a greeting message.

    Args:
        name: The name to greet. Defaults to "World".

    Returns:
        A greeting string.

    Example:
        >>> hello_world("Alice")
        'Hello, Alice!'
    """
    return f"Hello, {name}!"


if __name__ == "__main__":
    result = hello_world("Developer")
    print(result)
