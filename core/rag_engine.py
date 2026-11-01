"""Local vector retrieval and transcript question answering."""

from __future__ import annotations

from dataclasses import dataclass

from core.llm import get_llm


@dataclass
class RAGChain:
    retriever: object
    llm: object


def build_rag_chain(transcript: str) -> RAGChain:
    transcript = transcript.strip()
    if not transcript:
        raise ValueError("A non-empty transcript is required to build the RAG index.")

    try:
        from langchain_chroma import Chroma
        from langchain_core.documents import Document
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError as exc:
        raise RuntimeError(
            "RAG dependencies are not installed. Install the project requirements first."
        ) from exc

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    documents = splitter.split_documents([Document(page_content=transcript)])
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vector_store = Chroma.from_documents(documents=documents, embedding=embeddings)
    return RAGChain(retriever=vector_store.as_retriever(search_kwargs={"k": 4}), llm=get_llm())


def ask_question(rag_chain: RAGChain, question: str) -> str:
    question = question.strip()
    if not question:
        raise ValueError("A non-empty question is required.")
    if not isinstance(rag_chain, RAGChain):
        raise TypeError("rag_chain must be created by build_rag_chain().")

    documents = rag_chain.retriever.invoke(question)
    context = "\n\n".join(document.page_content for document in documents)
    prompt = (
        "Answer the question using only the transcript excerpts below. "
        "If the answer is not present, say that it is not available in the recording. "
        "Keep the answer concise and do not invent details.\n\n"
        f"Transcript excerpts:\n{context}\n\nQuestion: {question}"
    )
    response = rag_chain.llm.invoke(prompt)
    content = getattr(response, "content", response)
    return str(content).strip()
