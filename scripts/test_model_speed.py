#!/usr/bin/env python3
"""
快速模型测试脚本

通过发送相同问题到不同模型来对比性能
"""

import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

# 所有模型
MODELS = [
    "nvidia/z-ai/glm4.7",
    "nvidia/minimaxai/minimax-m2.1",
    "groq/llama-3.3-70b-versatile",
    "coding-aliyuncs/kimi-k2.5",
    "custom-coding-dashscope-aliyuncs-com/qwen3.5-plus"
]

# 测试问题
TEST_QUESTIONS = [
    "1+1=? (只回答数字)",
    "写一个 Python Hello World 函数",
    "广州是哪个省的省会？",
    "Explain quantum computing in one sentence",
]

def test_single_model(model):
    """测试单个模型的所有问题"""
    print(f"\n{'─'*60}")
    print(f"🧪 测试模型: {model}")
    print(f"{'─'*60}")

    results = []

    for question in TEST_QUESTIONS:
        print(f"\n❓ 问题: {question}")
        print("   ⏳ 等待响应...")

        # 记录开始时间
        start_time = time.time()

        # 使用 openclaw send 测试（发送到当前 session）
        try:
            cmd = [
                "openclaw",
                "send",
                f"--model={model}",
                f"--message={question}"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            end_time = time.time()
            response_time = round(end_time - start_time, 3)

            if result.returncode == 0:
                print(f"   ✅ 成功 - {response_time}s")
                results.append({
                    "question": question,
                    "success": True,
                    "response_time": response_time,
                    "stdout": result.stdout[:200] if result.stdout else ""
                })
            else:
                error_msg = result.stderr.strip() or "Unknown error"
                print(f"   ❌ 失败 - {error_msg[:100]}")
                results.append({
                    "question": question,
                    "success": False,
                    "response_time": response_time,
                    "error": error_msg[:200]
                })

        except subprocess.TimeoutExpired:
            print(f"   ❌ 超时 (30s)")
            results.append({
                "question": question,
                "success": False,
                "response_time": 30.0,
                "error": "Timeout"
            })
        except Exception as e:
            print(f"   ❌ 异常: {str(e)[:100]}")
            results.append({
                "question": question,
                "success": False,
                "response_time": 0,
                "error": str(e)[:200]
            })

        time.sleep(0.5)  # 避免频繁请求

    return {
        "model": model,
        "results": results
    }

def main():
    """主函数"""
    print("=" * 70)
    print("🧪 OpenClaw 大模型测试")
    print("=" * 70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试模型: {len(MODELS)} 个")
    print(f"测试问题: {len(TEST_QUESTIONS)} 个")

    all_results = []

    # 测试每个模型
    for model in MODELS:
        result = test_single_model(model)
        all_results.append(result)

    # 计算统计
    print("\n\n" + "=" * 70)
    print("📊 测试结果汇总")
    print("=" * 70)

    print(f"\n{'模型':<50} {'成功/总数':<10} {'平均时间':<10}")
    print("-" * 70)

    for model_result in all_results:
        model = model_result["model"]
        results = model_result["results"]

        total = len(results)
        success_count = sum(1 for r in results if r["success"])
        success_rate = (success_count / total * 100) if total > 0 else 0

        successful_times = [r["response_time"] for r in results if r["success"]]
        avg_time = (sum(successful_times) / len(successful_times)) if successful_times else 0

        print(f"{model:<50} {success_count}/{total:<3} {avg_time:>8.3f}s")

    # 排名
    print("\n🏆 按成功率排序:")
    ranked = sorted(
        all_results,
        key=lambda x: (sum(1 for r in x["results"] if r["success"]), x["model"])
    )

    for i, model_result in enumerate(ranked, 1):
        model = model_result["model"]
        results = model_result["results"]
        success_count = sum(1 for r in results if r["success"])
        total = len(results)
        success_rate = (success_count / total * 100)

        if success_count > 0:
            avg_time = sum(r["response_time"] for r in results if r["success"]) / success_count
            print(f"  {i}. {model} - {success_rate:.0f} 成功率, 平均 {avg_time:.3f}s")
        else:
            print(f"  {i}. {model} - ❌ 全部失败")

    # 保存结果
    output_dir = Path("/root/.openclaw/workspace/data/benchmark")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"speed_test_{timestamp}.json"

    output_data = {
        "timestamp": timestamp,
        "models_tested": MODELS,
        "questions": TEST_QUESTIONS,
        "results": all_results
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n📁 完整结果已保存: {output_file}")
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
