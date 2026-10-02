from chromadb.api.models.Collection import Collection
from chromadb.utils import embedding_functions
import chromadb
from app.config import BASE_DIR


KB_DIR = BASE_DIR / "data" / "kb"
CHROMA_DIR = BASE_DIR / "data" / "chroma"
_collection: Collection | None = None


def get_collection() -> Collection:
    """初始化本地向量库并导入课程资料"""
    global _collection
    if _collection is not None:
        return _collection
    KB_DIR.mkdir(parents=True, exist_ok=True)
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="BAAI/bge-small-zh-v1.5"
    )
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    col = client.get_or_create_collection(name="lab_kb", embedding_function=embedding_fn)
    if col.count() == 0:
        ids, docs, metas = [], [], []
        for path in sorted(KB_DIR.glob("*.md")):
            content = path.read_text(encoding="utf-8").strip()
            if content:
                docs.append(content)
                ids.append(path.stem)
                metas.append({"source": path.name})
        if docs:
            col.add(ids=ids, documents=docs, metadatas=metas)
    _collection = col
    return col


def search(query: str) -> str:
    """根据用户问题检索相关课程资料"""
    col = get_collection()
    if col.count() == 0:
        return ""
    res = col.query(query_texts=[query], n_results=min(5, col.count()))
    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    distances = (res.get("distances") or [[]])[0]
    score_parts = []
    for doc, meta, dist in zip(docs, metas, distances):
        score = 1 / (1 + dist)
        if score < 0.5:
            continue
        name = (meta or {}).get("source") or ""
        score_parts.append({"score": score, "content": f"[{name}]\n{doc}"})
    score_parts.sort(key=lambda item: item["score"], reverse=True)
    return "\n\n".join(item["content"] for item in score_parts[:2])
