# AST (Abstract Syntax Tree) 定义文件
# 这里定义了 DSL 的数据结构，它是通用的，不包含具体的业务逻辑

class Node:
    """所有 AST 节点的基类"""
    pass

class Script(Node):
    """表示整个脚本"""
    def __init__(self, domain, states):
        self.domain = domain    # 字符串: 领域名称 (例如 "电商助手")
        self.states = states    # 字典: {状态名: State对象}

    def __repr__(self):
        return f"<Script domain='{self.domain}' states={len(self.states)}>"

class State(Node):
    """表示一个对话状态"""
    def __init__(self, name, response, transitions=None, is_end=False):
        self.name = name                # 状态名 (例如 start)
        self.response = response        # 机器人回复的话
        self.transitions = transitions if transitions else [] # 列表: [Transition对象]
        self.is_end = is_end            # 布尔值: 是否是结束状态

    def __repr__(self):
        return f"<State name='{self.name}' is_end={self.is_end}>"

class Transition(Node):
    """表示状态之间的跳转规则"""
    def __init__(self, intent, description, target_state):
        self.intent = intent            # 意图标识 (例如 query_order)
        self.description = description  # 意图描述 (给 LLM 看的)
        self.target_state = target_state # 目标状态名

    def __repr__(self):
        return f"<Transition intent='{self.intent}' -> {self.target_state}>"