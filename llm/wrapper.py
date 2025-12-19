import os
import json
import urllib.request
import urllib.error
import time
from dotenv import load_dotenv


class LLMClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL")
        self.model = os.getenv("LLM_MODEL")

        self.base_url = self.base_url.rstrip('/')
        self.api_url = f"{self.base_url}/v1/chat/completions" if not self.base_url.endswith(
            "/v1") else f"{self.base_url}/chat/completions"

        proxy_url = os.getenv("https_proxy") or os.getenv("http_proxy")
        if proxy_url:
            proxy_handler = urllib.request.ProxyHandler({'http': proxy_url, 'https': proxy_url})
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)

    def chat(self, prompt, retry_count=3):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }

        for attempt in range(retry_count):
            try:
                # --- 核心改动 1: 基础冷却时间增加到 3 秒 ---
                # 对于免费版 API，慢就是稳
                time.sleep(3.0)

                req = urllib.request.Request(
                    self.api_url,
                    data=json.dumps(data).encode('utf-8'),
                    headers=headers
                )
                with urllib.request.urlopen(req, timeout=30) as response:
                    res_json = json.loads(response.read().decode('utf-8'))
                    return res_json['choices'][0]['message']['content'].strip()

            except urllib.error.HTTPError as e:
                error_detail = e.read().decode('utf-8')
                # --- 核心改动 2: 遇到 403/429 报错，直接死等 25 秒 ---
                # 这通常意味着这一分钟额度用完了，等 25 秒跨入下一个分钟窗口
                if (e.code == 403 or e.code == 429) and attempt < retry_count - 1:
                    wait_time = 25
                    print(f"\n[!] 触发额度限制 (RPM)，正在执行深度冷却 {wait_time} 秒以解锁...")
                    time.sleep(wait_time)
                    continue

                print(f"❌ LLM 调用最终失败 (HTTP {e.code}): {error_detail}")
                return "Error"
            except Exception as e:
                print(f"❌ 网络错误: {e}")
                return "Error"
        return "Error"

    def recognize_intent(self, user_input, choices):
        # 简化 Prompt，减少 Token 消耗，有时能稍微缓解频率压力
        prompt = f"Categorize intent. Input: '{user_input}'. Choices: {choices}. Return ONLY the word."
        result = self.chat(prompt)

        if result == "Error": return "unknown"

        # 增强清理逻辑
        clean_result = result.lower().replace(".", "").replace("\"", "").strip()
        for choice in choices:
            if choice.lower() in clean_result:
                return choice
        return "unknown"