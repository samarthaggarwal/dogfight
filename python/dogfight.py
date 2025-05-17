from actor import Actor
from scribe import Scribe


class Dogfight:
    def __init__(self, actors: dict[str, str], max_rounds: int = 3, consensus_threshold: float = 0.67):
        if len(actors) < 1:
            raise ValueError("At least 1 actor is required for a dogfight")
        self.actors = [Actor(name, personality) for name, personality in actors.items()]
        self.scribe = Scribe()
        if max_rounds < 1:
            raise ValueError("max_rounds must be at least 1")
        self.max_rounds = max_rounds
        if consensus_threshold <= 0 or consensus_threshold > 1:
            raise ValueError("consensus_threshold must be between 0 and 1")
        self.consensus_threshold = consensus_threshold

    def debate(self, problem: str) -> str:
        proposals = []
        votes = []
        reasons = []
        round_idx = 0
        draft = None
        while round_idx < self.max_rounds:
            for actor in self.actors:
                proposals.append(actor.generate_proposal(problem, draft))
            draft = self.scribe.generate_draft(problem, proposals)
            for actor in self.actors:
                vote, reason = actor.vote_on_draft(problem, draft)
                votes.append(vote)
                reasons.append(reason)
            print(f"Round {round_idx + 1} complete.")
            for i in range(len(self.actors)):
                print(f"### {self.actors[i].name}:\nVote: {'Agree' if votes[i] else 'Disagree'}\nReason: {reasons[i]}\n\n")
            if self._fraction_of_agreements(votes) >= self.consensus_threshold:
                break
            round_idx += 1
        return draft

    def _fraction_of_agreements(self, votes: list[bool]) -> float:
        return sum(votes) / len(votes)

if __name__ == '__main__':
    actors = {
        "Security Engineer": "security, compliance.",
        "Performance Engineer": "performance, scalability.",
        "ML Engineer": "machine learning, algorithms.",
        "Data Engineer": "data management, analytics.",
    }
    dogfight = Dogfight(actors, max_rounds=3, consensus_threshold=0.67)
    problem = "We want to build metrics logger to collect performance metrics from all our customers. Each customer has their own cloud project. Should we host the metrics logger in a central project or per customer?"
    proposal = dogfight.debate(problem)
    print(proposal)
