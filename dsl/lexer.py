import re


class Token:
    def __init__(self, type, value, line):
        self.type = type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1

    def tokenize(self):
        tokens = []
        while self.pos < len(self.text):
            char = self.text[self.pos]

            # 1. 跳过空白符
            if char.isspace():
                if char == '\n': self.line += 1
                self.pos += 1
                continue

            # 2. 【核心修复】支持 # 注释
            # 遇到 # 就一直跳过，直到行尾
            if char == '#':
                while self.pos < len(self.text) and self.text[self.pos] != '\n':
                    self.pos += 1
                continue

            # 3. 符号解析
            if char == ':':
                tokens.append(Token('COLON', ':', self.line))
                self.pos += 1
                continue

            # 解析 -> 箭头
            if self.text[self.pos:self.pos + 2] == '->':
                tokens.append(Token('ARROW', '->', self.line))
                self.pos += 2
                continue

            # 4. 字符串解析 "..." 或 '...'
            if char == '"' or char == "'":
                quote = char
                self.pos += 1  # 跳过开始的引号
                val = ""
                while self.pos < len(self.text) and self.text[self.pos] != quote:
                    val += self.text[self.pos]
                    self.pos += 1
                self.pos += 1  # 跳过结束的引号
                tokens.append(Token('STRING', val, self.line))
                continue

            # 5. 关键词与ID解析
            if char.isalpha() or char == '_':
                start = self.pos
                while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
                    self.pos += 1
                word = self.text[start:self.pos]

                # 关键词匹配
                if word == 'domain':
                    tokens.append(Token('DOMAIN', word, self.line))
                elif word == 'state':
                    tokens.append(Token('STATE', word, self.line))
                elif word == 'response':
                    tokens.append(Token('RESPONSE', word, self.line))
                elif word == 'transition':
                    tokens.append(Token('TRANSITION', word, self.line))
                elif word == 'end':
                    tokens.append(Token('END', word, self.line))
                else:
                    tokens.append(Token('ID', word, self.line))
                continue

            # 其他未知字符跳过
            self.pos += 1

        return tokens