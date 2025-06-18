# preCICE Config-Format

`config-format` is a tool meant to format preCICE configurations consistently. A uniform order simplifies cooperation debugging.

## Installation options

Install directly from PyPi using [pipx](https://pipx.pypa.io/stable/) or via pip:

```console
pipx install precice-config-format
```

## Usage

To format one or more preCICE configuration files in-place:

```console
precice-config-format FILE ...
```

The script returns with exit code 0 on success, 1 on error, and 2 if a file was modified.

## pre-commit hook

To use this script as a pre-commit hook select [a tag](https://github.com/precice/config-format/tags) and add:

```yaml
-   repo: https://github.com/precice/config-format
    rev: ''  # Use the tag you want to use
    hooks:
    -   id: precice-config-format
```

To exclude directories, use `exclude:`

```yaml
-   repo: https://github.com/precice/config-format
    rev: ''  # Use the tag you want to use
    hooks:
    -   id: precice-config-format
        exclude: '^thridparty' # optionally exclude directories here
```
