"""Mini Python agent: customer-support desk assistant with tool use via the Anthropic SDK.

The agent loop keeps calling Claude and running any requested tools until
Claude responds with a stop_reason other than "tool_use".
"""

from agent import run_agent

QUESTION = "Update my shipping address, refund $60 for order 1042, and tell me when my next delivery arrives."


def main() -> None:
    print(f"Question: {QUESTION}\n")
    answer = run_agent(QUESTION)
    print(f"Answer: {answer}")


if __name__ == "__main__":
    main()
