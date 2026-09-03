# pi

**This is `pi`, the agent toolkit and coding-agent CLI, not a Raspberry Pi.** Repository:
`earendil-works/pi` (formerly `badlogic/pi-mono`; the old URL redirects). A terminal coding agent
with a unified LLM API, an agent loop, a TUI, extensions, and Agent Skills support.

The default client for this skill, because it treats bring-your-own-endpoint as a first-class path
rather than an escape hatch, and because it ships a native llama.cpp router integration that no
other client here matches.

Verified against the published documentation on **2026-09-03**.

## Install

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
# or
curl -fsSL https://pi.dev/install.sh | sh
```

Run interactively with `pi`, non-interactively with `pi -p "prompt"`, continue the last session with
`pi -c`, browse previous sessions with `pi -r`.

## Path A: Ollama, the one-command route

```bash
ollama launch pi --model <model>
```

Ollama writes pi's configuration and starts it. Add `--config` to write the configuration without
launching, and `--restore` to put pi back to its default profile if the wiring goes wrong. Mention
`--restore` before running this against a pi installation the user has configured by hand.

## Path B: Ollama, configured by hand

Models are configured in `~/.pi/agent/models.json`, which pi reloads each time you open `/model`, so
no restart is needed after an edit.

For a local server only `id` is required per model:

```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "models": [
        { "id": "qwen3.5:9b" },
        { "id": "muse-glimmer:30b" }
      ]
    }
  }
}
```

**The `apiKey` is a required placeholder.** Ollama ignores it, but pi treats models as requiring
auth before they appear in `/model`. A keyless local server needs a dummy value here, a key saved
with `/login`, or `--api-key` at selection time. A model silently missing from `/model` is usually
this.

### Compatibility flags

Some OpenAI-compatible servers do not understand the `developer` role that pi uses for
reasoning-capable models, and some do not accept `reasoning_effort`. This applies to Ollama, vLLM,
SGLang, and similar servers.

```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "compat": {
        "supportsDeveloperRole": false,
        "supportsReasoningEffort": false
      },
      "models": [
        { "id": "gpt-oss:20b", "reasoning": true }
      ]
    }
  }
}
```

`compat` can sit at provider level (applies to all its models) or model level (overrides for one).
Set it at provider level for a local server; the quirks are the server's, not the model's.

Other flags that matter for local servers: `maxTokensField` (`max_completion_tokens` vs
`max_tokens`), `supportsUsageInStreaming`, `supportsFinishReason`, `requiresToolResultName`,
`requiresThinkingAsText`, `supportsStrictMode` for JSON-schema tools.

### Model fields worth setting

| Field | Default | Set it when |
| --- | --- | --- |
| `id` | required | always; this is what goes to the API |
| `contextWindow` | 128000 | the served context differs, which for a local model it usually does |
| `maxTokens` | 16384 | the model's output limit is lower |
| `reasoning` | `false` | the model has a thinking mode |
| `input` | `["text"]` | the model accepts images: `["text", "image"]` |
| `samplingParams` | omitted | you need `temperature`, `top_p`, `top_k`, `min_p` passed through |
| `cost` | zeros | never, for local models; zero is correct and keeps session accounting honest |

**Set `contextWindow` to what the server actually serves**, not to the model's native maximum. If
Ollama is running the model at 65536 and pi thinks the window is 262144, pi will not compact in
time and the server will truncate mid-session. Confirm the served value with `ollama ps` and copy
that number.

API types: `openai-completions` (most compatible, use this for local servers),
`openai-responses`, `anthropic-messages`, `google-generative-ai`.

## Path C: llama.cpp router, pi's native integration

The strongest option when you want per-model context presets, quantized KV cache, or multiple models
managed from inside pi. pi drives the llama.cpp router server directly, including downloading models
from Hugging Face.

Start the router **without** `--model` or `-m`; passing a model starts single-model mode instead.

```bash
llama-server \
  --models-dir ~/models \
  --no-models-autoload \
  --jinja \
  --host 127.0.0.1 \
  --port 8080 \
  -ngl 999 \
  -c 65536
```

- `--models-dir` discovers local GGUF files.
- `--no-models-autoload` keeps loading explicit, driven from pi.
- `--jinja` enables compatible chat templates **and tool calling**. Omitting it is a common cause of
  a model that will not call tools.
- `-ngl 999` offloads as many layers as possible to the GPU.
- `-c 65536` sets the context per loaded model. Omit it to use the model's native context, which may
  need substantially more memory.

Model directory layout: single-file models sit directly in the directory; multimodal and
multi-shard models go in their own subdirectories. Restart the router after adding files manually.

Then in pi:

```text
/login llama.cpp     # store the router URL, default http://127.0.0.1:8080
/llama               # load, unload, or download a model
/model               # select a loaded model for this session
```

`/llama` also offers **Download model…**, which searches Hugging Face and lets you choose a
repository and quantization, or accept an exact `owner/repository[:quant]`. The llama.cpp server
performs the download, so *its* process needs `HF_TOKEN` for gated repositories, not just pi's.
Search reads `HF_TOKEN`, then `$HF_TOKEN_PATH`, `$HF_HOME/token`, `$XDG_CACHE_HOME/huggingface/token`,
and `~/.cache/huggingface/token`; it works unauthenticated at lower rate limits.

**Only loaded models appear in `/model`.** Loading with `/llama` and then forgetting to select with
`/model` is the usual confusion.

Environment variables instead of `/login`:

```bash
export LLAMA_BASE_URL=http://127.0.0.1:8080
export LLAMA_API_KEY=optional-secret
```

Health checks: `curl http://127.0.0.1:8080/health` and `curl http://127.0.0.1:8080/models`.

## Selecting and cycling models

```bash
pi --model <pattern>              # pattern match
pi --list-models                  # what pi can see
pi --models "pattern1,pattern2"   # cycle between them with Ctrl+P
pi --thinking <level>             # reasoning intensity
```

`/model` in the editor (Ctrl+L) switches interactively. Cycling is genuinely useful locally: bind a
small fast model and a large capable one, and switch per task rather than paying 30B latency to
rename a variable.

## Context files and skills

pi loads `AGENTS.md`, `CLAUDE.md`, and `SYSTEM.md` from `~/.pi/agent/` and from the project
directory, and supports Agent Skills. Settings live at `~/.pi/agent/settings.json` globally and
`.pi/settings.json` per project, with the project file overriding.

**This matters more locally than it does with a hosted model.** A small model given a long
instruction file spends its attention budget on the instructions rather than the task, and pays the
prefill cost on every turn. Point a local setup at a trimmed instruction file: this skill ships one
at `../assets/AGENTS.lean.md`.

## Troubleshooting

| Symptom | Cause |
| --- | --- |
| Model missing from `/model` | No `apiKey` set for a keyless server, or (llama.cpp) not loaded via `/llama` yet. |
| Tool calls never happen | llama.cpp started without `--jinja`, or the model lacks tool support. |
| Session truncates unexpectedly | `contextWindow` in `models.json` exceeds what the server serves. |
| Errors mentioning the `developer` role | Set `compat.supportsDeveloperRole: false`. |
| Errors mentioning `reasoning_effort` | Set `compat.supportsReasoningEffort: false`. |
| Router not in router mode | It was started with `--model`, `-m`, or `-hf`. |
| Load fails or memory blows up | Lower `-c`, or unload another model. |
