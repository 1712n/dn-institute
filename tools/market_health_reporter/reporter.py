import requests
import json
from transformers import RagTokenizer, RagRetriever, RagTokenForGeneration
import torch
class MarketHealthReporter:
    def __init__(self, api_key, base_url="https://api.dn.institute/market-health"):
        response = requests.get(f"{self.base_url}/metrics/{metric_id}", headers={"Authorization": f"Bearer {self.api_key}"})
        return response.json()
    def initialize_rag(self):
        self.tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")
        self.retriever = RagRetriever.from_pretrained("facebook/rag-token-nq", index_name="exact", use_dummy_dataset=True)
        self.model = RagTokenForGeneration.from_pretrained("facebook/rag-token-nq", retriever=self.retriever)

    def generate_report_with_rag(self, metric_data):
        input_text = f"Generate a report on the following market health metric data: {metric_data}"
        input_ids = self.tokenizer.prepare_seq2seq_batch([input_text], return_tensors="pt")
        generated_ids = self.model.generate(input_ids["input_ids"])
        report = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        return report[0]

    def generate_report(self, metric_id):
        metric_data = self.fetch_metric_data(metric_id)
        if not hasattr(self, 'model'):
            self.initialize_rag()
        report = self.generate_report_with_rag(metric_data)
        return report