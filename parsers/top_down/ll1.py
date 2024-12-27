from ..grammar import Grammar, ProductionRule, EPSILON
from ..parser import Parser
from ..utils import First, Follow, is_left_factored
from typing import Sequence


class LL1(Parser):
    def __init__(self, grammar: Grammar, logging=False) -> None:
        if not is_left_factored(grammar) or grammar.is_left_recursive() or grammar.is_certainly_ambiguous():
            raise ValueError(f"{grammar} is not suitable for LL0 parsing.")
        super().__init__(grammar)
        self.logging = logging
        self._first_map: dict[str, set[str]] | None = None
        self._follow_map:  dict[str, set[str]] | None = None
        self._parse_table: dict[str, dict[str, ProductionRule |
                                          None]] = self._construct_parse_table()

    def calculate_first(self):
        if self._first_map:
            return self._first_map
        first_map: dict[str, set[str]] = dict()
        for t in self.grammar.terminals:
            first_map[t] = First(t, self.grammar)
        for nt in self.grammar.non_terminals:
            first_map[nt] = First(
                nt, self.grammar) if nt not in first_map else first_map[nt]
        if self.logging:
            for e in first_map:
                print(f"First({e}) -> {{ {" , ".join(first_map[e])} }}")
        self._first_map = first_map
        return first_map

    def calculate_follow(self):
        if self._follow_map:
            return self._follow_map
        first_dict = self.calculate_first()
        follow_dict: dict[str, set[str]] = dict()
        for nt in self.grammar.non_terminals:
            follow_dict[nt] = Follow(nt, self.grammar, first_dict)
        if self.logging:
            for e in follow_dict:
                print(f"Follow({e}) -> {{ {" , ".join(follow_dict[e])} }}")
        self._follow_map = follow_dict
        return follow_dict

    def _construct_parse_table(self):
        if self.logging:
            print(f"Grammer: \n{self.grammar}\n",)
        first_dict = self.calculate_first()
        follow_dict = self.calculate_follow()
        terminals: set[str] = self.grammar.terminals.copy()
        terminals.add('$')
        non_terminals = self.grammar.non_terminals.copy()
        table: dict[str, dict[str, ProductionRule | None]] = {nt: {t: None for t in terminals}
                                                              for nt in non_terminals}
        for lhs, rules in self.grammar.rules.items():
            choices = [rule.rhs for rule in rules]
            for choice in choices:
                if choice[0] == EPSILON:
                    follow_of_choice = follow_dict[lhs]
                    for each_follow_of_choice in follow_of_choice:
                        table[lhs][each_follow_of_choice] = ProductionRule(
                            lhs, choice)
                    continue
                first_of_choice = first_dict[choice[0]]
                for each_first_of_choice in first_of_choice:
                    if each_first_of_choice == EPSILON:
                        continue
                    else:
                        table[lhs][each_first_of_choice] = ProductionRule(
                            lhs, choice)
        if self.logging:
            self._print_parse_table(table, terminals)
        return table

    def _print_parse_table(self, table: dict[str, dict[str, ProductionRule | None]], cols: set[str]):
        columns = [""]
        columns.extend(cols)
        header = "|".join(c.center(15) for c in columns)
        print("-" * len(header))
        print(header)
        print("-" * len(header))
        for r in table:
            rows = [r]
            for c in table[r]:
                val = table[r][c]
                rows.append("--" if val is None else str(val))
            row_str = "|".join(row.center(15) for row in rows)
            print(row_str)
            print("-"*len(row_str))

    def parse(self, input: Sequence[str]) -> bool:
        tape = list(x for x in input)
        tape.append("$")
        tape_ptr = 0
        stack: list[str] = []
        table = self._parse_table
        stack.append("$")
        stack.append(self.grammar.start_symbol)
        if self.logging:
            print(
                f"Start Parsing: tape -> {tape[tape_ptr:]}, stack -> {stack}")
        while len(stack):
            if stack[-1] == tape[tape_ptr]:
                if self.logging:
                    print(f"Found Match: moving forward and popping stack:")
                stack.pop()
                tape_ptr += 1
                if self.logging:
                    print(f"Snap: tape -> {tape[tape_ptr:]}, stack -> {stack}")
            else:
                if self.logging:
                    print("Found Non Terminal: looking for rules to move forward:")
                rule = table[stack[-1]][tape[tape_ptr]]
                if rule is None:
                    if self.logging:
                        print(
                            f"Failed to parse: no move found to resolve {
                                tape[tape_ptr]} from {stack[-1]}"
                        )
                    return False
                if self.logging:
                    print(f"Rule Found: {rule}, expanding rule:")
                stack.pop()
                if rule.rhs[0] != EPSILON:
                    stack.extend(reversed(rule.rhs))
                if self.logging:
                    print(f"Snap: tape -> {tape[tape_ptr:]}, stack -> {stack}")
        if (tape_ptr == len(tape)):
            if self.logging:
                print("Successfully reached the end.")
                print("STRING ACCEPTED!!!")
            return True
        if self.logging:
            print("Stack became empty before reaching the end of the tape.")
            print("STRING IS NOT ACCEPTED!!!")
        return False


if __name__ == '__main__':
    g1 = Grammar.from_string(f"""
    S -> BA
    A -> aBA | {EPSILON}
    B -> DC
    C -> bDC | {EPSILON}
    D -> cSd | e
    """, {"a", "b", "c", "d", "e"}, {"S", "B", "A", "D", "C"})
    ll1_1 = LL1(g1, True)
    ll1_1.parse("cebeaed")
    g2 = Grammar.from_string(f"""
    E -> TP
    P -> +TP | {EPSILON}
    T -> FQ
    Q -> *FQ | {EPSILON}
    F -> (E) | id
    """, {"+", "*", "(", ")", "id"}, {"E", "P", "T", "Q", "F"}, "E")
    ll1_2 = LL1(g2, True)
    ll1_2.parse(["id", "+", "id", "*", "id"])
