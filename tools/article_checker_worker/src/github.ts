import type { DiffFile } from './types.js'

const GITHUB_API = 'https://api.github.com'

export async function fetchPrDiff(
  owner: string,
  repo: string,
  prNumber: number,
  token: string
): Promise<string> {
  const url = `${GITHUB_API}/repos/${owner}/${repo}/pulls/${prNumber}`
  const res = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'application/vnd.github.v3.diff',
      'User-Agent': 'ArticleCheckerWorker/1.0',
    },
  })
  if (!res.ok) throw new Error(`Failed to fetch PR diff: ${res.status}`)
  return res.text()
}

export async function postComment(
  owner: string,
  repo: string,
  issueNumber: number,
  body: string,
  token: string
): Promise<void> {
  const url = `${GITHUB_API}/repos/${owner}/${repo}/issues/${issueNumber}/comments`
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
      'User-Agent': 'ArticleCheckerWorker/1.0',
    },
    body: JSON.stringify({ body }),
  })
  if (!res.ok) throw new Error(`Failed to post comment: ${res.status}`)
}

export function parseDiff(diffText: string): DiffFile[] {
  const files: DiffFile[] = []
  const fileSections = diffText.split(/^diff --git /m).filter(Boolean)

  for (const section of fileSections) {
    const filenameMatch = section.match(/a\/(.+?) b\//)
    if (!filenameMatch) continue

    const filename = filenameMatch[1]
    // Only process markdown files
    if (!filename.endsWith('.md')) continue

    // Extract added lines (lines starting with +, excluding +++ header)
    const lines = section.split('\n')
    const addedLines: string[] = []

    for (const line of lines) {
      if (line.startsWith('+++')) continue
      if (line.startsWith('+')) {
        addedLines.push(line.substring(1))
      }
    }

    if (addedLines.length > 0) {
      files.push({ filename, content: addedLines.join('\n') })
    }
  }

  return files
}

export function isReviewer(username: string, reviewersJson: string): boolean {
  try {
    const reviewers: string[] = JSON.parse(reviewersJson)
    return reviewers.includes(username)
  } catch {
    return false
  }
}

export function parseRepoInfo(repoFullName: string): { owner: string; repo: string } {
  const [owner, repo] = repoFullName.split('/')
  return { owner, repo }
}
