from typing import Dict

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool
from langchain_tavily import TavilySearch
from langgraph.graph import END, START, StateGraph
from loguru import logger

from services.config import MAX_TOOL_CALLS
from services.models import State
from services.prompts import Prompts


def make_llm():
    # return init_chat_model("openai:gpt-5-mini", temperature=0)
    return init_chat_model("ollama:qwen3:8b")


def make_search_tool() -> Tool:
    tavily = TavilySearch(max_results=1, topic="general")

    def _run(query: str) -> str:
        return tavily.invoke({"query": query})

    return Tool.from_function(
        name="web_search",
        description="General web search. Input: a 'query' string. Returns synthesized results.",
        func=_run,  # expects a single str; model will pass {"query": "..."}
    )


def make_prompts():
    research_prompt = ChatPromptTemplate(
        [
            ("system", Prompts.RESEARCH_SYSTEM_PROMPT),
            ("user", Prompts.RESEARCH_USER_PROMPT),
        ]
    )

    write_prompt = ChatPromptTemplate(
        [("system", Prompts.WRITE_SYSTEM_PROMPT), ("user", Prompts.WRITE_USER_PROMPT)]
    )
    return research_prompt, write_prompt


def research_task(
    state: State, llm: BaseChatModel, prompt: ChatPromptTemplate, tools: list[Tool]
):
    if not state.get("topic"):
        raise ValueError("Topic is missing or empty in state")

    messages = state.get("messages", [])

    # Inject the research prompt only once (first pass)
    if not messages:
        prompt_msg = prompt.invoke({"topic": state["topic"]})
        messages = messages + prompt_msg.to_messages()

    logger.info(
        f"[research_task] Running research task. Existing messages={len(messages)} tool_call_count={state.get('tool_call_count', 0)}"
    )

    llm_with_search = llm.bind_tools(tools)
    msg = llm_with_search.invoke(messages)
    messages.append(msg)

    if getattr(msg, "tool_calls", None):
        logger.info(
            f"[research_task] LLM produced {len(msg.tool_calls)} tool call(s): "
            + ", ".join(f"{c['name']}" for c in msg.tool_calls)
        )
    else:
        logger.info("[research_task] No tool calls produced; Moving to write phase.")

    return {
        "research_brief": msg.content,
        "messages": messages,
    }


def tool_task(state: dict, tools_by_name: Dict[str, Tool]):
    result = []
    logger.info(
        f"[tool_task] Executing tool calls. tool_call_count_so_far={state.get('tool_call_count', 0)}"
    )
    for tool_call in state["messages"][-1].tool_calls:
        name = tool_call["name"]
        args = tool_call["args"]
        logger.info(f"[tool_task] Calling tool '{name}' with args={args}")
        tool = tools_by_name[name]
        try:
            observation = tool.invoke(args)
            logger.info(
                f"[tool_task] Tool '{name}' call succeeded. Observation length={len(str(observation))}"
            )
        except Exception as e:
            logger.exception(f"[tool_task] Tool '{name}' call failed: {e}")
            raise
        result.append(
            ToolMessage(content=str(observation), tool_call_id=tool_call["id"])
        )
    messages = state["messages"]
    messages += result
    logger.info(
        f"[tool_task] Added {len(result)} tool observation message(s). Total messages={len(messages)}"
    )
    return {
        "messages": messages,
        "tool_call_count": state.get("tool_call_count", 0) + 1,
    }


def write_task(state: State, llm, prompt: ChatPromptTemplate):
    if "research_brief" not in state or not state["research_brief"]:
        raise ValueError("Research brief is missing or empty in state")

    logger.info("[write_task] Generating article from research_brief.")
    prompt = prompt.invoke({"research_brief": state["research_brief"]})
    msg = llm.invoke(prompt)
    logger.info("[write_task] Article generation complete.")
    return {"article": msg.content}


def build_agent():
    llm = make_llm()

    search_tool = make_search_tool()
    tools = [search_tool]
    tools_by_name = {tool.name: tool for tool in tools}

    research_prompt, write_prompt = make_prompts()

    def _research(state: State):
        return research_task(state=state, llm=llm, prompt=research_prompt, tools=tools)

    def _tool(state: State):
        return tool_task(state=state, tools_by_name=tools_by_name)

    def _should_continue(state: State):
        """
        Decide if we should continue the loop or stop based upon whether the LLM made a tool call
        """
        if state.get("tool_call_count", 0) >= MAX_TOOL_CALLS:
            logger.warning("Reached max tool call count, ending workflow.")
            return END

        messages = state.get("messages", [])
        if not messages:
            return END
        last_message = messages[-1]
        # If the LLM makes a tool call, then perform an action
        return "tool" if getattr(last_message, "tool_calls", None) else "write"

    def _write(state: State):
        return write_task(state=state, llm=llm, prompt=write_prompt)

    workflow = StateGraph(State)
    workflow.add_node("research", _research)
    workflow.add_node("tool", _tool)
    workflow.add_node("write", _write)

    workflow.add_edge(START, "research")
    workflow.add_conditional_edges(
        "research",
        _should_continue,
        ["tool", "write", END],
    )
    workflow.add_edge("tool", "research")
    workflow.add_edge("write", END)

    return workflow.compile()
