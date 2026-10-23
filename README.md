# Campus RAG Assistant: development environment setup

This is the starter project for building your own RAG pipeline in Python. You'll develop and test it on your own computer first. Later, the same code can run on Google Cloud Run and connect to the Google Chat app.

By the end of this guide, `python check_setup.py` will confirm that Python, the packages, your Gemini API key and the local vector store all work.

**Time needed:** about 30 minutes.

---

## Step 1: Install Python (3.11 or newer)

Check whether you already have it. Open a terminal (Mac: the **Terminal** app; Windows: **PowerShell**) and run:

- **Mac:** `python3 --version`
- **Windows:** `py --version`

If it prints 3.11 or higher, skip to Step 2. Otherwise:

- **Mac:** download the installer from python.org/downloads and run it.
- **Windows:** download the installer from python.org/downloads. On the first screen, **tick "Add python.exe to PATH"** before clicking Install. This is the most common setup mistake on Windows.

Close and reopen the terminal afterwards, then check the version again.

## Step 2: Install VS Code

1. Download and install VS Code from code.visualstudio.com.
2. Open it, click the **Extensions** icon in the left bar (four squares), and install **Python** (by Microsoft).

## Step 3: Install Git (recommended)

Git keeps a history of your changes, which is useful for an independent study (and for showing your advisor your progress).

- **Mac:** run `git --version` in Terminal; if it isn't installed, macOS offers to install it.
- **Windows:** install from git-scm.com, keeping the default options.

If you use GitHub, make the repository **private**, since you'll eventually work with institutional documents. The included `.gitignore` already keeps your API key and documents out of Git.

## Step 4: Open the project

1. Unzip `campus-rag.zip` somewhere easy to find, such as your Documents folder.
2. In VS Code: **File > Open Folder**, and choose the `campus-rag` folder.
3. Open a terminal inside VS Code: **Terminal > New Terminal**. All the commands below go here.

## Step 5: Create a virtual environment

A virtual environment keeps this project's packages separate from everything else on your computer.

**Mac:**
```
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```
py -m venv .venv
.venv\Scripts\activate
```

When it's active, your terminal prompt starts with `(.venv)`. You need to activate it each time you open a new terminal; VS Code usually does this for you after the next step.

> **Windows error "running scripts is disabled on this system"?** Run this once, then try activating again:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

**Tell VS Code to use it:** press `Ctrl+Shift+P` (Mac: `Cmd+Shift+P`), choose **Python: Select Interpreter**, and pick the one that mentions `.venv`.

## Step 6: Install the packages

With `(.venv)` showing in your prompt:

```
pip install -r requirements.txt
```

This takes a minute or two. It installs:

| Package | What it's for |
|---|---|
| google-genai | Gemini API: turning text into vectors (embeddings) and writing answers |
| python-dotenv | Loading your API key from the `.env` file |
| pypdf | Extracting text from PDFs |
| numpy | Vector math |
| chromadb | A local vector store, saved as files on your computer |

## Step 7: Add your API key

1. Make a copy of `.env.example` named `.env`:
   - **Mac:** `cp .env.example .env`
   - **Windows:** `copy .env.example .env`
2. Open `.env` in VS Code and replace `paste-your-key-here` with your Gemini API key from aistudio.google.com. Save the file.

**Never share or commit the `.env` file.** Anyone with the key can use it at your expense.

**Waiting on IT for AI Studio access on your school account?** You can create a key with your personal Google account in the meantime and test with sample, non-sensitive documents. Switch to the school key before using institutional documents. It's a one-line change in `.env`.

## Step 8: Check everything works

```
python check_setup.py
```

A working setup ends with:

```
All checks passed. Your environment is ready to build the RAG pipeline.
```

If something fails, the script tells you what's wrong and how to fix it. Common ones:

| Message | What it means |
|---|---|
| `... is not installed` | The virtual environment isn't active. Activate it (Step 5) and run the script again. |
| `error 400/403` on steps 4 or 5 | The API key is wrong, or your school account isn't allowed to use AI Studio yet. |
| `Gemini is busy (error 503)` | Google's servers are overloaded for a moment. The script retries; if it still fails, wait a minute. |
| `error 404` on steps 4 or 5 | The model name has changed. Update `EMBEDDING_MODEL` or `GENERATION_MODEL` in `.env`. |

---

## Project layout

```
campus-rag/
├── check_setup.py        Confirms your environment works
├── requirements.txt      Python packages
├── .env.example          Template for your API key and model settings
├── .env                  Your actual key (you create this; never commit it)
├── data/docs/            Put your source documents here (PDF, .txt, .md)
└── eval/questions.csv    Test questions with expected answers and sources
```

Coming next, as you build the pipeline:

```
├── ingest.py             Extract text from documents, chunk it, embed it, store it
├── ask.py                Ask a question: retrieve chunks and generate an answer with sources
├── evaluate.py           Run every question in eval/questions.csv and score the results
└── index/                The vector store ChromaDB creates (rebuilt by ingest.py)
```

## Before moving on

1. **Add a few documents** to `data/docs/`: 5 to 10 non-sensitive PDFs or text files are plenty to start.
2. **Start your evaluation set.** Replace the example rows in `eval/questions.csv` with real questions faculty and staff might ask about those documents, along with the correct answers and which document contains each one. Aim for 20 to 30 to begin with. These become your benchmark for every design choice you make later.
