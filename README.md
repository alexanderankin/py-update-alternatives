# `py-update-alternatives`

[update-alternatives][debian wiki] ([man page][man page]) implementation:

* for multiple platforms
* in python

[debian wiki]: https://wiki.debian.org/DebianAlternatives
[man page]: https://man7.org/linux/man-pages/man1/update-alternatives.1.html

## usage

Basically, it is the same usage as `update-alternatives`,
except that the commands are not named with the `--` prefix,
as argparse does not support that.

Secondary (slave) links creation is not supported.
Aiming for backwards compatibility where those exist,
just not creation of new secondary links.

### rc files

Additionally, this supports a "run command" style file.
It will read these toml files before interpreting cli args
(which are overridable in programmatic usage):

```python
from pathlib import Path

# in order of lowest to highest priority
OPTIONS_LOCATIONS = [
    Path('etc', '.py-update-alternatives.toml'),
    Path.home().joinpath('.py-update-alternatives.toml'),
]

# override in programmatic usage
import update_alternatives
update_alternatives.OPTIONS_LOCATIONS = OPTIONS_LOCATIONS
```

the order of priority
 
1. cli arguments override all others
2. home folder if an option is not specified
3. `/etc` folder if an option is still not found
4. some built-in defaults (see test cases for rc files)  


## development

```shell
test -d ./.venv && python -m venv .venv
test -d ./.venv/bin && . .venv/bin/activate || . .venv/Scripts/activate
pip install -e .[dev]
```

```shell
pytest
#pytest --cov-report term --cov update_alternatives
#pytest --cov-report term --cov update_alternatives --cov-fail-under=80
#pytest --cov-report html --cov update_alternatives
ruff check
```
