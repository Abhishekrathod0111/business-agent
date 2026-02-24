import memory
from agents.research_agent import research
from agents.analysis_agent import analyze_company
from agents.decision_agent import make_decision


def run_agents(company):

    past = memory.search(company)

    if past:
        return {
            "result": past,
            "source": "memory"
        }


    # Step 1 Research
    raw_data = research(company)

    # Step 2 Analysis
    business_analysis = analyze_company(company, raw_data)

    # Step 3 Decision ← NEW
    decision = make_decision(company, business_analysis)


    final_result = {
        "company": company,
        "analysis": business_analysis,
        "decision": decision
    }


    # import json
    memory.store(company, final_result)

    return {
        "result": final_result,
        "source": "multi-agent"
    }