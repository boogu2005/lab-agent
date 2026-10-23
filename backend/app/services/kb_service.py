from chromadb.api.models.Collection import Collection
from chromadb.utils import embedding_functions
import chromadb
from app.config import BASE_DIR


KB_DIR = BASE_DIR / "data" / "kb"
CHROMA_DIR = BASE_DIR / "data" / "chroma"
_collection: Collection | None = None
_embedding_fn = None


def get_embedding_fn():
    """懒加载 embedding 模型，只创建一次。"""
    global _embedding_fn
    if _embedding_fn is None:
        _embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="BAAI/bge-small-zh-v1.5"
        )
    return _embedding_fn


def get_collection() -> Collection:
    """初始化本地向量库并导入课程资料"""
    global _collection
    if _collection is None:
        KB_DIR.mkdir(parents=True, exist_ok=True)
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = client.get_or_create_collection(
            name="lab_kb", embedding_function=get_embedding_fn()
        )

    col = _collection
    existing = col.get(include=["documents"])
    saved = dict(zip(existing["ids"], existing["documents"]))
    current = {}
    changed_ids, changed_docs, changed_metas = [], [], []
    for path in sorted(KB_DIR.glob("*.md")):
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        current[path.stem] = content
        if saved.get(path.stem) != content:
            changed_ids.append(path.stem)
            changed_docs.append(content)
            changed_metas.append({"source": path.name})
    if changed_ids:
        col.upsert(ids=changed_ids, documents=changed_docs, metadatas=changed_metas)
    removed = list(saved.keys() - current.keys())
    if removed:
        col.delete(ids=removed)
    return col


def warmup():
    """在启动阶段加载模型并执行一次检索。"""
    col = get_collection()
    if col.count() > 0:
        col.query(query_texts=["预热"], n_results=1)


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
