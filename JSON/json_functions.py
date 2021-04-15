import json

def is_json(string):
    """Check if string is valid JSON."""
    try:
        json_object = json.loads(string)
    except ValueError as e:
        return False

    return True


def print_json(parsed):
    """Pretty print JSON."""
    print(json.dumps(parsed, indent=4, sort_keys=True))


def prettify_json_file(path1, path2):
    """Reads JSON-formatted file and indents it."""
    with open(path1) as f:
        d = json.load(f)
    json_to_file(json_data=d, file_loc=path2)  # this function is under 'static file management'


def write_jsonl(sentences, file_loc=False):
    """Write list object to JSONL format.
    :param sentences: unlabeled sentences to convert to JSONL
    :type sentences: list
    :param file_loc: location of file to write to
    :type file_loc: str, bool
    """
    with jsonlines.open(file_loc, 'w') as writer:
        writer.write_all(sentences)
