QA_CHECK_DIR := ./youtube-transcript-agent/
QA_EXCLUDE_DIR := ./zero-shot-inference-on-multimodal-models/


.PHONY: all clean format_check format_fix lint_check lint_fix


# --- QA ---

format-check:
	uv run ruff format --check $(QA_CHECK_DIR) --exclude $(QA_EXCLUDE_DIR)

format-fix:
	uv run ruff format $(QA_CHECK_DIR) --exclude $(QA_EXCLUDE_DIR)

lint-check:
	uv run ruff check $(QA_CHECK_DIR) --exclude $(QA_EXCLUDE_DIR)

lint-fix:
	uv run ruff check --fix $(QA_CHECK_DIR) --exclude $(QA_EXCLUDE_DIR)

clean:
	find . -type f -name "*.DS_Store" -ls -delete
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf
	find . | grep -E ".pytest_cache" | xargs rm -rf
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf
	rm -rf .coverage*
