# Contributing to CineFlow

Thank you for your interest in contributing to CineFlow!

## Code of Conduct

Please be respectful, collaborative, and constructive when contributing to CineFlow.

## Development Workflow

1. **Fork the Repository** and create a feature branch (`git checkout -b feature/my-feature`).
2. **Install Dependencies**:
   ```bash
   uv sync
   ```
3. **Run Pre-Deployment Tests**:
   Ensure all 66 unit and integration tests pass before opening a PR:
   ```bash
   uv run pytest tests/unit tests/integration
   ```
4. **Code Quality & Formatting**:
   Ensure your code adheres to standard conventions:
   ```bash
   uv run ruff check .
   uv run ruff format --check .
   ```
5. **Run the Evaluation Benchmark**:
   If modifying agent prompts, models, or tool logic, verify against the Golden Dataset:
   ```bash
   uv run agents-cli eval generate --dataset tests/eval/datasets/golden_film_eval.json --output tests/eval/traces/cand/
   uv run agents-cli eval grade --traces tests/eval/traces/cand/<latest_trace>.json --config tests/eval/eval_config.yaml --output tests/eval/results/
   ```
6. **Submit a Pull Request** describing your changes and link any related issues.

## License

By contributing to CineFlow, you agree that your contributions will be licensed under the [Apache License, Version 2.0](LICENSE).
