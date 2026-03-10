import json
import logging
from datetime import datetime
from config import OPENAI_API_KEY, LLM_MODEL, LLM_MAX_TOKENS, LLM_TEMPERATURE
from utils.mock_data import mock_report_summary
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

logger = logging.getLogger(__name__)

def run(whale_data: dict, token_data: dict, gas_data: dict, report_detail: str = "Standard", target_wallet: str = "") -> dict:
    """
    Main entry point for synthesizing all agent data into a report.
    Uses OpenAI API if key is available, otherwise falls back to mock summary.
    """
    if not OPENAI_API_KEY:
        logger.info("OPENAI_API_KEY not set, using mock report summary.")
        return {
            "summary": mock_report_summary(whale_data, token_data, gas_data),
            "risk_score": 45,
            "date": datetime.now().strftime("%Y-%m-%d")
        }

    try:
        llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS
        )

        parser = JsonOutputParser()

        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are an expert on-chain analyst. Your task is to synthesize the provided blockchain data into a concise, insightful, and human-readable report.
            Highlight key findings, potential risks, and notable trends.
            The report should be structured as a JSON object with two keys: "summary" (string) and "risk_score" (integer between 0 and 100).
            Risk score 0 means no risk, 100 means extremely high risk.
            
            User requested report detail level: {report_detail}.
            {f"Focus the analysis on the target wallet: {target_wallet}." if target_wallet else ""}
            """),
            ("user", f"""
            Here is the latest on-chain data:
            Whale Movements: {json.dumps(whale_data, indent=2)}
            Token Trending: {json.dumps(token_data, indent=2)}
            Gas Analysis: {json.dumps(gas_data, indent=2)}

            Please provide a summary and a risk score.
            """)
        ])

        chain = prompt | llm | parser
        response = chain.invoke({
            "whale_data": whale_data,
            "token_data": token_data,
            "gas_data": gas_data
        })

        summary = response.get("summary", "Could not generate summary.")
        risk_score = response.get("risk_score", 50)

        logger.info("Generated report summary using OpenAI API.")
        return {
            "summary": summary,
            "risk_score": risk_score,
            "date": datetime.now().strftime("%Y-%m-%d")
        }

    except Exception as e:
        logger.error(f"Error generating report with OpenAI API: {e}", exc_info=True)
        logger.info("Falling back to mock report summary.")
        return {
            "summary": mock_report_summary(whale_data, token_data, gas_data),
            "risk_score": 45,
            "date": datetime.now().strftime("%Y-%m-%d")
        }