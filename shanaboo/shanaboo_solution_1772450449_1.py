name = "dn-institute-qa-bot"
main = "index.js"
compatibility_date = "2024-01-01"

[vars]
ENVIRONMENT = "production"

[[env.production.vars]]
ENVIRONMENT = "production"

[env.production.secrets]
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"
CLAUDE_API_KEY = "YOUR_CLAUDE_API_KEY"
WEBHOOK_SECRET = "YOUR_WEBHOOK_SECRET"