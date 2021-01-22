import firebase_admin
from firebase_admin import firestore, credentials

import os
import time
from typing import Tuple
import json


class DB:
    def __init__(self):
        cred = credentials.Certificate("./secret.json")
        if not firebase_admin._apps:
            app = firebase_admin.initialize_app(cred)
        else:
            app = firebase_admin.get_app("[DEFAULT]")
        self.app = app
        self.firestore = firestore.client()

    def set(
        self,
        key,
        value,
        data="data",
        document_id="default",
    ):
        doc = self.firestore.collection("data").document(document_id)
        if doc.get().exists:
            doc.update({key: json.dumps(value)})
        else:
            print(f"document {document_id} not found, creating...")
            doc.set({key: json.dumps(value)})

    def get(
        self,
        key,
        default=None,
        data="data",
        document="default",
    ):
        document = self.firestore.collection("data").document(document).get().to_dict()
        if document is None:
            return None
        result = document.get(key, default)
        if result is not default:
            return json.loads(result)
        else:
            return result

    def get_graph_and_gen_time_for_school(self, school_name) -> Tuple[any, float]:
        return (
            self.get(document=school_name, key="graph", default=None),
            self.get(document=school_name, key="gen_time", default=None),
        )

    def set_graph_for_school(self, school_name, graph):
        self.set(document_id=school_name, key="graph", value=graph)
        now = time.time()
        self.set(document_id=school_name, key="gen_time", value=now)


db = None


def get_db():
    global db
    if db:
        return db
    else:
        db = DB()
        return db
