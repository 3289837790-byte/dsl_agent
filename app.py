import streamlit as st
import os
import sys

# 路径适配
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from dsl.executor import DSLExecutor
from llm.wrapper import LLMClient


# === 回调函数：状态重置 ===
def reset_state():
    """当用户改变配置时，自动清空会话状态"""
    if 'executor' in st.session_state:
        del st.session_state['executor']
    if 'messages' in st.session_state:
        del st.session_state['messages']


# === 页面配置 ===
st.set_page_config(page_title="DSL智能客服系统", layout="wide")
st.title("🤖 基于 DSL 的多场景智能客服")

# === 侧边栏：开发者调试面板 ===
with st.sidebar:
    st.header("🔧 开发者调试面板")
    st.info("💡 提示：修改下方配置将自动重置当前会话。")

    st.markdown("---")

    # 1. 选择脚本 (绑定 on_change 自动重置)
    st.subheader("1. 业务场景装载")
    script_dir = "scripts"
    if not os.path.exists(script_dir):
        os.makedirs(script_dir)

    files = [f for f in os.listdir(script_dir) if f.endswith('.rsl')]
    selected_script = st.selectbox(
        "选择 DSL 脚本文件",
        files,
        on_change=reset_state  # <--- 关键点：变动即重置
    )

    # 2. 选择模式 (绑定 on_change 自动重置)
    st.subheader("2. 智能引擎配置")
    run_mode = st.radio(
        "选择运行内核",
        ["真实大模型 (DeepSeek)", "本地测试桩 (Stub)"],
        help="Stub模式不消耗Token，用于快速回归测试；Real模式调用远程API。",
        on_change=reset_state  # <--- 关键点：变动即重置
    )
    # 根据选项确定布尔值
    use_stub = True if "Stub" in run_mode else False

    st.markdown("---")

    # 仅保留一个手动重开按钮，用于同配置下的重试
    if st.button("🔄 手动重启会话", use_container_width=True):
        reset_state()
        st.rerun()

# === 核心逻辑：初始化 Session State ===
if "messages" not in st.session_state:
    st.session_state.messages = []

# 只有当 executor 不存在时才初始化 (保证会话连续性)
if "executor" not in st.session_state and selected_script:
    # 初始化 LLM 和 解释器
    script_path = os.path.join(script_dir, selected_script)

    try:
        # 传入 use_stub 参数
        client = LLMClient(use_stub=use_stub)
        executor = DSLExecutor(script_path, client)

        # 获取第一句开场白
        welcome_msg = executor.run()

        # 存入 Session
        st.session_state.executor = executor
        st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

    except Exception as e:
        st.error(f"❌ 系统初始化失败: {e}")

# === 聊天界面渲染 ===
# 1. 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 2. 处理用户输入
if prompt := st.chat_input("请输入您的回复..."):
    # 显示用户消息
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 调用解释器
    if 'executor' in st.session_state:
        agent = st.session_state.executor

        # 动态显示加载状态
        loading_text = "⚡ 规则引擎正在极速匹配..." if use_stub else "🧠 AI 大模型正在思考..."

        with st.spinner(loading_text):
            try:
                # 为了防止网络极快时闪烁太快看不清，Stub模式下可选择性保留极短延迟（可选）
                # import time; time.sleep(0.3)
                reply = agent.step(prompt)
            except Exception as e:
                reply = f"系统错误: {e}"

        # 显示机器人回复
        with st.chat_message("assistant"):
            st.write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

        # 检查是否结束
        if agent.is_finished:
            st.success("✅ 当前业务流程已结束，如需重新演示，请点击左侧【手动重启会话】或切换脚本。")