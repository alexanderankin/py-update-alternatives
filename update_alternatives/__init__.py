from argparse import ArgumentParser
from dataclasses import dataclass, fields, field
from enum import Enum
from pathlib import Path
from typing import TypeVar, Type, Optional, Dict, Any, List

IPT = TypeVar('IPT')


def ignore_properties(cls: Type[IPT], dict_: any) -> IPT:
    """omits extra fields like @JsonIgnoreProperties(ignoreUnknown = true)"""
    if isinstance(dict_, cls): return dict_  # noqa
    class_fields = {f.name for f in fields(cls)}
    filtered = {k: v for k, v in dict_.items() if k in class_fields}
    return cls(**filtered)


class Command(Enum):
    # --install link name path priority [--slave link name path]...
    install = 'install'
    # --set name path
    set = 'set'
    # --remove name path
    remove = 'remove'
    # --remove-all name
    remove_all = 'remove_all'
    # --all (call --config on all alternatives)
    all = 'all'
    # --auto name
    auto = 'auto'
    # --display name
    display = 'display'
    # --get-selections (print to stdout)
    get_selections = 'get_selections'
    # --set-selections (read from stdin)
    set_selections = 'set_selections'
    # --query name
    query = 'query'
    # --list name
    list = 'list'
    # --config name
    config = 'config'


@dataclass
class Installation:
    link: str
    name: str
    path: str
    priority: int


@dataclass
class NameAndPath:
    name: str
    path: str


@dataclass
class Name:
    name: str


COMMANDS_TYPES: Dict[Command, Optional[Type[Any]]] = {
    Command.install: Installation,
    Command.set: NameAndPath,
    Command.remove: NameAndPath,
    Command.remove_all: Name,
    Command.all: None,
    Command.auto: Name,
    Command.display: Name,
    Command.get_selections: None,
    Command.set_selections: None,
    Command.query: Name,
    Command.list: Name,
    Command.config: Name,
}


# noinspection SpellCheckingInspection
@dataclass
class Options:
    altdir: Optional[str] = None
    admindir: Optional[str] = None
    instdir: Optional[str] = None
    root: Optional[str] = None
    log: Optional[str] = None
    force: Optional[bool] = None
    skip_auto: Optional[bool] = None
    quiet: Optional[bool] = None
    verbose: Optional[bool] = None
    debug: Optional[bool] = None


# noinspection PyMethodMayBeStatic
@dataclass
class AlternativeUpdater:
    options: Options = field(default_factory=Options)

    def install(self, installation: Installation):
        print(f'installation: {installation}')

    def set(self, name_and_path: NameAndPath):
        print(f'set: name_and_path: {name_and_path}')

    def remove(self, name_and_path: NameAndPath):
        print(f'remove: name_and_path: {name_and_path}')

    def remove_all(self, name: Name):
        print(f'remove_all: name: {name}')

    def all(self):
        print(f'all')

    def auto(self, name: Name):
        print(f'auto: name: {name}')

    def display(self, name: Name):
        print(f'display: name: {name}')

    def get_selections(self):
        print(f'get_selections')

    def set_selections(self):
        print(f'set_selections')

    def query(self, name: Name):
        print(f'query: name: {name}')

    def list(self, name: Name):
        print(f'list: name: {name}')

    def config(self, name: Name):
        print(f'config: name: {name}')

    @dataclass
    class Query:
        name: str
        link: str
        status: str
        best: str
        value: str
        secondaries: List['AlternativeUpdater.Query.Secondary']
        alternatives: List['AlternativeUpdater.Query.Alternative']

        @dataclass
        class Secondary:
            name: str
            link: str

        @dataclass
        class Alternative:
            location: str
            priority: int
            secondaries: List['AlternativeUpdater.Query.Secondary']

        def stringify(self) -> str:
            lines = [self.status, self.link]
            for s in self.secondaries:
                lines.append(s.name)
                lines.append(s.link)
            lines.append('')
            for a in self.alternatives:
                lines.append(a.location)
                lines.append(str(a.priority))
                for s in a.secondaries:
                    lines.append(s.link)
            lines.append('')
            lines.append('')
            return '\n'.join(lines)

        @staticmethod
        def parse(path: Path) -> 'AlternativeUpdater.Query':
            lines = [i.strip() for i in path.read_text('utf-8').split('\n')]

            # @formatter:off
            i = 0
            status = lines[i]; i += 1  # noqa
            link = lines[i]; i += 1  # noqa
            # @formatter:on
            secondaries: List[AlternativeUpdater.Query.Secondary] = []
            while lines[i]:
                secondaries.append(AlternativeUpdater.Query.Secondary(
                    name=lines[i],
                    link=lines[i + 1]
                ))
                i += 2
            i += 1  # empty line after children

            alternatives: List[AlternativeUpdater.Query.Alternative] = []
            while lines[i]:
                alt_sec: List['AlternativeUpdater.Query.Secondary'] = []
                alternatives.append(AlternativeUpdater.Query.Alternative(
                    location=lines[i],
                    priority=int(lines[i + 1]),
                    secondaries=alt_sec
                ))
                i += 2
                while lines[i]:
                    alt_sec.append(
                        AlternativeUpdater.Query.Secondary(
                            name=Path(lines[i]).name,
                            link=lines[i]
                        )
                    )
                    i += 1
                i += 1

            return AlternativeUpdater.Query(
                name=path.name,
                link=link,
                status=status,
                best=(alternatives[-1]).location,
                value=str(Path(link).readlink()),
                secondaries=secondaries,
                alternatives=alternatives,
            )


def run():
    parser = ArgumentParser()

    parser.add_argument('--altdir')  # directory
    parser.add_argument('--admindir')  # directory
    parser.add_argument('--instdir')  # directory
    parser.add_argument('--root')  # directory
    parser.add_argument('--log')  # file
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--skip-auto', action='store_true')
    parser.add_argument('--quiet', action='store_true')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--debug', action='store_true')

    command = parser.add_subparsers(dest='command', required=True)
    commands = {c.value: command.add_parser(c.value) for c in Command}
    # print(commands)
    args = parser.parse_args()

    vars_args = vars(args)
    print(ignore_properties(Options, vars_args))


if __name__ == '__main__':
    run()
