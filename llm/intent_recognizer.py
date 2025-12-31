# llm/intent_recognizer.py
from .wrapper import get_llm_client

class IntentRecognizer:
    def __init__(self, llm_client=None):
        self.client = llm_client if llm_client else get_llm_client()

    def recognize(self, user_input, candidates):
        if self.client.__class__.__name__ == 'LLMStub':
            return self.client.chat(user_input)

        # 大模型模式：加入详细描述
        options = "\n".join([f"- {c['intent']}: {c['desc']}" for c in candidates])
        prompt = (
            f"你是一个意图识别专家。用户输入: \"{user_input}\"\n"
            f"候选列表:\n{options}\n"
            f"请只返回最匹配的意图代码单词。不匹配返回 'unknown'。"
        )
        res = self.client.chat(prompt)
        clean_res = res.lower().strip().replace("'", "").replace('"', "")
        for c in candidates:
            if c['intent'].lower() in clean_res: return c['intent']
        return "unknown"