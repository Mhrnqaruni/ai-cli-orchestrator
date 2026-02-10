# AI CLI Orchestrator

Let **Claude Code** orchestrate **Codex CLI** and **Gemini CLI** as autonomous workers — send sequential prompts with full conversation context, or use real-time bridge mode for interactive task delegation.

## What This Does

```
┌─────────────┐       commands        ┌─────────────┐
│             │ ───────────────────▶  │  Codex CLI  │
│ Claude Code │                       │  Gemini CLI │
│ (decides)   │ ◀───────────────────  │  (execute)  │
└─────────────┘       responses       └─────────────┘
```

**Claude Code** is the brain. It decides what needs to happen, then delegates execution to **Codex** or **Gemini** CLI tools — which can run shell commands, automate browsers, create files, and more.

Two modes of operation:

| Mode | Use Case |
|---|---|
| **Sequential Prompts** | Pre-written list of prompts sent one-by-one with full session context |
| **Bridge (Watchdog)** | Real-time — Claude writes a command file, bridge picks it up, sends to Gemini/Codex, saves response |

---

## 1. Sequential Prompt Runner (Codex)

Send a numbered list of prompts to Codex, one-by-one, in the **same session** with full conversation context preserved.

### How It Works

Uses `codex exec` for the first prompt and `codex exec resume --last` for every subsequent prompt — maintaining full context without needing a TTY.

### Quick Start

**Edit `codex_prompt.txt`:**
```
1. create a file called config.json with default settings
2. read config.json and add a "debug" field set to true
3. read config.json and confirm all fields are correct
```

**Run it:**
```bash
# Sandboxed mode (safe)
run_codex_prompts.bat

# Full auto — Codex can execute anything
run_codex_prompts.bat --yolo
```

### Options

| Flag | Description |
|---|---|
| `--yolo` | No sandbox, no approval prompts — Codex runs anything |
| `--full-auto` | Default. Sandboxed automatic execution |
| `--timeout=600` | Timeout per prompt in seconds (default: 300) |
| `--file=my_prompts.txt` | Use a different prompt file |

### Features

- Full conversation context across all prompts
- Auto-retry on timeout (up to 10 times) — no prompt is skipped
- All output saved to `codex_output.txt`

---

## 2. Bridge Mode (Gemini & Codex)

Real-time file-based bridge that lets Claude Code send commands to Gemini or Codex and read responses back — enabling multi-agent workflows.

### How It Works

```
1. Claude Code writes a task to gemini_command.txt
2. Bridge (running in separate terminal) detects the file change
3. Bridge pipes the command to Gemini CLI
4. Gemini executes (browser automation, file ops, etc.)
5. Bridge saves response to gemini_response.txt
6. Claude Code reads the response and decides what to do next
```

### Setup

**Terminal 1** — Start the bridge:
```bash
python gemini_simple_bridge.py    # for Gemini
python codex_simple_bridge.py     # for Codex
```

**Terminal 2** — Send commands (or let Claude Code do it):
```bash
python claude_to_gemini.py "open the browser and go to example.com"
python claude_to_codex.py "create a hello world app"
```

Or use interactively:
```bash
python claude_to_gemini.py
[CLAUDE] > search for latest Python release
[CLAUDE] > summarize what you found
```

### Use Cases

- Claude Code tells Gemini to automate a browser via CDP
- Claude Code tells Codex to write and test code
- Claude Code runs a bat file through Gemini (e.g. `run-cdp-profile.bat`)
- Chain multiple AI tools: Claude decides → Gemini executes → Claude reviews → Codex fixes

---

## Files

| File | Description |
|---|---|
| `codex_sequential.py` | Sequential prompt runner — sends prompts one-by-one to Codex with session context |
| `run_codex_prompts.bat` | Windows launcher for the sequential runner |
| `codex_prompt.txt` | Your prompt list (edit this) |
| `gemini_simple_bridge.py` | Watchdog bridge — connects Claude Code to Gemini CLI |
| `claude_to_gemini.py` | Helper to send commands to Gemini bridge |
| `codex_simple_bridge.py` | Watchdog bridge — connects Claude Code to Codex CLI |
| `claude_to_codex.py` | Helper to send commands to Codex bridge |

## Requirements

- Python 3.7+
- [OpenAI Codex CLI](https://github.com/openai/codex) (for Codex features)
- [Google Gemini CLI](https://github.com/google-gemini/gemini-cli) (for Gemini features)
- Windows (batch file is `.bat` — Python scripts work cross-platform)

## License

MIT
