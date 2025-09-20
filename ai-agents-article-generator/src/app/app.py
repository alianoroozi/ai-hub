from loguru import logger
from services.agent import build_agent


def main():
    try:
        agent = build_agent()
        state = {
            "topic": "Building AI Agents with langgraph",
        }
        result = agent.invoke(state)

        if "article" not in result:
            raise ValueError("Article not generated")

        logger.info(result["article"])

    except Exception as e:
        logger.exception(f"Error running agent: {e}")
        raise


if __name__ == "__main__":
    main()
