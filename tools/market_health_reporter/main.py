#!/usr/bin/env python3 🌰
"""
Market Health Reporter - Main Entry Point
"""
from market_health_api import MarketHealthAPI
from report_generator import ReportGenerator
from data_processor import DataProcessor
from rag_engine import RAGEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
    parser.add_argument("--output-dir", default="./reports", help="Output directory for reports")
    parser.add_argument("--config", default="config.yaml", help="Configuration file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--enable-rag", action="store_true", help="Enable RAG for additional context")
    parser.add_argument("--max-articles", type=int, default=5, help="Maximum articles to retrieve via RAG")
    
    return parser.parse_args()

def load_config(config_path: str) -> Dict:
    api = MarketHealthAPI()
    processor = DataProcessor(config)
    generator = ReportGenerator(config)
    
    # Initialize RAG engine if enabled
    rag_engine = None
    if args.enable_rag:
        openai_key = os.getenv("OPENAI_API_KEY")
        serpapi_key = os.getenv("SERPAPI_API_KEY")
        if not openai_key or not serpapi_key:
            raise ValueError("OPENAI_API_KEY and SERPAPI_API_KEY required for RAG")
        rag_engine = RAGEngine(openai_key, serpapi_key)

    # Fetch market health data
    logger.info(f"Fetching data for {args.exchange} on {args.date}")
    # Process metrics
    logger.info("Processing metrics...")
    processed_metrics = processor.process_metrics(raw_data)
    
    # Get RAG context if enabled
    rag_context = {}
    if rag_engine and processed_metrics:
        logger.info("Retrieving additional context via RAG...")
        rag_context = rag_engine.get_relevant_context(
            exchange=args.exchange,
            date=args.date,
            metrics=processed_metrics[:config["rag"]["max_articles"]],
            max_articles=args.max_articles
        )

    # Generate report with RAG context
    logger.info("Generating report...")
    report = generator.generate_report(
        exchange=args.exchange,
        metrics=processed_metrics,
        raw_data=raw_data,
        output_dir=args.output_dir,
        config=config,
        rag_context=rag_context
    )

    logger.info(f"Report generated: {report}")