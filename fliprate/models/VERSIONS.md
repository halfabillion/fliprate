# Local Ollama models (zero spend)

Recorded Thursday 12 Nov 2026, Europe/London (GMT).

- **Ollama binary:** `/workspace/tools/ollama/bin/ollama` version **0.40.13**
- **Host:** `127.0.0.1:11434`
- **OLLAMA_MODELS:** `/workspace/tools/ollama/models`
- The Ollama registry pull (`ollama pull`) hung on "pulling manifest" from this box (same issue as the earlier Swarm Alignment entry). Models were obtained as public GGUFs from Hugging Face (no account, no payment) and registered with `ollama create`.

| Ollama tag | Source GGUF (Q4_K_M) | Bytes | SHA-256 |
|---|---|---:|---|
| `qwen2.5:0.5b` | [Qwen/Qwen2.5-0.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF) `qwen2.5-0.5b-instruct-q4_k_m.gguf` | 491400032 | `74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db` |
| `qwen2.5:1.5b` | [Qwen/Qwen2.5-1.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF) `qwen2.5-1.5b-instruct-q4_k_m.gguf` | 1117320736 | `6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e` |
| `llama3.2:1b` | [bartowski/Llama-3.2-1B-Instruct-GGUF](https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF) `Llama-3.2-1B-Instruct-Q4_K_M.gguf` | 807694464 | `6f85a640a97cf2bf5b8e764087b1e83da0fdb51d7c9fab7d0fece9385611df83` |
| `qwen2.5-3b-local:latest` (already on box; too slow for the smoke test) | local `qwen2.5-3b-q4km.gguf` | 2104932916 | `626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d` |

Start the server:

```bash
export PATH="/workspace/tools/ollama/bin:$PATH"
export OLLAMA_MODELS="/workspace/tools/ollama/models"
ollama serve
```

A one-shot probe of `qwen2.5:1.5b` on this box (12 Nov 2026) answered "Paris" at 100 confidence in **2.71 s**. That timing informed the smoke budget; it is not a research result.

Seeded Ollama / llama.cpp calls can be only approximately reproducible because of KV-cache reuse (see the earlier Apart Swarm entry). All raw replies are logged so metrics can be recomputed.
