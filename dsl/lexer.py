import re

# 定义 Token 类型
TOKEN_TYPES = [
    ('DOMAIN', r'domain'),
    ('STATE', r'state'),
    ('RESPONSE', r'response'),
    ('TRANSITION', r'transition'),
    ('ARROW', r'->'),
    ('END', r'end'),
    ('STRING', r'"[^"]*"'),  # 双引号包裹的字符串
    ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),  # 标识符
    ('COLON', r':'),
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),  # 跳过空格和制表符
    ('MISMATCH', r'.'),  # 其他非法字符
]


class Token:
    def __init__(self, type, value, line):
        self.type = type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.current_line = 1

    def tokenize(self):
        pos = 0
        while pos < len(self.code):
            match = None
            for token_type, regex in TOKEN_TYPES:
                pattern = re.compile(regex)
                match = pattern.match(self.code, pos)
                if match:
                    text = match.group(0)
                    if token_type == 'NEWLINE':
                        self.current_line += 1
                    elif token_type == 'SKIP':
                        pass
                    elif token_type == 'MISMATCH':
                        raise SyntaxError(f"非法字符 '{text}' 在第 {self.current_line} 行")
                    else:
                        # 如果是字符串，去掉引号
                        if token_type == 'STRING':
                            text = text[1:-1]
                        token = Token(token_type, text, self.current_line)
                        self.tokens.append(token)

                    pos = match.end(0)
                    break
            if not match:
                raise SyntaxError(f"无法解析的字符在索引 {pos}")
        return self.tokens