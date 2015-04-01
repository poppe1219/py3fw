"""A utility tool module for working with files and folders.

As with all tool modules in this framework, no other framework modules are
allowed to be imported, with the exception of logging.
This is enforced to allow these tool modules to be imported from anywhere,
without risking recursive imports.

"""

__all__ = [
    'verify_dir',
    'verify_file',
    'join_path',
    'read_file',
    'write_file',
    'move',
    'dir_content'
]

import os
import re
import shutil


def verify_dir(path, createifnotexists=False):
    """Checks if the directory exists. Can also create it.

    The path must be a string.
    If the path does not exist and the parameter createifnotexists is set to
    true, the method will try to create it. Should that fail, an exception will
    be raised.
    Returns the path as a string if the path exists.

    """
    if type(path) != str:
        raise TypeError('The path variable must be a string.')
    if not os.path.isdir(path):
        if createifnotexists:
            os.makedirs(path, exist_ok=True)
            if not os.path.isdir(path):
                raise IOError('Directory could not be created: "%s"' % path)
        else:
            return False
    return True


def verify_file(path, createifnotexists=False):
    """Checks if the file exists. Can also create it (empty, of course).

    The file path must be a string.
    If the path/file does not exist and the parameter createifnotexists is set
    to true, the method will try to create it. Should that fail, an exception
    will be raised.
    Returns the path as a string if the path exists.

    """
    if type(path) != str:
        raise TypeError('The path variable must be a string.')
    file_path, file_name = os.path.split(path)  # @IgnorePep8 @UnusedVariable, pylint: disable-msg=unused-variable, line-too-long
    if file_path:
        file_path_exists = verify_dir(file_path, createifnotexists)
        if not file_path_exists:
            return False
    if os.path.isfile(path):
        return True
    if createifnotexists:
        with open(path, 'w+') as file:
            file.write('')
        return True
    return False


def read_file(path, encoding='utf-8'):
    """Reads the content of a file."""
    with open(path, 'r', encoding=encoding) as file:
        data = file.read()
    return data


def write_file(path, data, encoding='utf-8'):
    """Write content to a file."""
    with open(path, 'w+', encoding=encoding) as file:
        file.write(data)


def move(source, destination):
    """Move a file to a new destination."""
    shutil.move(source, destination)


def join_path(*path):
    """Joins parts of a path with the correct OS specific separator.

    Takes an arbitrary number of arguments that can be either strings, or lists
    or tuples containing strings.
    Returns a string.

    """
    error_message = 'Illegal argument type: %s'
    parts = []
    for arg in path:
        if type(arg) == str:
            parts.append(arg)
        elif type(arg) == list or type(arg) == tuple:
            for item in arg:
                if type(item) != str:
                    raise TypeError(error_message % type(arg))
            parts.extend(arg)
        else:
            raise TypeError(error_message % type(arg))
    return os.sep.join(parts)


def dir_content(path, recursive=False, files_only=False, dirs_only=False,
    filter_out=None, _parent_path=''):
    """Gets a structure representing the content of path.

    If path does not exist, an error will be thrown.
    recursive will make the function go into sub folders and return a tree.
    Setting files_only to True, returns a list containing only filenames.
    Setting dirs_only to True, returns a list containing only folder names.
    filter_out will take a regular expression for names to exclude.
    files_only can not be used in combination with recursive.

    """
    if recursive and files_only:
        raise AttributeError(('The attributes files_only can not be used in '
            'combination with recursive'))
    items = []
    if os.path.isdir(path):
        all_items = os.listdir(path)
        all_items.sort()
        dir_items = []
        file_items = []
        for name in all_items:
            item_path = join_path(path, name)
            item_type = 'dir'
            if os.path.isfile(item_path):
                item_type = 'file'
            if _skip_to_next(filter_out, name, item_type, files_only,
                dirs_only):
                continue
            if not _parent_path:
                parent_path = name
            else:
                parent_path = join_path(_parent_path, name)
            data = _set_directory_node_data(name, parent_path, item_type,
                item_path)
            if item_type == 'dir' and recursive == True:
                data['content'] = dir_content(item_path, recursive,
                    files_only, dirs_only, filter_out, parent_path)
            if item_type == 'dir':
                dir_items.append(data)
            elif item_type == 'file':
                file_items.append(data)
        items.extend(dir_items)
        items.extend(file_items)
    else:
        raise NotADirectoryError('Path is not a directory: %s' % path)
    return items


def _skip_to_next(filter_out, name, item_type, files_only, dirs_only):
    """Extracted logic from dir_content, to reduce its complexity."""
    if filter_out and re.match(filter_out, name) != None:
        return True
    elif files_only and item_type == 'dir':
        return True
    elif dirs_only and item_type == 'file':
        return True
    return False


def _set_directory_node_data(name, parent_path, item_type, item_path):
    """Returns a dictionary representing a node in a directory."""
    return {
        'name': name,
        'path': parent_path,
        'type': item_type,
        'size': os.path.getsize(item_path),
        'mtime': os.path.getmtime(item_path),
        'ctime': os.path.getctime(item_path)
    }


def remove_dir(path):
    shutil.rmtree(path)
