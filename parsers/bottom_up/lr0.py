
from __future__ import annotations
from ..grammar import Grammar, ProductionRule, EPSILON
from ..parser import Parser

# TODO: Not able to handle null productions, need to check that
# NOTE: seems it is not possible to parse, as there will be conflicts


class DottedProduction(ProductionRule):
    def __init__(self, dot_ptr: int, lhs: str, rhs: list[str]) -> None:
        # rhs = [] if len(rhs) == 1 and rhs[0] == EPSILON else rhs
        super().__init__(lhs, rhs)
        self.dot_ptr = dot_ptr
    # def is_null_production(self):
    #     return

    def is_reduced(self):
        return self.dot_ptr == len(self.rhs)

    def rule(self):
        return super().__str__()

    def __str__(self):
        dotted_rhs = self.rhs.copy()
        dotted_rhs.insert(self.dot_ptr, ".")
        return f"{self.lhs} -> {"".join(dotted_rhs)}"

    # def is_left_recursive(self):
    #     return False if not len(self.rhs) else super().is_left_recursive()

    # def is_right_recursive(self):
    #     return False if not len(self.rhs) else super().is_right_recursive()

    def shift(self, grammar: Grammar):
        if self.dot_ptr == len(self.rhs):
            raise RuntimeError(f"The production is already reduced")
        return (self.rhs[self.dot_ptr], Closure(DottedProduction(self.dot_ptr + 1, self.lhs, self.rhs), grammar))


class Closure():
    def __init__(self, rule: DottedProduction, grammar: Grammar) -> None:
        self.rules: list[DottedProduction] = [rule]
        if not rule.is_reduced():
            self._expand_rules(rule, grammar)

    def _expand_rules(self, rule: DottedProduction, grammar: Grammar):
        print(rule)
        if rule.rhs[rule.dot_ptr] in grammar.non_terminals:
            # include all the rules starting from it
            sub_sequent_rules = [DottedProduction(
                0, rule.lhs, rule.rhs) for rule in grammar.rules[rule.rhs[rule.dot_ptr]]]
            self.rules.extend(sub_sequent_rules)
            for sub_rule in sub_sequent_rules:
                self._expand_rules(sub_rule, grammar)

    def __str__(self) -> str:
        return "\n".join(str(x) for x in self.rules)

    def __eq__(self, other: Closure) -> bool:
        return str(self) == str(other)


class LR0(Parser):
    def __init__(self, grammar: Grammar, logging=False) -> None:
        self.logging = logging
        self.closures: list[Closure] = []
        self.transitions: dict[int, list[tuple[str, int]]] = dict()
        self.grammar = grammar
        self.table: list[dict[str, str | None]] | None = None
        augmented_rule = DottedProduction(0, "S'", [self.grammar.start_symbol])
        augmented_grammar = Closure(augmented_rule, grammar)
        self.closures.append(augmented_grammar)
        self._construct_dfa(augmented_grammar, 0)
        self._construct_table()

    def _construct_dfa(self, closure: Closure, closure_id: int):
        for rule in closure.rules:
            if not rule.is_reduced():
                on, to = rule.shift(self.grammar)
                existing = None
                for i, c in enumerate(self.closures):
                    if c == to:
                        existing = i
                        break
                last_idx = len(self.closures)
                # self.transitions.append(
                #     (on, closure_id, last_idx if existing is None else existing))
                if closure_id not in self.transitions:
                    self.transitions[closure_id] = []
                self.transitions[closure_id].append(
                    (on, last_idx if existing is None else existing))
                if existing is None:
                    self.closures.append(to)
                    self._construct_dfa(to, last_idx)
        if self.logging:
            self.print_dfa()

    def print_dfa(self):
        for i, c in enumerate(self.closures):
            print(f" I{i} ".center(15, "-"))
            for rule in c.rules:
                print(f"|{str(rule).center(13)}|")
            print(f"".center(15, "-"))
            if i in self.transitions:
                for on, to in self.transitions[i]:
                    print(f"I{i} --{on}--> I{to}")
            else:
                print("Item is reduced.")

    def _construct_table(self):
        total_set = list(self.grammar.terminals)
        total_set.append("$")
        terminals = total_set.copy()
        total_set.extend(self.grammar.non_terminals)
        table: list[dict[str, str | None]] = [
            {x: None for x in total_set} for _ in self.closures]
        for i, t in self.transitions.items():
            for on, to in t:
                table[i][on] = f"S{to}"
        for j, c in enumerate(self.closures):
            if len(c.rules) == 1 and c.rules[0].is_reduced():
                if any(x is None for x in table[i]):
                    raise RuntimeError(
                        f"Failed to construct the table, Shift-Reduce conflict at I{i}")
                if c.rules[0].lhs == "S'":
                    table[j]["$"] = "accept"
                else:
                    indices = [i for i, item in enumerate(
                        self.grammar.production_rules) if str(item) == c.rules[0].rule()]
                    if not len(indices):
                        raise ValueError(f"This won't occur")
                    for t in terminals:
                        table[j][t] = f"r{indices[0]}"
        self.table = table
        if self.logging:
            self.print_table()

    def print_table(self):
        total_set = list(self.grammar.terminals)
        total_set.append("$")
        total_set.extend(self.grammar.non_terminals)
        if not self.table:
            raise RuntimeError("Parsing table not constructed.")
        terminals = self.grammar.terminals.union({"$"})
        non_terminals = self.grammar.non_terminals
        cols_size = len(terminals) + len(non_terminals) + 1
        each_col_len = 10
        print("-" * (cols_size * each_col_len + len(total_set)))
        print(" " * (each_col_len), end="|")
        print("Action".center((each_col_len + 1) * len(terminals)-1), end="|")
        print("GOTO".center((each_col_len + 1) * len(non_terminals)))
        print("Closures".center(each_col_len) +
              "-" * (cols_size - 1) * (each_col_len+1))
        row_str = "|".join(row.center(each_col_len) for row in total_set)
        print(" " * (each_col_len) + "|" + row_str)
        print("-" * (cols_size * each_col_len + len(total_set)))
        for i, r in enumerate(self.table):
            rows = [f"I{i}"]
            for c in total_set:
                val = r[c]
                rows.append("--" if val is None else str(val))
            row_str = "|".join(row.center(each_col_len) for row in rows)
            print(row_str)
            print("-"*len(row_str))

    def parse(self, input: str) -> bool:
        stack: list[str | int] = []
        input = input + "$"
        look_at = 0
        stack.append(0)
        if not self.table:
            raise RuntimeError("Parsing table not constructed.")
        if self.logging:
            print(
                f"Start Parsing: tape -> {input[look_at:]}, stack -> {stack}")
        while len(stack):
            top = stack[-1]
            if type(top) != int:
                raise RuntimeError(
                    f"Invalid stack top expected int found str.")
            action = self.table[top][input[look_at]]
            if action is None:
                raise RuntimeError(
                    f"Failed to parse the string, no action found for I{
                        top} at {input[look_at]}"
                )
            if action == "accept":
                if self.logging:
                    print("STRING IS ACCEPTED!!!")
                return True
            elif action.startswith("S"):
                if self.logging:
                    print(
                        f"Shift Found: I{
                            top} --{input[look_at]}--> {action[-1]}"
                    )
                stack.append(input[look_at])
                stack.append(int(action[-1]))
                look_at += 1
            elif action.startswith("r"):
                rule = self.grammar.production_rules[int(action[-1])]
                if not rule:
                    raise ValueError(f"No rule found, for {action}")
                if self.logging:
                    print(f"Reduce Found: rule : {rule}")
                for _ in range(len(rule.rhs) * 2):
                    stack.pop()
                state = self.table[int(stack[-1])][rule.lhs]
                if state is None:
                    raise RuntimeError(
                        f"No state found at I{int(stack[-1])} {rule.lhs}"
                    )
                stack.append(rule.lhs)
                stack.append(int(state[-1]))
            else:
                raise RuntimeError(
                    f"No choice found"
                )
            if self.logging:
                print(f"Snap: tape -> {input[look_at:]}, stack -> {stack}")
        if self.logging:
            print("STRING IS REJECTED!!!")
        return False


if __name__ == "__main__":
    g = Grammar.from_string(f"""
    S -> ASB | c
    A -> a
    B -> b
    """, {"a", "b", "c"}, {"A", "B", "S"})
    lr0 = LR0(g, True)
    lr0.parse("aacbb")
