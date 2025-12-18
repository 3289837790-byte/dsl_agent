from dsl.parser import parse_dsl_file
from llm.intent_recognizer import IntentRecognizer


class DSLExecutor:
    def __init__(self, dsl_path):
        self.script = parse_dsl_file(dsl_path)
        self.recognizer = IntentRecognizer()
        self.current_state_name = 'start'
        self.is_finished = False

    def get_current_state(self):
        return self.script.states.get(self.current_state_name)

    def run(self):
        start_node = self.get_current_state()
        return start_node.response if start_node else "Error: Start state not found."

    def step(self, user_input):
        current_node = self.get_current_state()
        if current_node.is_end or not current_node.transitions:
            self.is_finished = True
            return None

        candidates = [{'intent': t.intent, 'desc': t.description} for t in current_node.transitions]

        # 简单处理：如果没有后续跳转，直接结束
        if not candidates:
            self.is_finished = True
            return None

        print(f"   [Debug] 正在识别意图，候选: {[c['intent'] for c in candidates]}")
        detected_intent = self.recognizer.recognize(user_input, candidates)

        if detected_intent == "unknown":
            return "抱歉，我没听懂，请重新说。"

        for trans in current_node.transitions:
            if trans.intent == detected_intent:
                self.current_state_name = trans.target_state
                new_state = self.get_current_state()
                if new_state.is_end:
                    self.is_finished = True
                return new_state.response

        return "系统错误：状态跳转失败。"