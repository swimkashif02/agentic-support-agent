import json
import sys
from agents.triage_agent import run_agent
from evals.grader import rule_based_grade, llm_judge_grade


def get_test_cases(mode: str) -> list:
    """Load test cases based on mode — all or failed only."""
    with open("evals/test_set.json") as f:
        all_cases = json.load(f)

    if mode == "failed":
        try:
            with open("evals/results.json") as f:
                previous_results = json.load(f)
            failed_ids = {r["test_id"] for r in previous_results if not r["passed"]}
            filtered = [t for t in all_cases if t["id"] in failed_ids]
            print(f"\n  Found {len(failed_ids)} previously failed tests")
            return filtered
        except FileNotFoundError:
            print("\n  No previous results found — running all tests instead")
            return all_cases

    return all_cases


def print_menu():
    print()
    print("=" * 60)
    print("  TECHCORP SUPPORT — EVAL RUNNER")
    print("=" * 60)
    print()
    print("  Select mode:")
    print()
    print("  1 — Run ALL 20 test cases")
    print("  2 — Run FAILED tests only")
    print("  0 — Exit")
    print()


def run_evals(mode: str = "all"):
    test_cases = get_test_cases(mode)

    if not test_cases:
        print("  No test cases to run.")
        return

    results = []
    passed = 0

    print()
    print("=" * 60)
    print(f"  RUNNING EVALS — {mode.upper()} ({len(test_cases)} tests)")
    print("=" * 60)

    for test in test_cases:
        print(f"\nTest {test['id']}: {test['input'][:50]}...")

        agent_output = run_agent(test["input"])

        rb_score  = rule_based_grade(test, agent_output)
        llm_score = llm_judge_grade(test["input"], agent_output.get("final_answer", ""))

        result = {
            "test_id":   test["id"],
            "input":     test["input"],
            "rb_score":  rb_score,
            "llm_score": llm_score,
            "passed":    rb_score["passed"]
        }
        results.append(result)

        if rb_score["passed"]:
            passed += 1
            print(f"  ✅ PASSED ({rb_score['score']}/{rb_score['max_score']})")
        else:
            print(f"  ❌ FAILED ({rb_score['score']}/{rb_score['max_score']})")
            for detail in rb_score["details"]:
                print(f"     {detail}")

    print(f"\n{'=' * 60}")
    print(f"  FINAL SCORE: {passed}/{len(test_cases)} = {passed/len(test_cases)*100:.0f}%")
    print(f"{'=' * 60}")

    # Merge results back into results.json
    if mode == "failed":
        try:
            with open("evals/results.json") as f:
                previous_results = json.load(f)
            rerun_ids = {r["test_id"] for r in results}
            merged = [r for r in previous_results if r["test_id"] not in rerun_ids]
            merged.extend(results)
            merged.sort(key=lambda x: x["test_id"])
            results = merged
        except FileNotFoundError:
            pass

    with open("evals/results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("  Results saved to evals/results.json")


if __name__ == "__main__":
    while True:
        print_menu()
        choice = input("  Enter your choice (0-2): ").strip()

        if choice == "1":
            run_evals(mode="all")
        elif choice == "2":
            run_evals(mode="failed")
        elif choice == "0":
            print("\n  Goodbye!\n")
            break
        else:
            print("\n  Invalid choice. Please enter 1, 2, or 0.")

        print()
        input("  Press Enter to return to the menu...")