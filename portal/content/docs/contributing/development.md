---
title: Development
sidebar:
  order: 1
---

Open Data Editor is written in PySide6, the official Python module from the [Qt for Python project](https://wiki.qt.io/Qt_for_Python), which provides access to the complete Qt 6.0+ framework.

You can refer to the [Official Documentation](https://doc.qt.io/qtforpython-6/) to learn more about it. (And it's a handy documentation to bookmark!)

## Prerequisites

We are using 3.11. To start working on the project you need the following dependencies in your machine:

- Python 3.11
- python3.11-dev (For PyInstaller)
- Node 18+ (For this documentation page)

## Enviroment

As common practice with all python project, you should create a Virtual Environment (using your favorite tool!) to install all the requirements.

If using Python's default virtual env you can execute:

```bash
python -m venv venv
source venv/bin/activate
```

## Makefile

The project provides a `Makefile` with some usefull commands.

```bash
make help
```

:::note
All make commands that executes python commands (like `make start` or `make install`) requires a manually activated virtualenv to run.
:::

## Installation

To start working on the project install the dependencies:

```bash
make install
```

> Make install will also cd into the `portal` folder and install all the dependencies for the astro project.

## Codebase

To work on the application:

```bash
make start
```

## Documentation

Documentation is written with [Starlight](https://starlight.astro.build/) (in the `portal` directory). The source articles are in the `portal/content/docs` directory. To start a live-reload server and work on the docs:

```bash
make docs
```

It will be automatically published on CloudFlare when merged to the `main` branch with previews available for pull requests.
