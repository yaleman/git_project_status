default: help

help:
    just --list

check: fmt lint type test

type:
    uv run mypy --strict $(basename $(pwd)) tests

lint:
    uv run ruff check $(basename $(pwd)) tests

test:
    uv run pytest

fmt:
    uv run ruff format $(basename $(pwd)) tests