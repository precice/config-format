# preCICE Config-Format

`config-format` is a tool meant to format preCICE configurations consistently. A uniform order simplifies cooperation debugging.

## Installation options

Install directly from PyPi using [pipx](https://pipx.pypa.io/stable/) or via pip:

```
pipx install precice-config-format
```

## Usage

To format a given preCICE configuration file in-place:

```
precice-config-format <CONFIG-FILE>
```

Consider using the [preCICE pre-commit hooks](https://github.com/precice/precice-pre-commit-hooks) to simplify using this tool.
