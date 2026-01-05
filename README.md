# MARK - With Kleos System

![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## What is MARK?

Mark is a personal, persistent, and intelligent assistant that lives entirely in your terminal. 
It combines the power of state-of-the-art LLMs (Google Gemini & Groq) with a local, secure memory system. 

**The coolest feature?** Local Memory.
If you tell Mark something, he remembers it forever (saved locally on your machine).

```text
> remember that my preferred language is Python
✅ I will remember: "my preferred language is Python"

> write a script to sort a list
(Mark writes the script in Python automatically because he remembers!)
```

Mark's memory is **100% local**. No data brokers, no cloud storage of your personal facts.

---

## The Kleos System

Kleos is Mark's advanced capabilities engine, entirely developed by me. It transforms Mark from a simple chatbot into a reasoning agent.

**Why use `/kleos`?**
Standard LLMs often rush to answer, missing context or nuance. Kleos forces a "Think before you speak" workflow.

### How it works:
1. **Analyze**: One provides a prompt. Kleos analyzes it and asks questions to reduce ambiguity, missing context, or hidden requirements.
2. **Refine**: It acts as an expert "Prompt Engineer", rewriting the query to be logically perfect.
3. **Execute**: After the user approves the new query, Kleos sends the optimized prompt to the AI.

**Result**: Drastically higher quality answers, better code, and deeper insights.

**Usage:**
```bash
/kleos Explain how to build a neural network from scratch
```
*(Mark will pause, analyze your request, optimize the internal prompt, and then deliver a superior tutorial)*

---


## Installation

Requirements: Python 3.8+

Linux tutorial (should work with every distro): https://youtu.be/dWaC3V3CXEA


---

## Configuration & Models

On first run, Mark guides you through setup. 

**Supported Providers (more to come..):**
1. **Groq** (Fast Inference, suggested)
   - `llama-3.3-70b-versatile`
   - `openai/gpt-oss-120b`
   - `moonshotai/Kimi-K2-Instruct`
2. **GOOGLE** (BETA)
   - `gemini-2.5-flash`
   - `gemini-2.5-flash-lite`
   - `gemini-3-flash-preview`
   - **`gemma-3-27b`** (with native language support)

You can change settings anytime with:
```bash
/config
```
or switch models on the fly:
```bash
/model
```

---

[NOTE: Mark has only been tested with free APIs, results may vary with paid APIs.]
[NOTE2: Gemini implementation is still in beta, results may vary. We suggest using Groq for now.]

## Command Reference

| Command | Description |
|---------|-------------|
| `/help` | Show this help menu |
| `/kleos <prompt>` | **Activate Kleos System** (Reasoning Mode) |
| `/model` | Switch AI Provider & Model |
| `/config` | Update API Keys and Defaults |
| `/memory list` | View all saved memories |
| `/memory search <q>` | Semantic search in memory |
| `/remember <text>` | Save a fact to local memory |
| `/reset` | Clear current conversation context |
| `/stats` | View session usage & token costs |
| `/exit` | Close Mark |

---

## Project Structure

```text
mark/
├── mark_cli/         # Core package
│   ├── main.py       # Application entry point
│   ├── memory/       # SQLite vector memory system
│   ├── providers/    # Async AI implementations
│   └── ui/           # Rich-based TUI implementation
├── docs/             # Website & Documentation (coming soon)
└── scripts/          # Verification tools
```

## Security

API keys are stored securely using your OS's native keychain (Windows Credential Manager, macOS Keychain, or Linux Secret Service). They are **never** stored in plain text.

---

### About
Created by **Valerio Pischedda** (piskevalee-cpu).
Started as a simple Telegram bot for school schedules, evolved into a powerful terminal AI companion.   

Note that this tool has been partially vibecoded and debugged by AI, it is still in beta, and may have some bugs. Please report any issues you find on the [GitHub repository](https://github.com/piskevalee-cpu/MARK), or send me an e-mail at piskevalee@gmail.com !

## License
MIT License

