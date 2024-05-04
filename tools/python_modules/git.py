from tools.python_modules.utils import execute, logging_decorator
import requests


@logging_decorator("Get PR")
def get_pull_request(github, pull_url: str):
    url_split = pull_url.split("/")

    if url_split[2] == "github.com":
        repo_name = url_split[3] + "/" + url_split[4]
    elif url_split[2] == "api.github.com":
        repo_name = url_split[4] + "/" + url_split[5]

    repo = github.get_repo(repo_name)
    pr_num = int(url_split[-1])
    print(f"Getting PR {pr_num} from {repo_name}")
    pr = repo.get_pull(pr_num)
    return pr


@logging_decorator("Get Diff From Git")
def get_diff_by_git(pr, pr_base: str, pr_head: str, subpath: str) -> str:
    fetch_cmd = ["git", "fetch", "--unshallow", "origin", pr_head]
    execute(fetch_cmd)

    diff_cmd = [
        "git",
        "diff",
        "--no-prefix",
        "--unified=0",
        f"{pr_base}...{pr_head}",
        "--",
        subpath,
        '| egrep "^\+"',
    ]
    diff = execute(diff_cmd).stdout
    return diff


@logging_decorator("Get Diff From URL")
def get_diff_by_url(pr) -> str:
    url = pr.diff_url
    print(f"Getting diff from {url}\n")

    response = requests.get(url)
    if response.status_code == 200:
        diff = response.text
    else:
        raise Exception(
            "Request was not successful. Status code:", response.status_code
        )

    print(diff)
    return diff


@logging_decorator("Parse Diff")
def parse_diff(diff: str) -> list[dict]:
    # split into files
    raw_files = diff.split("diff --git ")
    raw_files.remove(raw_files[0])  # remove first element which is empty

    # construct files as dictionaries
    files = []
    for raw_file in raw_files:
        # split into segments
        raw_segments = raw_file.split("@@")

        # pop and store file header
        file_header = raw_segments.pop(0)

        # construct segments as dictionaries
        segments = []
        for index, seg in enumerate(raw_segments):
            if index % 2 == 0:
                segment = {
                    "header": raw_segments[index],
                    "body": raw_segments[index + 1],
                }
                segments.append(segment)

        file = {"header": file_header, "body": segments}
        files.append(file)

    print(files)
    return files
