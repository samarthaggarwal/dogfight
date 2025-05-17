from typing import Tuple, List, Optional
from llm.anthropic_client import AnthropicClient


GENERAL_TRAITS = """
General Traits:
- seasoned expert with deep knowledge of the subject matter
- opinionated and prefers proven technologies
- not gullible but open to changing their mind when presented with a better alternative
- concise and focused
- technical and data-driven
- pragmatic
- focused on delivering results
"""
MAX_TOKENS = 1000


class Actor:
    def __init__(self, name: str, personality: str):
        """
        Args:
            name: The name of the actor (e.g., 'InfraExpert_1').
            personality: A description of the actor's persona and expertise 
                         (e.g., 'Seasoned infrastructure engineer focused on scalability and cost-efficiency. Opinionated and prefers proven technologies.')
        """
        self.name = name
        self.personality = personality
        self.llm_client = AnthropicClient()
        self.current_proposal: Optional[str] = None

    def generate_proposal(self, problem_statement: str) -> str:
        """
        Generates an initial proposal for the given problem statement based on the actor's personality.

        Args:
            problem_statement: The problem to generate a proposal for.

        Returns:
            A string containing the actor's proposal.
        """
        prompt = (
            f"You are {self.name}, a {self.personality} with the following traits: {GENERAL_TRAITS}.\n"
            f"Given the following problem statement, please generate a detailed and specific proposal to address it. Consider your unique perspective and expertise.\n"
            f"Problem Statement: {problem_statement}\n\n"
            f"Your Proposal:"
        )
        
        proposal = self.llm_client.generate_text(prompt, max_tokens=MAX_TOKENS)
        self.current_proposal = proposal
        print(f"Actor {self.name} generated proposal.")
        return proposal

    def vote_on_draft(
        self, 
        draft_proposal: str,
        alternatives: Optional[List[str]] = None
    ) -> Tuple[bool, str]:
        """
        Reviews a draft proposal (and any alternatives) and casts a vote (agree/disagree) with a rationale.

        Args:
            draft_proposal: The consolidated draft proposal from the Scribe.
            alternatives: Optional list of alternative solutions or points of view highlighted by the Scribe.

        Returns:
            A tuple containing:
                - bool: True if the actor agrees with the draft, False otherwise.
                - str: A rationale for the vote, especially important for disagreements.
        """
        prompt_parts = [
            f"You are {self.name}, a {self.personality}.\n"
            f"You are asked to review and vote on the following draft proposal. Your goal is to help refine it towards an optimal solution.\n"
            f"Draft Proposal:\n{draft_proposal}\n"
        ]

        if alternatives:
            prompt_parts.append("The Scribe also noted the following alternatives or points of contention:")
            for i, alt in enumerate(alternatives):
                prompt_parts.append(f"  Alternative {i+1}: {alt}")
            prompt_parts.append("\n")

        prompt_parts.extend([
            f"Based on your expertise and previous input (if any), do you agree with this draft proposal? "
            f"Provide a clear 'AGREE' or 'DISAGREE' vote, followed by a concise rationale. "
            f"If you disagree, explain why and suggest specific improvements or which alternative you'd prefer."
            f"\nYour Vote and Rationale: [AGREE/DISAGREE] Rationale: ..."
        ])

        prompt = "\n".join(prompt_parts)
        
        response = self.llm_client.generate_text(prompt, max_tokens=MAX_TOKENS)

        # Basic parsing of the vote and rationale (can be made more robust)
        vote_decision = False
        rationale = response
        if response.upper().startswith("AGREE"):
            vote_decision = True
            rationale = response[len("AGREE"):].lstrip(" :Rrationale").lstrip()
        elif response.upper().startswith("DISAGREE"):
            vote_decision = False
            rationale = response[len("DISAGREE"):].lstrip(" :Rrationale").lstrip()
        else:
            # If parsing fails, assume disagreement and use full response as rationale
            print(f"Warning: Could not parse vote from Actor {self.name}. Defaulting to DISAGREE. Response: {response}")
            vote_decision = False

        print(f"Actor {self.name} voted: {'Agree' if vote_decision else 'Disagree'}. Rationale: {rationale[:100]}...")
        return vote_decision, rationale

    def __repr__(self):
        return f"Actor(name='{self.name}', personality='{self.personality}')"


if __name__ == '__main__':
    security_eng = Actor("Security Engineer", "Seasoned security engineer focused on security and compliance. Opinionated and prefers proven technologies.")
    print(security_eng)
    proposal = security_eng.generate_proposal("We want to build a memory storage system across all MCPs. Each MCP is a separate cloud project. Should we host the memory in a central project or per MCP?")
    print(proposal)
    vote, rationale = security_eng.vote_on_draft(proposal)
    print(vote)
    print(rationale)
