#!/usr/bin/env python3
"""Script to generate a fancy shell prompt with git and virtualenv info.

`.zsh_prompt`
```shell
autoload -Uz add-zsh-hook

update_prompt_info() {
  local sep_l=""
  local sep_r=""

  # local user_host="%F{green}%n@%m%f"
  local user_host="%F{green}${sep_l}%f%K{green}%F{black}%n%K{cyan}%F{green}${sep_r}%F{black}%m%k%f"
  # local cwd="%F{blue}%~%f"
  local cwd="%K{blue}%F{cyan}${sep_r}%F{black}%~%k%F{blue}${sep_r}%f"

  local venv=""
  local git_raw="$("/home/brenden/repos/machine_setup/prompt.py")"
  local git_info=""

  if [[ -n "$VIRTUAL_ENV" ]]; then
    venv="%F{magenta}${sep_l}%K{magenta}%F{black}(${${VIRTUAL_ENV:t}})%k%f"
    if [[ -z "$git_raw" ]]; then
      venv+="%F{magenta}${sep_r}%f"
    fi
  fi

  if [[ -n "$git_raw" ]]; then
    if [[ -n "$venv" ]]; then
      if [[ "$git_raw" == *"*"* ]]; then
        git_info+="%K{magenta}%F{yellow}${sep_l}%f%k"
      elif [[ "$branch_name" == "main" || "$branch_name" == "development" ]]; then
        git_info+="%K{magenta}%F{green}${sep_l}%f%k"
      else
        git_info+="%K{magenta}%F{cyan}${sep_l}%f%k"
      fi
    else
      if [[ "$git_raw" == *"*"* ]]; then
        git_info+="%F{yellow}${sep_l}%f"
      elif [[ "$branch_name" == "main" || "$branch_name" == "development" ]]; then
        git_info+="%F{green}${sep_l}%f"
      else
        git_info+="%F{cyan}${sep_l}%f"
      fi
    fi

    local branch_name="${git_raw#* }"
    echo "* Branch name: $branch_name" >&2
    if [[ "$git_raw" == *"*"* ]]; then
      git_info+="%K{yellow}%F{black} ${git_raw}%k%F{yellow}${sep_r}%f"
    elif [[ "$branch_name" == "main" || "$branch_name" == "development" ]]; then
      git_info+="%K{green}%F{black} ${git_raw}%k%F{green}${sep_r}%f"
    else
      git_info+="%K{cyan}%F{black} ${git_raw}%k%F{cyan}${sep_r}%f"
    fi
  fi

  if [[ $? -eq 0 ]]; then
    caret="%F{green}%f"
  else
    caret="%F{red}%f"
  fi

  PROMPT="${user_host}${cwd} ${caret} "
  RPROMPT="${venv}${git_info}"
}

add-zsh-hook precmd update_prompt_info
```
"""

# System imports
# import os
import subprocess
from datetime import datetime

# Third-party imports
# from colorama import Back, Fore, Style, init

# Internal imports

# init(autoreset=True)


def get_git_status():
    """Return current git branch and dirty flag, or '' if not in a repo."""
    try:
        branch = (
            subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
        )
        status = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
        )
        time_since_last_commit = get_time_since_last_commit()

        dirty = "*" if status else ""
        return f"{branch}{dirty} ({time_since_last_commit})"
    except subprocess.CalledProcessError:
        return ""


def get_time_since_last_commit():
    """ """
    # Get last commit time (as seconds since epoch)
    commit_ts = (
        subprocess.check_output(
            ["git", "log", "-1", "--format=%ct"], stderr=subprocess.DEVNULL
        )
        .decode()
        .strip()
    )

    if commit_ts:
        commit_time = datetime.fromtimestamp(int(commit_ts))
        delta = datetime.now() - commit_time
        minutes = int(delta.total_seconds() // 60)
        if minutes < 60:
            ago = f"{minutes}m"
        elif minutes < 1440:
            ago = f"{minutes // 60}h"
        else:
            ago = f"{minutes // 1440}d"
        ago_str = f"{ago} ago"
    else:
        ago_str = "no commits"

    return ago_str


# def get_virtualenv():
#     """Return name of active Python virtualenv, or ''."""
#     venv = os.environ.get("VIRTUAL_ENV")
#     if venv:
#         name = os.path.basename(venv)
#         return f"{Fore.MAGENTA}({name}){Style.RESET_ALL}"
#     return ""


def main():
    git_info = get_git_status()
    # venv_info = get_virtualenv()
    parts = [
        p
        for p in [
            git_info,
            # venv_info,
        ]
        if p
    ]
    if parts:
        print(" | ".join(parts))
    else:
        print("")


if __name__ == "__main__":
    main()
