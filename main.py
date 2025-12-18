import os
import sys
from dotenv import load_dotenv  # 1. 导入 dotenv 加载工具
from dsl.executor import DSLExecutor

# 2. 强力修复路径 (防止报错 ModuleNotFoundError)
# 这两行代码保证了无论你在哪里运行 main.py，它都能找到 dsl 和 llm 包
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)


def main():
    # 3. 显式加载环境变量 (.env)
    # 这样程序一启动就会读取你的 API Key，不用等到调用 LLM 时才读
    load_dotenv()

    # 检查一下 Key 是否加载成功 (调试用，可删)
    if not os.getenv("LLM_API_KEY"):
        print("⚠️ 警告: 未检测到 LLM_API_KEY，请检查 .env 文件！")

    print("==========================================")
    print("   基于领域特定语言(DSL)的智能Agent系统")
    print("==========================================")

    # --- 新增的代码 START ---
    model_name = os.getenv("LLM_MODEL", "Unknown-Model")
    base_url = os.getenv("LLM_BASE_URL", "Unknown-URL")

    print(f"🚀 AI 引擎加载中...")
    print(f"🔧 服务提供商: SiliconFlow (硅基流动)")
    print(f"🧠 当前模型: {model_name}")  # 这里会显示 DeepSeek-V3
    print(f"🔗 接口地址: {base_url}")
    print("==========================================")
    # --- 新增的代码 END ---

    # 4. 列出可用脚本
    script_dir = "scripts"
    if not os.path.exists(script_dir):
        os.makedirs(script_dir)

    files = [f for f in os.listdir(script_dir) if f.endswith('.rsl') or f.endswith('.dsl')]

    if not files:
        print(f"错误：在 {script_dir} 目录下没有找到脚本文件。")
        return

    print("请选择要加载的业务场景：")
    for idx, f in enumerate(files):
        print(f"{idx + 1}. {f}")

    # 5. 用户选择脚本
    try:
        choice_str = input("\n请输入序号: ").strip()
        if not choice_str:
            choice = 0  # 默认选第一个
        else:
            choice = int(choice_str) - 1

        selected_file = os.path.join(script_dir, files[choice])
    except (ValueError, IndexError):
        print("输入无效，默认加载第一个脚本。")
        selected_file = os.path.join(script_dir, files[0])

    print(f"\n正在加载脚本: {selected_file} ...")

    try:
        # 6. 初始化执行器
        executor = DSLExecutor(selected_file)

        # 7. 开始对话循环
        print(f"Domain: {executor.script.domain}")
        print("-" * 30)

        # 获取第一句话
        bot_response = executor.run()
        print(f"Bot: {bot_response}")

        while not executor.is_finished:
            user_input = input("User: ").strip()

            if user_input.lower() in ['exit', 'quit', 'q']:
                print("对话结束。")
                break

            if not user_input:
                continue

            # 执行一步
            bot_response = executor.step(user_input)

            if bot_response:
                print(f"Bot: {bot_response}")

        print("-" * 30)
        print("流程结束 (End of Conversation)")

    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()