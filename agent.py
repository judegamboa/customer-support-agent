"""Primary agent loop: keeps calling Claude and running any requested tools
until Claude responds with a stop_reason other than "tool_use".
"""

import json
import logging

import anthropic

from config import API_KEY, MODEL
from receiver import run_receiver_agent
from tools import TOOL_FUNCTIONS, TOOLS

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 50

AGENT_SYSTEM_PROMPT = (
    "You are a customer-support agent. You can only look up orders, look up customers, and issue "
    "refunds using your tools -- you have no other knowledge of company policy and no general "
    "knowledge should be used to answer support questions. If a request needs information or a "
    "decision outside what your tools can provide (e.g. policy questions, ambiguous or out-of-range "
    "requests, or a customer who needs human judgment), call escalate instead of guessing or "
    "answering from general knowledge."
)


def run_agent(question: str) -> str:
    client = anthropic.Anthropic(api_key=API_KEY)
    messages = [{"role": "user", "content": question}]

    for iteration in range(1, MAX_ITERATIONS + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=AGENT_SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        tool_names = [
            block.name for block in response.content if block.type == "tool_use"
        ]
        print(f"stop_reason={response.stop_reason} tools_called={tool_names}")

        text = "".join(
            block.text for block in response.content if block.type == "text"
        )

        if response.stop_reason == "max_tokens":
            print("Warning: response was truncated (stop_reason=max_tokens).")
            return text
        if response.stop_reason == "refusal":
            print("Warning: the model refused to continue (stop_reason=refusal).")
            return text
        if response.stop_reason != "tool_use":
            return text

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            if block.name == "escalate":
                summary = block.input
                print(f"Handing off to receiver agent: reason={summary['reason']!r}")
                print(f"Handoff summary: {json.dumps(summary, indent=2)}")
                receiver_answer = run_receiver_agent(summary)
                print(f"Receiver answer: {receiver_answer}")
                return receiver_answer
            try:
                function = TOOL_FUNCTIONS[block.name]
                result = function(**block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    }
                )
            except Exception as exc:
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(exc),
                        "is_error": True,
                    }
                )

        messages.append({"role": "user", "content": tool_results})

    logger.warning(
        "Agent loop hit the safety-net iteration cap (%d) without finishing.",
        MAX_ITERATIONS,
    )
    return "Sorry, I couldn't complete this request in time."
