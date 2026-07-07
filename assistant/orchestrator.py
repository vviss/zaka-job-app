import re

from assistant import cache
from assistant.agents import planner, researcher, writer


def _parse_steps(plan):
    return [step.strip() for step in re.findall(r"\d+\.\s*(.+)", plan)]


def answer_question(team, question):
    cached = cache.get(team, question)
    if cached is not None:
        return cached

    plan = planner.make_plan(question)
    steps = _parse_steps(plan)
    research_query = steps[0] if steps else question

    findings = researcher.research(team, research_query)
    answer = writer.write(question, findings["notes"], findings["sources"])

    cache.put(team, question, answer)
    return answer
