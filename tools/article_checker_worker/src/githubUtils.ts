export async function fetchDiffText(prUrl: string, githubToken: string): Promise<string> {
    const headers = {
        "Authorization": `token ${githubToken}`,
        "Accept": "application/vnd.github.v3.diff"
    };

    const response = await fetch(prUrl, { headers });

    if (!response.ok) {
        throw new Error(`GitHub API responded with status: ${response.status}`);
    }

    return await response.text();
}

export function extractAdditionsFromDiff(diff: string): string {
    const additionLinesRegex = /^\+(?!\+\+ ).*$/gm;
    const additions = diff.match(additionLinesRegex);
    const cleanAdditions = additions ? additions.map(line => line.substring(1)).join(' ') : '';

    const fileNameRegex = /diff --git a\/(.+?) b\//;
    const fileNameMatch = diff.match(fileNameRegex);
    const fileName = fileNameMatch ? fileNameMatch[1] : 'unknown-file';

    return `${fileName}\n${cleanAdditions}`;
}

interface GitHubCommentResponse {
    html_url: string;
    [key: string]: any;
}

export async function postGitHubComment(pullUrl: string, comment: string, githubToken: string): Promise<void> {
    const issueUrl = pullUrl.replace('/pulls/', '/issues/');
    const url = `${issueUrl}/comments`;

    const headers = {
        "Authorization": `Bearer ${githubToken}`,
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    };

    const response = await fetch(url, {
        method: "POST",
        headers: headers,
        body: JSON.stringify({ body: comment }),
    });

    if (!response.ok) {
        throw new Error(`GitHub API responded with status: ${response.status}`);
    }

    const data = await response.json() as GitHubCommentResponse;
    console.log(`Comment posted successfully: ${data.html_url}`);
}