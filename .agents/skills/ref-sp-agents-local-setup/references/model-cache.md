# Model Cache

**Verified: 2026-09-03.** Source: ollama.com library pages for tags, sizes, contexts, and
capabilities; upstream Hugging Face `config.json` for architecture and KV-cache arithmetic.

This is a **dated snapshot, not a live source.** If today is more than roughly a month past the date
above, refresh it with the procedure in `./model-discovery.md` before recommending anything from it.
If the user asks about a model that is not here, do not extrapolate: look it up.

## How to read the columns

- **Download** is what Ollama reports for that tag, already quantized (roughly 4-bit for standard
  builds). It is the weights, not the footprint.
- **KV @64K** is the key/value cache at 64K context, f16, computed from the published config with
  sliding-window and KV-sharing layers accounted for. Halve it for `q8_0` cache.
- **Needs @64K** is `Download + KV + ~1 GB overhead`: the memory the model must have to run at the
  agent context floor. Meeting it in **VRAM or unified memory** gives usable speed; meeting it only
  in **system RAM** works but runs at CPU speed. These are the same number; only the placement
  differs, and `ollama ps` tells you which you got.
- **Tier** is judgement, not measurement. *Agentic* = sustained multi-turn tool use in long
  sessions. *Assist* = bounded, supervised, single-file work. *Utility* = completion, commit
  messages, summarization, classification.

Estimates run slightly conservative. A measured check on `qwen3.5:4b` came in at 5.4 GB against a
6.6 GB estimate.

## Tool-capable models that run locally

Every row below reports tool-calling support, which is the hard gate for agent use.

| Model (Ollama tag) | Architecture | Download | Native ctx | Think | Vision | KV @64K | Needs @64K | Tier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `qwen3.5:2b` | 2B dense | 2.7 GB | 256K | yes | yes | 0.8 GB | **~4.5 GB** | Utility |
| `qwen3.5:4b` | 4B dense | 3.4 GB | 256K | yes | yes | 2.2 GB | **~6.6 GB** | Utility |
| `gemma4:e2b` | 2B effective, sliding + KV-shared | 7.2 GB | 128K | yes | yes | 0.2 GB | **~8.4 GB** | Utility |
| `ornith:9b` | 9B dense, agentic-coding tuned | 5.6 GB | 256K | no | no | 2.2 GB | **~8.8 GB** | Assist |
| `qwen3.5:9b` | 9B dense | 6.6 GB | 256K | yes | yes | 2.2 GB | **~9.8 GB** | Assist |
| `gemma4:e4b` | 8B effective, sliding + KV-shared | 9.6 GB | 128K | yes | yes | 0.6 GB | **~11.2 GB** | Assist |
| `gemma4:12b` | 12B dense, sliding | 7.6 GB | 256K | yes | yes | 4.6 GB | **~13.2 GB** | Assist |
| `gpt-oss:20b` | ~21B MoE, sliding | 14 GB | 128K | yes | no | 1.6 GB | **~16.6 GB** | Assist |
| `granite4.1:8b` | 8B dense, all-global attention | 5.3 GB | 128K | no | no | 10.7 GB | **~17.0 GB** | Assist |
| `muse-glimmer:30b` | 30B dense, sliding, Apache-2.0 | 18 GB | 128K | yes | yes | 1.0 GB | **~20.0 GB** | Agentic |
| `gemma4:26b` | 26B MoE (A4B), sliding | 19 GB | 256K | yes | yes | 2.9 GB | **~22.9 GB** | Agentic |
| `qwen3.8:27b` | 27B dense | 18 GB | 256K | yes | yes | 4.3 GB | **~23.3 GB** | Agentic |
| `ornith:35b` | 35B MoE (256 experts, 8 active) | 21 GB | 256K | no | no | 1.3 GB | **~23.3 GB** | Agentic |
| `qwen3.5:35b` | 35B MoE (A3B) | 24 GB | 256K | yes | yes | 1.3 GB | **~26.3 GB** | Agentic |
| `nemotron-3.5-lightning` | 30B MoE (A3B) | 25 GB | 1M | yes | no | 3.5 GB | **~29.5 GB** | Agentic |
| `gemma4:31b` | 31B dense, sliding | 20 GB | 256K | yes | yes | 11.6 GB | **~32.6 GB** | Agentic |
| `granite4.1:30b` | 30B dense, all-global attention | 17 GB | 128K | no | no | 17.2 GB | **~35.2 GB** | Agentic |
| `qwen3.6:27b` | 27B, agentic-coding tuned | 18 GB | 256K | yes | yes | not verified | ~23 GB (est.) | Agentic |
| `nemotron3:33b` | 33B multimodal (video/audio/image) | 28 GB | 128K | yes | yes | not verified | ~30 GB (est.) | Agentic |
| `mistral-medium-3.5` | 128B dense | 80 GB | 256K | yes | yes | not verified | 85 GB+ (est.) | Agentic, workstation only |
| `qwen3-coder:30b` | 30B, coding-tuned, older generation | 19 GB | 256K | no | no | not verified | ~21 GB (est.) | Agentic |

Rows marked "not verified" had their sizes and capabilities read from ollama.com but their config
was not fetched. Verify before relying on the memory figure.

MLX builds (`-mlx` tags) exist for `qwen3.5`, `qwen3.6`, `qwen3.8`, `gemma4`, `muse-glimmer`, and
`nemotron-3.5-lightning`. Sizes are comparable to the GGUF builds. Prefer them on Apple Silicon.

## FIM completion models

A separate, older population. Fill-in-the-middle needs a base model trained with FIM tokens, which
most instruct-tuned chat models are not, and the frontier moved to agentic models rather than
completion. Contexts here are 8K to 32K, which is correct for the job: a completion engine sends a
window around the cursor, not a repo.

These are the models for the FIM harness class in the skill's Step 3. **Below the agent floor, this
is the tooling to recommend first**, because it runs entirely on the GPU with room to spare and
inline completion is a latency problem rather than a capability one.

| Model (Ollama tag) | Download | Native ctx | Fits in | Notes |
| --- | --- | --- | --- | --- |
| `qwen2.5-coder:0.5b` | 398 MB | 32K | ~1 GB | Smallest useful FIM model. |
| `qwen2.5-coder:1.5b` | 986 MB | 32K | ~2 GB | llama.cpp's `<8 GB VRAM` default (as Q8_0). |
| `codegemma:2b` | 1.6 GB | 8K | ~3 GB | FIM-specific variant of Gemma. |
| `stable-code` (3B) | 1.6 GB | 16K | ~3 GB | Instruct and completion variants. |
| `starcoder2` (3B) | 1.7 GB | 16K | ~3 GB | Openly trained; 7B and 15B also published. |
| `qwen2.5-coder:3b` | 1.9 GB | 32K | ~4 GB | llama.cpp's `<16 GB VRAM` default (as Q8_0). |
| `starcoder2:7b` | 4.0 GB | 16K | ~6 GB | |
| `qwen2.5-coder:7b` | 4.7 GB | 32K | ~7 GB | llama.cpp's `>16 GB VRAM` tier. |
| `qwen2.5-coder:14b` | 9.0 GB | 32K | ~12 GB | Diminishing returns for inline completion. |
| `qwen2.5-coder:32b` | 20 GB | 32K | ~24 GB | Latency defeats the purpose at this size. |

**Fits in** here is weights plus a small cache, not the 64K agent budget, because these serve short
completion windows.

The llama.cpp presets pull their own Q8_0 GGUF builds from Hugging Face rather than using Ollama, so
the download sizes differ from the Ollama tags above:

```bash
llama-server --fim-qwen-1.5b-default   # ggml-org/Qwen2.5-Coder-1.5B-Q8_0-GGUF, port 8012
llama-server --fim-qwen-3b-default     # ggml-org/Qwen2.5-Coder-3B-Q8_0-GGUF
```

Ages are worth stating when recommending: Qwen2.5-Coder and OpenCoder are roughly a year old,
StarCoder2, CodeGemma, and Stable Code roughly two. That is not a defect for this job, but do not
present them as current-generation models.

**Larger coder models are not FIM models.** `qwen3-coder`, `qwen3-coder-next` (52 GB),
`north-mini-code-1.0` (19 GB, 30B MoE, 488K context), and `kimi-k2.7-code` are agentic coding
models. They belong to the tool-calling class and are sized in the table above, not here.

## Cloud-only, listed for completeness

These appear high in Ollama's tool-capable search results but publish **no locally runnable tags**.
They run on Ollama's infrastructure and require an account, so data leaves the machine. Do not offer
them when the reason for going local is privacy or air-gapping.

`glm-5.3`, `glm-5.3-flash`, `glm-5.2`, `glm-5.1`, `deepseek-v4-flash`, `deepseek-v4-pro`,
`minimax-m2.7`, `minimax-m3`, `kimi-k2.7-code`, `kimi-k2.6`.

## Picking from this table

**Match to the accelerator, then to the job.**

| Accelerator memory | Reasonable pick |
| --- | --- |
| 4 to 6 GB | `qwen3.5:2b` for utility work. Not an agent. |
| 8 GB | `qwen3.5:4b`, or `ornith:9b` with `q8_0` KV cache. |
| 12 GB | `qwen3.5:9b` or `gemma4:e4b`. Genuine assist work. |
| 16 GB | `gpt-oss:20b` or `gemma4:12b`. |
| 24 GB | `muse-glimmer:30b`, `qwen3.8:27b`, or `gemma4:26b`. First tier where agentic work is real. |
| 32 GB+ | `qwen3.5:35b`, `nemotron-3.5-lightning`, `gemma4:31b`. |

**Notable characteristics worth knowing:**

- **Mixture-of-experts models are the local-inference win.** `qwen3.5:35b` (A3B) and
  `nemotron-3.5-lightning` (30B-A3B) activate roughly 3B parameters per token, so they generate at
  small-model speed while needing large-model memory. When memory is available and compute is the
  bottleneck, prefer MoE. When memory is the bottleneck, MoE is the worst choice per gigabyte.
- **`muse-glimmer:30b` is described by its publisher as built for always-on local agents**, Apache
  2.0, single-GPU. Its sliding-window design makes it the cheapest 30B here in cache terms: 1.0 GB
  at 64K, against 11.6 GB for `gemma4:31b`.
- **Granite 4.1 is the cautionary row.** An 8B model that needs 17 GB at 64K because it runs global
  attention on all 40 layers with 8 KV heads. Parameter count does not predict memory. This is
  exactly why the KV column exists.
- **`nemotron-3.5-lightning` advertises 1M context.** Do not enable it casually. Cache scales
  linearly, so 1M costs roughly 16x the 64K figure.
- **Thinking models cost tokens before they act.** Useful for hard reasoning, expensive in an agent
  loop where most turns are mechanical. If a model supports it, consider whether the client can turn
  it down per turn.
- **`granite4.1` and `ornith` report tools without thinking or vision.** For a text-only coding
  agent that is not a defect.

## Deliberately not ranked by benchmark

No leaderboard scores appear here. Benchmark numbers for local builds are confounded by
quantization, context length, sampling parameters, and prompt template, and the published figures
are almost always for the unquantized reference weights rather than the 4-bit build actually being
run. Choose by fit and capability, then test on the user's real task. One real task beats a
leaderboard.
