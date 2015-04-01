"""Docstring"""

import fw.file.tools as filetools


def create_tree(config):
    """Creates a file tree from the config. Non-disruptive."""
    root_path = config['root_path']
    tree_path = filetools.join_path(root_path, config['tree_id'])
    try:
        filetools.verify_dir(tree_path, createifnotexists=True)
        config['path'] = tree_path
        content = config.get('content', [])
        for node in content:
            _create_node(node, None, tree_path)
    except Exception as exc:  # pylint: disable-msg=broad-except
        return {
            'status': 'error',
            'errors': [exc]
        }
    return {'status': 'ok'}


def _create_node(node_config, parent_path, tree_path):
    """Recursive sub method to create_tree, is called once for each node."""
    name = node_config['name']
    if parent_path:
        node_path = filetools.join_path(parent_path, name)
    else:
        node_path = name
    node_config['path'] = node_path
    path = filetools.join_path(tree_path, node_path)
    if node_config['type'] == 'dir':
        filetools.verify_dir(path, createifnotexists=True)
        content = node_config.get('content', [])
        for child_node in content:
            _create_node(child_node, node_path, tree_path)
    else:
        filetools.verify_file(path, createifnotexists=True)


def move_tree(config, new_root_path):
    """Move an entire file tree, with all its content, to a new root path."""
    old_root_path = config['root_path']
    old_tree_path = filetools.join_path(old_root_path,
        config['tree_id'])
    new_tree_path = filetools.join_path(new_root_path,
        config['tree_id'])
    filetools.move(old_tree_path, new_tree_path)
    config['root_path'] = new_root_path
    config['path'] = new_tree_path


def make_dir(config, path):  # pylint: disable-msg=unused-argument
    """Create a new directory, both in the config and in the file system."""
    pass


def remove_dir(config, path, recursive=True):  # pylint: disable-msg=W0613
    """Remove a directory, both in the config and in the file system."""
    pass


def make_file(config, path):  # pylint: disable-msg=unused-argument
    """Create a new file, both in the config and in the file system."""
    pass


def remove_file(config, path):  # pylint: disable-msg=unused-argument
    """Remove a file, both in the config and in the file system."""
    pass
