# tests/run_all.py
# ==========================================
#
# Spustí všetky Python testy:
#   1. run_create_delete_child.py
#   2. run_create_app_delete.py
#   3. run_zs_prihlaska.py
#
# Ak ktorýkoľvek FAILNE → run_all.py sa ukončí chybou.

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import subprocess


def run_test(script_name):
    print(f"\n========================================")
    print(f"▶️  Spúšťam test: {script_name}")
    print("========================================\n")

    result = subprocess.run(
        ["python3", os.path.join(os.path.dirname(__file__), script_name)],
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    if result.returncode != 0:
        print(f"\n❌ TEST FAILED: {script_name}\n")
        sys.exit(result.returncode)
    else:
        print(f"\n✔️ OK: {script_name}\n")


def main():
    run_test("run_create_delete_child.py")
    run_test("run_create_app_delete.py")
    run_test("run_zs_prihlaska.py")

    print("\n========================================")
    print("🎉 ALL TESTS PASSED — všetky scenáre sú OK!")
    print("========================================\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
