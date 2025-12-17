#!/usr/bin/env python3
"""Print out zsh prompts."""

# System imports
import argparse
import os
import re
import subprocess
import socket

# Third-party imports

# Internal imports


# Constants
SEP_R = ""
SEP_L = ""
SPACER = "·"
CHEVRON = ""
USER_PLACEHOLDER = " "
ELLIPSIS = "…"
GIT_SYMBOL = ""
HOME_SYMBOL = "⌂"
DIR_SYMBOL = "📁"
VENV_SYMBOL = ""
GIT_AHEAD = "↑"
GIT_BEHIND = "↓"
GIT_STAGED = "+"
GIT_UNSTAGED = "~"
GIT_UNTRACKED = "?"
GIT_STASHED = "*"

MAX_PATH_LENGTH = 50

BLACK = "black"
RED = "red"
GREEN = "green"
YELLOW = "yellow"
BLUE = "blue"
MAGENTA = "magenta"
CYAN = "cyan"
WHITE = "white"


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
def terminal_width():
    """Return the width of the terminal in characters."""
    width = os.popen("stty size", "r").read().split()[1]
    return int(width)


def horizontal_rule(char=" "):
    """Return a long string of the given characters.

    The string will be as long as the width of the user's terminal in
    characters, and will have a newline at the end.

    """
    width = terminal_width()
    return char * width + _zero_width("\n")


def shorten_path(path: str, max_length=MAX_PATH_LENGTH):
    """Return the given path, shortened if it's too long.

    Parent directories will be collapsed. Examples (with SHORT_PATH_LENGTH=3 and MAX_PATH_LENGTH=30):

    /home/user -> ~
    /home/user/repos/django3g/core-> ~/repos/django3g/core
    /home/user/repos/django3g/core/management/commands/superimporter -> ~/rep…/core/dja…/man…/com…/superimporter
    """
    # Replace the user's homedir in path with ~
    homedir = os.path.expanduser("~")
    if path.startswith(homedir):
        path = "~" + path[len(homedir) :]

    parts = path.split(os.sep)

    # Remove empty strings.
    parts = [part for part in parts if part]
    path = os.sep.join(parts)

    # Starting from the root dir, truncate each dir to just its first letter
    # until the full path is < max_length or all the dirs have already been truncated.
    # Never truncate the last dir.
    i = 0
    # while len(path) > max_length and i < len(parts) - 1:
    for i, part in enumerate(parts[:-1]):
        if len(path) <= max_length:
            break
        part = parts[i]
        if len(part) > 1:
            first_letter = part[0]
            parts[i] = first_letter
            path = os.sep.join(parts)
    # return f"{DIR_SYMBOL} {path}"
    return path


def get_current_working_dir():
    """Return the full absolute path to the current working directory."""

    # Code for getting the current working directory, copied from
    # <https://github.com/Lokaltog/powerline/>.
    try:
        cwd = os.getcwd()
    except OSError as e:
        if e.errno == 2:
            # User most probably deleted the directory, this happens when
            # removing files from Mercurial repos for example.
            cwd = "[not found]"
        else:
            raise
    return cwd


def get_venv():
    """Return the name of the current virtual environment, or blank string if none."""
    path = os.getenv("VIRTUAL_ENV", "")
    if path:
        path = os.path.basename(path)
    return f"{path} {VENV_SYMBOL}" if path else ""


def get_git_branch():
    """Return the current git branch, or blank string if not in a git repo."""
    try:
        output = subprocess.check_output("git status".split(), stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        # Non-zero return code, assume the current working dir is not in a git
        # repo.
        return ""
    first_line = output.split(b"\n")[0]
    first_line = first_line.decode("utf-8")
    branch_name = first_line.split(" ")[-1]
    return f"{GIT_SYMBOL} {branch_name}"


def get_user_name():
    """Return the current user's username, or '????' if `USER` env var is not set."""
    return os.getenv("USER") or "????"


def get_host_name():
    """Return the current host's hostname using socket.gethostname(), or '[unknown host]' if it cannot be determined."""
    return socket.gethostname() or "[unknown host]"


def get_user_at_host():
    """Return 'user@host' if in an SSH session, else a placeholder symbol."""
    if os.environ.get("SSH_CONNECTION"):
        return f"{get_user_name()}@{get_host_name()}"
    else:
        return USER_PLACEHOLDER


def get_chevron(last_exit_status=False):
    """Return a chevron symbol, colored green if last exit status is zero, red otherwise."""
    fg = RED if last_exit_status else GREEN
    return style(CHEVRON, foreground=fg, bold=True)


def get_last_exit_status(last_exit_status=0):
    """Return the last exit status as a string, or blank string if zero."""
    try:
        last_exit_status = int(last_exit_status)
    except (TypeError, ValueError):
        return ""
    return f" ERR:{last_exit_status} " if last_exit_status > 0 else ""


def _parse_zsh_vcs_info(git_info: str):
    """Parse vcs info from zsh into a dictionary."""
    info = {}
    for item in git_info.split("|"):
        if ":" in item:
            key, value = item.split(":", 1)
            info[key] = value
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
    text += GIT_SYMBOL if vcs == "git" else vcs.upper()

    # Get branch name and add it.
    branch = info["branch"]
    text += f" {branch}"

    # Special coloring for main/master branch.
    if branch in ("main", "master"):
        git_bg = BLUE
        git_fg = WHITE

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


def get_vcs_string(git_porcelain: str, vcs_info=None):
    """Return a git info part dictionary based on git porcelain output.
    Expected command:
    `git status --porcelain=v2 --show-stash --branch --ahead-behind --untracked-files=normal`
    """
    # print()
    # print("#" * 100)
    # print(f' {" git_porcelain ":-^60} ')
    # print()
    # print(git_porcelain)
    # print()
    # print("#" * 100)
    # print()

    git_fg = BLACK
    git_bg = YELLOW

    if not git_porcelain.strip():
        return {
            "text": "",
            "foreground": git_fg,
            "background": git_bg,
        }

    lines = git_porcelain.strip().splitlines()

    if not lines or not any(lines):
        return {
            "text": "",
            "foreground": git_fg,
            "background": git_bg,
        }

    # Get branch name
    branch = "unknown"
    ahead = 0
    behind = 0
    stash = 0
    changes_staged = 0
    changes_unstaged = 0
    changes_untracked = 0

    # for i, line in enumerate(lines):
    for line in lines:
        if line.startswith("# branch.head"):
            branch = line.split(" ")[2]
        elif line.startswith("# branch.ab"):
            parts = line.split(" ")
            for part in parts[2:]:
                if part.startswith("+"):
                    ahead = int(part[1:])
                elif part.startswith("-"):
                    behind = int(part[1:])
        elif line.startswith("# stash"):
            stash = int(line.split(" ")[2])
        elif line and not line.startswith("#"):
            status = line[:2]
            if status[0] != " ":
                changes_staged += 1
            if status[1] != " ":
                changes_unstaged += 1
            if status == "??":
                changes_untracked += 1
        # else:
        #     print(f"Unrecognized line in git porcelain, line {i}:", line)

    parts = []

    # VCS symbol, or uppercase VCS name if not git.
    vcs = GIT_SYMBOL
    if vcs_info and any(vcs_info) and vcs_info.get("vcs") != "git":
        vcs = vcs_info.get("vcs", "?").upper()
    parts.append(vcs)

    # Get branch name and add it, color the branch specially if main/master.
    parts.append(branch)
    if branch in ("main", "master"):
        git_bg = BLUE
        git_fg = WHITE

    # Action from vcs_info
    if vcs_info and any(vcs_info) and vcs_info.get("action"):
        action = vcs_info["action"]
        parts = [f"[{action}]"] + parts
        git_fg = BLACK
        git_bg = MAGENTA

    if ahead > 0:
        parts.append(f"{GIT_AHEAD}{ahead}")
    if behind > 0:
        parts.append(f"{GIT_BEHIND}{behind}")
    if changes_staged > 0:
        parts.append(f"{GIT_STAGED}{changes_staged}")
    if changes_unstaged > 0:
        parts.append(f"{GIT_UNSTAGED}{changes_unstaged}")
    if changes_untracked > 0:
        parts.append(f"{GIT_UNTRACKED}{changes_untracked}")
    if stash > 0:
        parts.append(f"{GIT_STASHED}{stash}")

    text = " ".join(parts)

    return {
        "text": text,
        "foreground": git_fg,
        "background": git_bg,
    }


# endregion Part Methods


def printable_length(s):
    """Remove ANSI escape sequences and zero-width markers to get printable length"""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    zero_width = re.compile(r"%\{.*?%\}")
    return len(zero_width.sub("", ansi_escape.sub("", s)))


def parts_assembler(parts, side="left"):
    """Assemble prompt parts with separators."""
    prompt = ""
    parts = [part for part in parts if part["text"]]  # Remove empty parts.
    last_bg = None
    for i, part in enumerate(parts):
        part_text = part.pop("text")
        part_fg = part.pop("foreground")
        part_bg = part.pop("background")
        styles = part  # Remaining keys are styles.
        if prompt:
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
            prompt += style(symbol, foreground=fg, background=bg)
        else:
            # First part, add a leading separator with foreground matching the part's background.
            sep = style(SEP_L, foreground=part_bg, background=None)
            prompt += sep
        prompt += style(
            " " + part_text + " ",
            foreground=part_fg,
            background=part_bg,
            **styles,
        )
        if i == len(parts) - 1:
            # Last part, add a trailing separator with foreground matching the part's background.
            sep = style(SEP_R, foreground=part_bg, background=None)
            prompt += sep
        last_bg = part_bg
    return prompt


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


def bash_prompt(current_working_dir, last_exit_status, git_porcelain="", vcs_info=None):
    """Return a single bash prompt line."""
    user = get_user_at_host()
    path = shorten_path(current_working_dir)
    processed_git_info = get_vcs_string(git_porcelain, vcs_info)
    left_parts = [
        {"text": user, "foreground": WHITE, "background": BLUE, "bold": True},
        {"text": path, "foreground": BLACK, "background": GREEN},
        processed_git_info,  # returns a dict with appropriate text, fg, bg
    ]
    venv = get_venv()
    right_parts = [
        {"text": last_exit_status, "foreground": BLACK, "background": RED},
        {"text": venv, "foreground": BLACK, "background": MAGENTA},
    ]
    left_assembly = parts_assembler(left_parts, side="left")
    right_assembly = parts_assembler(right_parts, side="right")
    # Calculate spacing to right-align the right prompt.
    content_length = printable_length(left_assembly) + printable_length(right_assembly)

    needed_space = terminal_width() - content_length - 1
    # print("content_length: ", content_length)
    # print("terminal_width: ", terminal_width())
    # print("needed_space:   ", needed_space)
    spacing = str(SPACER * needed_space) if needed_space else ""
    # print(f'"{spacing}"')
    return f"{left_assembly}{spacing}{right_assembly}{_newline()}{get_chevron(last_exit_status)} "


def main():
    """Print the prompt."""
    side_choices = ("left", "right", "bash")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "side",
        metavar="left|right|bash",
        choices=side_choices,
        help="which zsh prompt to print (the left- or right-side prompt)",
    )
    parser.add_argument(
        "--last-exit-status",
        dest="last_exit_status",
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
    args = parser.parse_args()

    side = args.side
    print(args.last_exit_status)
    last_exit_status = get_last_exit_status(args.last_exit_status)
    print("last_exit_status:", last_exit_status)
    cwd = args.current_working_dir or get_current_working_dir()
    vcs_info = _parse_zsh_vcs_info(args.vcs_info or "")
    git_porcelain = args.git_porcelain or ""
    match side:
        # case "left":
        #     output = left_prompt(cwd, last_exit_status)
        # case "right":
        #     output = right_prompt(last_exit_status)
        case "bash":
            output = bash_prompt(cwd, last_exit_status, git_porcelain, vcs_info)
        case _:
            parser.error(f"Invalid side: {side}")

    print(output)


if __name__ == "__main__":
    main()
