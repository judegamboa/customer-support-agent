"""Mini Python agent: customer-support desk assistant with tool use via the Anthropic SDK.

The agent loop keeps calling Claude and running any requested tools until
Claude responds with a stop_reason other than "tool_use".
"""

import json
import logging
import os

import anthropic
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# --- Config ------------------------------------------------------------------

API_KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
QUESTION = "Find the order for customer 1042 and tell me its status."


# --- Tools (return fake data) -------------------------------------------------

def lookup_order(order_id: str) -> dict:
    return {
        "order_id": order_id,
        "status": "delivered",
        "item": "Wireless Mouse",
        "amount": 29.99,
        "customer_id": "cust_42",
    }


def lookup_orders_by_customer(customer_id: str) -> dict:
    return {
        "customer_id": customer_id,
        "orders": [
            {
                "order_id": "1002",
                "status": "delivered",
                "item": "Wireless Mouse",
                "amount": 29.99,
            }
        ],
    }


def lookup_customer(customer_id: str) -> dict:
    return {
        "customer_id": customer_id,
        "name": "Jamie Rivera",
        "email": "jamie.rivera@example.com",
        "since": "2022-03-15",
    }


def issue_refund(order_id: str, amount: float) -> dict:
    return {
        "refund_id": "ref_7788",
        "order_id": order_id,
        "amount": amount,
        "status": "approved",
    }


# --- Tool schemas --------------------------------------------------------------

TOOLS = [
    {
        "name": "lookup_order",
        "description": (
            "Look up a single order's status, item, amount, and owning customer ID by its order ID. "
            "Use this when the customer asks about an order's status, contents, or price and you "
            "already have the order_id, or when you need the customer_id to then call "
            "lookup_customer. Do not use this to find which order(s) belong to a customer_id (use "
            "lookup_orders_by_customer) or guess an order_id from a customer_id. Do not use this to "
            "look up a customer directly (use lookup_customer) or to process a refund (use "
            "issue_refund)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID to look up, e.g. '1002'. Required.",
                },
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "lookup_orders_by_customer",
        "description": (
            "Find the order(s) placed by a given customer, by their customer ID, returning each "
            "order's ID, status, item, and amount. Use this when the customer asks about 'my orders' "
            "or you are given a customer_id and need to find the associated order(s), instead of "
            "guessing an order_id. Do not use this to look up an order you already have the order_id "
            "for (use lookup_order) or to look up customer account details (use lookup_customer)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The customer ID whose orders to find, e.g. '1042' or 'cust_42'. Required.",
                },
            },
            "required": ["customer_id"],
        },
    },
    {
        "name": "lookup_customer",
        "description": (
            "Look up a customer's name, email, and signup date by their customer ID. Use this when the "
            "customer asks about their own account details, or after lookup_order gives you a "
            "customer_id and the user wants to know who the order belongs to. Do not use this to look "
            "up order details (use lookup_order) or to issue a refund (use issue_refund)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The customer ID to look up, e.g. 'cust_42'. Required.",
                },
            },
            "required": ["customer_id"],
        },
    },
    {
        "name": "issue_refund",
        "description": (
            "Issue a refund for a specific order and amount, returning a refund confirmation with its "
            "own refund_id. Only use this after confirming with the customer which order and amount to "
            "refund; do not call it just to check refund eligibility (use lookup_order for that first). "
            "The amount must be a positive number and should not exceed the order's original amount."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID to refund, e.g. '1002'. Required.",
                },
                "amount": {
                    "type": "number",
                    "description": "The dollar amount to refund, e.g. 29.99. Must be positive. Required.",
                },
            },
            "required": ["order_id", "amount"],
        },
    },
]

TOOL_FUNCTIONS = {
    "lookup_order": lookup_order,
    "lookup_orders_by_customer": lookup_orders_by_customer,
    "lookup_customer": lookup_customer,
    "issue_refund": issue_refund,
}


# --- Agent loop ----------------------------------------------------------------

MAX_ITERATIONS = 50


def run_agent(question: str) -> str:
    client = anthropic.Anthropic(api_key=API_KEY)
    messages = [{"role": "user", "content": question}]

    for iteration in range(1, MAX_ITERATIONS + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
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


# --- Entry point -----------------------------------------------------------------

def main() -> None:
    print(f"Question: {QUESTION}\n")
    answer = run_agent(QUESTION)
    print(f"Answer: {answer}")


if __name__ == "__main__":
    main()
