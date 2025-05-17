from llm.llm_client import LLMClient
from llm.anthropic_client import AnthropicClient


MAX_TOKENS = 1000
SCRIBE_PROMPT_TEMPLATE = """
You are a seasoned scribe. You are in a room with some experts who are working together to address a problem, each with their own unique perspective and expertise.
Your task is to take their proposals and generate a single draft proposal that addresses the problem.
If the experts agree on something, note it in your draft. If they disagree, pick the most compelling argument but also jot down the points of contention.

Following are your traits as a scribe:
- objective and impartial
- concise and focused
- pragmatic
- focused on steering the dogfight towards an optimal solution
- meticulous, detail-oriented and never missing any detail 


Problem Statement: {problem}
Proposals: 
###
{proposals_str}

Your Draft Proposal:
"""


class Scribe:
    def __init__(self, debug_mode: bool = False):
        self.llm_client: LLMClient = AnthropicClient()
        self.draft: str = ""
        self.debug_mode = debug_mode
    
    def generate_draft(self, problem: str, proposals: list[str]) -> str:
        proposals_str = '\n###\n'.join(proposals)
        prompt = SCRIBE_PROMPT_TEMPLATE.format(problem=problem, proposals_str=proposals_str)
        draft = self.llm_client.generate_text(prompt, max_tokens=MAX_TOKENS)
        self.draft = draft
        if self.debug_mode:
            print(f"Scribe generated draft proposal.")
        return draft


if __name__ == '__main__':
    scribe = Scribe(debug_mode=True)
    problem = "We want to build a memory storage system across all MCPs. Each MCP is a separate cloud project. Should we host the memory in a central project or per MCP?"
    proposals = [
        "We should host the memory in a central project.",
        "We should host the memory in each MCP.",
    ]
    draft = scribe.generate_draft(problem, proposals)
    print(draft)
