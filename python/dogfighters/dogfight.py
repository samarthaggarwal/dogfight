from dogfighters.actor import Actor
from dogfighters.scribe import Scribe
from concurrent.futures import ThreadPoolExecutor


class Dogfight:
    def __init__(
        self,
        actors: dict[str, str],
        max_rounds: int = 3,
        consensus_threshold: float = 0.67,
        debug_mode: bool = False
    ):
        if len(actors) < 1:
            raise ValueError("At least 1 actor is required for a dogfight")
        self.actors = [Actor(name, personality, debug_mode=debug_mode) for name, personality in actors.items()]
        self.scribe = Scribe(debug_mode=debug_mode)
        if max_rounds < 1:
            raise ValueError("max_rounds must be at least 1")
        self.max_rounds = max_rounds
        if consensus_threshold <= 0 or consensus_threshold > 1:
            raise ValueError("consensus_threshold must be between 0 and 1")
        self.consensus_threshold = consensus_threshold
        self.debug_mode = debug_mode
        self.executor = ThreadPoolExecutor(max_workers=len(actors) if len(actors) > 0 else 1)

    def debate(self, problem: str) -> str:
        proposals = []
        round_idx = 0
        draft = None

        while round_idx < self.max_rounds:
            # Generate proposals in parallel
            proposal_futures = [
                self.executor.submit(actor.generate_proposal, problem, draft)
                for actor in self.actors
            ]
            proposals = [future.result() for future in proposal_futures]

            # Process the draft and voting sequentially
            draft = self.scribe.generate_draft(problem, proposals)

            # Reset votes and reasons for this round
            votes = []
            reasons = []

            # Collect votes in parallel
            vote_futures = [
                self.executor.submit(actor.vote_on_draft, problem, draft)
                for actor in self.actors
            ]
            votes, reasons = zip(*[future.result() for future in vote_futures])

            if self.debug_mode:
                print(f"Round {round_idx + 1} complete. Votes: {votes}")
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
    dogfight = Dogfight(actors, max_rounds=3, consensus_threshold=0.67, debug_mode=False)
    problem = "We want to build metrics logger to collect performance metrics from all our customers. Each customer has their own cloud project. Should we host the metrics logger in a central project or per customer?"
    proposal = dogfight.debate(problem)
    print(proposal)
