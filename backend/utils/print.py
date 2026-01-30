import json


def to_serializable(obj):
    if hasattr(obj, "model_dump_json"):
        return json.loads(obj.model_dump_json())
    elif hasattr(obj, "__dict__"):
        return obj.__dict__
    else:
        return str(obj)


def json_print(data: dict):
    print(json.dumps(data, indent=2))


def prettify_json(data: dict):
    return json.dumps(data, indent=2)
