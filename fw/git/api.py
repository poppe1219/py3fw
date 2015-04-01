"""Git module, for interacting with Git repositories.

Derived from:
    gitapi
    https://github.com/haard/gitapi
    MIT/BSD license. Copyright Fredrik Haard.

Modified extensively.

"""

import re
import json
import subprocess
import urllib.parse


def command(repo, *args):
    """Run a git command on this Repo and return the result."""
    if repo is not None:
        path = repo.get('path', '.')
    else:
        path = '.'
    proc = subprocess.Popen(["git"] + list(args), stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, cwd=path)
    out, err = [x.decode("utf-8") for x in  proc.communicate()]

    if proc.returncode or 'Warning:' in err:
        cmd = "git " + " ".join(args)
        raise Exception("Error running %s:\n\tErr: %s\n\tOut: %s\n\tExit: %s"
            % (cmd, err, out, proc.returncode))
    return out, err


def clone(url, path, *args):
    """Clone repository at given `url` to `path`, returns repo dictionary."""
    _, err = command(None, "clone", url, path, *args)
    if "Cloning into ".format(path) in err and 'done.' in err:
        return {
            "path": path,
            "user": None
        }
    else:
        raise Exception('Failed to clone "{}": {}'.format(url, err))


def init(repo):
    """Initialize a new Repo."""
    _, _ = command(repo, "init")


def sha1(repo):
    """Get the output of the git id command (truncated node)."""
    if not repo:
        raise Exception('Repo value must not be None when getting sha1.')
    out, _ = command(repo, "log", "--pretty=format:%H", "-n", "1")
    return out.strip("\n +")


def add(repo, filepath):
    """Add a file to the Repo."""
    _, _ = command(repo, "add", filepath)


def remove(repo, filepath):
    """Remove a file from the Repo."""
    _, _ = command(repo, "rm", filepath)


def checkout(repo, reference):
    """Update to the revision indetified by reference."""
    cmd = ["checkout", str(reference)]
    _, _ = command(repo, *cmd)  # pylint: disable=star-args


def branches(repo):
    """Gets a list with the names of all branches."""
    out, _ = command(repo, "branch")
    return [head.strip(" *") for head in out.split("\n") if head]


def branch(repo, name, start="HEAD"):
    """Create the branch named 'name'."""
    out, _ = command(repo, "branch", name, start)
    return out


def tags(repo, pattern=None, points_at=None, **kwargs):
    """Get repository tags."""
    args = []
    for key in kwargs:
        args.extend([key, kwargs[key]])
    if points_at:
        args.extend(['--points-at', points_at])
    if pattern:
        args.append(pattern)
    out, _ = command(repo, "tag", "-l", *args)  # pylint: disable=star-args
    return [tag for tag in out.split("\n") if tag]


def tag(repo, name):
    """Create the tag named 'name'."""
    out, _ = command(repo, "tag", name)
    return out


def merge(repo, reference):
    """Merge reference to current."""
    _, _ = command(repo, "merge", reference)


def reset(repo, hard=True, *files):
    """Revert repository."""
    hard = ["--hard"] if hard else []
    cmd = ["reset"] + hard + list(files)
    _, _ = command(repo, *cmd)  # pylint: disable=star-args


def node(repo):
    """Get the full node id of the current revision."""
    out, _ = command(repo, "log", "-r", sha1(repo), "--template",
        "{node}")
    return out.strip()


def commit(repo, message, user=None, files=None, close_branch=False):
    """Commit changes to the repository."""
    if files is None:
        files = []
    userspec = []
    if user is None:
        user = repo.get('user')
    if user is not None:
        userspec = ['--author', user]
    close = "--close-branch" if close_branch else ""
    _, _ = command(repo, "commit", "-m", message, close,
                    *userspec + files)


def log(repo, identifier=None, limit=None, template=None, **kwargs):
    """Get repositiory log."""
    cmds = ["log"]
    if identifier:
        cmds += [identifier, '-n', '1']
    if limit:
        cmds += ['-n', str(limit)]
    if template:
        cmds += [str(template)]
    if kwargs:
        for key in kwargs:
            cmds += [key, kwargs[key]]
    out, _ = command(repo, *cmds)  # pylint: disable=star-args
    return out


def status(repo, empty=False):
    """Get repository status.

    Returns a dict containing a *change char* -> *file list* mapping,
    where the change chars are: A, M, R, !, ?.

    Example - added one.txt, modified a_folder/two.txt and three.txt:

        {
            'A': ['one.txt'],
            'M': ['a_folder/two.txt', 'three.txt'],
            '!': [],
            '?': [],
            'R': []
        }

    If empty is set to non-False value, don't add empty lists.

    """
    out, _ = command(repo, 'status', '-s')
    out = out.strip()
    #default empty set
    if empty:
        changes = {}
    else:
        changes = {}
    if not out:
        return changes
    lines = out.split("\n")
    status_split = re.compile(r"^([^\s]+)\s+(.*)$")

    for change, path in [status_split.match(x.strip()).groups()
            for x in lines]:
        changes.setdefault(change, []).append(path)
    return changes


def push(repo, destination=None, branch_name=None):
    """Push changes from this Repo."""
    args = [arg for arg in (destination, branch_name) if not arg is None]
    _, _ = command(repo, "push", *args)  # pylint: disable=star-args


def pull(repo, source=None):
    """Pull changes to this Repo."""
    if source is None:
        _, _ = command(repo, "pull")
    else:
        _, _ = command(repo, "pull", source)


def fetch(repo, source=None):
    """Fetch changes to this Repo."""
    if source is None:
        _, _ = command(repo, "fetch")
    else:
        _, _ = command(repo, "fetch", source)


def revision(repo, identifier=None):
    """Get the identified (sha1) revision as a revision dictionary."""
    template = ('--pretty=format:{"node":"%h","author":"%an", '
        '"parents":"%p","date":"%ci","desc":"%s"}')
    out = log(repo, identifier=identifier, template=template)
    json_log = json.loads(out)
    rev = {}
    for key in json_log.keys():
        if key == 'parents':
            parents = urllib.parse.unquote(json_log.get(key, ''))
            rev[key] = parents.split()
        else:
            rev[key] = urllib.parse.unquote(json_log.get(key, ''))
    return rev


def read_config(repo):
    """Read the configuration as seen with 'git config -l'.

    Is called by __init__ - only needs to be called explicitly
    to reflect changes made since instantiation.

    """
    out, _ = command(repo, "config", "-l")
    cfg = {}
    for row in out.split("\n"):
        section, _, value = row.partition("=")
        main, _, sub = section.partition(".")
        sect_cfg = cfg.setdefault(main, {})
        sect_cfg[sub] = value.strip()
    repo['cfg'] = cfg
    return cfg


def config(repo, section, key):
    """Return the value of a configuration variable."""
    cfg = repo.get('cfg')
    if not cfg:
        cfg = read_config(repo)
    return cfg.get(section, {}).get(key, None)


def configbool(repo, section, key):
    """Return a config value as a boolean value.

    Empty values, the string 'false' (any capitalization),
    and '0' are considered False, anything else True.

    """
    cfg = repo.get('cfg')
    if not cfg:
        cfg = read_config(repo)
    value = cfg.get(section, {}).get(key, None)
    if not value:
        return False
    if value.upper() in ["0", "FALSE", "NONE"]:
        return False
    return True


def configlist(repo, section, key):
    """Return a config value as a list.

    Will try to create a list delimited by commas, or whitespace if no
    commas are present.

    """
    cfg = repo.get('cfg')
    if not cfg:
        cfg = read_config(repo)
    value = cfg.get(section, {}).get(key, None)
    if not value:
        return []
    if value.count(","):
        return value.split(",")
    else:
        return value.split()


def create_repo(path, user=None):
    """Creates and returns a dictionary representing the repository.

    Example:
        {
            "path": "/my/path/myrepo",
            "user": "username <user.name@mail.com>",
            "cfg": {...}
        }

    """
    repo = {
        "path": path,
        "user": user
    }
    init(repo)
    return repo
