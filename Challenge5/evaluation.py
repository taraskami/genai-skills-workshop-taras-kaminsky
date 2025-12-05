import os
import vertexai
from vertexai.evaluation import EvalTask

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)

EVAL_DATASET = [
    {
        "prompt": "What is the ADS phone number?",
        "response": "You can reach ADS statewide at 1-800-SNOW-ADS (1-800-766-9237).",
        "reference": "The ADS statewide phone number is 1-800-SNOW-ADS (1-800-766-9237).",
    },
    {
        "prompt": "How do I report an unplowed road?",
        "response": "You can report unplowed roads through the SnowLine app or by calling your regional ADS office.",
        "reference": "Report unplowed roads via the SnowLine app or contact your regional ADS office.",
    },
    {
        "prompt": "What is the SnowLine app?",
        "response": "SnowLine is the official ADS mobile app that provides real-time plow tracking, road conditions, and lets you report issues.",
        "reference": "SnowLine is ADS's mobile app for tracking plows and road conditions.",
    },
    {
        "prompt": "Does ADS handle school closures?",
        "response": "No, ADS does not make school closure decisions. That's handled by individual school districts based on local conditions.",
        "reference": "School closure decisions are made by individual school districts, not ADS.",
    },
    {
        "prompt": "When was ADS established?",
        "response": "The Alaska Department of Snow was established in 1959 when Alaska became a state.",
        "reference": "ADS was established in 1959.",
    },
]


def run_evaluation():
    
    eval_task = EvalTask(
        dataset=EVAL_DATASET,
        metrics=[
            "fluency",           # Language quality
            "coherence",         # Logical flow
            "safety",            # Safe content
            "groundedness",      # Factual accuracy
            "fulfillment",       # Answers the question
        ],
    )

    print("Running evaluation (this may take a minute)...")
    result = eval_task.evaluate()

    print("\n" + "=" * 60)
    print("  Results")
    print("=" * 60)
    
    print("\nSummary Metrics:")
    print("-" * 40)
    for metric, value in result.summary_metrics.items():
        print(f"  {metric}: {value:.3f}")
    
    print("\nPer-Sample Scores:")
    print("-" * 40)
    metrics_df = result.metrics_table
    print(metrics_df.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("  Evaluation complete!")
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    run_evaluation()
