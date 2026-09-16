.PHONY: help start stop llm app clean logs kill demo showcase demo-models

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help:
	@echo "$(BLUE)Recall App - Available Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)QUICK START:$(NC)"
	@echo "  $(GREEN)make demo$(NC)       - Start all 4 apps + LiteLLM (fastest)"
	@echo "  $(GREEN)make start$(NC)      - Start LiteLLM proxy + Recall app"
	@echo ""
	@echo "$(YELLOW)SHOWCASE & DEMO:$(NC)"
	@echo "  $(GREEN)make showcase$(NC)   - Interactive workflow showcase (after running make demo)"
	@echo "  $(GREEN)make demo-models$(NC) - Show demo with different model combinations"
	@echo ""
	@echo "$(YELLOW)MANAGEMENT:$(NC)"
	@echo "  $(GREEN)make llm$(NC)        - Start only LiteLLM proxy"
	@echo "  $(GREEN)make app$(NC)        - Start only Recall app"
	@echo "  $(GREEN)make stop$(NC)       - Stop all processes"
	@echo "  $(GREEN)make kill$(NC)       - Force kill all processes"
	@echo "  $(GREEN)make logs$(NC)       - Show running processes"
	@echo "  $(GREEN)make clean$(NC)      - Clean up runtime data and caches"
	@echo "  $(GREEN)make reset$(NC)      - Reset demo data (fresh start)"
	@echo ""
	@echo "$(BLUE)ENDPOINTS (all 4 apps):$(NC)"
	@echo "  🎯 Recall Dashboard:    http://127.0.0.1:8501"
	@echo "  👥 Club Portal:         http://127.0.0.1:8101"
	@echo "  📚 Class Booking:       http://127.0.0.1:8102"
	@echo "  🎁 Member Offers:       http://127.0.0.1:8103"
	@echo "  🧠 LiteLLM Proxy:       http://127.0.0.1:4000"
	@echo ""
	@echo "$(BLUE)WORKFLOW:$(NC)"
	@echo "  1. Run $(GREEN)make demo$(NC) to start everything"
	@echo "  2. Open http://127.0.0.1:8501 in browser"
	@echo "  3. Use sidebar to select models:"
	@echo "     • Investigator (phi/mistral/neural-chat)"
	@echo "     • Scope Reviewer (orca-mini/mixtral)"
	@echo "     • Judge (phi/mistral)"
	@echo "     • Auditor (phi/mistral)"
	@echo "  4. Follow the workflow in the dashboard"
	@echo "  5. Run $(GREEN)make showcase$(NC) for guided demo"
	@echo ""

start: stop llm-bg app
	@echo "$(GREEN)✓ Recall app is running!$(NC)"
	@echo "  Dashboard: http://127.0.0.1:8501"
	@sleep 2

llm-bg:
	@echo "$(BLUE)Starting LiteLLM proxy...$(NC)"
	@nohup litellm --model ollama/phi > .litellm.log 2>&1 &
	@echo "$$!" > .litellm.pid
	@sleep 2
	@echo "$(GREEN)✓ LiteLLM running on localhost:4000$(NC)"

llm:
	@echo "$(BLUE)Starting LiteLLM proxy (foreground)...$(NC)"
	@echo "$(RED)Press Ctrl+C to stop$(NC)"
	@litellm --model ollama/phi

app:
	@echo "$(BLUE)Starting Recall app...$(NC)"
	@python3 run_demo.py

stop:
	@echo "$(BLUE)Stopping all processes...$(NC)"
	@if [ -f .litellm.pid ]; then \
		kill $$(cat .litellm.pid) 2>/dev/null || true; \
		rm -f .litellm.pid; \
		echo "$(GREEN)✓ LiteLLM stopped$(NC)"; \
	fi
	@pkill -f "streamlit run app.py" 2>/dev/null || true
	@pkill -f "withdrawal.service_app" 2>/dev/null || true
	@echo "$(GREEN)✓ All processes stopped$(NC)"

kill:
	@echo "$(RED)Force killing all processes...$(NC)"
	@pkill -9 -f litellm 2>/dev/null || true
	@pkill -9 -f streamlit 2>/dev/null || true
	@pkill -9 -f withdrawal 2>/dev/null || true
	@rm -f .litellm.pid .litellm.log
	@echo "$(GREEN)✓ All processes killed$(NC)"

logs:
	@echo "$(BLUE)Running processes:$(NC)"
	@ps aux | grep -E "(litellm|streamlit|withdrawal)" | grep -v grep || echo "$(RED)No processes running$(NC)"
	@echo ""
	@if [ -f .litellm.log ]; then \
		echo "$(BLUE)LiteLLM log (last 10 lines):$(NC)"; \
		tail -10 .litellm.log; \
	fi

clean:
	@echo "$(BLUE)Cleaning up...$(NC)"
	@rm -rf .runtime __pycache__ .pytest_cache *.pyc
	@rm -f .litellm.log .litellm.pid
	@echo "$(GREEN)✓ Cleaned$(NC)"

reset:
	@echo "$(RED)Resetting demo data (fresh start)...$(NC)"
	@make kill
	@make clean
	@echo "$(GREEN)✓ Ready for fresh start$(NC)"
	@echo "Run: $(BLUE)make start$(NC)"

# ============================================================================
# DEMO & SHOWCASE COMMANDS
# ============================================================================

demo: stop llm-bg
	@echo ""
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║         RECALL - FULL DEMO (All 4 Apps Running)            ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)✓ LiteLLM proxy started on port 4000$(NC)"
	@echo ""
	@echo "$(BLUE)Starting all 4 apps...$(NC)"
	@python3 run_demo.py

showcase:
	@echo ""
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║              INTERACTIVE WORKFLOW SHOWCASE                 ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)STEP 1: GIVE CONSENT$(NC)"
	@echo "  → Open: $(BLUE)http://127.0.0.1:8101$(NC) (Club Portal)"
	@echo "  → Click 'Give Consent' button"
	@echo "  → Watch data get shared to other apps"
	@echo ""
	@echo "$(YELLOW)STEP 2: VIEW PERSONALIZATION$(NC)"
	@echo "  → Open: $(BLUE)http://127.0.0.1:8102$(NC) (Class Booking)"
	@echo "  → See personalized class recommendations"
	@echo "  → Open: $(BLUE)http://127.0.0.1:8103$(NC) (Member Offers)"
	@echo "  → See targeted offers based on your data"
	@echo ""
	@echo "$(YELLOW)STEP 3: INVESTIGATE DATA TRAIL$(NC)"
	@echo "  → Back to: $(BLUE)http://127.0.0.1:8501$(NC) (Recall Dashboard)"
	@echo "  → In sidebar, select models:"
	@echo "     • Investigator: phi (fast) or mistral (better)"
	@echo "     • Scope Reviewer: orca-mini (default)"
	@echo "     • Judge: phi (fast)"
	@echo "     • Auditor: phi (fast)"
	@echo "  → Click 'Investigate data trail' button"
	@echo "  → Watch LLM agents discover where your data is"
	@echo ""
	@echo "$(YELLOW)STEP 4: REVIEW PROPOSAL$(NC)"
	@echo "  → Read the investigation results"
	@echo "  → See which records will be deleted"
	@echo "  → Review the evidence trail (diagram)"
	@echo ""
	@echo "$(YELLOW)STEP 5: APPROVE & WITHDRAW$(NC)"
	@echo "  → Check 'I approve these deletions'"
	@echo "  → Click 'Approve & withdraw' button"
	@echo "  → Watch deletion happen in real-time"
	@echo ""
	@echo "$(YELLOW)STEP 6: VERIFY DELETION$(NC)"
	@echo "  → Check other apps (8101, 8102, 8103)"
	@echo "  → Your data is actually gone!"
	@echo "  → Download verification receipt"
	@echo ""
	@echo "$(GREEN)✓ Demo complete!$(NC)"
	@echo ""

demo-models:
	@echo ""
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║           MODEL COMBINATIONS TO TRY                         ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Configuration 1: FAST (Recommended for demos)$(NC)"
	@echo "  Investigator:    $(GREEN)ollama/phi$(NC)         (2.7B) - ⚡ Very Fast"
	@echo "  Scope Reviewer:  $(GREEN)ollama/orca-mini$(NC)  (3B)   - ⚡ Fast"
	@echo "  Judge:           $(GREEN)ollama/phi$(NC)         (2.7B) - ⚡ Very Fast"
	@echo "  Auditor:         $(GREEN)ollama/phi$(NC)         (2.7B) - ⚡ Very Fast"
	@echo "  $(BLUE)Edit .env: Set all to phi/orca-mini$(NC)"
	@echo ""
	@echo "$(YELLOW)Configuration 2: BALANCED (Better reasoning)$(NC)"
	@echo "  Investigator:    $(GREEN)ollama/mistral$(NC)    (7B)   - ⚡⚡ Balanced"
	@echo "  Scope Reviewer:  $(GREEN)ollama/orca-mini$(NC)  (3B)   - ⚡ Fast"
	@echo "  Judge:           $(GREEN)ollama/mistral$(NC)    (7B)   - ⚡⚡ Balanced"
	@echo "  Auditor:         $(GREEN)ollama/phi$(NC)        (2.7B) - ⚡ Very Fast"
	@echo "  $(BLUE)Edit .env: Mix phi, mistral, orca-mini$(NC)"
	@echo ""
	@echo "$(YELLOW)Configuration 3: BEST (Slow but most accurate)$(NC)"
	@echo "  Investigator:    $(GREEN)ollama/neural-chat$(NC) (7B)   - ⚡⚡ Balanced"
	@echo "  Scope Reviewer:  $(GREEN)ollama/mixtral$(NC)    (26GB) - ⚡ Slow (Best reasoning)"
	@echo "  Judge:           $(GREEN)ollama/neural-chat$(NC) (7B)   - ⚡⚡ Balanced"
	@echo "  Auditor:         $(GREEN)ollama/mistral$(NC)    (7B)   - ⚡⚡ Balanced"
	@echo "  $(BLUE)Note: Requires 16GB+ RAM, ~40s per inference$(NC)"
	@echo ""
	@echo "$(BLUE)To switch models:$(NC)"
	@echo "  1. Edit .env file:"
	@echo "     LLM_INVESTIGATOR_MODEL=ollama/mistral"
	@echo "     LLM_SCOPE_REVIEWER_MODEL=ollama/orca-mini"
	@echo "     etc."
	@echo ""
	@echo "  2. Reload browser ($(GREEN)F5$(NC)) - Streamlit will pick up new models"
	@echo ""
	@echo "  3. Select models from sidebar in Recall Dashboard"
	@echo ""
	@echo "$(YELLOW)Model sizes (download if needed):$(NC)"
	@echo "  phi:           1.6GB  - Smallest, fastest"
	@echo "  orca-mini:     2.0GB  - Small, good reasoning"
	@echo "  mistral:       5.0GB  - Medium, good balance"
	@echo "  neural-chat:   4.1GB  - Medium, conversational"
	@echo "  mixtral:      26.0GB  - Large, best reasoning"
	@echo ""
	@echo "$(BLUE)Download models with:$(NC)"
	@echo "  ollama pull phi"
	@echo "  ollama pull orca-mini"
	@echo "  ollama pull mistral"
	@echo "  ollama pull neural-chat"
	@echo "  ollama pull mixtral"
	@echo ""
