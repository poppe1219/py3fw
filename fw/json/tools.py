"""A utility tool module for working with json.

As with all tool modules in this framework, no other framework modules are
allowed to be imported, with the exception of logging.
This is enforced to allow these tool modules to be imported from anywhere,
without risking recursive imports.

"""

import re
import json


def deep_copy(original):
    """Recursive method that deep copies a json structure.

    All mutable objects in the new structure gets new memory addresses,
    i.e. real copies are created.

    """
    if type(original) == dict:
        # List comprehension was slower than the following three lines.
        copy = original.copy()  # Shallow copy first to get correct keys.
        for key, value in copy.items():
            copy[key] = deep_copy(value)  # Deep copy for each key.
    elif type(original) == list:
        copy = [deep_copy(value) for value in original]  # Deep copy each item.
    else:  # str, int, float, True, False, None (immutable types)
        copy = original  # Ordinary assignment will copy immutables.
    return copy


def merge(overlay, base):
    """Recursive method that merges two json structures.

    Dictionaries will be recursively merged. Lists and immutable objects will
    will be copied, i.e. lists do not get merged, they get copied.

    Notice:
    Dictionaries are prohibited inside lists and will cause an exception.
    This is because lists are treated as immutable objects when merging.
    (If you can come up with an algorithm for merging two lists, while
     overriding base values with overlay values and somehow still retain a
     fair order within the list, please share that with me...)

    'overlay' will keep all previous key value pairs.
    Only the keys in base that do not exist in overlay, will get copied into
    overlay. The input parameter 'base' will remain unchanged.

    """
    if type(overlay) == dict:
        for key, value in base.items():
            if not key in overlay.keys():
                overlay[key] = merge(None, value)
            elif type(overlay[key]) == dict and type(value) == dict:
                merge(overlay[key], value)
        return
    else:
        if overlay:
            return overlay  # Value already set in overlay, keep it.
        else:  # Get values from base.
            if type(base) == list:
                new_list = []
                for value in base:
                    if type(value) == dict:
                        raise Exception('Cannot handle dicts inside lists!')
                    # Copy list to get a copy of the mutable object.
                    new_list.append(merge(None, value))
                return new_list
            else:  # Immutable types.
                return base  # str, int, float, True, False, None.


def dumps(json_data, sort_keys=True, indent=4, ensure_ascii=False,
    compact=False):
    """Converts json (like json.dumps), but provides 'pretty print' defaults.

    The default values will produce a string that is indented, has newlines
    and is sorted. If written to a file, it is readable and can be diffed
    against other versions of the same file.

    """
    if compact:
        indent = None
        separators = (',', ':')
    else:
        separators = (',', ': ')
    json_text = json.dumps(json_data, sort_keys=sort_keys, indent=indent,
        ensure_ascii=ensure_ascii, separators=separators)
    return json_text


def loads(text, parse_comments=True):
    """Parse a json text, with the option to parse out comments (JS style).

    Primarily intended for parsing config files in json format,
    where the use of comments may be desirable.

    As Douglas Crockford suggests:

       "Suppose you are using JSON to keep configuration files,
        which you would like to annotate. Go ahead and insert all
        the comments you like. Then pipe it through JSMin before
        handing it to your JSON parser."

    (https://plus.google.com/+DouglasCrockfordEsq/posts/RK8qyGVaGSr)

    Inspired by Damien Riquet's example:
    http://www.lifl.fr/~riquetd/parse-a-json-file-with-comments.html

    """
    if parse_comments:
        regex = re.compile(r'(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
            re.DOTALL | re.MULTILINE
        )
        match = regex.search(text)
        while match:
            text = text[:match.start()] + text[match.end():]
            match = regex.search(text)
    return json.loads(text)
