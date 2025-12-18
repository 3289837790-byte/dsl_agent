import json
from .wrapper import LLMClient


class IntentRecognizer:
    def __init__(self):
        self.client = LLMClient()

    def recognize(self, user_input, candidates):
        """
        user_input: 用户的自然语言输入
        candidates: 一个字典列表，例如 [{'intent': 'refund', 'desc': '申请退款'}, ...]
        返回: 匹配到的 intent 字符串，如果无法匹配返回 None
        """
        # 如果没有候选，直接返回 None
        if not candidates:
            return None

        # 构建提示词 (Prompt Engineering)
        # 核心技巧：要求 LLM 只输出 Key，不要废话
        options_str = "\n".join([f"- {c['intent']}: {c.get('desc', '')}" for c in candidates])

        prompt = (
            f"你是一个智能客服意图识别助手。请根据用户输入，从以下候选中选择最匹配的一个意图。\n"
            f"用户输入: \"{user_input}\"\n\n"
            f"候选意图:\n{options_str}\n\n"
            f"要求：\n"
            f"1. 必须且只能返回候选意图中的 'intent' 字段的值。\n"
            f"2. 如果用户输入与任何候选都不匹配，请返回 'unknown'。\n"
            f"3. 不要包含任何解释或标点符号，只输出意图代码。"
        )

        try:
            response = self.client.chat(prompt).strip()
            # 简单的清洗，防止 LLM 输出 "意图是: xxx"
            response = response.replace("'", "").replace('"', "").strip()

            # 验证返回是否有效
            valid_intents = [c['intent'] for c in candidates]
            if response in valid_intents:
                return response
            return "unknown"
        except Exception as e:
            print(f"[Intent Error] {e}")
            return None