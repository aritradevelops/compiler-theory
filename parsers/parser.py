from abc import ABC, abstractmethod
from .grammar import Grammar


class Parser(ABC):
    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar
        super().__init__()

    @abstractmethod
    def parse(self, input: str) -> bool:
        """Parse the given input string and return whether it is valid."""
        pass
