from os import environ
from pathlib import Path
from subprocess import run as subprocess_run, PIPE

PATH = Path(__file__).parent.parent.joinpath('update_alternatives')


def cli_usage(*args: str):
    return subprocess_run(
        ['python', str(PATH)] + list(args),
        stdout=PIPE,
        stderr=PIPE,
        encoding='utf-8',
        env=environ,
    )


def test_basic():
    run = cli_usage()
    assert 'usage:' in run.stderr


def test_get_selections():
    run = cli_usage('get-selections')
    assert 'get_selections' in run.stdout
