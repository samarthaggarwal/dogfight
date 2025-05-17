import re
from typing import Tuple, Optional
from llm.anthropic_client import AnthropicClient


ACTOR_TRAITS = """
- seasoned expert with deep knowledge of the subject matter
- opinionated and prefers proven technologies
- NOT at all gullible and strongly opposes a proposal if you don't agree
- open to changing your mind when presented with a strong proof/argument of a better alternative
- concise and focused
- technical and data-driven
- pragmatic
- focused on delivering results
"""
MAX_TOKENS = 1000


VOTE_PROMPT_TEMPLATE_STR = """
You are {name_param}, a seasoned expert in {expertise_param} with the following traits:
{actor_traits_param}

You are asked to review and vote on a proposal to solve a problem. Your goal is to help refine it towards an optimal solution.

<problem_statement>
{problem_param}
</problem_statement>

<draft_proposal>
{draft_proposal_param}
</draft_proposal>

Output your binary vote and a concise reason for it in the following format. Do NOT include any additional text.
If you disagree, explain why and suggest specific improvements or which alternative you'd prefer.
<vote>
{{your vote - AGREE or DISAGREE}}
</vote>
<reason>
{{your reason - concise and focused}}
</reason>
"""

class Actor:
    def __init__(self, name: str, expertise: str, debug_mode: bool = False):
        """
        Args:
            name: The name of the actor (e.g., 'Infra Engineer').
            expertise: A description of the actor's persona and expertise
                         (e.g., 'Seasoned infrastructure engineer focused on scalability and cost-efficiency. Opinionated and prefers proven technologies.')
        """
        self.name = name
        self.expertise = expertise
        self.llm_client = AnthropicClient()
        self.current_proposal: Optional[str] = None
        self.debug_mode = debug_mode

    def generate_proposal(self, problem: str, draft: Optional[str] = None) -> str:
        """
        Generates an initial proposal for the given problem statement based on the actor's expertise.

        Args:
            problem: The problem to generate a proposal for.
            draft: An optional draft proposal that the actor should consider.

        Returns:
            A string containing the actor's proposal.
        """
        prompt = (
            f"You are {self.name}, a seasoned expert in {self.expertise} with the following traits:\n{ACTOR_TRAITS}\n\n"
            f"Given the following problem statement. Think carefully about it and generate a detailed and specific proposal to address it. Consider your unique perspective and expertise.\n"
            f"Problem Statement: {problem}\n\n"
            f"Your Proposal:"
        )

        proposal = self.llm_client.generate_text(prompt, max_tokens=MAX_TOKENS)
        self.current_proposal = proposal
        if self.debug_mode:
            print(f"Actor {self.name} generated proposal.")
        return proposal

    def vote_on_draft(
        self, 
        problem: str,
        draft_proposal: str,
    ) -> Tuple[bool, str]:
        """
        Reviews a draft proposal and casts a vote (agree/disagree) with a reason.

        Args:
            problem: The problem statement.
            draft_proposal: The consolidated draft proposal from the Scribe.

        Returns:
            A tuple containing:
                - bool: True if the actor agrees with the draft, False otherwise.
                - str: A reason for the vote, especially important for disagreements.
        """
        prompt = VOTE_PROMPT_TEMPLATE_STR.format(
            name_param=self.name,
            expertise_param=self.expertise,
            actor_traits_param=ACTOR_TRAITS,
            problem_param=problem,
            draft_proposal_param=draft_proposal
        )
        response = self.llm_client.generate_text(prompt, max_tokens=MAX_TOKENS)
        vote_decision, reason = self.parse_vote(response)

        if self.debug_mode:
            print(f"### Actor: {self.name}:\nVote: {'Agree' if vote_decision else 'Disagree'}\nReason: {reason}\n\n")
        return vote_decision, reason

    def parse_vote(self, response_text: str) -> Tuple[bool, str]:
        try:
            vote_match = re.search(r"<vote>\s*(AGREE|DISAGREE)\s*</vote>", response_text, re.IGNORECASE)
            reason_match = re.search(r"<reason>\s*(.*?)\s*</reason>", response_text, re.DOTALL | re.IGNORECASE)

            if vote_match and reason_match:
                vote_str = vote_match.group(1).upper()
                reason_str = reason_match.group(1).strip()
                
                vote_decision = (vote_str == "AGREE")
                return vote_decision, reason_str
            else:
                if self.debug_mode:
                    print(f"Warning: Could not parse vote or reason tags from Actor {self.name}. Defaulting to DISAGREE. Response: {response_text}")
                return False, response_text
        except Exception as e:
            if self.debug_mode:
                print(f"Error during parsing vote for Actor {self.name}: {e}. Defaulting to DISAGREE. Response: {response_text}")
            return False, response_text

    def __repr__(self):
        return f"Actor(name='{self.name}', expertise='{self.expertise}')"


if __name__ == '__main__':
    security_eng = Actor("Security Engineer", "security and compliance", debug_mode=True)
    print(security_eng)
    problem = "We want to build metrics logger to collect performance metrics from all our customers. Each customer has their own cloud project. Should we host the metrics logger in a central project or per customer?"
    proposal = security_eng.generate_proposal(problem)
    print(proposal)
    vote, reason = security_eng.vote_on_draft(problem, proposal)
    print(vote)
    print(reason)
