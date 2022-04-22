# Troubleshooting

## Type checking
Some modules might not define type which leads to error when using `mypy`.
To suppress those warnings use `# type: ignore` after the import statement of the affected library.
More information [here](https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports).

## Format checking
When using `:math` in doc strings you might encounter `W605 invalid escape sequence` errors.
You can ignore this error by globally by passing `--ignore=W605` or on a per file basis in the config file `.flask8`
More information [here](https://flake8.pycqa.org/en/3.1.1/user/ignoring-errors.html#ignoring-errors-with-flake8)