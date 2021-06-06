from typing import List, Optional
import re
import os
import yaml
from dataclasses import dataclass


@dataclass
class Question:
    label: str
    description: str
    required: bool
    regexp: Optional[str]
    regexp_message: Optional[str]


@dataclass
class SelectQuestion(Question):
    choices: List[str]


@dataclass
class IntegerQuestion(Question):
    pass


def load_from_yaml() -> List[Question]:
    question_file = "./questions.yaml"
    assert os.path.exists(question_file), question_file
    with open(question_file, "r") as question_def_file:
        question_def_dicts = yaml.safe_load_all(question_def_file)
        loaded_questions: List[Question] = []
        for i, q in enumerate(question_def_dicts):
            if q is None:
                raise ValueError(
                    f"Error parsing question {i} in {question_file}. Is there an extra '---'?"
                )
            if "type" not in q:
                raise ValueError(
                    f"Error parsing question {i} in {question_file}. No type defined."
                )
            if "regexp" in q:
                if "regexp_message" not in q:
                    raise ValueError(
                        f"Question {i} in {question_file} must define a regexp error message"
                    )
                try:
                    re.compile(q["regexp"])
                except re.error:
                    raise ValueError(
                        f"Error compiling regexp {q['regexp']} for question {i} in {question_file}"
                    )
            else:
                q["regexp"] = None
                q["regexp_message"] = None

            if q["type"] == "text":
                del q["type"]  # remove unexpected fields
                loaded_questions.append(Question(**q))
            elif q["type"] == "select":
                del q["type"]  # remove unexpected fields
                loaded_questions.append(SelectQuestion(**q))
            elif q["type"] == "integer":
                del q["type"]  # remove unexpected fields
                loaded_questions.append(IntegerQuestion(**q))
            else:
                raise ValueError(f"Unknown source definition: {q}")
    return loaded_questions


def load_winners_from_yaml() -> List[str]:
    winners_file = "./winners.yaml"
    if not os.path.exists(winners_file):
        print(
            f"Couldn't find {winners_file}, did you download it from the secret bucket? gsutil cp gs://vape-survey-secrets/winners.yaml winners.yaml"
        )
        return {}
    with open(winners_file, "r") as winners_def_file:
        return {
            x["identifier"]: {"password": x["password"], "code": x["code"]}
            for x in list(yaml.safe_load_all(winners_def_file))
        }
