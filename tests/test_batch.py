import sys
import os

# 1. 路径修复
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, '..'))

from dsl.executor import DSLExecutor


def run_batch_test(dsl_script, test_case_file):
    print(f"\n{'=' * 20} 批量测试启动 {'=' * 20}")
    print(f"[*] 脚本文件: {dsl_script}")
    print(f"[*] 用例文件: {test_case_file}")

    # 检查文件
    if not os.path.exists(dsl_script) or not os.path.exists(test_case_file):
        print("[!] 错误: 文件路径不存在")
        return

    # 初始化执行器
    executor = DSLExecutor(dsl_script)
    print(f"[*] Bot 初始化成功 (Domain: {executor.script.domain})")
    print(f"Bot (Start): {executor.run()}")
    print("-" * 60)

    # 读取测试用例
    try:
        with open(test_case_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"[!] 读取用例文件失败: {e}")
        return

    total_steps = 0
    passed_steps = 0

    for line in lines:
        line = line.strip()
        # 跳过注释和空行
        if not line or line.startswith('#'):
            continue

        total_steps += 1

        # 解析格式: 输入 ||| 期望关键词
        try:
            if '|||' not in line:
                print(f"[!] 格式错误跳过 (缺少 |||): {line}")
                continue

            user_input, expected_keyword = line.split('|||')
            user_input = user_input.strip()
            expected_keyword = expected_keyword.strip()
        except ValueError:
            print(f"[!] 解析错误跳过: {line}")
            continue

        # 执行交互
        try:
            actual_response = executor.step(user_input)
        except Exception as e:
            print(f"[!] 执行出错: {e}")
            actual_response = ""

        # 验证结果 (断言)
        # 只要实际回复不为空，且包含关键词，就算通过
        if actual_response and expected_keyword in actual_response:
            print(f"[PASS] 输入: '{user_input}'")
            print(f"       -> 期望包含: '{expected_keyword}'")
            print(f"       -> 实际回复: '{actual_response}'")
            passed_steps += 1
        else:
            print(f"[FAIL] 输入: '{user_input}'")
            print(f"       -> 期望包含: '{expected_keyword}'")
            print(f"       -> 实际回复: '{actual_response}'")

    print("-" * 60)
    print(f"测试总结: 总计 {total_steps} 个步骤, 通过 {passed_steps} 个")
    if total_steps > 0 and total_steps == passed_steps:
        print("结果: 全部通过 (ALL GREEN)")
    else:
        print("结果: 存在失败用例")
    print(f"{'=' * 50}\n")


if __name__ == "__main__":
    # 运行批量测试

    # 1. 测试电商
    run_batch_test(
        dsl_script="scripts/ecommerce_dsl.rsl",
        test_case_file="tests/test_data/ecommerce_cases.txt"
    )

    # 2. 测试电信
    run_batch_test(
        dsl_script="scripts/telecom_dsl.rsl",
        test_case_file="tests/test_data/telecom_cases.txt"
    )

    # 3. 测试 IT 支持
    run_batch_test(
        dsl_script="scripts/tech_support_dsl.rsl",
        test_case_file="tests/test_data/tech_cases.txt"
    )
