from scanner import Scanner, TokenType
from inter_code_gen import code_generator
import json


class Parser:
    def __init__(self, code):
        self.scanner = Scanner(code)
        self.code_gen = code_generator()
        self.stack = [0]

        data = json.load(open('table_generator/table.json'))
        self.grammar = data['grammar']
        self.parse_table = data['parse_table']

    def parse(self):
        advance_input = True
        token = None

        while True:
            if advance_input is True:
                token = self.scanner.get_next_token()
            if token.type in (TokenType.COMMENT, TokenType.WHITESPACE):
                continue
            input_token = token.type if token.type in ['NUM', 'ID'] else token.string
            action = self.parse_table[str(self.stack[-1])][input_token]

            # Accept
            if action == 'accept':
                break
            # Shift
            if action.startswith('shift_'):
                # print("before", self.stack)
                self.stack.append(input_token)
                self.stack.append(int(''.join(action[6:])))
                advance_input = True
                # print("shift _ stack", self.stack)
            # Reduce
            elif action.startswith('reduce_'):
                # print("before", self.stack)
                r = self.grammar[''.join(action[7:])]
                lhs = r[:r.index("->")]
                rhs = r[r.index("->") + 1:]

                if 'epsilon' not in rhs:
                    for _ in range(2 * len(rhs)):
                        # self.code_gen.codegen(action=input_token)
                        self.stack.pop()

                for i in range(len(lhs)):
                    self.stack += [lhs[i]]

                goto = self.parse_table[str(self.stack[-2])][str(self.stack[-1])]
                self.stack.append(int(goto[5:]))

                # print("reduce", r)
                # print("reduce _ stack", self.stack)
                self.code_gen.codegen(action=r[0], last_input=token.string)
                advance_input = False
            else:
                break
