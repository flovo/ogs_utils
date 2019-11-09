from pathlib import Path
from typing import Any
from datetime import datetime
import gzip
import pickle
import json
import os

compression_level = 9

def atomic_save(path: Path, obj: Any) -> None:
    sec = datetime.now()
    tmp_file_json = path.parent / "~{name}.json.gz.tmp_{sec}~".format(name=path.name, sec=sec)
    tmp_file_pickle = path.parent / "~{name}.pickle.gz.tmp_{sec}~".format(name=path.name, sec=sec)
    with gzip.open(tmp_file_pickle, "wb", compresslevel=compression_level) as f:
        pickle.dump(obj=obj, file=f, protocol=4)
    with gzip.open(tmp_file_json, "wt", compresslevel=compression_level) as f:
        json.dump(obj=obj, fp=f)
    os.rename(tmp_file_pickle, path.parent / "{name}.pickle.gz".format(name=path.name))
    os.rename(tmp_file_json, path.parent / "{name}.json.gz".format(name=path.name))


def load(path: Path) -> dict:
    # try to load the pickled version first, only if that failed, load the json
    try:
        with gzip.open(path.parent / "{name}.pickle.gz".format(name=path.name), "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, pickle.UnpicklingError):
        #journal.send("{} {}".format("Could not open", path.parent / "{name}.pickle.gz".format(name=path.name)), PRIORITY=journal.LOG_INFO)
        with gzip.open(path.parent / "{name}.json.gz".format(name=path.name), "rt") as f:
            return json.load(f)