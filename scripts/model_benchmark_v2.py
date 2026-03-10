#!/usr/bin/env python3
"""
OpenClaw 大模型性能基准测试 V2

使用 OpenClaw CLI 测试所有已配置模型的响应速度和 Token 使用量。
"""

import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

# 模型列表
MODELS = [
    "nvidia/z-ai/glm4.7",
    "nvidia/minimaxai/minimax-m2.1",
    "groq/llama-3.3-70b-versatile",
    "coding-aliyuncs/kimi-k2.5",
    "custom-coding-dashscope-aliyuncs-com/qwen3.5-plus"
]

# 测试提示词
TEST_PROMPTS = [
    {
        "name": "简单中文",
        "prompt": "请用中文简单介绍一下你自己，不超过50字。"
    },
    {
        "name": "简单英文",
        "prompt": "Introduce yourself in English, no more than 50 words."
    },
    {
        "name": "代码任务",
        "prompt": "用Python写一个计算斐波那契数列第n项的函数。"
    },
    {
        "name": "逻辑推理",
        "prompt": "有5个苹果，小明吃了2个，小红拿了1个，还剩几个？请说明推理过程。"
    }
]

def test_model_with_cli(model, prompt):
    """使用 OpenClaw CLI 测试单个模型"""
    # 发送测试消息到当前 session
    cmd = f'openclaw send --message="{prompt}" --model="{model}"'

    start_time = time.time()

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        end_time = time.time()

        response_time = round(end_time - start_time, 3)

        return {
            "model": model,
            "prompt": prompt,
            "success": result.returncode == 0,
            "response_time": response_time,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            "model": model,
            "prompt": prompt,
            "success": False,
            "response_time": 30.0,
            "error": "Timeout",
            "stdout": "",
            "stderr": ""
        }
    except Exception as e:
        return {
            "model": model,
            "prompt": prompt,
            "success": False,
            "response_time": 0,
            "error": str(e),
            "stdout": "",
            "stderr": ""
        }

def get_session_stats():
    """获取当前 session 的 stats"""
    try:
        cmd = "openclaw status --json 2>&1 | grep -A 20 'Sessions'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return str(e)

def main():
    """主测试函数"""
    results = []

    print("🧪 OpenClaw 大模型性能基准测试 V2")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试模型数: {len(MODELS)}")
    print(f"测试场景数: {len(TEST_PROMPTS)}")
    print("=" * 80)

    for model in MODELS:
        print(f"\n{'='*60}")
        print(f"🧪 测试模型: {model}")
        print(f"={'='*60}")

        for test in TEST_PROMPTS:
            print(f"\n📝 测试: {test['name']}")
            print(f"   提示: {test['prompt'][:50]}...")

            result = test_model_with_cli(model, test["prompt"])
            results.append(result)

            if result["success"]:
                print(f"   ✅ 成功 - 响应时间: {result['response_time']}s")
            else:
                print(f"   ❌ 失败: {result.get('error', 'Unknown')}")

            time.sleep(1)  # 避免过于频繁的请求

    # 保存结果
    output_dir = Path("/root/.openclaw/workspace/data/benchmark")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"model_benchmark_v2_{timestamp}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n\n{'='*60}")
    print(f"📊 测试完成！结果已保存到: {output_file}")
    print(f"={'='*60}")

    # 生成汇总报告
    generate_summary(results)

def generate_summary(results):
    """生成汇总报告"""
    print("\n\n📈 性能对比汇总\n")

    # 按模型分组
    model_stats = {}
    for r in results:
        model_id = r["model"]
        if model_id not in model_stats:
            model_stats[model_id] = {
                "total": 0,
                "success": 0,
                "avg_response_time": 0,
                "tests": []
            }
        model_stats[model_id]["total"] += 1
        model_stats[model_id]["tests"].append(r)
        if r["success"]:
            model_stats[model_id]["success"] += 1
            model_stats[model_id]["avg_response_time"] += r["response_time"]

    print(f"{'模型':<50} {'成功率':<10} {'平均响应'}")
    print("-" * 80)

    for model_id, stats in sorted(model_stats.items()):
        success_rate = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
        avg_time = stats["avg_response_time"] / stats["success"] if stats["success"] > 0 else 0
        print(f"{model_id:<50} {success_rate:<9.1f}% {avg_time:.3f}s")

    # 性能排名
    print("\n🏆 成功率和响应速度排名：")
    successful_models = [(m, s["success"], s["avg_response_time"] / s["success"] if s["success"] > 0 else 0) for m, s in model_stats.items()]

    # 按成功率排序
    successful_models.sort(key=lambda x: (-x[1], x[2]))

    for i, (model, success, avg_time) in enumerate(successful_models, 1):
        success_rate = (success / model_stats[model]["total"] * 100)
        if success > 0:
            print(f"  {i}. {model} - 成功率 {success_rate:.1f}%, 响应时间 {avg_time:.3f}s")
        else:
            print(f"  {i}. {model} - 成功率 {success_rate:.1f}% (所有测试失败)")

if __name__ == "__main__":
    main()
