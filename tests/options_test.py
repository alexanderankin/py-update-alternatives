import shutil
from pathlib import Path

import pytest

from update_alternatives import Options, read_options, OPTIONS_LOCATIONS

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
    [Options(altdir='blah'), Options(altdir='alt'), Options(altdir='alt')],
    [Options(debug=False), Options(force=True), Options(debug=False, force=True)],
])
def test_option_combine_with(original, argument, expected):
    assert expected == original.combine_with(argument)


def test_multiple_locations(tmp_path: Path):
    OPTIONS_LOCATIONS.clear()
    OPTIONS_LOCATIONS.append(tmp_path)
    assert Options() == read_options()

    OPTIONS_LOCATIONS.append(tmp_path.joinpath('partial.toml'))
    shutil.copy(src=SAMPLES.joinpath('partial.toml'), dst=tmp_path.joinpath('partial.toml'))
    assert Options(admindir='admin-dir') == read_options()

    OPTIONS_LOCATIONS.append(tmp_path.joinpath('partial2.toml'))
    shutil.copy(src=SAMPLES.joinpath('partial2.toml'), dst=tmp_path.joinpath('partial2.toml'))
    assert Options(admindir='admin2-dir', log='log2') == read_options()

    OPTIONS_LOCATIONS.clear()
    OPTIONS_LOCATIONS.append(tmp_path.joinpath('partial2.toml'))
    OPTIONS_LOCATIONS.append(tmp_path.joinpath('partial.toml'))
    assert Options(admindir='admin-dir', log='log2') == read_options()
