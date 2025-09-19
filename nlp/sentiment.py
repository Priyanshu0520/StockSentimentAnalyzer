from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
import re

# Load FinBERT
tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
labels = ["neutral", "positive", "negative"]

# Text cleaning
def clean_text(text):
    text = re.sub(r"http\S+", "", text)  # remove links
    text = re.sub(r"@\S+", "", text)     # remove mentions
    text = re.sub(r"\.+", ".", text)     # clean extra dots
    return text.strip()

def analyze_sentiment(texts):
    results = []
    for text in texts:
        if not text.strip():
            continue
        cleaned = clean_text(text)
        inputs = tokenizer(cleaned, return_tensors="pt", truncation=True, padding=True, max_length=128)
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=1).detach().numpy()[0]
        sentiment = labels[np.argmax(probs)]
        results.append(sentiment)
    return results
