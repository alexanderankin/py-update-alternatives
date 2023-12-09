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

Additionally, this supports a "run command" style file.


## development

```shell
test -d ./.venv && python -m venv .venv
test -d ./.venv/bin && . .venv/bin/activate || . .venv/Scripts/activate
pip install -e .[test]
```

```shell
pytest
```
