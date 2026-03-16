import random
import time

class MarketHealthAnalyzer:
    def __init__(self, data_source):
        self.data_source = data_source

    def analyze_market(self):
        # Simulate market analysis
        data = self._fetch_data()
        processed_data = self._process_data(data)
        insights = self._generate_insights(processed_data)
        return insights

    def _fetch_data(self):
        return random.sample(self.data_source, 5)

    def _process_data(self, data):
        return [d * random.uniform(0.8, 1.2) for d in data]

    def _generate_insights(self, processed_data):
        return {"insight": "Market stability is at {:.2f}%".format(sum(processed_data)/len(processed_data))}

if __name__ == '__main__':
    data_source = [100, 200, 150, 300, 250, 175, 225, 400]
    analyzer = MarketHealthAnalyzer(data_source)
    while True:
        insights = analyzer.analyze_market()
        print(insights)
        time.sleep(5)