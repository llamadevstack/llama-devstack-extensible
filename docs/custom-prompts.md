# Custom Prompt Sets

You can create your own prompt sets by adding JSON files to:

```bash
/custom-prompts/
```

Each file should contain a `"prompts"` array with Continue.dev-compatible entries.

### Example: `custom-prompts/my_team_prompts.json`

```json
{
  "prompts": [
    {
      "name": "Evaluate Risk Score",
      "context": "selection",
      "preprocessor": "Mistral (No Logging)",
      "prompt": "Evaluate the selected code and identify any logic that could produce inaccurate risk scores. Suggest improvements."
    }
  ]
}
```

To activate your custom prompt set, add the filename (without `.json`) to `llama-dev.config.json`:

```json
{
  "prompt_sets": ["summarize", "my_team_prompts"]
}
```

Then run:

```bash
./configure-from
```