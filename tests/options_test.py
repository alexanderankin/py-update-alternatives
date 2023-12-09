from pathlib import Path

import pytest

from update_alternatives import Options

SAMPLES = Path(__file__).parent.joinpath('sample-run-command-files')


@pytest.mark.parametrize('sample,expected', [
    ['blank.toml', Options()],
    ['complete.toml', Options(
        altdir='alt-dir',
        admindir='admin-dir',
        instdir='inst-dir',
        root='root',
        log='log',
        force=True,
        skip_auto=True,
        quiet=True,
        verbose=False,
        debug=False,
    )],
])
def test_options_from_toml(sample, expected):
    assert expected == Options.from_toml(SAMPLES.joinpath(sample).read_text())


@pytest.mark.parametrize('original,argument,expected', [
    [Options(), Options(), Options()],
    [Options(), Options(altdir='alt'), Options(altdir='alt')],
    [Options(altdir='alt'), Options(), Options(altdir='alt')],
    [Options(debug=False), Options(force=True), Options(debug=False, force=True)],
])
def test_option_combine_with(original, argument, expected):
    assert expected == original.combine_with(argument)
