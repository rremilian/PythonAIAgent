# Python AI Agent

A terminal-based AI Agent written in Python. This project provides a modular, extensible chat interface with support for file operations, shell command execution, and optional molecular structure conversion. It is designed for local use and easy customization.

## Features

- **Terminal Chat Interface:** Interact with the assistant directly from your terminal.
- **File Tools:** Read, list, and edit files in your filesystem.
- **Shell Command Execution:** Run shell commands securely from within the assistant.
- **Molecular Tools:** Convert SMILES strings to Cartesian coordinates (using RDKit).

## Optional: Retrieval-Augmented Generation (RAG)

The `misc/rag.py` script provides a simple RAG implementation for experimenting with retrieval-augmented question answering. This is just for testing purposes and is not required for the main agent functionality.

## Requirements

- Python 3.8+
- Anthropic API Key

## Usage

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the assistant:
   ```bash
   python main.py
   ```

## Project Structure

```
main.py           # Main assistant application
misc/
    rag.py        # (Optional) RAG module for document retrieval
README.md         # Project documentation
```