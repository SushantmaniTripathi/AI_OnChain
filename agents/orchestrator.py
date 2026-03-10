"""
orchestrator.py — Coordinates all agents and assembles the final report.
Run order:
  1. Whale Tracker    (parallel-safe)
  2. Token Trending   (parallel-safe)
  3. Gas Analyzer     (parallel-safe)
  4. Report Synth     (depends on 1-3 outputs)
"""
import logging
import concurrent.futures
from datetime import datetime
from agents import whale_tracker, token_trending, gas_analyzer, report_synthesizer
from utils.database import save_report, init_db
from utils.mock_data import mock_whale_data, mock_token_data, mock_gas_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_all_agents(progress_callback=None) -> dict:
    """
    Run all data collection agents in parallel, then synthesize.
    progress_callback(message: str) is called with status updates for the UI.
    """
    init_db()

    def update(msg):
        logger.info(msg)
        if progress_callback:
            progress_callback(msg)

    update("Starting data collection agents...")

    # --- Run data agents in parallel ---------------------------------------------
    whale_data  = None
    token_data  = None
    gas_data    = None
    errors      = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(whale_tracker.run):   "whale",
            executor.submit(token_trending.run):  "token",
            executor.submit(gas_analyzer.run):    "gas",
        }
        for future in concurrent.futures.as_completed(futures):
            agent_name = futures[future]
            try:
                result = future.result(timeout=60)
                if agent_name == "whale": whale_data = result
                if agent_name == "token": token_data = result
                if agent_name == "gas":   gas_data   = result
                update(f"✓ {agent_name.capitalize()} agent completed")
            except Exception as e:
                errors[agent_name] = str(e)
                update(f"✗ {agent_name.capitalize()} agent failed: {e}")

    # --- Fallback to mock data for any failed agent ------------------------------
    from utils.mock_data import mock_whale_data, mock_token_data, mock_gas_data
    if whale_data is None: whale_data = mock_whale_data()
    if token_data is None: token_data = mock_token_data()
    if gas_data   is None: gas_data   = mock_gas_data()

    # --- Synthesize report -------------------------------------------------------
    update("Generating AI report summary...")
    report = report_synthesizer.run(whale_data, token_data, gas_data)

    # --- Persist to database -----------------------------------------------------
    save_report(
        whale_data, token_data, gas_data,
        report["summary"], report["risk_score"]
    )

    update("✅ Report complete!")

    return {
        "whale":       whale_data,
        "tokens":      token_data,
        "gas":         gas_data,
        "report":      report,
        "errors":      errors,
        "generated_at": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    # CLI usage: python orchestrator.py
    result = run_all_agents()
    print("\n" + "—" * 60)
    print(result["report"]["summary"])
    print("—" * 60)
    print(f"Risk Score: {result['report']['risk_score']}/100")

