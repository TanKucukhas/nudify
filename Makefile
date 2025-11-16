.PHONY: help install server test validate clean

help:
	@echo "AI Image Generation Lab - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install    - Install dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make server     - Start the backend server"
	@echo "  make test       - Run tests"
	@echo "  make validate   - Validate experiment configs"
	@echo "  make format     - Format code with black"
	@echo ""
	@echo "Experiments:"
	@echo "  make exp001     - Run experiment 001"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean      - Remove temporary files"

install:
	python3.13 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	@echo "✓ Installation complete!"
	@echo "  Run 'source venv/bin/activate' to activate the environment"

server:
	@echo "Starting backend server..."
	./venv/bin/python -m backend.server

test:
	./venv/bin/pytest -v

validate:
	@echo "Validating experiment configs..."
	./venv/bin/python scripts/run_experiments.py \
		--config configs/exp001_params.json \
		--dry-run

format:
	./venv/bin/black backend/ scripts/

exp001:
	@echo "Running experiment 001..."
	./venv/bin/python scripts/run_experiments.py \
		--config configs/exp001_params.json

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete
	@echo "✓ Cleaned temporary files"
