import argparse
import yaml
import cohere
import requests
import re
import os
import pickle
import hnswlib
from typing import List, Dict
from unstructured.partition.html import partition_html
from unstructured.chunking.title import chunk_by_title
from utils import name_list_writer, extract_url_from_comment, read_file, parse_txt_file, save_output
import nltk
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')


data_path = 'tools\rag_report\data'
index_path = 'tools\rag_report\db\index'
vectors_path = 'tools\rag_report\db\vectors'
names_file = 'tools\rag_report\name_list_data.txt'
system_prompt_1 = 'tools\rag_report\prompts\system_prompt_1.txt'
system_prompt = 'tools\rag_report\prompts\rag_system_prompt.txt'
output_path = 'tools\rag_report\outputs'


# Vectorstore hyperparameters
TOP_K = 5
EMBEDDING_SIZE = 1024
BATCH_SIZE = 90
SIMILARITY_FUNCTION = "l2"
EF_CONSTRUCTION = 200
M = 48

# LLM hyperparameters
EMBED_MODEL = "embed-english-v3.0"
CHAT_MODEL = "command-r-plus-08-2024"
TEMPERATURE = 0
MAX_NUMBER_TOKENS = 126000


def parse_cli_args():
    """
    Parse CLI arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohere-api-key", dest="cohere_api_key", help="LLM API key", required=True)
    parser.add_argument("--issue", dest="issue", help="Issue number", required=True)
    parser.add_argument("--article-raw-url", dest="article_raw_url", help="Market Health Reporter post (article) name", required=True)
    parser.add_argument("--github-token", dest="github_token", help="Github token", required=True)
    return parser.parse_args()


class Vectorstore:
    def __init__(self, raw_documents: List[Dict[str, str]], cohere_client):
        self.raw_documents = raw_documents
        self.docs = []
        self.docs_embs = []
        self.retrieve_top_k = TOP_K
        self.load_and_chunk()
        self.embed(cohere_client)
        self.index()
    
    def load_and_chunk(self) -> None:
        """
        Loads the text from the sources and chunks the HTML content for new documents only.
        """
        print("Loading documents for embedding...")
        for raw_document in self.raw_documents:
            elements = partition_html(filename=os.path.join(data_path, raw_document["name"]))
            chunks = chunk_by_title(elements)
            for chunk in chunks:
                self.docs.append(
                    {
                        "text": str(chunk),
                        "name": raw_document["name"],
                    }
                )
        print("Loading documents for embedding...Done")

    def embed(self, cohere_client) -> None:
        """
        Embeds the document chunks using the Cohere API.
        """
        print("Embedding document chunks...")
        batch_size = BATCH_SIZE
        self.docs_len = len(self.docs)
        for i in range(0, self.docs_len, batch_size):
            batch = self.docs[i : min(i + batch_size, self.docs_len)]
            texts = [item["text"] for item in batch]
            docs_embs_batch = cohere_client.embed(texts=texts, 
                                                  model=EMBED_MODEL, 
                                                  embedding_types = ["float"], 
                                                  input_type="search_document"
                                                  ).embeddings.float_
            self.docs_embs.extend(docs_embs_batch)
        print("Embedding document chunks...Done")
        print(f"Embeddings batch received: {len(docs_embs_batch)}")

    def index(self) -> None:
        """
        Indexes the documents for efficient retrieval.
        """
        print(f"Number of embeddings prepared for indexing: {len(self.docs_embs)}")
        print('Indexing documents...')

        if len(self.docs_embs) > 0:
            print(f"Length of each embedding: {len(self.docs_embs[0])} (should match EMBEDDING_SIZE of {EMBEDDING_SIZE})")

        self.idx = hnswlib.Index(space=SIMILARITY_FUNCTION, dim=EMBEDDING_SIZE)
        self.idx.init_index(max_elements=self.docs_len, ef_construction=EF_CONSTRUCTION, M=M)
        print("Adding items to the index...")
        try:
            self.idx.add_items(data = self.docs_embs)
            print(f"Indexing complete with {self.idx.get_current_count()} documents.")
            print('Indexing documents...Done')
        except Exception as e:
            print(f'An error occurred: {e}')

    def save_index_and_vectors(self) -> None:
      """
      Saves the index to a file.
      """
      print("Saving index...")
      self.idx.save_index(os.path.join(index_path, 'index.bin'))
      print("Index saved.")

      print("Saving vectors...")
      with open(os.path.join(vectors_path, 'vectors.pkl'), "wb") as f:
          pickle.dump(self.docs_embs, f)
      print("Vectors saved.")

    def retrieve(self, query: str, cohere_client) -> List[Dict[str, str]]:
        """
        Retrieves document chunks based on the given query.
        """
        try:
            print('Sending queries to cohere api for embedding...')
            query_emb = cohere_client.embed(
                                            texts=[query], model="embed-english-v3.0", embedding_types= ['float'], input_type="search_query"
                                            ).embeddings.float_
            print('Sending queries to cohere api for embedding...Done')

            if self.idx.get_current_count() == 0:
                print('Index is empty; no documents available for retrieval.')
                return []

            print('Knn quering for retrieving top k docs...')
            doc_ids = self.idx.knn_query(query_emb, k=self.retrieve_top_k)[0][0]
            docs_retrieved = []
            for doc_id in doc_ids:
                     docs_retrieved.append({
                         "text": self.docs[doc_id]["text"],
                         "name": self.docs[doc_id]["name"],
                                             })
            print('Knn quering for retrieving top k docs...Done')
            print(f'{len(docs_retrieved)} docs retrieved')
            return docs_retrieved
        except Exception as e:
            print(f"An error occurred dduring retrieval:{e}")
            return []          


def main():
    print('Starting the script...')  
    try:
        print('Parsing arguments...')
        args = parse_cli_args()
        print('Parsing arguments...Done')
        print('Writing the "name_list_data.txt" file...')
        name_list_writer()
        print('Writing the "name_list_data.txt" file...Done')
        print('Getting the article...')
        raw_url = extract_url_from_comment(args.article_raw_url)
        article = requests.get(raw_url).text
        print('Getting the article...Done')
    except Exception as e:
        print(f'An error occurred: {e}')

    print('Startimg cohere client...')
    cohere_client = cohere.ClientV2(api_key=args.cohere_api_key)
    print('Startimg cohere client...Done')

    print('Initializing vectorstore...')
    vectorstore = Vectorstore(parse_txt_file(names_file), cohere_client)
    print('Initializing vectorstore...Done')
    vectorstore.save_index_and_vectors()

    if article.startswith('---'):
        yaml_content = article.split('---')[1]
        article = article.split('---')[2:]
        yaml_data = yaml.safe_load(yaml_content)
        entities = yaml_data.get('entities')
        marketvenueid = entities[0]
    else:
        print('No YAML sections found')

    print('Running an LLM to create search topics on the index...')
    system_message = read_file(system_prompt_1)
    res = cohere_client.chat(model="command-r-plus-08-2024", 
                    messages=[{"role": "system", "content": system_message},
                            {"role": "user", "content": article,},
                            ],
                temperature = TEMPERATURE,
                )
    queries = res.message.content[0].text.split('\n')
    cleaned_queries = [re.sub(r'^\d+\.\s*', '', query) for query in queries]
    print('Running an LLM to create search topics on the index...Done')
    print(f'Questions created: {cleaned_queries}')

    print('Searching for the similar context...')
    contexts = []
    for query in cleaned_queries:
        contexts.append(vectorstore.retrieve(query, cohere_client))
    print('Searching for the similar context...Done')
    print(f'Similar context found. Total number of context chunks is {len(contexts)}')

    print("Feeding the context into the LLM...")
    rag_system_prompt = read_file(system_prompt)
    add_contents = []
    for i in range(len(contexts)):
        for j in range(len(contexts[i])):
            add_contents.append(contexts[i][j]['text'])

    final_prompt = f"### Instructions:\n {rag_system_prompt} \n\n ### Article:\n {article} \n\n ### Passages with possible additional information:\n {add_contents}"
    tokens = cohere_client.tokenize(text=final_prompt, model="command-r-08-2024", offline=False)
    number_of_tokens = len(tokens.tokens)
    print(f'Total number of tokens is {number_of_tokens}')
    
    if number_of_tokens > MAX_NUMBER_TOKENS:
        print('The number of tokens exceed the MAX number possible')
    else:
        response = cohere_client.chat(model=CHAT_MODEL,
                        messages=[{"role": "user", "content": final_prompt},
                                 ],
                        temperature = TEMPERATURE)
        output = response.message.content[0].text
        print("Feeding the context into the LLM...Done")
        print("The new article: ", output)

        save_output(output, output_path, marketvenueid)
        print('Output is saved.')

if __name__ == "__main__":
    main()
