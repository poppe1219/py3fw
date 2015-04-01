"""Docstring"""

import fw.uuid
import fw.git.api as gitapi
import fw.file.tools as filetools
import fw.config.manage as configmanage


def new_repo(root_path, name, user=None, repo_id=None, ignore_content=None):
    """Doc string."""
    uid = repo_id
    if repo_id is None:
        uid = fw.uuid.get_unique_id()
    path = filetools.join_path(root_path, uid)
    filetools.verify_dir(path, createifnotexists=True)
    repo_info = gitapi.create_repo(path, user)
    overrides = {
        '@config_id': uid,
        'root_path': root_path,
        'path': path,
        'user': user,
        'name': name
    }
    config = configmanage.create_new_config('GitRepo', overrides=overrides)
    filename = write_git_ignore(path, ignore_content=ignore_content)
    gitapi.add(repo_info, filename)
    message = "Created new repo: {}.".format(uid)
    gitapi.commit(repo_info, message, user)
    return config


def write_git_ignore(parent_path, ignore_content=None):
    """Writes the .gitignore file into the specified path."""
    if ignore_content is None:  # Use default content.
        ignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
"""
    filetools.verify_dir(parent_path, createifnotexists=True)
    filename = filetools.join_path(parent_path, ".gitignore")
    filetools.write_file(filename, data=ignore_content)
    return filename


def move_repo(config, new_root_path):
    """Move an entire file repo, with all its content, to a new root path."""
    old_root_path = config['root_path']
    old_repo_path = filetools.join_path(old_root_path, config['@config_id'])
    new_repo_path = filetools.join_path(new_root_path, config['@config_id'])
    filetools.move(old_repo_path, new_repo_path)
    config['root_path'] = new_root_path
    config['path'] = new_repo_path


def remove_repo(config):
    """Remove a repository."""
    filetools.remove_dir(config['path'])
