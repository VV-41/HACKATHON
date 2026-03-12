import os
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

VECTORIZER_PATH = "tfidf_vectorizer.pkl"
MATRIX_PATH = "tfidf_matrix.pkl"
DATASET_PATH = "legal_dataset.csv"


class LegalAssistantModel:
    def __init__(self, dataset_path=DATASET_PATH):
        self.dataset_path = dataset_path
        self.df = None
        self.vectorizer = None
        self.tfidf_matrix = None

    def load_dataset(self):
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset not found at: {self.dataset_path}")

        self.df = pd.read_csv(self.dataset_path)

        required_columns = ["question", "answer", "category"]
        for col in required_columns:
            if col not in self.df.columns:
                raise ValueError(f"Dataset must contain column: {col}")

        self.df = self.df.dropna(subset=["question", "answer", "category"])
        self.df["question"] = self.df["question"].astype(str)
        self.df["answer"] = self.df["answer"].astype(str)
        self.df["category"] = self.df["category"].astype(str)

    def train(self):
        self.load_dataset()

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000
        )

        self.tfidf_matrix = self.vectorizer.fit_transform(self.df["question"])

        with open(VECTORIZER_PATH, "wb") as f:
            pickle.dump(self.vectorizer, f)

        with open(MATRIX_PATH, "wb") as f:
            pickle.dump(self.tfidf_matrix, f)

    def load_trained(self):
        self.load_dataset()

        if not os.path.exists(VECTORIZER_PATH) or not os.path.exists(MATRIX_PATH):
            self.train()
            return

        with open(VECTORIZER_PATH, "rb") as f:
            self.vectorizer = pickle.load(f)

        with open(MATRIX_PATH, "rb") as f:
            self.tfidf_matrix = pickle.load(f)

    def predict(self, user_query, top_k=3):
        if not user_query or not user_query.strip():
            return {
                "query": user_query,
                "best_answer": "Please enter a valid legal question.",
                "category": "Unknown",
                "similarity": 0.0,
                "top_matches": []
            }

        if self.vectorizer is None or self.tfidf_matrix is None:
            self.load_trained()

        query_vector = self.vectorizer.transform([user_query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()

        top_indices = similarities.argsort()[::-1][:top_k]

        best_idx = top_indices[0]
        best_score = float(similarities[best_idx])

        top_matches = []
        for idx in top_indices:
            top_matches.append({
                "question": self.df.iloc[idx]["question"],
                "answer": self.df.iloc[idx]["answer"],
                "category": self.df.iloc[idx]["category"],
                "similarity": round(float(similarities[idx]), 4)
            })

        if best_score < 0.15:
            return {
                "query": user_query,
                "best_answer": (
                    "I could not find a strong match in the legal database. "
                    "Please rephrase your query or consult a professional lawyer."
                ),
                "category": "No strong match",
                "similarity": round(best_score, 4),
                "top_matches": top_matches
            }

        return {
            "query": user_query,
            "best_answer": self.df.iloc[best_idx]["answer"],
            "category": self.df.iloc[best_idx]["category"],
            "similarity": round(best_score, 4),
            "top_matches": top_matches
        }


if __name__ == "__main__":
    model = LegalAssistantModel()
    model.train()
    print("Model trained successfully.")