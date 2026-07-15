"""
router/domain_router.py
Weighted scoring router — evaluates ALL domains simultaneously.

Changes in this version
------------------------
1. Full B.Tech CSE syllabus coverage in _EDUCATION_KW:
   All subjects across 4 years of B.Tech CSE added with appropriate weights.

2. General domain is strictly for general knowledge / current facts.
   Query intent words (what is, explain) only boost education score
   when a CS subject noun is also present — they don't route to education alone.

3. Fixed: "what is" + non-CS topic (e.g. "capital of India") → general,
          "what is" + CS topic (e.g. "what is DBMS") → education.
"""

import re
from functools import lru_cache
from typing import Final

from constants.domains import (
    COLLEGE_DOMAIN,
    CODING_DOMAIN,
    EDUCATION_DOMAIN,
    GENERAL_DOMAIN,
    MEDICAL_DOMAIN,
    PDF_DOMAIN,
    LIVE_DOMAIN,
    CAREER_DOMAIN,
    SCHOLARSHIP_DOMAIN,
)
from tools.query_classifier import classify_intent
from utils.logger import get_logger

logger = get_logger(__name__)

_H: Final[int] = 3   # high signal
_M: Final[int] = 2   # medium signal
_L: Final[int] = 1   # low signal

# boost constants
_EDU_BOOST: Final[int] = 2


def _score(query: str, domain: str) -> int:
    """
    Calculate weighted keyword score for a domain.
    Supports whole-word matching for single words and substring
    matching for multi-word phrases.
    """
    total = 0
    for pattern, weight in _SINGLE_WORD_KEYWORDS[domain]:
        if pattern.search(query):
            total += weight

    for kw, weight in _PHRASE_KEYWORDS[domain].items():
        if kw in query:
            total += weight

    return total


# ── PDF ───────────────────────────────────────────────────────────────────────
_PDF_KW: dict[str, int] = {
    "pdf": _H,
    "uploaded": _H,
    "document": _M,
    "this document": _H,
    "my document": _H,
    "the document": _M,
    "file": _L,
    "this file": _H,
    "my file": _H,
    "page": _L,
    "pages": _L,
    "extract": _M,
    "summarize": _M,
    "from the pdf": _H,
    "in the pdf": _H,
}

# ── Coding ────────────────────────────────────────────────────────────────────
_CODING_KW: dict[str, int] = {
    "write a": _H, "write the": _H, "write an": _H,
    "program for": _H, "program to": _H,
    "code for": _H, "code to": _H,
    "implement": _H, "debug": _H,
    "build a": _H, "build an": _H, "develop a": _H, "create a": _H,
    "python": _H, "java": _H, "javascript": _H, "typescript": _H,
    "golang": _H, "rust": _H, "kotlin": _H, "c language": _H,
    "flask": _H, "django": _H, "fastapi": _H, "react": _H,
    "nodejs": _H, "spring boot": _H,
    "code": _M, "program": _M,
    "sorting algorithm": _M, "searching algorithm": _M,
    "dynamic programming": _M,
    "rest api": _M, "runtime error": _M, "syntax error": _M,
    "leetcode": _M, "hackerrank": _M,
    "linked list": _L, "binary tree": _L, "hash table": _L,
}

# ── Medical ───────────────────────────────────────────────────────────────────
_MEDICAL_KW: dict[str, int] = {
    "i have": _H, "i am suffering": _H, "i feel": _H,
    "not feeling well": _H, "body pain": _H,
    "fever": _H, "headache": _H, "cough": _H, "vomit": _H,
    "nausea": _H, "dizziness": _H, "fatigue": _H, "rash": _H,
    "chest pain": _H, "sore throat": _H, "running nose": _H,
    "stomach pain": _H, "fainted": _H, "fainting": _H,
    "shortness of breath": _H, "difficulty breathing": _H,
    "left arm pain": _H, "face drooping": _H, "slurred speech": _H,
    "symptom": _H, "symptoms": _H, "illness": _H, "disease": _H,
    "pain": _M, "ache": _M, "sick": _M,
    "medicine": _M, "medication": _M, "diagnosis": _M,
    "hospital": _M, "doctor": _M, "clinic": _M,
    "infection": _M, "flu": _M, "allergy": _M,
    "diabetes": _M, "asthma": _M, "covid": _M,
    "blood pressure": _M, "heart rate": _M, "mental health": _M,
    "depression": _M, "anxiety": _M,
}

# ── College ───────────────────────────────────────────────────────────────────
_COLLEGE_KW: dict[str, int] = {
    "eamcet": _H, "eamcet rank": _H, "my rank is": _H,
    "seat allotment": _H, "college predictor": _H,
    "bc_a": _H, "bc_b": _H, "bc_c": _H, "bc_d": _H, "bc_e": _H,
    "rank": _L, "cutoff": _H, "counselling": _H, "counseling": _H,
    "admission": _H, "jntuh": _H,
    "cbit": _M, "vjit": _M, "mgit": _M, "mrec": _M, "mrcet": _M,
    "kmit": _M, "ngit": _M, "vbit": _M, "mvsr": _M,
    "college": _M, "engineering college": _M,
}

# ── Education — Full B.Tech CSE syllabus ──────────────────────────────────────
# Year 1
_Y1: dict[str, int] = {
    "linear algebra": _H, "matrices": _H, "eigenvalues": _H,
    "differential equations": _H, "calculus": _H,
    "engineering chemistry": _H, "engineering physics": _H,
    "engineering drawing": _H, "c programming": _H,
    "programming basics": _H, "flowchart": _H, "pseudocode": _H,
    "dbms": _H,
    "os": _H,
    "operating system": _H,
    "law": _H,
    "motion": _H,
    "physics": _H,
    "chemistry": _H,
    "math": _H,
    "algorithm": _H,
    "computer networks": _H,
    "cn": _H,
    "oops": _H,
    "data structure": _H
}

# Year 2
_Y2: dict[str, int] = {
    "data structures": _H, "linked list": _M, "binary tree": _M,
    "stack": _M, "queue": _M, "heap": _M, "graph": _M,
    "hashing": _H, "sorting": _H, "searching": _H,
    "algorithm": _H, "recursion": _H, "complexity": _M,
    "digital logic": _H, "boolean algebra": _H, "logic gate": _H,
    "flip flop": _H, "karnaugh map": _H, "combinational circuit": _H,
    "sequential circuit": _H, "microprocessor": _H, "8085": _H, "8086": _H,
    "assembly language": _H,
    "object oriented": _H, "oops": _H, "oopj": _H,
    "class": _L, "object": _L, "inheritance": _H,
    "polymorphism": _H, "encapsulation": _H, "abstraction": _H,
    "java": _L,   # low here — coding gets high for java
    "discrete mathematics": _H, "set theory": _H, "graph theory": _H,
    "relations": _H, "functions": _H, "permutations": _H,
    "combinations": _H, "propositional logic": _H, "predicate logic": _H,
}

# Year 3
_Y3: dict[str, int] = {
    "dbms": _H, "database": _H, "sql": _M, "normalization": _H,
    "er diagram": _H, "er model": _H, "relational model": _H,
    "acid properties": _H, "transaction": _H, "indexing": _H,
    "b tree": _H, "b+ tree": _H, "relational algebra": _H,
    "nosql": _H, "mongodb": _H,
    "operating system": _H, "os concepts": _H,
    "process scheduling": _H, "cpu scheduling": _H,
    "fcfs": _H, "sjf": _H, "round robin": _H, "priority scheduling": _H,
    "deadlock": _H, "deadlock prevention": _H, "deadlock avoidance": _H,
    "memory management": _H, "paging": _H, "segmentation": _H,
    "virtual memory": _H, "page replacement": _H, "thrashing": _H,
    "semaphore": _H, "mutex": _H, "critical section": _H,
    "multithreading": _H, "thread": _M, "threads": _M,
    "concurrency": _H, "parallelism": _H, "synchronization": _H,
    "file system": _H, "disk scheduling": _H,
    "computer network": _H, "networking": _H,
    "osi model": _H, "tcp ip": _H, "tcp": _M, "udp": _M,
    "ip address": _H, "dns": _M, "http": _M, "https": _M,
    "subnetting": _H, "routing": _H, "switching": _H,
    "network topology": _H, "socket programming": _H,
    "computer architecture": _H, "pipelining": _H,
    "cache memory": _H, "ram": _M, "rom": _M, "cpu": _M, "gpu": _M,
    "risc": _H, "cisc": _H, "instruction set": _H,
    "compiler design": _H, "lexical analysis": _H,
    "syntax analysis": _H, "parsing": _H, "semantic analysis": _H,
    "code generation": _H, "code optimization": _H,
    "finite automata": _H, "turing machine": _H, "automata": _H,
    "context free grammar": _H, "pushdown automaton": _H,
    "theory of computation": _H, "formal languages": _H,
}

# Year 4
_Y4: dict[str, int] = {
    "machine learning": _H, "deep learning": _H, "neural network": _H,
    "artificial intelligence": _H, "ai": _M, "ml": _M,
    "supervised learning": _H, "unsupervised learning": _H,
    "reinforcement learning": _H, "decision tree": _H,
    "random forest": _H, "svm": _H, "knn": _H, "kmeans": _H,
    "gradient descent": _H, "backpropagation": _H,
    "cnn": _H, "rnn": _H, "lstm": _H, "transformer": _H,
    "natural language processing": _H, "nlp": _M,
    "computer vision": _H, "image processing": _H,
    "cloud computing": _H, "aws": _H, "azure": _H, "gcp": _H,
    "saas": _H, "paas": _H, "iaas": _H, "virtualization": _H,
    "docker": _H, "kubernetes": _H, "microservices": _H,
    "software engineering": _H, "sdlc": _H, "agile": _H,
    "scrum": _H, "waterfall": _H, "spiral model": _H,
    "software testing": _H, "unit testing": _H, "integration testing": _H,
    "design pattern": _H, "solid principles": _H,
    "mvc": _H, "mvvm": _H, "orm": _H,
    "cyber security": _H, "cryptography": _H, "encryption": _H,
    "rsa": _H, "aes": _H, "des": _H, "diffie hellman": _H,
    "firewall": _H, "intrusion detection": _H,
    "blockchain": _H, "distributed system": _H,
    "internet of things": _H, "iot": _M, "embedded system": _H,
    "data science": _H, "big data": _H, "hadoop": _H, "spark": _H,
    "data warehouse": _H, "data mining": _H,
    "api": _L, "rest": _L, "graphql": _H, "web services": _H,
}

_EDUCATION_KW: dict[str, int] = {
    **_Y1,
    **_Y2,
    **_Y3,
    **_Y4,
}


# Singular forms (users often ask 'what is differential equation' not 'equations')
_EDUCATION_KW.update({
    'differential equation': _H,
    'integral calculus': _H,
    'propositional logic': _H,
    'context free grammar': _H,
    'finite automaton': _H,
    'pushdown automaton': _H,
    'instruction set architecture': _H,
    'page replacement algorithm': _H,
    'disk scheduling algorithm': _H,
    # CS fundamentals
    'data type': _H,
    'pointer': _H,
    'pointers': _H,
    'array': _H,
    'arrays': _H,
    'variable': _H,
    'variables': _H,
    'loop': _L,
    'loops': _L,
    'conditional': _M,
    'conditionals': _M,
    'control structure': _H,
    'control structures': _H,
    'iteration': _H,
    'iterations': _H,
    'traversal': _H,
    'traversals': _H,
    'binary search': _H,
    'linear search': _H,
    'bubble sort': _H,
    'insertion sort': _H,
    'merge sort': _H,
    'quick sort': _H,
    'selection sort': _H,
    'heap sort': _H,
    'breadth first search': _H,
    'depth first search': _H,
    'preorder': _M,
    'inorder': _M,
    'postorder': _M,
    'greedy algorithm': _H,
    'backtracking': _H,
    'divide and conquer': _H,
    'brute force': _M,
    'time complexity': _H,
    'space complexity': _H,
    'big o': _H,
    'asymptotic': _H,
    'compiler': _H,
    'compilers': _H,
    'interpreter': _H,
    'interpreters': _H,
    'assembler': _H,
    'assemblers': _H,
    'syntax': _H,
    'semantic': _H,
    'dynamic programming': _H,
    'hash table': _H,
    'runtime error': _H,
    'syntax error': _H,
    'rest api': _L,
    # Math
    'algebra': _H,
    'geometry': _H,
    'trigonometry': _H,
    'statistics': _H,
    'probability': _H,
    'integral': _H,
    'derivative': _H,
    'derivatives': _H,
    'limit': _H,
    'limits': _H,
    'series': _H,
    'sequence': _H,
    'sequences': _H,
    'vector': _H,
    'vectors': _H,
    # Physics
    'thermodynamics': _H,
    'electromagnetism': _H,
    'optics': _H,
    'kinematics': _H,
    'dynamics': _H,
    'statics': _H,
    'mechanics': _H,
    'newton': _H,
    'einstein': _H,
    'relativity': _H,
    'quantum': _H,
    'photon': _H,
    'photons': _H,
    'electron': _H,
    'electrons': _H,
    'proton': _H,
    'protons': _H,
    'neutron': _H,
    'neutrons': _H,
    'atom': _H,
    'atoms': _H,
    'molecule': _H,
    'molecules': _H,
    'energy': _L,
    'energies': _L,
    'force': _L,
    'forces': _L,
    'velocity': _H,
    'velocities': _H,
    'acceleration': _H,
    'accelerations': _H,
    'momentum': _H,
    'momenta': _H,
    # Chemistry
    'element': _H,
    'elements': _H,
    'compound': _H,
    'compounds': _H,
    'reaction': _H,
    'reactions': _H,
    'acid': _H,
    'acids': _H,
    'catalyst': _H,
    'catalysts': _H,
    'organic chemistry': _H,
    'inorganic chemistry': _H,
    'biochemistry': _H,
    'electrochemistry': _H,
    # Biology / Life Science
    'biology': _H,
    'cell': _H,
    'cells': _H,
    'tissue': _H,
    'tissues': _H,
    'organ': _M,
    'organs': _M,
    'organism': _H,
    'organisms': _H,
    'species': _H,
    'genetics': _H,
    'gene': _H,
    'genes': _H,
    'dna': _H,
    'rna': _H,
    'chromosome': _H,
    'chromosomes': _H,
    'mitosis': _H,
    'meiosis': _H,
    'photosynthesis': _H,
    'respiration': _H,
    'evolution': _H,
    'evolutions': _H,
    'ecosystem': _H,
    'ecosystems': _H,
    'population': _H,
    'populations': _H,
    'homeostasis': _H,
    'metabolism': _H,
    'enzyme': _H,
    'enzymes': _H,
    'protein': _H,
    'proteins': _H,
    'carbohydrate': _H,
    'carbohydrates': _H,
    'lipid': _H,
    'lipids': _H,
    'virus': _H,
    'viruses': _H,
    'bacteria': _H,
    'bacterium': _H,
    'fungi': _H,
    'fungus': _H,
})
# Domain priority for tie-breaking
_DOMAIN_PRIORITY: Final[tuple[str, ...]] = (
    PDF_DOMAIN,
    CODING_DOMAIN,
    MEDICAL_DOMAIN,
    COLLEGE_DOMAIN,
    EDUCATION_DOMAIN,
)


# Intent words that indicate an educational intent
_EDU_INTENTS: Final[frozenset[str]] = frozenset((
    "what is",
    "explain",
    "define",
    "describe",
    "difference between",
    "compare",
    "advantages of",
    "disadvantages of",
    "features of",
    "uses of",
    "applications of",
    "how does",
    "how do",
    "importance of",
))


# Domain -> keywords map for easier iteration
_DOMAIN_KEYWORDS: dict[str, dict[str, int]] = {
    PDF_DOMAIN: _PDF_KW,
    CODING_DOMAIN: _CODING_KW,
    MEDICAL_DOMAIN: _MEDICAL_KW,
    COLLEGE_DOMAIN: _COLLEGE_KW,
    EDUCATION_DOMAIN: _EDUCATION_KW,
}


# Precompute keyword structures for faster scoring
_SINGLE_WORD_KEYWORDS: dict[str, list[tuple[re.Pattern, int]]] = {
    domain: [
        (re.compile(rf"\b{re.escape(kw)}\b"), weight)
        for kw, weight in keywords.items()
        if " " not in kw
    ]
    for domain, keywords in _DOMAIN_KEYWORDS.items()
}

_PHRASE_KEYWORDS: dict[str, dict[str, int]] = {
    domain: {
        kw: weight
        for kw, weight in keywords.items()
        if " " in kw
    }
    for domain, keywords in _DOMAIN_KEYWORDS.items()
}


@lru_cache(maxsize=512)
def route_domain(query: str) -> str:
    """
    1. Hybrid classification (Rule filter + LLM Fallback)
    2. Detailed fallback scoring for 'local' intent.
    Returns: 'pdf' | 'coding' | 'medical' | 'college' | 'education' | 'general' | 'live' | 'career' | 'scholarship'
    """
    q = query.strip().lower()
    
    # 1. Ask the hybrid classifier
    intent = classify_intent(q)
    
    valid_domains = {
        "live": LIVE_DOMAIN,
        "career": CAREER_DOMAIN,
        "scholarship": SCHOLARSHIP_DOMAIN,
        "college": COLLEGE_DOMAIN,
        "coding": CODING_DOMAIN,
        "medical": MEDICAL_DOMAIN,
        "education": EDUCATION_DOMAIN
    }
    
    if intent in valid_domains:
        logger.info("Hybrid classifier selected: %s", intent)
        return valid_domains[intent]
        
    # 2. If 'local' or unknown, use fine-grained scoring
    scores = {domain: _score(q, domain) for domain in _DOMAIN_KEYWORDS}

    # Boost education score when query INTENT words combine with CS subject
    # (prevents "what is" alone routing to education for non-CS questions)
    if scores["education"] > 0 and any(q.startswith(w) for w in _EDU_INTENTS):
        scores["education"] += _EDU_BOOST

    # Log domain scores for debugging
    logger.debug("Domain scores: %s", scores)

    max_score = max(scores.values())

    if max_score == 0:
        logger.info("Domain selected: %s", GENERAL_DOMAIN)
        return GENERAL_DOMAIN

    # Prefer domains in priority order when scores tie
    selected = next(
        domain
        for domain in _DOMAIN_PRIORITY
        if scores[domain] == max_score
    )

    logger.info("Domain selected: %s", selected)
    return selected
