from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

app = FastAPI(title="CODECHARCHA API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

posts_db: dict = {}
comments_db: dict = {}

class PostCreate(BaseModel):
    title: str
    subtitle: Optional[str] = None
    content: str
    category: str = "Systems"
    tags: List[str] = []
    status: str = "LIVE_PRODUCTION"
    registry_id: str = "CC-SYS-01-ALPH"
    ref_id: str = "992-01"
    author: str = "Anonymous"
    read_time: int = 5

class PostUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None

class Post(PostCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    views: int = 0
    rev: str = "REV_01"

class CommentCreate(BaseModel):
    author: str
    content: str

class Comment(CommentCreate):
    id: str
    post_id: str
    created_at: datetime

def _seed():
    seed_posts = [
        {
            "title": "Architecting Scalable Inference Engines for LLMs",
            "subtitle": "From KV-Cache optimization to PagedAttention dispatch",
            "content": "The transition from training-centric workloads to inference-optimized architectures represents the largest shift in AI systems engineering over the last decade. Modern serving stacks must handle thousands of concurrent sessions without sacrificing token throughput or first-token latency. Engineers are rethinking everything from tokenizer pipelines to GPU memory allocation strategies. The pressure to reduce cost-per-token has pushed teams toward radical scheduler redesigns. What once worked at 7B parameters simply collapses under the weight of 70B models in production.\n\nTo serve high-concurrency requests across billion-parameter models, we need more than just raw GPU power. We need a choreographed dance between the tokenizer, the transformer blocks, and the decentralized memory controllers. Autoscaling inference clusters must adapt dynamically to bursty traffic without pre-warming entire replicas. Disaggregated serving separates the prefill phase from the decode phase to better utilize heterogeneous hardware. This architectural split alone can reduce p99 latency by over 30% in high-traffic deployments.\n\n## The KV-Cache Problem\n\nThe bottleneck in modern LLM serving is memory bandwidth. PagedAttention treats GPU memory like virtual pages, allowing prefix caching across sequences. When multiple users share a common system prompt, the cached KV tensors can be reused across all sessions simultaneously. This dramatically reduces redundant computation and unlocks higher effective batch sizes. Without prefix caching, a 4096-token system prompt is recomputed on every single request — a colossal waste.\n\n## Continuous Batching\n\nContinuous batching allows new requests to join mid-generation, reducing tail latency by **45%** on US-EAST-1 infrastructure.\n\n```rust\npub fn allocate_block(&mut self) -> Result<BlockIndex, Error> {\n    match self.free_list.pop() {\n        Some(index) => {\n            self.metadata[index].ref_count = 1;\n            Ok(index)\n        },\n        None => self.evict_lru_block()\n    }\n}\n```",
            "category": "AI/ML Lab",
            "tags": ["LLM", "Inference", "Systems", "Rust"],
            "status": "LIVE_PRODUCTION",
            "registry_id": "INF-ENG-2024",
            "ref_id": "992-01",
            "author": "Arjun Mehta",
            "read_time": 8,
        },
        {
            "title": "Distributed Training Paradigms for LLMs",
            "subtitle": "Multi-node gradient synchronization across high-latency interconnects",
            "content": "Deep-dive into multi-node gradient synchronization across high-latency interconnects — exploring the friction between compute efficiency and data consistency. Training frontier models demands thousands of GPUs coordinating in lock-step across datacenter fabrics not originally designed for this traffic pattern. Network topology becomes as critical a constraint as raw FLOPS. A poorly tuned AllReduce schedule can idle expensive A100s for hundreds of milliseconds per step. Getting this right is the difference between a training run that converges and one that bankrupts a compute budget.\n\nAt scale, model state can no longer reside on a single device. Teams operating at the frontier now routinely stack data parallelism, tensor parallelism, and pipeline parallelism into three-dimensional hybrid strategies. Megatron-LM pioneered the tensor-parallel approach, splitting individual weight matrices across GPUs within a node. Pipeline parallelism staggers forward and backward passes across node boundaries to maximize hardware utilization. Tuning the micro-batch size and pipeline depth simultaneously is more art than science — subtle mismatches produce devastating bubble overhead.\n\n## Data Parallelism vs Model Parallelism\n\nAt scale, no single GPU can hold the full model. We split across three dimensions: data, tensor, and pipeline parallelism.\n\n## Ring-AllReduce\n\nThe dominant gradient aggregation strategy in data-parallel training. Each GPU sends and receives data in a ring topology, achieving O(N) bandwidth efficiency. NCCL's fused kernels compress communication overhead into the backward pass itself, hiding latency behind active computation. On InfiniBand fabrics, carefully tuned ring configurations can sustain near-peak bisection bandwidth across 512-GPU clusters. Beyond a certain scale, hierarchical AllReduce — rings within nodes, trees between nodes — becomes the only viable approach.",
            "category": "Systems",
            "tags": ["DDP", "TORCH_DDP", "MEGATRON"],
            "status": "LIVE_PRODUCTION",
            "registry_id": "DDP-SYS-02",
            "ref_id": "881-02",
            "author": "Priya Nair",
            "read_time": 11,
        },
        {
            "title": "Edge Inference & Latency Budgeting",
            "subtitle": "Mapping 8-bit quantization artifacts onto low-power silicon",
            "content": "Deploying quantized models at the edge requires a fundamentally different mental model than cloud inference. The luxury of horizontal scaling disappears entirely — you get one SoC, a fixed thermal envelope, and a user who expects sub-100ms responses. Every operator in the compute graph must be profiled against the target silicon's actual memory bandwidth, not theoretical peak. On-device models live and die by their memory footprint; a model that fits in LPDDR5 cache behaves orders of magnitude differently than one that spills to NAND. Latency budgeting is not an afterthought — it is the primary design constraint from day one.\n\nPost-training quantization pipelines have matured significantly, but calibration dataset selection remains an underappreciated lever. The wrong calibration set can introduce systematic outliers that degrade INT8 accuracy far beyond the theoretical 0.5% floor. Activation quantization is consistently harder than weight quantization because activations vary dynamically with input distribution. Techniques like SmoothQuant redistribute quantization difficulty from activations to weights, enabling more stable INT8 inference. For latency-critical paths, mixed-precision strategies — INT8 for attention, FP16 for final projection layers — often outperform uniform quantization.\n\n## INT8 Quantization Pipeline\n\nPost-training quantization with INT8 achieves 2x memory reduction with minimal accuracy degradation on most vision and language tasks.\n\n## ONNX Runtime on ARM\n\nONNX Runtime with the NNAPI execution provider unlocks hardware acceleration on Android devices. Fusing Conv-BN-ReLU sequences into single kernels cuts operator dispatch overhead dramatically on Cortex-A78 cores. Proper thread affinity pinning to big cores versus efficiency cores can shave another 15–20ms off end-to-end latency on flagship mobile SoCs.",
            "category": "Systems",
            "tags": ["Edge", "Quantization", "ONNX"],
            "status": "LIVE_PRODUCTION",
            "registry_id": "EDG-INF-03",
            "ref_id": "774-03",
            "author": "Rohan Kapoor",
            "read_time": 6,
        },
        {
            "title": "Memory-Safe Systems Programming",
            "subtitle": "Formal verification of concurrent primitives in embedded environments",
            "content": "Rust's ownership model eliminates an entire class of concurrency bugs at compile time, but for safety-critical embedded systems, we need stronger guarantees — formal verification. In avionics, automotive, and medical device firmware, a use-after-free or data race is not a crash report — it is a liability event. DO-178C and ISO 26262 certification bodies increasingly accept mathematically verified code as evidence of correctness. Traditional testing strategies cannot exhaustively cover the state space of concurrent systems under all scheduler interleavings. Formal methods close that gap by reasoning over all possible executions simultaneously.\n\nThe ownership invariant is Rust's foundational guarantee: every value has exactly one owner, and when that owner goes out of scope the value is dropped without exception. This single rule eliminates double-frees, dangling pointers, and a substantial fraction of buffer overflows that plague C and C++ codebases. Lifetimes extend this reasoning across function boundaries, ensuring borrowed references never outlive the data they point to. The borrow checker enforces these constraints at zero runtime cost — no garbage collector, no reference counting overhead, no hidden pauses. For embedded targets where heap allocation itself is forbidden, this compile-time discipline is not optional — it is the entire memory model.\n\n## Formal Verification with Creusot\n\nCreusot translates Rust programs into Why3 proof obligations, mathematically proving the absence of deadlocks. Developers annotate functions with pre- and post-conditions using Rust attributes, which Creusot converts into first-order logic assertions. The Why3 backend dispatches these obligations to SMT solvers including Z3 and CVC5 for automated discharge. For complex concurrent primitives, interactive proof assistants like Coq can be used where automation falls short. This full stack — from Rust source to verified machine code — is now within reach for production embedded firmware.",
            "category": "Systems",
            "tags": ["Rust", "Safety", "Embedded"],
            "status": "ARCHIVED",
            "registry_id": "MEM-SYS-04",
            "ref_id": "663-04",
            "author": "Ananya Singh",
            "read_time": 9,
        },
    ]
    for i, data in enumerate(seed_posts):
        post_id = str(uuid.uuid4())
        now = datetime.utcnow()
        post = Post(id=post_id, created_at=now, updated_at=now, views=100 + i * 47, rev=f"REV_0{i+1}", **data)
        posts_db[post_id] = post

_seed()

@app.get("/")
def root():
    return {"system": "CODECHARCHA_API", "status": "OPERATIONAL"}

@app.get("/posts", response_model=List[Post])
def list_posts(category: Optional[str] = None, tag: Optional[str] = None, search: Optional[str] = None, skip: int = 0, limit: int = 20):
    posts = list(posts_db.values())
    posts.sort(key=lambda p: p.created_at, reverse=True)
    if category:
        posts = [p for p in posts if p.category.lower() == category.lower()]
    if tag:
        posts = [p for p in posts if tag.lower() in [t.lower() for t in p.tags]]
    if search:
        s = search.lower()
        posts = [p for p in posts if s in p.title.lower() or s in p.content.lower()]
    return posts[skip:skip+limit]

@app.get("/posts/{post_id}", response_model=Post)
def get_post(post_id: str):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    posts_db[post_id].views += 1
    return posts_db[post_id]

@app.post("/posts", response_model=Post, status_code=201)
def create_post(data: PostCreate):
    post_id = str(uuid.uuid4())
    now = datetime.utcnow()
    post = Post(id=post_id, created_at=now, updated_at=now, rev=f"REV_01", **data.dict())
    posts_db[post_id] = post
    return post

@app.patch("/posts/{post_id}", response_model=Post)
def update_post(post_id: str, data: PostUpdate):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    post = posts_db[post_id]
    for k, v in data.dict(exclude_unset=True).items():
        setattr(post, k, v)
    post.updated_at = datetime.utcnow()
    return post

@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: str):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    del posts_db[post_id]

@app.get("/posts/{post_id}/comments", response_model=List[Comment])
def list_comments(post_id: str):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    return [c for c in comments_db.values() if c.post_id == post_id]

@app.post("/posts/{post_id}/comments", response_model=Comment, status_code=201)
def create_comment(post_id: str, data: CommentCreate):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    cid = str(uuid.uuid4())
    comment = Comment(id=cid, post_id=post_id, created_at=datetime.utcnow(), **data.dict())
    comments_db[cid] = comment
    return comment

@app.get("/categories")
def list_categories():
    cats = {}
    for p in posts_db.values():
        cats[p.category] = cats.get(p.category, 0) + 1
    return [{"name": k, "count": v} for k, v in cats.items()]

@app.get("/tags")
def list_tags():
    tags = {}
    for p in posts_db.values():
        for t in p.tags:
            tags[t] = tags.get(t, 0) + 1
    return [{"name": k, "count": v} for k, v in sorted(tags.items(), key=lambda x: -x[1])]

@app.get("/stats")
def stats():
    posts = list(posts_db.values())
    return {"total_posts": len(posts), "total_views": sum(p.views for p in posts), "live": sum(1 for p in posts if p.status == "LIVE_PRODUCTION"), "archived": sum(1 for p in posts if p.status == "ARCHIVED"), "categories": len(set(p.category for p in posts))}