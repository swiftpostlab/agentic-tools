# Hermes Agent

Nous Research's agent. Repository: `NousResearch/hermes-agent`. Distinctive for shipping a
**managed local runtime**: the desktop app installs and updates a llama.cpp build, sizes models
against the actual machine, and manages memory placement with no exposed knobs.

Choose Hermes over pi when the user wants local inference handled for them, wants a GUI, or is
already in the Nous ecosystem. Choose pi when you want direct control over the server.

Verified against the published documentation on **2026-09-03**.

## Configuration model

Settings resolve in priority order: CLI arguments, then `~/.hermes/config.yaml`, then
`~/.hermes/.env` for secrets, then built-in defaults. `hermes config set` routes values
automatically, API keys to `.env` and everything else to `config.yaml`.

Repo instruction files need no bridge: Hermes auto-injects `.hermes.md`, `AGENTS.md`, `CLAUDE.md`,
and `.cursorrules` when present. The user-level surface is `~/.hermes/SOUL.md`, an identity file
rather than a config file.

**Injected context files are truncated at `context_file_max_chars`, default 20,000.** A long
`AGENTS.md` is silently cut. This bites hardest on local setups, where the prompt is also the thing
you are paying prefill for. Use a trimmed instruction file: `../assets/AGENTS.lean.md`.

## Path A: managed local runtime (desktop)

**Settings → Providers → Local Models**, or "Run models locally" during onboarding.

1. **Install runtime.** Downloads and verifies an official llama.cpp build for the hardware, a few
   hundred MB, kept updated.
2. **Pick a model** from the catalog. Every row is priced against the machine: green *Fits your
   GPU*, amber *Uses system RAM*, red *Too big for this machine*, with the context window and the
   download size for the build chosen for that hardware.
3. **Download**, then **Use**.

What it decides for you, and the reasoning is worth knowing even if you never use the GUI:

- It picks the highest-quality quantization that runs fully on the GPU, and **never offers below
  4-bit**, on the grounds that the quality loss stops being worth it. A machine that cannot run the
  4-bit build fully on GPU simply cannot run that model well.
- Models start at a context window that fits the GPU and **grow toward their native maximum** as the
  conversation needs room. "Context window grown" in the status feed is that happening, not an error.
- **Every recommended model gets at least 64K context.** When a model exceeds GPU memory, overflow
  goes to system RAM in the order that hurts least: expert weights first, never the attention cache.
- Conversation compression only starts at the model's maximum window; growth comes first.
- Idle models unload after 15 minutes and reload on the next message.

**Find more models** searches all of Hugging Face with a per-file fit check sized to the machine.
**Add model file** links an existing local `.gguf` without copying it.

If a `llama-server` is already running, Hermes detects and uses it rather than starting its own.

### Headless configuration

The desktop UI writes these; they are documented for CLI and headless use.

```yaml
local_runtime:
  enabled: false     # true starts the managed server with Hermes
  backend: auto      # auto | cuda | metal | vulkan | hip | cpu
  tag: b10362        # pinned llama.cpp release
```

Selecting a local model as the main model uses the standard provider settings:
`model.provider: llamacpp` plus `model.default`.

Models and runtimes live under the Hermes home directory, in `models/` and `runtimes/llamacpp/`.

Platform support: NVIDIA CUDA or CPU on Windows and Linux, Metal on Apple Silicon, Vulkan for AMD.
8 GB of GPU memory runs the small catalog models comfortably; 16 GB+ runs the 27B to 35B class at
high quality.

## Path B: Ollama

One command, if Ollama is installed:

```bash
ollama launch hermes --model <model>
```

By hand, `hermes setup` and choose **Custom Endpoint**, base URL `http://localhost:11434/v1`, API
key empty or `no-key`. Or edit `~/.hermes/config.yaml`:

```yaml
model:
  default: "<model>"
  provider: "custom"
  base_url: "http://localhost:11434/v1"
```

`hermes setup --portal` gets a model provider and the Tool Gateway tools without hand-editing YAML.

### The context trap

**Hermes requires at least 64K context**, and Ollama will not give it that by default. Either set
`OLLAMA_CONTEXT_LENGTH=65536` on the server (see `./ollama.md`), or bake it into a derived model:

```bash
cat > /tmp/Modelfile <<'EOF'
FROM <model>
PARAMETER num_ctx 65536
EOF
ollama create <model>-64k -f /tmp/Modelfile
```

Then point `model.default` at `<model>-64k`. Verify with `ollama ps` that `CONTEXT` reads 65536.

## Path C: manual server on macOS

Hermes documents both backends against an OpenAI-compatible endpoint.

**llama.cpp**, `brew install llama.cpp`:

```bash
llama-server -m ~/models/<model>.gguf \
  -ngl 99 -c 131072 -np 1 -fa on \
  --cache-type-k q4_0 --cache-type-v q4_0 \
  --host 127.0.0.1
```

`--cache-type-k q4_0 --cache-type-v q4_0` is the significant flag pair on a memory-constrained
machine. Published impact for a 9B model at 128K context: f16 cache ~16 GB, `q8_0` ~8 GB, `q4_0`
~4 GB. Serving on `0.0.0.0` exposes the model to the network; keep `127.0.0.1` unless you
deliberately want LAN access.

**MLX**, via omlx (`omlx.ai`), serves on `http://127.0.0.1:8000` by default and supports multiple
models simultaneously.

Which to pick, from Nous's own benchmarks on an M5 Max running Qwen3.5-9B at comparable
quantization:

| Metric | llama.cpp (Q4_K_M) | MLX (mxfp4) |
| --- | --- | --- |
| Time to first token, avg | **67 ms** | 289 ms |
| Generation, avg | 70 tok/s | **96 tok/s** |
| Total for 512 tokens | 7.3 s | **5.5 s** |

llama.cpp for interactive low-latency work and for memory-constrained machines, where its quantized
KV cache has no equivalent. MLX for long-form generation and bulk processing, where total completion
time matters more than first-token latency. This is a real tradeoff, not a ranking: "MLX is faster
on Mac" is true for throughput and false for responsiveness.

## Timeouts

Hermes auto-detects local endpoints (localhost, LAN addresses) and relaxes streaming timeouts
without configuration.

| Timeout | Default | Local adjustment | Override |
| --- | --- | --- | --- |
| Stream read (socket) | 120 s | raised to 1800 s | `HERMES_STREAM_READ_TIMEOUT` |
| Stale stream detection | 180 s | disabled | `HERMES_STREAM_STALE_TIMEOUT` |
| API call (non-streaming) | 1800 s | unchanged | `HERMES_API_TIMEOUT` |

Set overrides in `~/.hermes/.env`.

**A silent first turn is prefill, not a hang.** Hermes sends its system prompt and tool schemas on
every call, so on slow hardware the first turn can be minutes of silence before any token appears.
Mitigate by keeping the model loaded (`OLLAMA_KEEP_ALIVE=24h`) and trimming the fixed prompt;
`hermes prompt-size` reports what that prompt costs.

## Tool calling

Without tool support Hermes cannot edit files or run commands; the model returns plain text where a
function call should be. Hermes's own Ollama guide is blunt that only some commonly available models
have reliable tool calling.

Verify the specific build with `ollama show <model>` and confirm `tools` appears under Capabilities.
Then test it: ask for something that requires reading a named file, and check that a tool is
actually invoked rather than narrated.
