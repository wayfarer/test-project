.PHONY: run stop clean help

# Default target
.DEFAULT_GOAL := help

# PID files for tracking processes
SERVER_PID := $(CURDIR)/.server.pid
CLIENT_PID := $(CURDIR)/.client.pid

run: stop ## Run both server and client concurrently (attached to terminal)
	@echo "Starting server and client..."
	@echo "Press Ctrl+C to stop both services"
	@sh -c "trap 'kill \$$(cat $(SERVER_PID) 2>/dev/null) \$$(cat $(CLIENT_PID) 2>/dev/null) 2>/dev/null; rm -f $(SERVER_PID) $(CLIENT_PID); exit' INT TERM; \
	cd $(CURDIR)/server && poetry run python -m server & echo \$$! > $(SERVER_PID); \
	cd $(CURDIR)/client && npm run dev & echo \$$! > $(CLIENT_PID); \
	wait"

stop: ## Stop both server and client
	@if [ -f $(SERVER_PID) ]; then \
		kill $$(cat $(SERVER_PID)) 2>/dev/null && echo "Server stopped" || echo "Server already stopped"; \
		rm -f $(SERVER_PID); \
	fi
	@if [ -f $(CLIENT_PID) ]; then \
		kill $$(cat $(CLIENT_PID)) 2>/dev/null && echo "Client stopped" || echo "Client already stopped"; \
		rm -f $(CLIENT_PID); \
	fi
	@echo "Checking for processes on ports 5000 and 5173-5176..."
	@lsof -ti :5000 | xargs kill -9 2>/dev/null || true
	@for port in 5173 5174 5175 5176; do lsof -ti :$$port | xargs kill -9 2>/dev/null || true; done

clean: stop ## Clean up PID files and logs
	@rm -f $(SERVER_PID) $(CLIENT_PID)
	@echo "Cleaned up"

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

