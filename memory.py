import faiss
import numpy as np
import os
import pickle
import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

INDEX_FILE = "memory.index"
DATA_FILE = "memory.pkl"

if os.path.exists(INDEX_FILE):
    index = faiss.read_index(INDEX_FILE)
    with open(DATA_FILE, "rb") as f:
        data = pickle.load(f)
else:
    index = faiss.IndexFlatL2(384)
    data = []


def store(company, analysis_dict):
    """
    analysis_dict must be structured JSON (dict)
    """

    record = {
        "company": company,
        "analysis": analysis_dict
    }

    embedding = model.encode([company])

    index.add(np.array(embedding))
    data.append(record)

    faiss.write_index(index, INDEX_FILE)

    with open(DATA_FILE, "wb") as f:
        pickle.dump(data, f)


def search(company):

    if len(data) == 0:
        return None

    embedding = model.encode([company])
    D, I = index.search(np.array(embedding), k=5)

    for idx in I[0]:
        record = data[idx]

        if record["company"].lower() == company.lower():
            return record["analysis"]

    return None


def get_all_companies():
    return [record["company"] for record in data]