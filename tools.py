"""Tools (fake data) and their schemas for the customer-support agent."""

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
        "name": "escalate",
        "description": (
            "Hand off this request to a human-support specialist when you cannot finish it yourself "
            "(e.g. missing data, ambiguous request, conflicting tool results, or a policy decision you "
            "aren't able to make). Call this instead of guessing or giving an incomplete answer. "
            "Include every finding you've gathered so far, tagged with where it came from, plus any "
            "decisions you already made and any questions still open."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "Why you cannot complete this request yourself. Required.",
                },
                "findings": {
                    "type": "array",
                    "description": "Every relevant fact gathered so far, each attributed to its source.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The finding itself.",
                            },
                            "source": {
                                "type": "string",
                                "description": (
                                    "The tool call or record this finding came from, e.g. "
                                    "'lookup_order(order_id=1002)'."
                                ),
                            },
                        },
                        "required": ["content", "source"],
                    },
                },
                "decisions_made": {
                    "type": "array",
                    "description": "Decisions already made or ruled out while working the request.",
                    "items": {"type": "string"},
                },
                "open_questions": {
                    "type": "array",
                    "description": "Questions that remain unresolved and need human/receiver judgment.",
                    "items": {"type": "string"},
                },
            },
            "required": ["reason", "findings", "decisions_made", "open_questions"],
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
