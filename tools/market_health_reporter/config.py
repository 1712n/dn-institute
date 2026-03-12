OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")

# RAG Configuration 🌰
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
MAX_RAG_ARTICLES = 5
RAG_SEARCH_QUERY_TEMPLATES = [
    "{exchange} cryptocurrency market news {date}",
    "{metric} spike analysis {exchange} {date}",
    "crypto exchange {exchange} {metric} unusual activity {date}"
]

# Report Configuration
REPORT_TEMPLATES_DIR = "templates"
OUTPUT_DIR = "output"