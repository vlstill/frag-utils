from __future__ import annotations
import hashlib
import os.path
import psycopg2  # type: ignore
from typing import Optional, Union, List


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
                      files: List[File]) -> None:
    with db.cursor() as cur:
        cur.execute("insert into submission (author, assignment_id)"
                    "  values (%s, %s)"
                    "  returning (id)",
                    (author, asgn_id))
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

# vim: colorcolumn=80 expandtab sw=4 ts=4
