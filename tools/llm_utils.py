import re
import json
import tiktoken


def extract_json(text):
    json_pattern = r'```json\s*(\{.*?\})\s*```'
    match = re.search(json_pattern, text, re.DOTALL)

    if match:
        json_text = match.group(1)
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            return "Invalid JSON format"
    else:
        return "JSON not found"


def remove_plus(text):
    return '\n'.join(line.lstrip('+') for line in text.split('\n'))


def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(encoding.encode(text))


def trimming_text(text, threshold):
    token_count = count_tokens(text)
    while token_count > threshold:
        tokens = text.split()
        tokens = tokens[:-1]
        text = ' '.join(tokens)
        token_count = count_tokens(text)
    return text