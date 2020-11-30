import firebase_admin
from firebase_admin import firestore, credentials

import os
import time
from typing import Tuple
import json


class DB:
    def __init__(self):
        cred = credentials.Certificate("./secret.json")
        self.app = firebase_admin.initialize_app(cred)
        self.firestore = firestore.client()

    def set(
        self,
        key,
        value,
        data="data",
        document="default",
    ):
        self.firestore.collection(data).document(document).update(
            {key: json.dumps(value)}
        )

    def get(
        self,
        key,
        default=None,
        data="data",
        document="default",
    ):
        result = (
            self.firestore.collection("data")
            .document(document)
            .get()
            .to_dict()
            .get(key, default)
        )
        if result is not default:
            return json.loads(result)
        else:
            return result


db = DB()


def get_graph_and_gen_time_for_school(school_name) -> Tuple[any, float]:
    return (
        db.get(document=school_name, key="graph"),
        db.get(document=school_name, key="gen_time"),
    )


def set_graph_for_school(school_name, graph):
    db.set(document=school_name, key="graph", value=graph)
    now = time.time()
    db.set(document=school_name, key="gen_time", value=now)
