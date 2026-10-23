"""
check_setup.py: confirms your development environment is ready.

Run it from the project folder with your virtual environment active:
    python check_setup.py

It checks, in order:
  1. Python version
  2. Required packages are installed
  3. Your .env file and Gemini API key
  4. The embedding model works (used to index documents and questions)
  5. The generation model works (used to write answers)
  6. The local vector store (ChromaDB) works
"""

import os
import sys
import time

OK = "  [OK]  "
FAIL = "  [FAIL]"
problems = []


def step(title):
    print(f"\n{title}")


def fail(message, fix):
    print(f"{FAIL} {message}")
    print(f"         Fix: {fix}")
    problems.append(message)


def with_retry(call, what):
    """Gemini sometimes answers 503/429 ('busy'). Retry a few times before failing."""
    from google.genai import errors

    for attempt in range(4):
        try:
            return call()
        except errors.APIError as e:
            if e.code in (429, 500, 503) and attempt < 3:
                wait = 2 * (attempt + 1)
                print(f"         {what}: Gemini is busy (error {e.code}); retrying in {wait}s...")
                time.sleep(wait)
                continue
            raise


# 1. Python version -----------------------------------------------------------
step("1. Python version")
if sys.version_info >= (3, 10):
    print(f"{OK} Python {sys.version.split()[0]}")
else:
    fail(f"Python {sys.version.split()[0]} is too old",
         "install Python 3.11 or newer (see README.md, step 1).")

# 2. Packages -----------------------------------------------------------------
step("2. Packages")
missing = []
for module, package in [("google.genai", "google-genai"), ("dotenv", "python-dotenv"),
                        ("pypdf", "pypdf"), ("numpy", "numpy"), ("chromadb", "chromadb")]:
    try:
        __import__(module)
        print(f"{OK} {package}")
    except ImportError:
        missing.append(package)
        fail(f"{package} is not installed",
             "activate your virtual environment, then run: pip install -r requirements.txt")

if missing:
    print("\nStopping here: install the missing packages, then run this again.")
    sys.exit(1)

# 3. API key ------------------------------------------------------------------
step("3. .env file and API key")
from dotenv import load_dotenv

if not os.path.exists(".env"):
    fail("No .env file in this folder",
         "copy .env.example to .env and paste your API key into it (README.md, step 5).")
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY", "").strip()
embed_model = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
gen_model = os.getenv("GENERATION_MODEL", "gemini-flash-latest")

if not api_key or api_key == "paste-your-key-here":
    fail("GEMINI_API_KEY is missing", "put your key from aistudio.google.com in the .env file.")
    print("\nStopping here: add your API key, then run this again.")
    sys.exit(1)
print(f"{OK} API key found (ends in ...{api_key[-4:]})")

from google import genai
from google.genai import errors, types

client = genai.Client(api_key=api_key)

# 4. Embeddings ---------------------------------------------------------------
step(f"4. Embedding model ({embed_model})")
dims = None
try:
    result = with_retry(lambda: client.models.embed_content(
        model=embed_model,
        contents=["How do I submit a reimbursement request?"],
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    ), "embedding")
    dims = len(result.embeddings[0].values)
    print(f"{OK} Got a vector with {dims} numbers")
except errors.APIError as e:
    hint = ("your API key was rejected; check it in .env." if e.code in (400, 401, 403)
            else "check EMBEDDING_MODEL in .env, or try again in a minute.")
    fail(f"Embedding call failed (error {e.code}): {e.message}", hint)
except Exception as e:
    fail(f"Embedding call failed: {e}", "check your internet connection and API key.")

# 5. Generation ---------------------------------------------------------------
step(f"5. Generation model ({gen_model})")
try:
    reply = with_retry(lambda: client.models.generate_content(
        model=gen_model,
        contents="Reply with exactly: setup works",
        config=types.GenerateContentConfig(temperature=0),
    ), "generation")
    print(f"{OK} Model replied: {(reply.text or '').strip()[:60]!r}")
except errors.APIError as e:
    hint = ("your API key was rejected; check it in .env." if e.code in (400, 401, 403)
            else "check GENERATION_MODEL in .env, or try again in a minute.")
    fail(f"Generation call failed (error {e.code}): {e.message}", hint)
except Exception as e:
    fail(f"Generation call failed: {e}", "check your internet connection and API key.")

# 6. Vector store -------------------------------------------------------------
step("6. Local vector store (ChromaDB)")
try:
    import chromadb

    store = chromadb.EphemeralClient()   # in memory only; nothing is saved
    col = store.create_collection("setup_check", embedding_function=None,
                                  configuration={"hnsw": {"space": "cosine"}})
    col.add(ids=["a", "b"], embeddings=[[1.0, 0.0], [0.0, 1.0]],
            documents=["about parking", "about payroll"])
    hit = col.query(query_embeddings=[[0.9, 0.1]], n_results=1)["documents"][0][0]
    assert hit == "about parking"
    print(f"{OK} Stored and searched test vectors")
except Exception as e:
    fail(f"ChromaDB test failed: {e}", "reinstall with: pip install --upgrade chromadb")

# Summary ---------------------------------------------------------------------
print("\n" + "-" * 60)
if problems:
    print(f"{len(problems)} problem(s) found. Fix them and run this script again.")
    sys.exit(1)
print("All checks passed. Your environment is ready to build the RAG pipeline.")
