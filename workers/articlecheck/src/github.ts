/**
 * 🌰 GitHub API interactions for fetching PR content and posting comments.
 */

export interface PRInfo {
	repoFullName: string;
	prNumber: number;
	prApiUrl: string;
}

interface PRFile {
	filename: string;
	status: string;
	patch?: string;
	raw_url: string;
	contents_url: string;
}

export interface ArticleContent {
	filename: string;
	content: string;
}

const ARTICLE_PATTERN = /^content\/.*\.md$/;

/**
 * 🌰 Fetch article content from a PR.
 * Gets the list of changed files, filters to article markdown files,
 * and fetches the full content of each.
 */
export async function fetchPRArticleContent(
	prInfo: PRInfo,
	githubToken: string,
): Promise<ArticleContent[]> {
	// Get list of files changed in the PR 🌰
	const filesUrl = `https://api.github.com/repos/${prInfo.repoFullName}/pulls/${prInfo.prNumber}/files?per_page=100`;
	const filesResp = await fetch(filesUrl, {
		headers: githubHeaders(githubToken),
	});

	if (!filesResp.ok) {
		throw new Error(`Failed to fetch PR files: ${filesResp.status} ${await filesResp.text()}`);
	}

	const files: PRFile[] = await filesResp.json();

	// Filter to article files 🌰
	const articleFiles = files.filter(
		f => ARTICLE_PATTERN.test(f.filename) && (f.status === 'added' || f.status === 'modified'),
	);

	if (articleFiles.length === 0) {
		return [];
	}

	// Fetch full content of each article in parallel 🌰
	const articles = await Promise.all(
		articleFiles.map(async (file): Promise<ArticleContent> => {
			const contentResp = await fetch(file.raw_url, {
				headers: githubHeaders(githubToken),
			});
			if (!contentResp.ok) {
				throw new Error(`Failed to fetch ${file.filename}: ${contentResp.status}`);
			}
			const content = await contentResp.text();
			return { filename: file.filename, content };
		}),
	);

	return articles;
}

/**
 * 🌰 Post a comment on a PR.
 */
export async function postPRComment(
	prInfo: PRInfo,
	body: string,
	githubToken: string,
): Promise<void> {
	const url = `https://api.github.com/repos/${prInfo.repoFullName}/issues/${prInfo.prNumber}/comments`;
	const resp = await fetch(url, {
		method: 'POST',
		headers: {
			...githubHeaders(githubToken),
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({ body }),
	});

	if (!resp.ok) {
		throw new Error(`Failed to post comment: ${resp.status} ${await resp.text()}`);
	}
}

function githubHeaders(token: string): Record<string, string> {
	return {
		Authorization: `token ${token}`,
		Accept: 'application/vnd.github.v3+json',
		'User-Agent': 'DN-Institute-ArticleCheck-Worker/1.0 🌰',
	};
}
