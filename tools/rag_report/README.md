## A RAG implementaion for the Market Health Reporter.


### Usage
* You will need [Cohere API Key](https://cohere.com/) added to the GitHub account secretes. 
* The tool uses an existing report (article) from the Market Health Reporter. This is done intentionally to avoid inflaiting the token countduring the Market Health API call. 
* To use the RAG tool, type the command /rag:: followed by a URL link to the Market Health Reporter report. Example:
```
/rag:: https://raw.githubusercontent.com/1712n/dn-institute/refs/heads/main/content/research/market-health/posts/2021-01-05-Senso/index.md
```


## GitHub Actions Workflow
The GitHub Actions workflow performs a RAG implementation for the Market Health Reporter report when a comment containing the keyword `rag::` is made on an issue. The workflow creates a new branch, runs the RAG implementation script, commits the results, and opens a new pull request (PR) with the new report.


### Scripts descriptions:
* `utils.py` contains helper functions for file handling, URL extraction and saving outputs.
* `rag_reporter.py` orchestrates the main workflow:
  - You have to save all .html files from external sources to the 'data' folder. Currently, some SEC press releases are included for testing.
  - The script records all files from the 'data' folder into 'name_list_data.txt' for recordkeeping.
  - It then requests the Market Health report from the provided url.
  - Sends the article to the LLM to generate 5 search topics for further research.
  - Reads HTML files from the 'data' folder, partitions the HTML content into smaller chunks, and stores each chunk for embedding.
  - Embeds document chunks using Cohere's API.
  - Creates and populates a similarity search index with embeddings using HNSWLIB.
  - Saves both the index and embeddings to files in the 'db' directory.
  - Embeds the 5 search topics using Cohere's API.
  - Searches and retrieves top 5 most similar document chunks from the vectorestore.
  - Feeds the article and additional content from vectorstore to the LLM using Cohere's API.
  - Saves the new report to the 'output' directory


### Hyperparameters
- TOP_K = 5: the number of most similar documents to retrieve from the vectorstore. A higher value provides more context but may introduce more noise;
- EMBEDDING_SIZE = 1024: the number of vector dimensions, depending on the [embedding model](https://docs.cohere.com/v2/docs/cohere-embed);
- BATCH_SIZE = 90: the size of text chunks for efficient embedding;
- SIMILARITY_FUNCTION = "l2": the distance function for similarity search, possible options are: 'l2': Eucledian distance, 'ip': Inner product, and 'cosine': Cosine similarity. There is no one-fit-all distance function, the choice of function depends on the data characteristics;
- EF_CONSTRUCTION = 200: defines the construction time/accuracy trade-off in the HNSW index;
- M = 48: defines the maximum number of outgoing connections in the graph for the index. Adjusting EF_CONSTRUCTION and M did not yield significant differences, likely due to the small number of documents;
- EMBED_MODEL = "embed-english-v3.0": the cohere embedding model, selectable from the [embed section](https://docs.cohere.com/v2/docs/cohere-embed);
- CHAT_MODEL = "command-r-plus-08-2024": the cohere LLM model, selectable from the [models section](https://docs.cohere.com/v2/docs/models);
- TEMPERATURE = 0: controls the randomness in generation. For RAG, lower temperatures result in less random outputs;
- MAX_NUMBER_TOKENS = 126000: the maximum number of input tokens, based on the model's context window of 128K tokens.


## Notes
1. The RAG implementation uses a pre-existing report from the Market Health Reporter. This approach avoids increasing the token count during the initial Market Health API call. Additional text in the request can limit the period the Market Health API retrieves data for.
2.  HNSWLIB is used as an in-memory vectorstore to create a lightweight serverless solution. Currently, all documents from the 'data' directory are embedded every time the script runs. Open-source vector databases like ChromaDB offer more efficient solutions for storing embeddings, including metadata for better SQL filtering.
3. LangChain and LlamaIndex offer versatile methods for reading various data types and chunking techniques. However, they can be challenging to customize if the built-in solutions do not meet specific requirements.
4. Cohere LLMs are used due to their free testing tier with API limits of 10 calls per minute and up to 100K tokens per call. The model [command-r-plus-08-2024](https://huggingface.co/CohereForAI/c4ai-command-r-plus-08-2024) has advanced capabilities, including a context length of up to 128K tokens.
5. The script saves new reports to a separate 'output' directory to preserve the original reports.
