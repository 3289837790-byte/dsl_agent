import os
import sys
from dsl.executor import DSLExecutor


def main():
    print("==========================================")
    print("   基于领域特定语言(DSL)的智能Agent系统")
    print("==========================================")

    # 1. 列出可用脚本
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

    # 2. 用户选择脚本
    try:
        choice = int(input("\n请输入序号: ")) - 1
        selected_file = os.path.join(script_dir, files[choice])
    except (ValueError, IndexError):
        print("输入无效，默认加载第一个脚本。")
        selected_file = os.path.join(script_dir, files[0])

    print(f"\n正在加载脚本: {selected_file} ...")

    try:
        # 3. 初始化执行器
        executor = DSLExecutor(selected_file)

        # 4. 开始对话循环
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