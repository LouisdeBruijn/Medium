import json
import html


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
     

def unescape_html(
        text: str) -> str:
    """Converts any HTML entities found in text to their textual representation.
    :param text: utterance that may contain HTML entities
    :type text: str
    Example of HTML entities found during annotations
        html_entities = [("&nbsp;", " ")
            , ("&amp;", "&")
            , ("&gt;", ">")
            , ("&lt;", "<")
            , ("&le;", "≤")
            , ("&ge;", "≥")]
    :return: utterance wihtout HTML entities
    :rtype: str
    """
    return html.unescape(text)


def unescape_html_wrapper(json_data):
    """Escapes HTML entities from strings in data to be saved in JSON format.
    :param json_data: The data that is going to be saved in JSON format.
    :type json_data: list
    :return: The data with HTML entities unescaped
    :rtype: list
    """
    if isinstance(json_data, list):
        for idx, elem in enumerate(json_data):
            if isinstance(elem, str):
                json_data[idx] = unescape_html(elem)
            elif isinstance(elem, dict):
                for key, value in elem.items():
                    if isinstance(value, str):
                        elem[key] = unescape_html(value)

    return json_data
