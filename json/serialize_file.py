import json
import logging
from logging import info

def timestamp_file(file_loc: str) -> str:
    """Adds a date timestamp to the filename.
    :param file_loc: location of file to write to
    :type file_loc: str, bool
    :return: the file location with the timestamp appended to the end of the file
    :rtype: str
    """
    now = datetime.now()
    date_time = now.strftime("_%Y-%m-%d-%H-%M-%S")
    file, extension = os.path.splitext(file_loc)

    return file + date_time + extension


def json_to_file(file_loc=False, json_data=None, create_indexes=False, with_timestamp=True):
    """Create JSON file object.
    :param file_loc: location of file to write to
    :type file_loc: str, bool
    :param json_data: data to write
    :type json_data: dict, list
    :param create_indexes: whether to create indexes in the values
    :type create_indexes: bool
    :param with_timestamp: whether to timestamp the file
    :type with_timestamp: bool
    """
    if create_indexes:
        for idx, element in enumerate(json_data):
            element['id'] = element.get('id', idx)

    if file_loc:
        if with_timestamp:
            file_loc = timestamp_file(file_loc)

        with open(file_loc, "w") as outf:
            json.dump(json_data, outf, allow_nan=False, default=str, indent=2)
        info("Saved output in file: '{0}'.".format(os.path.join(os.path.abspath(os.getcwd()), file_loc)))
