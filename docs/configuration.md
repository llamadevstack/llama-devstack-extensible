# Config-Driven Setup

Llama Devstack supports a declarative configuration approach using:

```bash
llama-dev.config.json
```

This file controls:
- Which local models are used
- Whether logging is enabled
- Which prompt sets to install
- Whether to use the MCP router

## Sample Structure

```json
{
  "autocomplete_model": "phi",
  "log_requests": true,
  "prompt_sets": ["summarize", "generate_tests", "refactor_code", "apply_standards"],
  "use_mcp": true,
  "local_models": {
    "phi": 11434,
    "mistral": 11435
  }
}
```

## Usage

Once defined, configure your environment by running:

```bash
./configure-from
```

This generates your `.continue/config.json` file and prepares Continue.dev for use.

## Example Profiles

- **offline-only.json** — no logging, no MCP, fully local
- **cloud-heavy.json** — logging enabled, MCP router used
- **low-memory.json** — summarization only, for minimal setups

See `docs/config-examples/` for these files.