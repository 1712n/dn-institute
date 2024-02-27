import os
import subprocess
import re


default_subprocess_config = {
    # FIXME: Is this required?
    # "cwd": os.environ["GITHUB_WORKSPACE"],
    "stdout": subprocess.PIPE,
    "universal_newlines": True,
    "check": True,
}


def execute(cmd: list[str], config: dict = default_subprocess_config):
    cmd_str = " ".join(cmd)
    print(f"Executing: {cmd_str}")
    process = subprocess.run(cmd, **config)
    print(process.stdout)
    print(f"Process exited with code {process.returncode}")
    return process


def logging_decorator(group_name):
    def decorator_wrapper(original_func):
        def wrapper_func(*func_args, **func_kwargs):
            if os.environ.get("GITHUB_ACTIONS") == "true":
                print(f"::group::{group_name}")
                result = original_func(*func_args, **func_kwargs)
                print("::endgroup::")
            else:
                print(f"=={group_name}==\n")
                result = original_func(*func_args, **func_kwargs)
                print("\n==End==\n\n")

            return result

        return wrapper_func

    return decorator_wrapper


def read_file(file_path: str) -> str:
    """
    Reads content from a file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def extract_between_tags(tag, string, strip=True):
    """
    Helper to extract text between XML tags.
    """
    ext_list = re.findall(f"<{tag}\\s?>(.+?)</{tag}\\s?>", string, re.DOTALL)
    if strip:
        ext_list = [e.strip() for e in ext_list]

    if ext_list:
        return ext_list[-1]
    else:
        return None