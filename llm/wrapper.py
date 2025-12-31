import os
import json
import urllib.request
import urllib.error
import socket
import time
from dotenv import load_dotenv


class LLMClient:
    def __init__(self, use_stub=False):
        load_dotenv()
        env_mode = os.getenv("RUN_MODE", "real").lower()
        self.use_stub = use_stub or (env_mode == "stub")

        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.siliconflow.cn/v1")
        self.model = os.getenv("LLM_MODEL", "deepseek-ai/DeepSeek-V3")

        if "/v1" in self.base_url:
            self.api_url = self.base_url.rstrip("/") + "/chat/completions"
        else:
            self.api_url = self.base_url.rstrip("/") + "/v1/chat/completions"

        self.proxy_url = os.getenv("http_proxy")
        if self.proxy_url:
            proxy_handler = urllib.request.ProxyHandler({
                'http': self.proxy_url,
                'https': self.proxy_url
            })
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)

    def _local_stub_match(self, user_input, choices):
        """本地匹配逻辑 - 修正版"""
        for choice in choices:
            # 1. 关键词拆分
            keywords = choice.split('/')
            for kw in keywords:
                # 【核心修改】只保留单向匹配：用户输入必须包含关键词
                # 删除了 'or user_input in kw'，防止 "感兴趣" 匹配到 "不感兴趣"
                if kw in user_input:
                    return choice

            # 2. 数字特判 (保留)
            if user_input.isdigit() and ("订单" in choice or "单号" in choice):
                return choice
        return None

    def chat(self, prompt, retry_count=3):
        if self.use_stub: return None

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }

        for attempt in range(retry_count):
            try:
                if attempt > 0: time.sleep(1.5)
                req = urllib.request.Request(
                    self.api_url,
                    data=json.dumps(data).encode('utf-8'),
                    headers=headers
                )
                with urllib.request.urlopen(req, timeout=60) as response:
                    res_json = json.loads(response.read().decode('utf-8'))
                    return res_json['choices'][0]['message']['content'].strip()
            except Exception:
                pass
        return None

    def recognize_intent(self, user_input, choices):
        # 1. Stub 模式
        if self.use_stub:
            match = self._local_stub_match(user_input, choices)
            if match:
                print(f"   (⚡ Stub命中: '{user_input}' -> '{match}')")
                return match
            return "unknown"

        # 2. Real 模式
        print(f"   (🧠 大模型正在思考: '{user_input}'...)")

        prompt = f"用户输入:'{user_input}'\n候选:{choices}\n请选出最匹配的一项，只返回文字。"
        ai_result = self.chat(prompt)

        if ai_result:
            for choice in choices:
                if choice in ai_result:
                    return choice

        # 4. 降级
        fallback_match = self._local_stub_match(user_input, choices)
        if fallback_match:
            return fallback_match

        return "unknown"


def get_llm_client(use_stub=False):
    return LLMClient(use_stub=use_stub)