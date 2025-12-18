import streamlit as st
import os
import sys

# 1. 路径修复
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from dsl.executor import DSLExecutor

# --- 页面配置 ---
st.set_page_config(page_title="智能客服 Agent", page_icon="🤖")
st.title("🤖 基于 DSL 的多业务智能客服")

# --- 侧边栏：选择脚本 ---
st.sidebar.header("配置面板")
script_dir = "scripts"
if not os.path.exists(script_dir):
    os.makedirs(script_dir)

files = [f for f in os.listdir(script_dir) if f.endswith('.rsl') or f.endswith('.dsl')]
selected_script = st.sidebar.selectbox("选择业务场景脚本", files)

# --- 初始化 Session State (保持对话状态) ---
if "executor" not in st.session_state or st.session_state.get("current_script") != selected_script:
    # 如果换了脚本，或者第一次启动，重新加载 Executor
    script_path = os.path.join(script_dir, selected_script)
    st.session_state.executor = DSLExecutor(script_path)
    st.session_state.current_script = selected_script
    st.session_state.messages = []

    # 获取开场白
    initial_msg = st.session_state.executor.run()
    st.session_state.messages.append({"role": "assistant", "content": initial_msg})

# --- 显示历史消息 ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- 处理用户输入 ---
if prompt := st.chat_input("请输入您的问题..."):
    # 1. 显示用户输入
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. 调用 Executor 处理
    executor = st.session_state.executor

    if not executor.is_finished:
        with st.spinner("AI 正在识别意图并查询规则引擎..."):
            response = executor.step(prompt)

        if response:
            with st.chat_message("assistant"):
                st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

        if executor.is_finished:
            st.success("对话流程已结束。您可以更换脚本或刷新页面重新开始。")
    else:
        st.warning("对话已经结束了，请刷新页面重置。")

# --- 侧边栏显示当前状态 (调试用) ---
st.sidebar.markdown("---")
st.sidebar.subheader("当前状态监控")
st.sidebar.code(f"State: {st.session_state.executor.current_state_name}")
st.sidebar.info("这是一个基于 DSL 解析器 + LLM 意图识别的混合架构系统。")