from pathlib import Path

import pytest

from update_alternatives import AlternativeUpdater


@pytest.fixture
def alternative_updater():
    return AlternativeUpdater()


@pytest.mark.parametrize("sample",
                         [
                             'cc',
                             'which',
                             'vim',
                             'python'
                         ])
def test(sample, alternative_updater):
    sample_path = Path(__file__).parent.joinpath('sample-alternatives-files', sample)
    round_trip = alternative_updater.Query.parse(sample_path).stringify()
    assert round_trip == sample_path.read_text()
