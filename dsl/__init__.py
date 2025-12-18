class DSLInterpreter:
    def __init__(self, llm_client):
        self.ast = None
        self.current_state = None
        self.variables = {}
        self.llm_client = llm_client
        self.conversation_history = []

    def load_script(self, ast):
        self.ast = ast
        # 设置初始状态为第一个状态
        if ast['states']:
            self.current_state = ast['states'][0]['name']

    def execute(self, user_input):
        if not self.current_state:
            return "Error: No initial state set"

        # 查找当前状态
        current_state_obj = self.find_state(self.current_state)
        if not current_state_obj:
            return "Error: Current state not found"

        # 处理用户输入
        response = self.process_transitions(current_state_obj, user_input)

        # 记录对话历史
        self.conversation_history.append({
            'user': user_input,
            'agent': response,
            'state': self.current_state
        })

        return response

    def find_state(self, state_name):
        for state in self.ast['states']:
            if state['name'] == state_name:
                return state
        return None

    def process_transitions(self, state_obj, user_input):
        # 先检查条件转移（when）和默认转移（default）
        for transition in state_obj['transitions']:
            if transition['type'] == 'when_transition':
                if self.evaluate_condition(transition['condition']):
                    return self.execute_action(transition['action'],
                                               transition['next_state'])
            elif transition['type'] == 'default_transition':
                return self.execute_action(transition['action'],
                                           transition['next_state'])

        # 然后检查触发词转移（on）
        for transition in state_obj['transitions']:
            if transition['type'] == 'on_transition':
                if transition['trigger'].lower() in user_input.lower():
                    return self.execute_action(transition['action'],
                                               transition['next_state'])

        # 如果没有匹配的转移，使用LLM进行意图识别
        return self.fallback_llm_processing(state_obj, user_input)

    def execute_action(self, action, next_state):
        self.current_state = next_state

        if action['type'] == 'respond':
            return action['value']
        elif action['type'] == 'call_llm':
            # 这里可以调用LLM生成响应
            # 暂时返回固定响应
            return "I'll help you with that using AI..."
        elif action['type'] == 'set_variable':
            # 设置变量，这里我们暂时没有具体值，所以先设为None
            # 在实际应用中，可能需要从用户输入中提取信息来设置变量
            self.variables[action['var_name']] = None
            return f"Variable {action['var_name']} set. Moving to next state."

    def evaluate_condition(self, condition):
        var_value = self.variables.get(condition['var'], "")
        return var_value == condition['value']

    def fallback_llm_processing(self, state_obj, user_input):
        # 使用LLM分析用户意图并找到最相关的转移
        transitions_info = []
        for t in state_obj['transitions']:
            if t['type'] == 'on_transition':
                transitions_info.append(
                    f"Trigger: {t['trigger']} -> Action: {t['action'].get('value', 'LLM call')}")

        # 调用LLM进行意图匹配
        best_match = self.llm_client.match_intent(
            user_input, transitions_info
        )

        if best_match:
            # 找到匹配的转移并执行
            for transition in state_obj['transitions']:
                if (transition['type'] == 'on_transition' and
                        transition['trigger'] == best_match):
                    return self.execute_action(transition['action'],
                                               transition['next_state'])

        return "I'm not sure how to help with that. Can you rephrase?"


class LLMClient:
    pass