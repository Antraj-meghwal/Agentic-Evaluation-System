import chromadb

from sentence_transformers import (
    SentenceTransformer
)


class RAGVectorStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="data/chroma"
        )

        self.collection = (
            self.client.get_or_create_collection(
                name="grading_memory"
            )
        )

        self.embedding_model = (
            SentenceTransformer(
                "all-MiniLM-L6-v2"
            )
        )

    def add_answer(
        self,
        crop_id: str,
        question_id: str,
        answer_text: str,
        final_score: int
    ):

        embedding = (
            self.embedding_model.encode(
                answer_text
            ).tolist()
        )

        self.collection.add(
            ids=[crop_id],

            embeddings=[embedding],

            documents=[answer_text],

            metadatas=[
                {
                    "question_id":
                    question_id,

                    "final_score":
                    final_score
                }
            ]
        )

    def retrieve_similar_answers(
        self,
        question_id: str,
        query_text: str,
        top_k: int = 3
    ):

        query_embedding = (
            self.embedding_model.encode(
                query_text
            ).tolist()
        )

        results = self.collection.query(
            query_embeddings=[
                query_embedding
            ],

            n_results=top_k
        )

        filtered_results = []

        if not results["documents"]:
            return filtered_results

        for i in range(
            len(results["documents"][0])
        ):

            metadata = (
                results["metadatas"][0][i]
            )

            if (
                metadata["question_id"]
                == question_id
            ):

                filtered_results.append(
                    {
                        "answer":
                        results["documents"][0][i],

                        "score":
                        metadata["final_score"]
                    }
                )

        return filtered_results