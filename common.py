from __future__ import annotations
import argparse
import getpass
import hashlib
import itertools
import os.path
import psycopg2  # type: ignore
import re
import signal
import sys
import time
import yaml

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Union, List, Type, TypeVar, Any, Callable, \
    Iterable

τ = TypeVar("τ")

RE_INTERVAL = re.compile(r"([0-9]+) *(s|m|h)")


def fprint(what: Any, *args: Any, **kvargs: Any) -> None:
    print(what, flush=True, *args, **kvargs)


def sha256(data: Union[str, bytes]) -> bytes:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).digest()


class File:
    def __init__(self, name: Optional[str] = None, path: Optional[str] = None,
                 data: Optional[Union[bytes, str]] = None) -> None:
        if path is not None:
            assert data is None
            with open(path, 'rb') as h:
                self.data = h.read()
        elif isinstance(data, str):
            self.data = data.encode(data, 'utf-8')
        else:
            assert isinstance(data, bytes)
            self.data = data
        if name is None:
            assert path is not None
            self.name = os.path.basename(path)
        else:
            self.name = name


def submit_assignment(asgn_id: int, author: int, db: psycopg2.connection,
                      files: List[File],
                      timestamp: Optional[datetime] = None) -> None:
    with db.cursor() as cur:
        if timestamp is not None:
            cur.execute("""
                insert into submission (author, assignment_id, stamp)
                  values (%s, %s, %s)
                  returning (id)
                  """, (author, asgn_id, timestamp))
        else:
            cur.execute("""
                insert into submission (author, assignment_id)
                  values (%s, %s)
                  returning (id)
                  """, (author, asgn_id))
        sid = cur.fetchone()[0]

        for f in files:
            file_sha = sha256(f.data)
            cur.execute("insert into content (sha, data)"
                        "  values (%s, %s)"
                        "  on conflict do nothing",
                        (file_sha, f.data))
            cur.execute("insert into submission_in"
                        "  (submission_id, assignment_id, name, content_sha)"
                        "  values (%s, %s, %s, %s)",
                        (sid, asgn_id, f.name, file_sha))


def cmdparser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('config', metavar="CONFIG.yaml", nargs=1, type=str,
                        help="poller configuration file")
#    parser.add_argument('--reeval-all', action='store_const',
#                        const=True, default=False,
#                        help="re-evaluate all last submissions of exercises")
    parser.add_argument('--oneshot', action='store_const',
                        const=True, default=False,
                        help="run only one poll, then exit")
#    parser.add_argument('--force', action='extend', type=str, nargs=1,
#                        default=[], metavar="PATH",
#                        help="Force submission of exercise from given path "
#                             "even if it was already processed. Can be used "
#                             "multiple times.")
    return parser


class BaseAssignment:
    def __init__(self, raw: dict, name: str, config: BaseConfig,
                 db: Optional[psycopg2.connection] = None) -> None:
        self.name = name
        self.raw = raw
        self.enabled = self._enabled()
        self.id: Optional[int] = None
        self.file_names: Optional[List[str]] = None
        if db is not None:
            self.id = get_asgn_id(self.name, db)
            if self.id is not None:
                self.file_names = get_asgn_files(self.id, db)

    def _enabled(self) -> bool:
        en = self.raw.get("enabled", True)
        if isinstance(en, bool):
            return en

        now = datetime.today().date()
        fr = en.get("from", now)
        to = en.get("to", now)
        assert isinstance(fr, date)
        assert isinstance(to, date)
        return bool(fr <= now <= to)

    def _str(self, extra: Optional[str]) -> str:
        out = f"Assignment[{self.name} enabled = {self.enabled} "
        if self.id is not None:
            out += f" id = {self.id}"
        if self.file_names is not None:
            out += f" file_names = {self.file_names}"
        if extra is not None:
            out += " " + extra
        return out + "]"


class BaseConfig:
    def __init__(self, raw: dict) -> None:
        self.raw = raw

    @staticmethod
    def _check(val: Any, typ: Type[τ]) -> τ:
        assert isinstance(val, typ)
        return val

    def interval(self) -> int:
        raw_interval = self.raw.get("interval", 300)
        if isinstance(raw_interval, int):
            return raw_interval
        if isinstance(raw_interval, str):
            m = RE_INTERVAL.fullmatch(raw_interval)
            if not m:
                raise Exception("Invalid interval specification: "
                                f"{raw_interval}, must be integer with an "
                                "optional suffix 's' (seconds), 'm' (minutes) "
                                "or 'h' (hours)")
            return int(m[1]) * {'s': 1, 'm': 60, 'h': 3600}[m[2]]
        raise Exception(f"Not an interval: {raw_interval}")

    def _assignments(self) -> dict:
        return BaseConfig._check(self.raw.get("assignments", {}), dict)

    def course(self) -> str:
        return BaseConfig._check(self.raw["course"], str)

    def frag_db(self) -> str:
        return BaseConfig._check(self.raw["frag db"], str)

    def frag_user(self) -> str:
        if "user" in self.raw:
            return BaseConfig._check(self.raw["user"], str)
        return getpass.getuser()

    def connect_db(self) -> psycopg2.connection:
        db = psycopg2.connect(dbname=self.course(), host=self.frag_db(),
                              user=self.frag_user())
        with db.cursor() as cur:
            cur.execute("set search_path to frag")
        return db


τ_config = TypeVar("τ_config", bound=BaseConfig)


def get_asgn_id(name: str, db: psycopg2.connection) -> Optional[int]:
    with db.cursor() as cur:
        cur.execute("select id from assignment where name = %s",
                    (name,))
        rec = cur.fetchone()
        if rec is None:
            return rec
        assert isinstance(rec[0], int)
        return rec[0]


def get_asgn_files(asgn_id: int, db: psycopg2.connection) -> List[str]:
    with db.cursor() as cur:
        cur.execute("select name from assignment_in where assignment_id = %s",
                    (asgn_id,))
        return [tup[0] for tup in cur.fetchall()]


@dataclass
class Person:
    uid: int
    login: str
    name: str
    is_teacher: bool


def _get_people(table: str, is_teacher: bool, db: psycopg2.connection) \
        -> Iterable[Person]:
    with db.cursor() as cur:
        cur.execute(f"select id, login, name from {table}")
        return (Person(uid, login.tobytes().decode('ascii'), name, is_teacher)
                for uid, login, name in cur.fetchall())


def get_teachers(db: psycopg2.connection) -> Iterable[Person]:
    return _get_people("teacher_list join person"
                       "  on (teacher_list.teacher = person.id)", True, db)


def get_students(db: psycopg2.connection) -> Iterable[Person]:
    return _get_people("enrollment join person "
                       "  on (enrollment.student = person.id)", False, db)


def get_people(db: psycopg2.connection) -> Iterable[Person]:
    return itertools.chain(get_teachers(db), get_students(db))


def get_config(args: argparse.Namespace, Config: Type[τ_config]) -> τ_config:
    try:
        with open(args.config[0], "r") as config_handle:
            return Config(yaml.safe_load(config_handle))
    except OSError:
        fprint(f"Could not open config {args.config}")
        sys.exit(2)


def poller(args: argparse.Namespace, Config: Type[τ_config],
           poll: Callable[[argparse.Namespace, τ_config], None]) -> None:
    stop_signal = False

    def stop(sig: int, stack: Any) -> None:
        nonlocal stop_signal
        stop_signal = True
        fprint(f"cancellation pending (SIG={sig})… ")

    signal.signal(signal.SIGTERM, stop)

    while True:
        config = get_config(args, Config)
        interval = config.interval()
        start = time.perf_counter()
        poll(args, config)
        sleep_for = int((max(0, interval - (time.perf_counter() - start))))
        for _ in range(sleep_for):
            if stop_signal or args.oneshot:
                return
            time.sleep(1)
        if stop_signal or args.oneshot:
            return


def main(cmdparser: Callable[[], argparse.ArgumentParser],
         Config: Type[τ_config],
         check_init_db: Callable[[τ_config], None],
         poll: Callable[[argparse.Namespace, τ_config], None]) -> None:
    parser = cmdparser()
    args = parser.parse_args()
    fprint(args)
    check_init_db(get_config(args, Config))
    poller(args, Config, poll)

# vim: colorcolumn=80 expandtab sw=4 ts=4
