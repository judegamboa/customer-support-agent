# customer-support-agent

Mini Python agent: a customer-support desk assistant with tool use via the Anthropic SDK. The primary agent keeps calling Claude and running any requested tools until Claude finishes, or escalates the request to a second "receiver" agent when it can't complete it itself.

## Project layout

- `config.py` — loads environment variables and configures logging
- `tools.py` — fake data tools (`lookup_order`, `lookup_orders_by_customer`, `lookup_customer`, `issue_refund`) and their schemas, including `escalate`
- `agent.py` — the primary agent loop
- `receiver.py` — the receiver agent that handles escalated handoffs
- `main.py` — entry point; edit `QUESTION` here to change what's asked

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in this directory (copy `.env.example`) and set your API key:

   ```bash
   cp .env.example .env
   ```

   Then edit `.env`:

   ```
   ANTHROPIC_API_KEY=your-api-key-here
   ANTHROPIC_MODEL=claude-sonnet-5
   ```

   `ANTHROPIC_MODEL` is optional and defaults to `claude-sonnet-5` if not set.

## Running

```bash
python3 main.py
```

This prints the question (from `QUESTION` in `main.py`), the agent's tool-call trace (`stop_reason` and tool names per pass), and the final answer. If the agent calls `escalate`, you'll also see the handoff summary and the receiver agent's answer.
