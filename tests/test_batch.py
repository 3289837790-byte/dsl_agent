import os
import sys
import time

# ================= 配置区 =================
# True = 测试桩模式 (提交作业、截图用这个)
# False = 真实模式 (演示用这个)
USE_STUB = True
# ==========================================

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dsl.executor import DSLExecutor
from llm.wrapper import get_llm_client


def run_batch_test(dsl_script_rel_path, test_case_file_rel_path):
    dsl_path = os.path.join(project_root, dsl_script_rel_path)
    case_path = os.path.join(project_root, test_case_file_rel_path)
    case_name = os.path.basename(test_case_file_rel_path)

    print(f"\n📄 正在测试场景: {case_name}")

    if not os.path.exists(dsl_path):
        print(f"   ⚠️ 跳过 (缺少脚本): {dsl_script_rel_path}")
        return
    if not os.path.exists(case_path):
        print(f"   ⚠️ 跳过 (缺少测试数据): {test_case_file_rel_path}")
        return

    # 初始化
    client = get_llm_client(use_stub=USE_STUB)
    try:
        executor = DSLExecutor(dsl_path, llm_client=client)
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return

    # 运行开场白
    print(f"   🤖 Bot开场: {executor.run()}")

    stats = {"pass": 0, "fail": 0}

    with open(case_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if '|||' not in line or line.strip().startswith('#'): continue

            user_input, expected_keyword = line.split('|||')
            user_input = user_input.strip()
            expected_keyword = expected_keyword.strip()

            actual_reply = executor.step(user_input)
            if not actual_reply: actual_reply = "（无回复）"

            is_pass = expected_keyword in actual_reply
            status_icon = "✅" if is_pass else "❌"

            if is_pass:
                stats["pass"] += 1
            else:
                stats["fail"] += 1

            print(f"   [{line_num}] {status_icon} 输入: {user_input:<10} | 预期: {expected_keyword:<6}")
            if not is_pass:
                print(f"      L--> 实际回复: {actual_reply}")

    total = stats["pass"] + stats["fail"]
    print(f"   📊 结果: {stats['pass']}/{total} 通过")


if __name__ == "__main__":
    print("=" * 60)
    print(f"🚀 全场景自动化回归测试 (模式: {'Stub/测试桩' if USE_STUB else 'Real/大模型'})")
    print("=" * 60)

    # ---------------------------------------------------------
    # 场景 1: IT 技术支持 (3个分支)
    # ---------------------------------------------------------
    print("\n[Scnenario 1: IT Support]")
    # 分支 A: 蓝屏
    run_batch_test("scripts/tech_support_dsl.rsl", "tests/test_data/tech_cases_blue_screen.txt")
    # 分支 B: 断网
    if os.path.exists(os.path.join(project_root, "tests/test_data/tech_cases_network.txt")):
        run_batch_test("scripts/tech_support_dsl.rsl", "tests/test_data/tech_cases_network.txt")
    # 分支 C: 黑屏/电源 (新增!)
    if os.path.exists(os.path.join(project_root, "tests/test_data/tech_cases.txt")):
        run_batch_test("scripts/tech_support_dsl.rsl", "tests/test_data/tech_cases.txt")

    # ---------------------------------------------------------
    # 场景 2: 电商客服 (2个分支)
    # ---------------------------------------------------------
    print("\n[Scnenario 2: E-Commerce]")
    run_batch_test("scripts/ecommerce_dsl.rsl", "tests/test_data/ecommerce_cases.txt")
    if os.path.exists(os.path.join(project_root, "tests/test_data/ecommerce_logistics.txt")):
        run_batch_test("scripts/ecommerce_dsl.rsl", "tests/test_data/ecommerce_logistics.txt")

    # ---------------------------------------------------------
    # 场景 3: 电信客服 (2个分支)
    # ---------------------------------------------------------
    print("\n[Scnenario 3: Telecom]")
    run_batch_test("scripts/telecom_dsl.rsl", "tests/test_data/telecom_cases.txt")
    if os.path.exists(os.path.join(project_root, "tests/test_data/telecom_upgrade.txt")):
        run_batch_test("scripts/telecom_dsl.rsl", "tests/test_data/telecom_upgrade.txt")