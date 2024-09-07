class code_generator:
    def __init__(self):
        self.pb = []
        self.ss = []

        self.top = -1
        self.i = 0

        self.data_p = 100
        self.temp_p = 500

        self.data_block = dict()
        self.scope_p = 0
        self.while_switch_scope_stack = [0] * 100

    def pop(self, n):
        self.ss = self.ss[:self.top - n + 1]
        self.top -= n

    def push(self, m):
        self.ss.append(m)
        self.top += 1

    def get_temp(self):
        t = self.temp_p
        self.temp_p += 4
        return t

    def codegen(self, action, last_input=''):
        if action == 'PID':
            p = self.find_address_in_symbol_table(last_input)
            self.push(p)
        elif action == 'Declare':
            a = self.ss[self.top]
            self.pb.append('(ASSIGN, #0, ' + str(a) + ',   )')
            self.i += 1
            self.pop(1)
        elif action == 'Array_declare':
            a = self.ss[self.top - 1]
            b = self.ss[self.top]
            self.pb.append('(ASSIGN, #0, ' + str(a) + ',   )')
            self.i += 1
            self.pop(2)
            self.data_p += 4 * (int(b[1:]) - 1)
        elif action == 'Add_scope':
            self.scope_p += 1
        elif action == 'Reduce_scope':
            self.scope_p -= 1
        elif action == 'Mark_assignment':
            self.pop(1)
        elif action == 'Break':
            last_while_scope = self.find_last_while_scope()
            last_switch_scope = self.find_last_switch_scope()
            if last_switch_scope == last_while_scope == -1:
                return
            if last_switch_scope < last_while_scope:
                a = self.ss[self.top - (self.scope_p - last_while_scope) * 2] - 1
            else:
                a = self.ss[self.top - (self.scope_p - last_switch_scope) * 2 - 1]
            self.pb.append(f'(JP, {a},  ,   )')
            self.i += 1
        elif action == 'Save':
            self.push(self.i)
            self.pb.append('')
            self.i += 1
        elif action == 'Jpf':
            a = self.ss[self.top]
            b = self.ss[self.top - 1]
            self.pb[int(a)] = '(JPF, ' + str(b) + ', ' + str(self.i) + ' )'
            self.pop(2)
        elif action == 'Jpf_save':
            a = self.ss[self.top]
            b = self.ss[self.top - 1]
            self.pb[int(a)] = '(JPF, ' + str(b) + ', ' + str(self.i + 1) + ' )'
            self.pop(2)
            self.push(self.i)
            self.pb.append('')
            self.i += 1
        elif action == 'Jp':
            a = self.ss[self.top]
            self.pb[int(a)] = '(JP, ' + str(self.i) + ',  ,   )'
            self.pop(1)
        elif action == 'Jmp_save':
            self.while_switch_scope_stack[self.scope_p] = last_input
            self.pb.append(f'(JP, {self.i + 2},  ,   )')
            self.i += 1
            self.push(self.i)
            self.pb.append('')
            self.i += 1
        elif action == 'Label':
            self.push(self.i)
        elif action == 'While':
            self.pb[self.ss[self.top - 3]] = f'(JP, {self.i + 1},  ,   )'
            a = self.ss[self.top]
            b = self.ss[self.top - 1]
            self.pb[int(a)] = '(JPF, ' + str(b) + ', ' + str(self.i + 1) + ' )'
            c = self.ss[self.top - 2]
            self.pb.append('(JP, ' + str(c) + ',  ,   )')
            self.i += 1
            self.pop(4)
        elif action == 'Eq_switch':
            t = self.get_temp()
            a = self.ss[self.top]
            b = self.ss[self.top - 1]
            self.pb.append('(EQ, ' + str(b) + ', ' + str(a) + ', ' + str(t) + ' )')
            self.i += 1
            self.pop(1)
            self.push(t)
        elif action == 'Switch_Jmp':
            self.scope_p -= 1
            a = self.ss[self.top - 1]
            self.pb[int(a)] = f'(JP, {self.i},  ,   )'
            self.pop(2)
        elif action == 'Assign':
            a = self.ss[self.top]
            b = self.ss[self.top - 1]
            self.pb.append('(ASSIGN, ' + str(a) + ', ' + str(b) + ',   )')
            self.i += 1
            self.pop(1)
        elif action in ['Add', 'Sub', 'Mult', 'Div', 'Lt', 'Eq']:
            t = self.get_temp()
            a = self.ss[self.top]
            b = self.ss[self.top - 1]
            self.pb.append('(' + action.upper() + ', ' + str(b) + ', ' + str(a) + ', ' + str(t) + ' )')
            self.i += 1
            self.pop(2)
            self.push(t)
        elif action == 'Print':
            a = self.ss[self.top]
            self.pb.append('(PRINT, ' + str(a) + ',  ,   )')
            self.i += 1
            self.pop(1)
        elif action == 'Array_access':
            t = self.get_temp()
            a = self.ss[self.top - 1]
            b = self.ss[self.top]
            self.pb.append('(MULT, ' + str(b) + ', #4, ' + str(t) + ' )')
            self.pb.append('(ADD, #' + str(a) + ', ' + str(t) + ', ' + str(t) + ' )')
            self.i += 2
            self.pop(2)
            self.push(f'@{t}')
        elif action == 'Save_constant':
            self.push(f'#{last_input}')

        self.write_program_block_to_file()

    def write_program_block_to_file(self):
        with open('output.txt', 'w') as f:
            f.write('\n'.join([f'{num}\t{code}' for num, code in zip(list(range(len(self.pb))), self.pb)]))
        with open('semantic_errors.txt', 'w') as f:
            f.write('The input program is semantically correct.')

    def find_address_in_symbol_table(self, ID):
        if self.data_block.get(ID) is None:
            self.data_block[ID] = self.data_p
            self.data_p += 4
        return self.data_block[ID]

    def find_last_while_scope(self):
        for i in reversed(range(self.scope_p)):
            if self.while_switch_scope_stack[i] == 'while':
                return i
        return -1

    def find_last_switch_scope(self):
        for i in reversed(range(self.scope_p)):
            if self.while_switch_scope_stack[i] == 'switch':
                return i
        return -1
