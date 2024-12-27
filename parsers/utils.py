""" This methods are not optimized, rather implemented in a way your brain will think """
from __future__ import annotations
from .grammar import Grammar, EPSILON


def First(symbol: str, grammar: Grammar):
    # if symbol is a terminal then return itself, i.e First(a) -> { a }
    if symbol in grammar.terminals or symbol == EPSILON:
        return {symbol}
    # if symbol is non terminal then check for its first recursively e.g.
    # A -> bBc | Bc, B -> d | ε , First(B) -> { d , ε }, First(A) -> { b, d, c }
    rules = grammar.rules[symbol]
    choices = [rule.rhs for rule in rules]
    if not rules:
        raise ValueError(f"No rule found for symbol {symbol}")
    first_set = set()
    for each_choice in choices:
        for i in range(len(each_choice)):
            # calculate the first of from the start
            first_of_this = First(each_choice[i], grammar)
            # if it does not contain ε then break
            # or if it is the last element then add with ε
            if EPSILON not in first_of_this or i == len(each_choice) - 1:
                first_set.update(first_of_this)
                break
            # else add without the ε as the first of next element will add
            else:
                first_set.update(first_of_this - {EPSILON})
    return first_set


def Follow(symbol: str, grammar: Grammar, first_map: dict[str, set[str]]):
    if symbol in grammar.terminals or symbol == EPSILON:
        raise ValueError(f"{symbol} is not a non terminal.")
    follow_set = set()
    if symbol == grammar.start_symbol:
        follow_set.add('$')
    for lhs, rules in grammar.rules.items():
        choices = [rule.rhs for rule in rules]
        # if symbol is present in rhs
        for each_choice in choices:
            if each_choice == EPSILON:
                continue
            follow_of_this = set()
            occurrences = [i for i, char in enumerate(
                each_choice) if char == symbol]
            for each_occurrence in occurrences:
                # S -> aAA, A -> a | ε, Follow(S) -> { $ }, Follow(A) -> { a, $ }
                next = each_occurrence + 1
                while next < len(each_choice):
                    first_of_next = first_map[each_choice[next]]
                    if EPSILON not in first_of_next:
                        follow_of_this.update(first_of_next)
                        break
                    else:
                        follow_of_this.update(first_of_next - {EPSILON})
                        next += 1
                # if the rule has run until the end or
                # the occurrence is the last element
                # then add its parent
                if next >= len(each_choice) and symbol != lhs:
                    follow_of_this.update(
                        Follow(lhs, grammar, first_map))
                follow_set.update(follow_of_this)
    return follow_set


def is_left_factored(g: Grammar):
    """
    if two rules of any production has common prefix 
    then the compiler won't be able to determine
    which production to follow. grammars with no 
    such conflicts are left factored.
    """
    for lhs in g.rules:
        print(",".join([str(x) for x in g.rules[lhs]]))
        list_of_first_of_rhs = [First(x.rhs[0], g)
                                for x in g.rules[lhs]]
        if len(set(tuple(inner_set) for inner_set in list_of_first_of_rhs)) != len(list_of_first_of_rhs):
            return False
    return True

# class GrammarUtil():
#     def __init__(self, grammar: Grammar, logging=False) -> None:
#         self.grammar = grammar
#         self.logging = logging
#         self.first_map = None
#         self.follow_map = None

#     def calculate_first(self):
#         if self.first_map:
#             return self.first_map
#         first_map: dict[str, set[str]] = dict()
#         for t in self.grammar.terminals:
#             first_map[t] = First(t, self.grammar)
#         for nt in self.grammar.nonterminals:
#             first_map[nt] = First(
#                 nt, self.grammar) if nt not in first_map else first_map[nt]
#         if self.logging:
#             for e in first_map:
#                 print(f"First({e}) -> {{ {" , ".join(first_map[e])} }}")
#         self.first_map = first_map
#         return first_map

#     def calculate_follow(self):
#         if self.follow_map:
#             return self.follow_map
#         first_dict = self.calculate_first()
#         follow_dict: dict[str, set[str]] = dict()
#         for nt in self.grammar.nonterminals:
#             follow_dict[nt] = Follow(nt, self.grammar, first_dict)
#         if self.logging:
#             for e in follow_dict:
#                 print(f"Follow({e}) -> {{ {" , ".join(follow_dict[e])} }}")
#         self.follow_map = follow_dict
#         return follow_dict

#     def is_left_recursive(self):
#         return any(
#             choice[0] == rule.lhs
#             for rule in self.grammar.rules.values()
#             for choice in rule.rhs
#         )

#     def is_right_recursive(self):
#         return any([
#             choice[-1] == rule.lhs
#             for rule in self.grammar.rules.values()
#             for choice in rule.rhs
#         ])

#     def is_certainly_ambiguous(self):
#         return self.is_left_recursive() and self.is_right_recursive()


# if __name__ == '__main__':

#     g1 = Grammar.from_string("""
#         S -> aA | bB
#         A -> ε
#         B -> ε
#     """)
#     g2 = Grammar.from_string("""
#         S -> AaB | BA
#         A -> a | b
#         B -> d | e
#         """)
#     g3 = Grammar.from_string("""
#         S -> AaB
#         A -> b | ε
#         B -> c
#         """)

#     g4 = Grammar.from_string("""
#         S -> AB
#         A -> a | ε
#         B -> b | ε
#         """)

#     g5 = Grammar.from_string("""
#         S -> ABCDE
#         A -> a | ε
#         B -> b | ε
#         C -> c | ε
#         D -> d
#         E -> e | ε
#         """)
#     g6 = Grammar.from_string("""
#         S -> ABCDE
#         A -> a | ε
#         B -> b | ε
#         C -> c | ε
#         D -> d
#         E -> e | ε
#     """)
#     for i, g in enumerate([g1, g2, g3, g4, g5, g6]):
#         gu = GrammarUtil(g, True)
#         print(f"------------")
#         print(f"Grammar: {i}")
#         print(f"------------")
#         print(g)
#         print(f"----------")
#         print(f"First: {i}")
#         print(f"----------")
#         gu.calculate_first()
#         print(f"----------")
#         print(f"Follow: {i}")
#         print(f"----------")
#         gu.calculate_follow()
#         print("\n\n")
