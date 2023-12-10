import os
from argparse import ArgumentParser
from dataclasses import dataclass, fields, field, asdict
from enum import Enum
from pathlib import Path
from typing import TypeVar, Type, Optional, Dict, Any, List, Union

try:
    import tomllib
except ImportError:
    # https://stackoverflow.com/a/75677482
    from pip._vendor import tomli as tomllib  # noqa

IPT = TypeVar('IPT')


def ignore_properties(cls: Type[IPT], dict_: any) -> IPT:
    """omits extra fields like @JsonIgnoreProperties(ignoreUnknown = true)"""
    if isinstance(dict_, cls): return dict_  # noqa
    class_fields = {f.name for f in fields(cls)}
    filtered = {k: v for k, v in dict_.items() if k in class_fields}
    return cls(**filtered)


COMMAND_REPLACEMENTS = {
    'remove-all': 'remove_all',
    'get-selections': 'get_selections',
    'set-selections': 'set_selections',
}


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

    def as_alternative(self) -> 'AlternativeUpdater.Query.Alternative':
        return AlternativeUpdater.Query.Alternative(
            location=self.path,
            priority=self.priority
        )


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

    @staticmethod
    def from_toml(sample_text):
        return ignore_properties(Options, tomllib.loads(sample_text))

    def combine_with(self, argument: 'Options') -> 'Options':
        """self is lower priority than argument"""
        me = {k: v for (k, v) in asdict(self).items() if v is not None}
        you = {k: v for (k, v) in asdict(argument).items() if v is not None}
        me.update(you)
        return Options(**me)


# in order of lowest to highest priority
OPTIONS_LOCATIONS = [
    Path('etc', '.py-update-alternatives.toml'),
    Path.home().joinpath('.py-update-alternatives.toml'),
]


def read_options(locations: Optional[List[Union[str, Path]]] = None,
                 final_options: Optional[Options] = None):
    o = Options()
    locations = locations or OPTIONS_LOCATIONS
    for location in locations:
        if location.exists() and location.is_file():
            o = o.combine_with(Options.from_toml(location.read_text('utf-8')))
    if final_options:
        o = o.combine_with(final_options)
    return o


def _readlink_f(path: Path) -> Path:
    while path.is_symlink():
        path = path.readlink()
    return path


# noinspection PyMethodMayBeStatic
@dataclass
class AlternativeUpdater:
    options: Options = field(default_factory=Options)

    def install(self, installation: Installation):
        """untested"""
        admin_path = Path(self.options.admindir).joinpath(installation.name)
        alt_path = Path(self.options.altdir).joinpath(installation.name)

        if not admin_path.exists():
            query = AlternativeUpdater.Query(
                name=installation.name,
                link=installation.link,
                status='auto',
                best=installation.path,
                value=installation.path,
                alternatives=[installation.as_alternative()]
            )
            # if new alternative is the only one, link it
            # but: if you install and there are others, don't
            # todo confirm what update-alternatives does and match
            # inner link:
            os.link(src=alt_path, dst=query.best)
            # outer link:
            os.link(src=installation.link, dst=alt_path)
        else:
            query = AlternativeUpdater.Query.parse(admin_path)

            # allow the user to manipulate the outer link here
            if query.link != installation.link:
                # inform user of change
                print(f'update_alternatives: renaming {query.name} link '
                      f'from {query.link} to {installation.link}')
                # remove old
                os.remove(query.link)
                # create new
                os.link(src=installation.link, dst=alt_path)
                # update database
                query.link = installation.link

            # search existing alternatives for matching inner link
            # if found - update, else append
            found = False
            for alt in query.alternatives:
                if alt.location == installation.path:
                    alt.priority = installation.priority
                    found = True
                    break
            if not found:
                query.alternatives.append(installation.as_alternative())

        admin_path.write_text(query.stringify())

    def set(self, name_and_path: NameAndPath):
        print(f'set: name_and_path: {name_and_path}')

    def remove(self, name_and_path: NameAndPath):
        print(f'remove: name_and_path: {name_and_path}')

    def remove_all(self, name: Name):
        print(f'remove_all: name: {name}')

    def all(self):
        print(f'all')

    def auto(self, name: Name):
        """untested"""
        q = self._query(name.name)
        q.status = 'auto'
        highest = q.get_best()
        self.set(NameAndPath(name=name.name, path=highest.location))

    def display(self, name: Name):
        print(f'display: name: {name}')

    def get_selections(self):
        print(f'get_selections')

    def set_selections(self):
        print(f'set_selections')

    def _query(self, name: str):
        path = Path(self.options.admindir).joinpath(name)
        if not path.exists():
            raise Exception(f'no such alternative: {name}')
        query = AlternativeUpdater.Query.parse(path)
        return query

    def query(self, name: Name):
        print(self._query(name.name).to_query())

    def list(self, name: Name):
        print(f'list: name: {name}')

    def config(self, name: Name):
        print(f'config: name: {name}')

    @dataclass
    class Query:
        name: str
        link: str
        status: str
        # todo make this a property
        best: str
        value: str
        secondaries: List['AlternativeUpdater.Query.Secondary'] = field(default_factory=list)
        alternatives: List['AlternativeUpdater.Query.Alternative'] = field(default_factory=list)

        @dataclass
        class Secondary:
            name: str
            link: str

        @dataclass
        class Alternative:
            location: str
            priority: int
            secondaries: List['AlternativeUpdater.Query.Secondary'] = field(default_factory=list)

            @staticmethod
            def best(*alts: 'AlternativeUpdater.Query.Alternative') \
                    -> Optional['AlternativeUpdater.Query.Alternative']:
                return next(iter(sorted(alts, key=lambda x: x.priority, reverse=True)), None)

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

        def to_query(self) -> str:
            lines = [
                f'Name: {self.name}',
                f'Link: {self.link}',
                f'Status: {self.status}',
                f'Best: {self.best}',
                f'Value: {_readlink_f(Path(self.link))}',
            ]

            for a in (self.alternatives or []):
                lines.append('')
                lines.append(f'Alternative: {a.location}')
                lines.append(f'Priority: {a.priority}')

            return '\n'.join(lines)

        def get_best(self) -> Optional[Alternative]:
            return AlternativeUpdater.Query.Alternative.best(*self.alternatives)

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
                for j in range(len(secondaries)):
                    alt_sec.append(
                        AlternativeUpdater.Query.Secondary(
                            name=Path(lines[i]).name,
                            link=lines[i]
                        )
                    )
                    i += 1
                # i += 1

            return AlternativeUpdater.Query(
                name=path.name,
                link=link,
                status=status,
                best=AlternativeUpdater.Query.Alternative.best(*alternatives).location,
                value=str(_readlink_f(Path(link))),
                secondaries=secondaries,
                alternatives=alternatives,
            )


def run(args: Optional[List[str]] = None):
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

    # command sub parser
    command = parser.add_subparsers(dest='command', required=True)
    # command parsers
    commands = {c: command.add_parser(c.value) for c in Command}
    # print(commands)

    # add in arguments
    for cmd_parser_e in commands.items():
        cmd = cmd_parser_e[0]
        cmd_parser = cmd_parser_e[1]
        cmd_type = COMMANDS_TYPES[cmd]
        if cmd_type is None: continue  # noqa
        # noinspection PyDataclass
        cmd_fields = fields(cmd_type)
        for f in cmd_fields:
            cmd_parser.add_argument(f.name, type=f.type)

    if args is None:
        import sys
        args = sys.argv[1:]

    args = [COMMAND_REPLACEMENTS.get(a, a) for a in args]
    args = parser.parse_args(args)
    selected_command = Command[args.command]
    argument_type = COMMANDS_TYPES[selected_command]
    vars_args = vars(args)

    options = ignore_properties(Options, vars_args)
    options = read_options(final_options=options)
    # method arguments
    m_args = [] if argument_type is None \
        else [ignore_properties(argument_type, vars_args)]

    getattr(AlternativeUpdater(options), selected_command.value)(*m_args)


if __name__ == '__main__':
    run()
