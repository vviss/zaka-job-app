import re

from assistant import cache
from assistant.agents import planner, researcher, writer


def _parse_steps(plan):
    return [step.strip() for step in re.findall(r"\d+\.\s*(.+)", plan)]


def answer_question(team, question):
    cached = cache.get(team, question)
    if cached is not None:
        return cached

    # Review: the logic was only giving the first step (steps[0]) as research_query
    # which not only is lacking the full picture, 
    # but also sometimes contains zero context about the original question
    plan = planner.make_plan(question)
    steps = _parse_steps(plan)
    findings = researcher.research(team, question, steps)
    answer = writer.write(question, findings["notes"], findings["sources"])

    cache.put(team, question, answer)
    return answer
