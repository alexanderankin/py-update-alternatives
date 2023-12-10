import textwrap
from pathlib import Path

import pytest

from update_alternatives import AlternativeUpdater


@pytest.fixture
def alternative_updater():
    return AlternativeUpdater()


@pytest.mark.parametrize(
    'sample, expected',
    [
        [
            'cc',
            AlternativeUpdater.Query(
                name='cc',
                link='/usr/bin/cc',
                status='auto',
                best='/usr/bin/gcc',
                value='/etc/alternatives/cc',
                secondaries=[
                    AlternativeUpdater.Query.Secondary(
                        name='cc.1.gz',
                        link='/usr/share/man/man1/cc.1.gz'
                    )
                ],
                alternatives=[
                    AlternativeUpdater.Query.Alternative(
                        location='/usr/bin/gcc',
                        priority=20,
                        secondaries=[AlternativeUpdater.Query.Secondary(
                            name='gcc.1.gz',
                            link='/usr/share/man/man1/gcc.1.gz')
                        ]
                    )
                ]
            ),
        ],
        [
            'which',
            AlternativeUpdater.Query(
                name='which',
                link='/usr/bin/which',
                status='auto',
                best='/usr/bin/which.debianutils',
                value='/etc/alternatives/which',
                secondaries=[
                    AlternativeUpdater.Query.Secondary(
                        name='which.1.gz',
                        link='/usr/share/man/man1/which.1.gz'),
                    AlternativeUpdater.Query.Secondary(
                        name='which.de1.gz',
                        link='/usr/share/man/de/man1/which.1.gz'),
                    AlternativeUpdater.Query.Secondary(
                        name='which.es1.gz',
                        link='/usr/share/man/es/man1/which.1.gz'),
                    AlternativeUpdater.Query.Secondary(
                        name='which.fr1.gz',
                        link='/usr/share/man/fr/man1/which.1.gz'),
                    AlternativeUpdater.Query.Secondary(
                        name='which.it1.gz',
                        link='/usr/share/man/it/man1/which.1.gz'),
                    AlternativeUpdater.Query.Secondary(
                        name='which.ja1.gz',
                        link='/usr/share/man/ja/man1/which.1.gz'),
                    AlternativeUpdater.Query.Secondary(
                        name='which.pl1.gz',
                        link='/usr/share/man/pl/man1/which.1.gz'),
                    AlternativeUpdater.Query.Secondary(
                        name='which.sl1.gz',
                        link='/usr/share/man/sl/man1/which.1.gz')],
                alternatives=[
                    AlternativeUpdater.Query.Alternative(
                        location='/usr/bin/which.debianutils', priority=0,
                        secondaries=[
                            AlternativeUpdater.Query.Secondary(
                                name='which.debianutils.1.gz',
                                link='/usr/share/man/man1/which.debianutils.1.gz'),
                            AlternativeUpdater.Query.Secondary(
                                name='which.debianutils.1.gz',
                                link='/usr/share/man/de/man1/which.debianutils.1.gz'),
                            AlternativeUpdater.Query.Secondary(
                                name='which.debianutils.1.gz',
                                link='/usr/share/man/es/man1/which.debianutils.1.gz'),
                            AlternativeUpdater.Query.Secondary(
                                name='which.debianutils.1.gz',
                                link='/usr/share/man/fr/man1/which.debianutils.1.gz'),
                            AlternativeUpdater.Query.Secondary(
                                name='which.debianutils.1.gz',
                                link='/usr/share/man/it/man1/which.debianutils.1.gz'),
                            AlternativeUpdater.Query.Secondary(
                                name='which.debianutils.1.gz',
                                link='/usr/share/man/ja/man1/which.debianutils.1.gz'),
                            AlternativeUpdater.Query.Secondary(
                                name='which.debianutils.1.gz',
                                link='/usr/share/man/pl/man1/which.debianutils.1.gz'),
                            AlternativeUpdater.Query.Secondary(
                                name='which.debianutils.1.gz',
                                link='/usr/share/man/sl/man1/which.debianutils.1.gz')
                        ]
                    )
                ]
            )
        ],
        [
            'vim',
            AlternativeUpdater.Query(
                name='vim',
                link='/usr/bin/vim',
                status='auto',
                best='/usr/bin/vim.basic',
                value='/etc/alternatives/vim',
                alternatives=[
                    AlternativeUpdater.Query.Alternative(
                        location='/usr/bin/vim.basic',
                        priority=30,
                    ),
                ]
            )
        ],
        [
            'python',
            AlternativeUpdater.Query(
                name='python',
                link='/usr/local/bin/python',
                status='auto',
                best='/usr/bin/python3.11',
                value='/etc/alternatives/python',
                alternatives=[
                    AlternativeUpdater.Query.Alternative(
                        location='/usr/bin/python3.10',
                        priority=310,
                    ),
                    AlternativeUpdater.Query.Alternative(
                        location='/usr/bin/python3.11',
                        priority=311,
                    ),
                ]
            )
        ],
    ]
)
def test(sample: str, expected: AlternativeUpdater.Query, alternative_updater):
    sample_path = Path(__file__).parent.joinpath('sample-alternatives-files', sample)

    query = alternative_updater.Query.parse(sample_path)
    assert query == expected

    round_trip = query.stringify()
    assert round_trip == sample_path.read_text()


@pytest.mark.parametrize(
    'sample, expected',
    [
        [
            'python',
            """
                Name: python
                Link: /usr/local/bin/python
                Status: auto
                Best: /usr/bin/python3.11
                Value: /etc/alternatives/python
                
                Alternative: /usr/bin/python3.10
                Priority: 310
                
                Alternative: /usr/bin/python3.11
                Priority: 311
                """
        ],
    ]
)
def test_to_query(sample: str,
                  expected: str,
                  alternative_updater: AlternativeUpdater):
    expected = textwrap.dedent(expected).strip()
    sample_path = Path(__file__).parent.joinpath('sample-alternatives-files', sample)

    query = alternative_updater.Query.parse(sample_path)
    actual = query.to_query().strip()
    assert expected == actual
