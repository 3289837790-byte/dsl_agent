import os
import sys
import time

# ================= 配置区 =================
# True  = 本地测试桩 (极速，⚡ 图标，不联网)
# False = 真实大模型 (智能，🧠 图标，联网)
USE_STUB = True
# ==========================================

# 路径适配
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from dsl.executor import DSLExecutor
from llm.wrapper import LLMClient


def list_scripts(script_dir):
    if not os.path.exists(script_dir):
        return []
    return [f for f in os.listdir(script_dir) if f.endswith(".rsl")]


def main():
    print("==========================================")
    print("   基于领域特定语言(DSL)的智能Agent系统")
    print("==========================================")

    # 1. 初始化 AI 引擎
    print(f"🚀 引擎加载中... (模式: {'Stub/本地桩' if USE_STUB else 'Real/大模型'})")
    try:
        # 使用配置区的开关
        llm_client = LLMClient(use_stub=USE_STUB)

        if USE_STUB:
            print(f"🔧 服务: Local Rule Engine (本地规则引擎)")
            print(f"⚡ 状态: 离线极速模式")
        else:
            print(f"🔧 服务: SiliconFlow (硅基流动)")
            print(f"🧠 模型: {llm_client.model}")

        print("✅ 接口连接就绪")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return

    script_dir = "scripts"

    while True:
        scripts = list_scripts(script_dir)
        if not scripts:
            print(f"❌ 错误: {script_dir} 文件夹为空")
            return

        print("\n" + "=" * 40)
        print("📍 请选择业务场景 (输入 q 退出)：")
        for i, f in enumerate(scripts, 1):
            print(f"   {i}. {f}")
        print("=" * 40)

        choice = input("请输入序号 > ").strip()

        if choice.lower() in ['q', 'quit', 'exit']:
            print("👋 再见！")
            break

        selected_script_path = None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(scripts):
                selected_script_path = os.path.join(script_dir, scripts[idx])
            else:
                print("⚠️ 序号无效")
                continue
        except ValueError:
            print("⚠️ 请输入数字")
            continue

        try:
            print(f"\n📂 正在加载: {scripts[idx]} ...")
            executor = DSLExecutor(selected_script_path, llm_client)
            print(f"✅ 解析成功! Domain: {executor.script.domain}")
        except Exception as e:
            print(f"❌ 解析失败: {e}")
            continue

        print("-" * 50)
        print(f"Bot: {executor.run()}")

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if user_input.lower() in ['back', 'menu', '返回']:
                    print("🔙 返回主菜单...")
                    break

                if user_input.lower() in ['exit', 'quit', '退出', 'q']:
                    print("👋 再见！")
                    sys.exit(0)

                if not user_input: continue

                reply = executor.step(user_input)
                print(f"Bot: {reply}")

                if executor.is_finished:
                    print("\n" + "-" * 30)
                    print("✅ 当前业务流程已结束")
                    print("-" * 30)
                    input("按回车键返回主菜单...")
                    break

            except KeyboardInterrupt:
                print("\n🔙 强制返回菜单")
                break
            except Exception as e:
                print(f"❌ 运行时错误: {e}")
                break


if __name__ == "__main__":
    main()