"""Tests for the main module."""

import pytest

from words_on_paper.main import hello_world


class TestHelloWorld:
    """Test cases for hello_world function."""

    def test_hello_world_default(self) -> None:
        """Test hello_world with default parameter."""
        result = hello_world()
        assert result == "Hello, World!"

    def test_hello_world_with_name(self) -> None:
        """Test hello_world with a custom name."""
        result = hello_world("Alice")
        assert result == "Hello, Alice!"

    def test_hello_world_with_empty_string(self) -> None:
        """Test hello_world with an empty string."""
        result = hello_world("")
        assert result == "Hello, !"

    @pytest.mark.parametrize(
        "name,expected",
        [
            ("Bob", "Hello, Bob!"),
            ("Charlie", "Hello, Charlie!"),
            ("Diana", "Hello, Diana!"),
        ],
    )
    def test_hello_world_parametrized(self, name: str, expected: str) -> None:
        """Test hello_world with multiple inputs."""
        result = hello_world(name)
        assert result == expected
