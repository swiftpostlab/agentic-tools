# Ollama

The default runtime for this skill. It manages downloads, picks a hardware backend, places layers
across GPU and CPU, and exposes both its own API and an OpenAI-compatible one, which is what makes
it the least-effort path to a working agent.

Verified against Ollama 0.32.5 and the current published documentation on **2026-09-03**. Re-check
environment variable names and defaults if the installed version is much newer.

## Install and first run

```bash
curl -fsSL https://ollama.com/install.sh | sh    # Linux
ollama --version
curl http://localhost:11434/api/tags             # server is up
```

macOS and Windows install as an application that registers a login item and runs the server in the
background. That background server is the thing that reads configuration, which is why shell exports
do not affect it.

## The settings whose defaults are wrong for agents

Two defaults will break an agent setup, and both are easy to miss because nothing reports an error.

### Context length

The default context is small. Ollama's own FAQ states 4096 tokens; its context-length page describes
VRAM-tiered defaults instead (under 24 GiB VRAM: 4K; 24 to 48 GiB: 32K; 48 GiB and above: 256K).
The documentation is not self-consistent here, so **do not reason about which applies. Measure it
with `ollama ps` and set it explicitly.**

Ollama's own guidance: tasks that need large context, including agents and coding tools, should be
set to at least 64000 tokens.

```bash
OLLAMA_CONTEXT_LENGTH=65536 ollama serve
```

Per-session, inside `ollama run`: `/set parameter num_ctx 65536`.
Per-request, through the API: `"options": {"num_ctx": 65536}`.

### Keep-alive

Models unload after 5 minutes idle by default. For an agent that means re-loading and re-prefilling
a large system prompt every time the user pauses to think.

```bash
OLLAMA_KEEP_ALIVE=24h
```

Overridable per request with the `keep_alive` field on `/api/generate` and `/api/chat`. A value of
`0` unloads immediately, which is how you free memory without restarting the server.

## Setting environment variables so the server actually sees them

This is the most common configuration failure. The server is a background service; it does not
inherit your shell.

**Linux (systemd):**

```bash
systemctl edit ollama.service
```

```ini
[Service]
Environment="OLLAMA_CONTEXT_LENGTH=65536"
Environment="OLLAMA_KEEP_ALIVE=24h"
```

Then `systemctl daemon-reload && systemctl restart ollama`.

**macOS (application):**

```bash
launchctl setenv OLLAMA_CONTEXT_LENGTH 65536
```

Restart the Ollama application afterwards. `launchctl setenv` does not survive a reboot on its own.

**Windows:** set them as user environment variables, then restart the Ollama application.

Confirm the change landed by loading a model and reading the `CONTEXT` column of `ollama ps`. Do not
assume.

## Full environment variable reference

| Variable | Purpose | Default |
| --- | --- | --- |
| `OLLAMA_CONTEXT_LENGTH` | Server-wide context window | 4096 (see the inconsistency noted above) |
| `OLLAMA_KEEP_ALIVE` | How long an idle model stays loaded | 5m |
| `OLLAMA_HOST` | Bind address and port | `127.0.0.1:11434` |
| `OLLAMA_MODELS` | Where model blobs are stored | platform-specific |
| `OLLAMA_FLASH_ATTENTION` | Force flash attention on (`1`) or off (`0`) | automatic when supported |
| `OLLAMA_KV_CACHE_TYPE` | KV cache quantization: `f16`, `q8_0`, `q4_0` | `f16` |
| `OLLAMA_NUM_PARALLEL` | Parallel requests per model | 1 |
| `OLLAMA_MAX_LOADED_MODELS` | Models resident at once | 3 x GPU count, or 3 on CPU |
| `OLLAMA_MAX_QUEUE` | Requests queued before returning 503 | 512 |
| `OLLAMA_ORIGINS` | Allowed CORS origins | local only |
| `OLLAMA_VULKAN` | Vulkan backend, for AMD and Intel GPUs outside ROCm support | off |
| `OLLAMA_NO_CLOUD` | Disable cloud model routing | off |

**`OLLAMA_NUM_PARALLEL` is a memory multiplier.** Required memory scales by
`OLLAMA_NUM_PARALLEL x OLLAMA_CONTEXT_LENGTH`. For a single-user agent, leave it at 1. Raising it
to 4 at 64K context is a request for 256K worth of cache.

`OLLAMA_MAX_LOADED_MODELS` defaults to 3, which on a memory-tight machine means two forgotten models
can starve the one you care about. Set it to 1 when memory is the constraint.

## KV cache quantization

The highest-leverage memory saving available, and the first thing to reach for when a model almost
fits. Requires flash attention, which Ollama enables automatically on supporting backends.

```bash
OLLAMA_FLASH_ATTENTION=1
OLLAMA_KV_CACHE_TYPE=q8_0
```

| Type | Memory vs f16 | Quality |
| --- | --- | --- |
| `f16` | baseline | Default, no loss |
| `q8_0` | ~1/2 | Very small loss, usually not noticeable. **Use this when f16 does not fit.** |
| `q4_0` | ~1/4 | Small to medium loss, more visible at high context |

This is a **global** setting: it applies to every model on the server, not per model.

Impact scales with the model's grouped-query attention design. Models with a high GQA count are more
sensitive to cache quantization than models with a low one, so verify output quality on a real task
after changing it rather than assuming it is free.

## Modelfile parameters

Environment variables set server-wide defaults. A Modelfile bakes settings into a named model, which
is the clean way to give one model a 64K context without changing the server.

```
FROM qwen3.5:9b
PARAMETER num_ctx 65536
```

```bash
ollama create qwen3.5-9b-64k -f ./Modelfile
```

Useful parameters: `num_ctx` (context window, default 2048 at the Modelfile layer),
`num_predict` (max output tokens), `temperature` (default 0.8), `top_k`, `top_p`,
`repeat_penalty` (default 1.0, disabled), `repeat_last_n` (default 64), and `stop` (repeatable).

`ollama show --modelfile <model>` prints the effective Modelfile for any model, which is the fastest
way to see what template and stop tokens it ships with.

Instructions beyond `PARAMETER`: `FROM`, `TEMPLATE`, `SYSTEM`, `ADAPTER` for (Q)LoRA,
`LICENSE`, `MESSAGE` for seeded history, and `REQUIRES` for a minimum Ollama version.

Leave `temperature` and the sampling parameters alone unless you have a reason. Model publishers
tune them per model, and `ollama show` will tell you what they chose.

## Inspecting a model

```bash
ollama show gemma4:e4b
```

```
  Model
    architecture        gemma4
    parameters          8.0B
    context length      131072
    embedding length    2560
    quantization        Q4_K_M
    requires            0.20.0

  Capabilities
    completion, vision, audio, tools, thinking

  Parameters
    temperature 1, top_k 64, top_p 0.95
```

The `Capabilities` block is the authoritative answer to "does this model support tool calling" for
the build you actually have. Trust it over any table, including this skill's.

## Apple Silicon and MLX

Ollama's Mac inference stack is built on Apple's MLX framework, introduced in preview in 0.19
(March 2026) and taking advantage of unified memory. Ollama reported roughly 1.6x faster prefill and
close to 2x faster generation against the previous stack, with the largest gains on M5-series chips
and their GPU Neural Accelerators.

Two things follow:

- **On Apple Silicon, prefer an MLX build when one exists.** Many library models publish `-mlx`
  tags alongside the GGUF ones, for example `qwen3.8:27b-mlx`. Sizes are comparable; the backend
  differs.
- **MLX acceleration in Ollama started narrow.** The preview accelerated specific architectures and
  required a Mac with more than 32 GB of unified memory. Coverage has expanded since, but confirm
  for the specific model rather than assuming. If a model has no `-mlx` tag, it is running on the
  general backend.

MLX is not automatically the right answer even on a Mac. Benchmarks published by Nous on an M5 Max
running Qwen3.5-9B put llama.cpp at 67 ms time-to-first-token against MLX's 289 ms, while MLX
generated 96 tokens/second against llama.cpp's 70. MLX wins total completion time; llama.cpp wins
responsiveness and, with quantized KV cache, wins clearly on memory-constrained machines. For an
interactive agent on a 16 GB Mac, llama.cpp with `q4_0` KV cache is a defensible choice over MLX.

## Launching a client

Ollama configures several agent clients directly:

```bash
ollama launch pi --model <model>
ollama launch hermes --model <model>
ollama launch <integration> --config      # write config without launching
```

Supported integrations as of 0.32.5: `claude`, `chatgpt` (aliases `codex-app`, `codex-desktop`,
`codex-gui`), `hermes`, `hermes-desktop`, `openclaw` (aliases `clawdbot`, `moltbot`), `opencode`,
`codex`, `copilot`, `omp`, `droid`, `kimi`, `pi`, `pool`, `cline`, `qwen`, `vscode`.

Flags: `--model`, `--config`, `--restore` (restore an integration to its default profile), `-y`.
Extra arguments pass through after `--`, for example
`ollama launch codex -- --sandbox workspace-write`.

`--restore` is the undo. Mention it before running `launch` against a client the user has already
configured by hand, because `launch` writes to that client's configuration.

## Cloud tags

Some library entries carry `-cloud` tags, and some models are cloud-only. Those run on Ollama's
infrastructure, not on the machine, and require a signed-in account. They are a legitimate option
but they are **not local inference**: data leaves the machine. When the reason for going local is
privacy or air-gapping, filter cloud tags out and set `OLLAMA_NO_CLOUD`.

## Troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| `ollama ps` shows a CPU percentage | Model plus cache exceeds VRAM. Lower context, quantize KV to `q8_0`, or use a smaller model. |
| `CONTEXT` shows 4096 after configuring 65536 | The server never saw the variable. Set it as a service environment variable, not a shell export, and restart. |
| Minutes of silence before the first token | Prefill of the agent's system prompt and tool schemas. Normal. Keep the model loaded and raise the client's stream timeout. |
| Model responds but never calls tools | The model lacks tool support, or its tool calling degrades under a long prompt. Check `ollama show` capabilities, then test with a minimal prompt. |
| 503 responses under load | Queue full. Raise `OLLAMA_MAX_QUEUE`, or reduce concurrency. |
| GPU disappears after suspend/resume on Linux | Known NVIDIA driver issue. `sudo rmmod nvidia_uvm && sudo modprobe nvidia_uvm`. |
| Model was fine, now everything is slow | Another model is resident. Check `ollama ps`, `ollama stop <model>`, and consider `OLLAMA_MAX_LOADED_MODELS=1`. |
