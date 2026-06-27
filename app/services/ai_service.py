import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from app.models import InterestedService, Lead, LeadStatus


@dataclass
class QueryAnalysis:
    category: str
    intent: str
    summary: str
    suggested_response: str
    lead_score: int
    priority: str
    ai_provider: str = "rule_based"


SERVICE_KEYWORDS = {
    "AI Chatbot": ["ai", "chatbot", "bot", "automation", "assistant", "llm"],
    "Website Development": ["website", "web", "landing page", "seo", "wordpress"],
    "Mobile App Development": ["mobile", "app", "android", "ios", "application"],
    "Data Analytics": ["data", "analytics", "dashboard", "report", "bi", "insights"],
}

INTENT_KEYWORDS = {
    "Pricing Inquiry": ["price", "pricing", "cost", "budget", "quote", "estimate"],
    "Meeting Request": ["meeting", "demo", "call", "consultation", "schedule"],
    "Purchase Intent": ["need", "want", "build", "develop", "looking for", "require"],
    "Support Request": ["issue", "problem", "error", "not working", "support"],
}


def analyze_query(
    description: str,
    customer_name: str | None = None,
    service: InterestedService | None = None,
) -> QueryAnalysis:
    """Analyze a customer query using configured LLM provider or a local fallback."""
    provider = os.getenv("AI_PROVIDER", "rule_based").lower()
    llm_analysis = _analyze_with_llm(provider, description, customer_name, service)
    if llm_analysis:
        return llm_analysis

    return _rule_based_analysis(description, customer_name, service)


def update_lead_scoring(lead: Lead, query_descriptions: list[str] | None = None) -> None:
    """Update lead score and priority from lead metadata, status, meeting, and query text."""
    query_descriptions = query_descriptions or []
    combined_query_text = " ".join(query_descriptions)
    analysis = _rule_based_analysis(
        combined_query_text or lead.interested_service.value,
        lead.name,
        lead.interested_service,
    )

    score = analysis.lead_score
    score += {
        LeadStatus.NEW: 5,
        LeadStatus.CONTACTED: 15,
        LeadStatus.MEETING_SCHEDULED: 30,
        LeadStatus.PROPOSAL_SENT: 45,
        LeadStatus.CONVERTED: 100,
        LeadStatus.CLOSED: 0,
    }.get(lead.status, 0)

    if lead.meeting_date and lead.meeting_time:
        score += 10

    lead.lead_score = min(score, 100)
    lead.priority = _priority_from_score(lead.lead_score)


def _rule_based_analysis(
    description: str,
    customer_name: str | None = None,
    service: InterestedService | None = None,
) -> QueryAnalysis:
    text = description.lower()
    category = service.value if service else _detect_category(text)
    intent = _detect_intent(text)
    summary = _summarize(description)
    score = _score_query(text, category, intent)
    priority = _priority_from_score(score)
    suggested_response = _suggest_response(customer_name, category, intent)

    return QueryAnalysis(
        category=category,
        intent=intent,
        summary=summary,
        suggested_response=suggested_response,
        lead_score=score,
        priority=priority,
    )


def _detect_category(text: str) -> str:
    for category, keywords in SERVICE_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category
    return "General Inquiry"


def _detect_intent(text: str) -> str:
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return intent
    return "Information Request"


def _summarize(description: str) -> str:
    clean_text = " ".join(description.split())
    sentences = re.split(r"(?<=[.!?])\s+", clean_text)
    first_sentence = sentences[0] if sentences else clean_text
    return first_sentence[:180] + ("..." if len(first_sentence) > 180 else "")


def _score_query(text: str, category: str, intent: str) -> int:
    score = 20
    if category != "General Inquiry":
        score += 15
    if intent in {"Purchase Intent", "Pricing Inquiry", "Meeting Request"}:
        score += 25
    if any(word in text for word in ["urgent", "asap", "immediately", "this week"]):
        score += 20
    if any(word in text for word in ["business", "company", "enterprise", "clients"]):
        score += 10
    if any(word in text for word in ["demo", "meeting", "proposal", "quote"]):
        score += 10
    return min(score, 100)


def _priority_from_score(score: int) -> str:
    if score >= 75:
        return "Hot"
    if score >= 45:
        return "Warm"
    return "Cold"


def _suggest_response(customer_name: str | None, category: str, intent: str) -> str:
    greeting = f"Hi {customer_name}," if customer_name else "Hi,"
    if intent == "Pricing Inquiry":
        return (
            f"{greeting} thanks for your interest in {category}. We can share a tailored "
            "proposal after understanding your requirements, expected timeline, and budget range."
        )
    if intent == "Meeting Request":
        return (
            f"{greeting} thanks for reaching out. We can schedule a discovery call to discuss "
            f"your {category} requirement and next steps."
        )
    if intent == "Purchase Intent":
        return (
            f"{greeting} thanks for sharing your requirement. NexAltis can help with {category}. "
            "Could you share your goals, timeline, and any existing systems we should integrate with?"
        )
    return (
        f"{greeting} thanks for contacting NexAltis. We received your query and will review the "
        "details to recommend the best next step."
    )


def _analyze_with_llm(
    provider: str,
    description: str,
    customer_name: str | None,
    service: InterestedService | None,
) -> QueryAnalysis | None:
    if provider == "ollama":
        return _analyze_with_ollama(description, customer_name, service)
    if provider == "gemini":
        return _analyze_with_gemini(description, customer_name, service)
    if provider == "openai":
        return _analyze_with_openai(description, customer_name, service)
    return None


def _analysis_prompt(
    description: str,
    customer_name: str | None,
    service: InterestedService | None,
) -> str:
    return (
        "Analyze this sales lead query and return ONLY JSON with keys: "
        "category, intent, summary, suggested_response, lead_score, priority. "
        "priority must be Cold, Warm, or Hot. lead_score must be 0-100.\n\n"
        f"Customer: {customer_name or 'Unknown'}\n"
        f"Service: {service.value if service else 'Unknown'}\n"
        f"Query: {description}"
    )


def _parse_llm_response(data: Any, provider: str) -> QueryAnalysis | None:
    try:
        if isinstance(data, str):
            payload = json.loads(_extract_json(data))
        else:
            payload = data

        score = int(payload.get("lead_score", 0))
        return QueryAnalysis(
            category=str(payload.get("category", "General Inquiry")),
            intent=str(payload.get("intent", "Information Request")),
            summary=str(payload.get("summary", ""))[:500],
            suggested_response=str(payload.get("suggested_response", ""))[:1000],
            lead_score=max(0, min(score, 100)),
            priority=str(payload.get("priority") or _priority_from_score(score)),
            ai_provider=provider,
        )
    except (TypeError, ValueError, json.JSONDecodeError):
        return None


def _extract_json(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text


def _post_json(url: str, payload: dict[str, Any], headers: dict[str, str] | None = None) -> Any:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers or {"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _analyze_with_ollama(
    description: str,
    customer_name: str | None,
    service: InterestedService | None,
) -> QueryAnalysis | None:
    try:
        url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        model = os.getenv("OLLAMA_MODEL", "llama3.2")
        data = _post_json(
            url,
            {
                "model": model,
                "prompt": _analysis_prompt(description, customer_name, service),
                "stream": False,
                "format": "json",
            },
        )
        return _parse_llm_response(data.get("response", ""), "ollama")
    except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError):
        return None


def _analyze_with_gemini(
    description: str,
    customer_name: str | None,
    service: InterestedService | None,
) -> QueryAnalysis | None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={api_key}"
        )
        data = _post_json(
            url,
            {
                "contents": [
                    {
                        "parts": [
                            {"text": _analysis_prompt(description, customer_name, service)}
                        ]
                    }
                ]
            },
        )
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return _parse_llm_response(text, "gemini")
    except (urllib.error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError):
        return None


def _analyze_with_openai(
    description: str,
    customer_name: str | None,
    service: InterestedService | None,
) -> QueryAnalysis | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        data = _post_json(
            "https://api.openai.com/v1/chat/completions",
            {
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "messages": [
                    {
                        "role": "user",
                        "content": _analysis_prompt(description, customer_name, service),
                    }
                ],
                "temperature": 0.2,
            },
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        text = data["choices"][0]["message"]["content"]
        return _parse_llm_response(text, "openai")
    except (urllib.error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError):
        return None
