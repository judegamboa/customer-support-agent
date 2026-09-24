"""Receiver agent: handles handoffs escalated by the primary agent."""

import anthropic

from config import API_KEY, MODEL


def build_receiver_prompt(summary: dict) -> str:
    findings_xml = "\n".join(
        "  <finding>\n"
        f"    <source>{finding['source']}</source>\n"
        f"    <content>{finding['content']}</content>\n"
        "  </finding>"
        for finding in summary["findings"]
    )
    decisions_xml = "\n".join(
        f"  <decision>{decision}</decision>" for decision in summary["decisions_made"]
    )
    questions_xml = "\n".join(
        f"  <question>{question}</question>" for question in summary["open_questions"]
    )

    return (
        "<handoff>\n"
        f"  <reason>{summary['reason']}</reason>\n"
        "  <findings>\n"
        f"{findings_xml}\n"
        "  </findings>\n"
        "  <decisions_made>\n"
        f"{decisions_xml}\n"
        "  </decisions_made>\n"
        "  <open_questions>\n"
        f"{questions_xml}\n"
        "  </open_questions>\n"
        "</handoff>"
    )


def run_receiver_agent(summary: dict) -> str:
    client = anthropic.Anthropic(api_key=API_KEY)
    prompt = build_receiver_prompt(summary)
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=(
            "You are a support specialist receiving a handoff from another agent that could not "
            "finish a customer request. You will only see the structured summary below -- no other "
            "context. Use the <finding> elements (each with <source> and <content>) plus "
            "<decisions_made> and <open_questions> to give the best possible final answer or next "
            "step for the customer."
        ),
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text")
