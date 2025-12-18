import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv


class LLMClient:
    def __init__(self):
        # 加载配置
        load_dotenv()
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL")
        self.model = os.getenv("LLM_MODEL")

        # 修正 URL 格式 (防止拼写错误)
        if self.base_url.endswith("/v1"):
            self.api_url = f"{self.base_url}/chat/completions"
        else:
            self.api_url = f"{self.base_url}/v1/chat/completions"

        # 设置代理 (这就是为什么我们要用 urllib，因为它能完美兼容你的环境)
        self.proxy_url = os.getenv("http_proxy")
        if self.proxy_url:
            proxy_handler = urllib.request.ProxyHandler({
                'http': self.proxy_url,
                'https': self.proxy_url
            })
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)

    def chat(self, prompt):
        """发送对话给大模型"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "DSL-Agent/1.0"
        }

        # 构造请求数据
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,  # 设低一点，让AI回答更精准
            "max_tokens": 500
        }

        try:
            req = urllib.request.Request(
                self.api_url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers
            )
            with urllib.request.urlopen(req) as response:
                res_json = json.loads(response.read().decode('utf-8'))
                return res_json['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"❌ LLM 调用失败: {e}")
            return "Error"

    def recognize_intent(self, user_input, choices):
        """
        核心功能：意图识别
        输入: "我要退货", ["refund", "query"]
        输出: "refund"
        """
        prompt = f"""
        你是一个意图分类助手。
        用户输入: "{user_input}"
        可选的意图列表: {choices}

        请分析用户的意图，并从列表中选出一个最匹配的单词返回。
        如果都不匹配，返回 "unknown"。
        注意：只返回单词，不要加任何标点、不要加解释。
        """
        result = self.chat(prompt)
        # 清洗一下结果，防止AI话多
        for choice in choices:
            if choice in result:
                return choice
        return "unknown"