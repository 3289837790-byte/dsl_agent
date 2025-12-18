from .lexer import Lexer
from .ast import Script, State, Transition


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected_type=None):
        token = self.current_token()
        if not token:
            raise SyntaxError("意外的文件结束")

        if expected_type and token.type != expected_type:
            raise SyntaxError(f"第 {token.line} 行语法错误: 期望 {expected_type}, 实际是 {token.type}")

        self.pos += 1
        return token

    def parse(self):
        # 1. 解析 Domain
        self.consume('DOMAIN')
        domain_name = self.consume('STRING').value

        states = {}

        # 2. 循环解析 State
        while self.pos < len(self.tokens):
            if self.current_token().type == 'STATE':
                state_node = self.parse_state()
                states[state_node.name] = state_node
            else:
                # 跳过可能多余的换行
                self.consume()

        return Script(domain_name, states)

    def parse_state(self):
        self.consume('STATE')
        state_name = self.consume('ID').value
        self.consume('COLON')

        response_text = ""
        transitions = []
        is_end = False

        # 解析 state 内部的内容 (response, transition, end)
        # 这里做一个简化的假设：直到遇到下一个 state 或者文件结束，都属于当前 state
        while self.pos < len(self.tokens) and self.current_token().type != 'STATE':
            token = self.current_token()

            if token.type == 'RESPONSE':
                self.consume()
                response_text = self.consume('STRING').value

            elif token.type == 'TRANSITION':
                self.consume()
                intent = self.consume('ID').value
                desc = self.consume('STRING').value
                self.consume('ARROW')
                target = self.consume('ID').value
                transitions.append(Transition(intent, desc, target))

            elif token.type == 'END':
                self.consume()
                is_end = True

            else:
                # 忽略其他的（比如换行）
                self.pos += 1

        return State(state_name, response_text, transitions, is_end)


def parse_dsl_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()

    lexer = Lexer(code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    return parser.parse()