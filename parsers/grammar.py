from __future__ import annotations
EPSILON = "ε"


class ProductionRule:
    def __init__(self, lhs: str, rhs: list[str]) -> None:
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self) -> str:
        return f"{self.lhs} -> {"".join(self.rhs)}"

    def is_left_recursive(self):
        return self.rhs[0] == self.lhs

    def is_right_recursive(self):
        return self.rhs[0] == self.lhs

    def is_certainly_ambiguous(self):
        return self.is_left_recursive() and self.is_right_recursive()

    def __eq__(self, value: ProductionRule) -> bool:
        return str(self) == str(value)

    @staticmethod
    def from_string(rule: str, terminals: set[str], non_terminals: set[str]) -> ProductionRule:
        lhs, rhs_str = rule.split("->")
        lhs = lhs.strip()
        rhs_str = rhs_str.strip()
        if rhs_str == EPSILON:
            return ProductionRule(lhs, [EPSILON])
        rhs: list[str] = []
        i = 0
        while i < len(rhs_str):
            if rhs_str[i] in terminals or rhs_str[i] in non_terminals:
                rhs.append(rhs_str[i])
            else:
                for j in range(i+1, len(rhs_str)):
                    if rhs_str[i:j] in terminals or rhs_str in non_terminals:
                        i = j
                        break
            i += 1
        return ProductionRule(lhs, rhs)


class Grammar:
    def __init__(self, start_symbol: str, non_terminals: set[str], terminals: set[str], production_rules: list[ProductionRule]):
        self.start_symbol = start_symbol
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.production_rules = production_rules
        self.rules: dict[str, list[ProductionRule]] = dict()
        for rule in self.production_rules:
            if not rule.lhs in self.rules:
                self.rules[rule.lhs] = [rule]
            else:
                self.rules[rule.lhs].append(rule)
        # Validation: Ensure all non-terminals have at least one rule
        for non_terminal in self.non_terminals:
            if not any(rule.lhs == non_terminal for rule in production_rules):
                raise ValueError(
                    f"No production rule found for non-terminal '{non_terminal}'.")

    @staticmethod
    def from_string(input: str, terminals: set[str], non_terminals: set[str], start_symbol: str | None = None) -> Grammar:
        rules = [r.strip() for r in input.split("\n") if len(r.strip())]
        productions_rules = []
        for rule in rules:
            lhs, rhs_combined = [x.strip() for x in rule.split("->")]
            choices = [x.strip() for x in rhs_combined.split("|")]
            for rhs in choices:
                productions_rules.append(
                    ProductionRule.from_string(
                        f"{lhs} -> {rhs}", terminals, non_terminals)
                )
        return Grammar(
            start_symbol or productions_rules[0].lhs,
            non_terminals,
            terminals,
            productions_rules
        )

    def __str__(self) -> str:
        return "\n".join([str(rule) for rule in self.production_rules])

    # def is_deterministic(self):
    #     return self.is_left_factored()

    def is_left_recursive(self):
        return all(rule.is_left_recursive() for rule in self.production_rules)

    def is_right_recursive(self):
        return all(rule.is_right_recursive() for rule in self.production_rules)

    def is_certainly_ambiguous(self):
        return all(rule.is_certainly_ambiguous() for rule in self.production_rules)


if __name__ == "__main__":
    g1 = Grammar.from_string("""
    S -> aA | bB
    A -> ε
    B -> ε
    """, {"a", "b"}, {"S", "A", "B"})
    print("Grammar: 1")
    print(g1)

    g2 = Grammar.from_string("""
        S -> AaB | BA
        A -> a | b
        B -> d | e
        """, {"a", "b", "d", "e"}, {"S", "B", "A"})
    print("Grammar: 2")
    print(g2)

    g3 = Grammar.from_string("""
        S -> AaB
        A -> b | ε
        B -> c
        """, {"a", "b", "c"}, {"S", "A", "B"})
    print("Grammar: 3")
    print(g3)

    g4 = Grammar.from_string("""
        S -> AB
        A -> a | ε
        B -> b | ε
        """, {"a", "b"}, {"S", "A", "B"})
    print("Grammar: 4")
    print(g4)

    g5 = Grammar.from_string("""
        S -> ABCDE
        A -> a | ε
        B -> b | ε
        C -> c | ε
        D -> d
        E -> e | ε
        """, {"a", "b", "c", "d", "e"}, {"S", "A", "B", "C", "D", "E"})
    print("Grammar: 5")
    print(g5)
