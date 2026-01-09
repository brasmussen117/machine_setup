#!/usr/bin/env python3
"""Print out zsh prompts."""

# System imports
import argparse
import os
import re
import subprocess
import socket
from copy import deepcopy
from datetime import datetime

# Third-party imports

# Internal imports


# Constants
SEP_R = ""
SEP_L = ""
SPACER = "·"
CHEVRON = ""
USER_PLACEHOLDER = " "
ELLIPSIS = "…"
BRANCH_SYMBOL = ""
DIR_SYMBOL = ""
VENV_SYMBOL = ""
GIT_AHEAD = "↑"
GIT_BEHIND = "↓"
GIT_STAGED = "+"
GIT_UNSTAGED = "~"
GIT_UNTRACKED = "?"
GIT_STASHED = "*"

MAX_PATH_LENGTH = 70

BLACK = "black"
RED = "red"
GREEN = "green"
YELLOW = "yellow"
BLUE = "blue"
MAGENTA = "magenta"
CYAN = "cyan"
WHITE = "white"

# Section colors (allow override via environment variables)
USER_FG = os.getenv("PROMPT_USER_FG", BLACK)
USER_BG = os.getenv("PROMPT_USER_BG", WHITE)

PATH_FG = os.getenv("PROMPT_PATH_FG", WHITE)
PATH_BG = os.getenv("PROMPT_PATH_BG", BLUE)

VENV_FG = os.getenv("PROMPT_VENV_FG", BLACK)
VENV_BG = os.getenv("PROMPT_VENV_BG", MAGENTA)


# region Styling Utilities
def _zero_width(s):
    """Return the given string, wrapped in zsh zero-width codes.

    This tells zsh that the string is a zero-width string, eg. for prompt
    alignment and cursor positioning purposes. For example, ANSI escape
    sequences should be marked as zero-width.

    """
    return f"%{{{s}%}}"


def _foreground(s, color):
    colors = {
        BLACK: "\x1b[30m",
        RED: "\x1b[31m",
        GREEN: "\x1b[32m",
        YELLOW: "\x1b[33m",
        BLUE: "\x1b[34m",
        MAGENTA: "\x1b[35m",
        CYAN: "\x1b[36m",
        WHITE: "\x1b[37m",
    }
    return f"{_zero_width(colors[color])}{s}"


def _background(s, color):
    colors = {
        BLACK: "\x1b[40m",
        RED: "\x1b[41m",
        GREEN: "\x1b[42m",
        YELLOW: "\x1b[43m",
        BLUE: "\x1b[44m",
        MAGENTA: "\x1b[45m",
        CYAN: "\x1b[46m",
        WHITE: "\x1b[47m",
    }
    return f"{_zero_width(colors[color])}{s}"


def _bold(s):
    bold = _zero_width("\x1b[1m")
    return f"{bold}{s}"


def _quick_bold(s):
    end_bold = _zero_width("\x1b[22m")
    return f"{_bold(s)}{end_bold}"


def _underline(s):
    underline = _zero_width("\x1b[4m")
    return f"{underline}{s}"


def _reverse(s):
    reverse = _zero_width("\x1b[7m")
    return f"{reverse}{s}"


def _reset(s):
    reset = _zero_width("\x1b[0m")
    return f"{s}{reset}"


def _newline():
    return _zero_width("\n")


def style(s, foreground=None, background=None, bold=False, underline=False, reverse=False):
    """Return the given string, wrapped in the given color.

    Foreground and background can be one of:
    black, red, green, yellow, blue, magenta, cyan, white.

    Also resets the color and other attributes at the end of the string.
    """
    if not s:
        return s
    if foreground:
        s = _foreground(s, foreground)
    if background:
        s = _background(s, background)
    if bold:
        s = _bold(s)
    if underline:
        s = _underline(s)
    if reverse:
        s = _reverse(s)
    s = _reset(s)
    return s


# endregion Styling Utilities


# region Part Methods
def _terminal_width():
    """Return the width of the terminal in characters."""
    width = os.popen("stty size", "r").read().split()[1]
    return int(width)


def _horizontal_rule(char=SPACER):
    """Return a long string of the given characters.

    The string will be as long as the width of the user's terminal in
    characters, and will have a newline at the end.
    """
    width = _terminal_width()
    return char * width + _zero_width("\n")


def _spacer(width: int, char=SPACER):
    """Return a string of spaces with the given width, or empty string if width is 0."""
    return char * width


def _shorten_path(path: str, max_length=MAX_PATH_LENGTH):
    """Return the given path, shortened if it's too long.

    Parent directories will be collapsed.

    Examples:
    /home/ubuntu -> ~
    /home/ubuntu/repos/django3g/core-> ~/repos/django3g/core
    /home/ubuntu/repos/django3g/core/management/commands/superimporter -> ~/r/c/d/m/commands/superimporter
    """
    # Replace the user's homedir in path with ~
    if not path.startswith("~"):
        homedir = os.path.expanduser("~")
        if path.startswith(homedir):
            path = "~" + path[len(homedir) :]

    parts = path.split(os.sep)

    # Remove empty strings.
    parts = [part for part in parts if part]

    # Bold the last part of the path
    if parts and any(parts):
        parts[-1] = _bold(parts[-1])

    # Rejoin the parts
    path = os.sep.join(parts)

    # Starting from the root dir, truncate each dir to just its first letter
    # until the full path is < max_length or all the dirs have already been truncated.
    # Never truncate the last dir.
    for i, part in enumerate(parts[:-1]):
        if len(path) <= max_length:
            break
        part = parts[i]
        if len(part) > 1:
            first_letter = part[0]
            parts[i] = first_letter
            path = os.sep.join(parts)

    return path


def get_path(path: str, max_length=MAX_PATH_LENGTH):
    """Return the given path, shortened if it's too long, with a folder symbol."""
    short_path = _shorten_path(path, max_length)
    return {"text": f"{DIR_SYMBOL} {short_path}", "foreground": PATH_FG, "background": PATH_BG}


def get_current_working_dir():
    """Return the full absolute path to the current working directory."""
    current_working_dir = "[not found]"
    try:
        current_working_dir = _shorten_path(os.getcwd())
    except OSError as exc:
        if exc.errno != 2:
            raise exc
    return {"text": current_working_dir, "foreground": PATH_FG, "background": PATH_BG}


def get_venv():
    """Return the name of the current virtual environment, or blank string if none."""
    path = os.getenv("VIRTUAL_ENV", "")
    shell_level = os.getenv("SHLVL", "0")
    text = ""
    if path:
        # We're in a virtualenv, and not deeply nested shells.
        path = os.path.basename(path)
        text += f"{path} {VENV_SYMBOL}"
    try:
        shell_level = int(shell_level)
        if shell_level > 1:
            if text:
                text += " "
            text += f"{'('*shell_level}shell{')'*shell_level}"
    except (TypeError, ValueError):
        pass

    return {"text": text, "foreground": VENV_FG, "background": VENV_BG}


def get_git_branch():
    """Return the current git branch, or blank string if not in a git repo."""
    try:
        output = subprocess.check_output("git status".split(), stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        # Non-zero return code, assume the current working dir is not in a git
        # repo.
        return ""
    first_line = output.split(b"\n", maxsplit=1)[0]
    first_line = first_line.decode("utf-8")
    branch_name = first_line.split(" ")[-1]
    return f"{BRANCH_SYMBOL} {branch_name}"


def _get_user_name():
    """Return the current user's username, or '????' if `USER` env var is not set."""
    return os.getenv("USER") or "????"


def _get_host_name():
    """Return the current host's hostname using socket.gethostname(), or '[unknown host]' if it cannot be determined."""
    return socket.gethostname() or "[unknown host]"


def get_user_at_host():
    """Return 'user@host' if in an SSH session, else a placeholder symbol."""
    styles = {"text": "", "foreground": USER_FG, "background": USER_BG, "bold": False}
    if os.environ.get("SSH_CONNECTION"):
        styles["text"] = f"{_get_user_name()}@{_get_host_name()}"
    else:
        styles["text"] = USER_PLACEHOLDER
        styles["bold"] = True

    return styles


def get_chevron(last_exit_status=False):
    """Return a chevron symbol, colored green if last exit status is zero, red otherwise."""
    fg = RED if last_exit_status else GREEN
    return style(CHEVRON, foreground=fg, bold=True)


def get_last_exit_status_from_code(last_exit_str="0"):
    """Return the last exit status as a string, or blank string if zero."""

    output = {"text": "", "foreground": BLACK, "background": RED, "bold": True}

    # Exit early if last exit status is zero or not an integer.
    if last_exit_str == "0":
        return output
    try:
        last_exit_code = int(last_exit_str)
    except (TypeError, ValueError):
        return output

    # Update output for a fallback generic error message.
    output["text"] = f"ERR {last_exit_code}"

    # Concise message dict
    messages = {
        1: {"text": "ERROR", "foreground": WHITE, "background": RED},
        2: {"text": "USAGE", "foreground": BLACK, "background": YELLOW},
        126: {"text": "NOEXEC", "foreground": BLACK, "background": YELLOW},
        127: {"text": "CMD NOT FOUND", "foreground": WHITE, "background": RED},
        128: {"text": "BAD EXIT", "foreground": BLACK, "background": YELLOW},
        130: {"text": "INTERRUPTED", "foreground": BLACK, "background": CYAN},
        134: {"text": "ABORT", "foreground": WHITE, "background": RED},
        137: {"text": "KILLED", "foreground": WHITE, "background": RED},
        139: {"text": "SEGFAULT", "foreground": WHITE, "background": RED},
        143: {"text": "TERM", "foreground": BLACK, "background": CYAN},
        255: {"text": "FATAL", "foreground": WHITE, "background": RED},
    }

    return messages.get(last_exit_code, output)


def _parse_zsh_vcs_info(git_info: str):
    """Parse vcs info from zsh into a dictionary."""
    info = {}
    for item in git_info.split("|"):
        if ":" in item:
            key, value = item.split(":", 1)
            info[key] = value
    return info


def _parse_git_porcelain(git_porcelain: str):
    """Parse git porcelain output into a dictionary. Expected command:
    `git status --porcelain=v2 --show-stash --branch --ahead-behind --untracked-files=normal`
    """
    git_porcelain = git_porcelain.strip()
    _msg = (
        "Make sure to run"
        " `git status --porcelain=v2 --show-stash --branch --ahead-behind --untracked-files=normal`"
        " and pass its output to the script using the `--git-porcelain` argument."
        f" Got: '{git_porcelain}'"
    )
    if not git_porcelain:
        raise ValueError(f"No git porcelain information found. {_msg}")

    lines = git_porcelain.splitlines()

    if not any(lines):
        raise ValueError(f"Failed to parse git porcelain information. No lines found in the input. {_msg}")

    info = {
        "branch": "unknown",
        "ahead": 0,
        "behind": 0,
        "staged": 0,
        "unstaged": 0,
        "untracked": 0,
        "unmerged": 0,
        "stash": 0,
    }

    for line in lines:
        if line.startswith("# branch.head"):
            info["branch"] = line.split(" ", 2)[2]
        elif line.startswith("#branch.ab"):
            # Example: "# branch.ab +1 -2"
            parts = line.split(" ")
            for part in parts[2:]:
                if part.startswith("+"):
                    info["ahead"] = int(part[1:])
                elif part.startswith("-"):
                    info["behind"] = int(part[1:])
        elif line.startswith("# stash"):
            info["stash"] = int(line.split(" ", 2)[2])
        elif line and not line.startswith("#"):
            # Parse individual file status lines.
            # Example: "1 M. N... 100644 100644 100644 abcdef1 abcdef2 file.txt"
            indicator = line[0]
            if indicator == "1" or indicator == "2":
                if line[2] != ".":
                    info["staged"] += 1
                if line[3] != ".":
                    info["unstaged"] += 1
            elif indicator == "?":
                info["untracked"] += 1
            elif indicator == "u":
                info["unmerged"] += 1
    return info


def get_git_info(git_info: str):
    """Return a git info part dictionary."""
    info = _parse_zsh_vcs_info(git_info)
    if not git_info or not any(info) or not info.get("branch"):
        return {
            "text": "",
            "foreground": BLACK,
            "background": YELLOW,
        }

    text = ""
    git_fg = BLACK
    git_bg = YELLOW

    # VCS symbol, or uppercase VCS name if not git.
    vcs = info.get("vcs", "")
    text += BRANCH_SYMBOL if vcs == "git" else vcs.upper()

    # Get branch name and add it.
    branch = info["branch"]
    text += f" {branch}"

    # Special coloring for main/master branch.
    if branch in ("main", "master"):
        git_fg = WHITE
        git_bg = GREEN

    # Staged changes.
    staged = info.get("staged", "0")
    if staged not in ("0", ""):
        text += f" +{staged}"

    # Unstaged changes.
    unstaged = info.get("unstaged", "0")
    if unstaged not in ("0", ""):
        text += f" ~{unstaged}"

    # Misc changes.
    misc = info.get("misc", "0")
    if misc not in ("0", ""):
        text += f" *{misc}"

    # Action.
    action = info.get("action", "")
    if action:
        text += f" [{action}]"
        git_fg = BLACK
        git_bg = MAGENTA

    return {
        "text": text,
        "foreground": git_fg,
        "background": git_bg,
    }


def get_vcs_info(git_porcelain: str, vcs_info=None, time_of_last_commit=None):
    """Return a git info part dictionary based on git porcelain output.
    Expected command:
    `git status --porcelain=v2 --show-stash --branch --ahead-behind --untracked-files=normal`
    """

    # Default color scheme
    git_fg = BLACK
    git_bg = YELLOW

    # Add the branch symbol first
    parts = [_quick_bold(BRANCH_SYMBOL)]

    # Parse the output from the `git porcelain` command
    try:
        porcelain = _parse_git_porcelain(git_porcelain)
    except ValueError:
        return {
            "text": "",
            "foreground": git_fg,
            "background": git_bg,
        }

    # Get branch name and add it, color the branch specially if main/master.
    branch = porcelain["branch"]
    parts.append(_quick_bold(branch))  # Bold ONLY the branch name
    if branch in ("main", "master"):
        # Style the git info differently if we're on the main branch.
        git_bg = BLUE
        git_fg = WHITE

    # Action from vcs_info
    if vcs_info and any(vcs_info) and vcs_info.get("action"):
        action = vcs_info["action"]
        parts = [f"[{action}]"] + parts
        git_fg = BLACK
        git_bg = RED

    # Add status counts from porcelain
    if porcelain["ahead"] > 0:
        parts.append(f"{GIT_AHEAD}{porcelain['ahead']}")
    if porcelain["behind"] > 0:
        parts.append(f"{GIT_BEHIND}{porcelain['behind']}")
    if porcelain["staged"] > 0:
        parts.append(f"{GIT_STAGED}{porcelain['staged']}")
    if porcelain["unstaged"] > 0:
        parts.append(f"{GIT_UNSTAGED}{porcelain['unstaged']}")
    if porcelain["untracked"] > 0:
        parts.append(f"{GIT_UNTRACKED}{porcelain['untracked']}")
    if porcelain["stash"] > 0:
        parts.append(f"{GIT_STASHED}{porcelain['stash']}")

    # Time since last commit
    if time_of_last_commit is not None:
        pretty_msg = get_time_since_last_commit(time_of_last_commit)
        if pretty_msg:
            parts.append(f"({pretty_msg})")

    return {
        "text": " ".join(parts),
        "foreground": git_fg,
        "background": git_bg,
    }


def get_time_since_last_commit(time_of_last_commit):
    """Return the time since the last git commit in a human-readable format."""
    try:
        time_of_last_commit = int(time_of_last_commit)
    except (TypeError, ValueError):
        return ""
    time_since_last_commit = int(datetime.now().timestamp()) - time_of_last_commit
    if time_since_last_commit < 60:  # 1 minute
        return "just now"
    elif time_since_last_commit < 3600:  # 1 hour
        return f"{time_since_last_commit // 60}m"
    elif time_since_last_commit < 86400:  # 1 day
        return f"{time_since_last_commit // 3600}h"
    else:
        return f"{time_since_last_commit // 86400}d"


# endregion Part Methods


def printable_length(s):
    """Remove ANSI escape sequences and zero-width markers to get printable length"""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    zero_width = re.compile(r"%\{.*?%\}")
    return len(zero_width.sub("", ansi_escape.sub("", s)))


def parts_assembler(parts, side="left"):
    """Assemble prompt parts with separators."""
    assembly = ""
    parts = [part for part in parts if part.get("text")]  # Remove empty parts.
    last_bg = None
    for i, part in enumerate(parts):
        part_text = part.pop("text")
        part_fg = part.pop("foreground")
        part_bg = part.pop("background")
        styles = part  # Remaining keys are styles.
        if assembly:
            # Not the first part, add a separator before it.
            match side:
                case "left":
                    symbol = SEP_R
                    fg = last_bg
                    bg = part_bg
                case "right":
                    symbol = SEP_L
                    fg = part_bg
                    bg = last_bg
                case _:
                    raise ValueError(f"Invalid side: {side}")
            assembly += style(symbol, foreground=fg, background=bg)
        else:
            # First part, add a leading separator with foreground matching the part's background.
            sep = style(SEP_L, foreground=part_bg, background=None)
            assembly += sep
        assembly += style(
            " " + part_text + " ",
            foreground=part_fg,
            background=part_bg,
            **styles,
        )
        if i == len(parts) - 1:
            # Last part, add a trailing separator with foreground matching the part's background.
            sep = style(SEP_R, foreground=part_bg, background=None)
            assembly += sep
        last_bg = part_bg
    return assembly


# def left_prompt(current_working_dir, last_exit_status=None):
#     """Return my zsh left prompt."""
#     # hr = style(horizontal_rule("·"))
#     parts = (
#         {"text": get_user_at_host(), "foreground": BLACK, "background": BLUE},
#         {"text": shorten_path(current_working_directory), "foreground": BLACK, "background": GREEN},
#         {"text": get_git_branch(), "foreground": BLACK, "background": CYAN},
#     )
#     # return f"{hr} {user} {cwd} {chevron} "
#     assembled_parts = parts_assembler(parts, side="left")
#     # return f"{hr}{assembled_parts} {get_chevron(last_exit_status)} "
#     newline = _zero_width("\n")
#     return f"{newline}{assembled_parts} {get_chevron(last_exit_status)} "
#     # return f"{assembled_parts}{newline} {get_chevron(last_exit_status)} "


# def right_prompt(last_exit_status):
#     """Return my zsh right prompt."""
#     parts = (
#         {"text": last_exit_status, "foreground": BLACK, "background": RED, "bold": True},
#         {"text": get_venv(), "foreground": BLACK, "background": MAGENTA},
#     )
#     assembled_parts = parts_assembler(parts, side="right")
#     return assembled_parts


def bash_prompt(parts: dict):
    """Return a single bash prompt line."""

    parts_copy = deepcopy(parts)
    path_length = MAX_PATH_LENGTH
    path_text = parts["path"]["text"][2:]  # Ignore folder symbol for length calculation.

    left_parts = [parts_copy[key] for key in ("user", "path", "vcs")]
    right_parts = [parts_copy[key] for key in ("exit", "venv")]
    left_side = parts_assembler(left_parts, side="left")
    right_side = parts_assembler(right_parts, side="right")

    # Calculate spacing to right-align the right prompt.
    content_length = printable_length(left_side) + printable_length(right_side)

    space = _terminal_width() - content_length - 1
    if space < 0:
        # We don't have enough space to fit both halves of the prompt, attempt to shorten path further
        path_length = printable_length(path_text) + space - 2
        new_path = get_path(path_text, max_length=path_length)
        left_parts = [parts["user"], new_path, parts["vcs"]]
        left_side = parts_assembler(left_parts, side="left")
        content_length = printable_length(left_side) + printable_length(right_side)
        space = _terminal_width() - content_length - 1

    return f"{left_side}{_spacer(space)}{right_side}{_newline()}{get_chevron(parts['exit']['text'])} "


def _get_parts(args):
    """Validate command-line arguments."""
    user = get_user_at_host()
    venv = get_venv()

    last_exit_status = get_last_exit_status_from_code(args.last_exit_code)
    cwd = args.current_working_dir
    path = get_path(cwd) if cwd else get_current_working_dir()

    parsed_vcs_info = _parse_zsh_vcs_info(args.vcs_info or "")
    git_porcelain = args.git_porcelain or ""
    time_of_last_commit = args.time_of_last_commit or ""
    vcs = get_vcs_info(git_porcelain, parsed_vcs_info, time_of_last_commit)

    return {"user": user, "path": path, "vcs": vcs, "exit": last_exit_status, "venv": venv}


def main():
    """Print the prompt."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "side",
        metavar="left|right|bash",
        choices=("left", "right", "bash"),
        help="which zsh prompt to print (the left- or right-side prompt)",
    )
    parser.add_argument(
        "--last-exit-code",
        dest="last_exit_code",
        # type=int,
        help="the exit status (int) of the previous shell command "
        "(default: None, printing last exit status will not be "
        "supported)",
    )
    parser.add_argument(
        "--current-working-dir",
        dest="current_working_dir",
        type=str,
        help="the current working directory (default: None, using `os.getcwd()`)",
    )
    parser.add_argument(
        "--vcs-info",
        dest="vcs_info",
        type=str,
        help="the vcs information (default: None)",
    )
    parser.add_argument(
        "--git-porcelain",
        dest="git_porcelain",
        type=str,
        help="the git information (default: None)",
    )
    parser.add_argument(
        "--time-of-last-commit",
        dest="time_of_last_commit",
        type=str,
        help="the time of the last git commit in seconds since epoch (default: None, using `git log -1 --format=%ct`)",
    )

    args = parser.parse_args()

    parts = _get_parts(args)

    match args.side:
        # case "left":
        #     output = left_prompt(cwd, last_exit_status)
        # case "right":
        #     output = right_prompt(last_exit_status)
        case "bash":
            output = bash_prompt(parts)
        case _:
            parser.error(f"Invalid side: {args.side}")

    print(output)


if __name__ == "__main__":
    main()
