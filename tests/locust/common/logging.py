# tests/locust/common/logging.py

def header(title):
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def flow_start(flow_name, child_name=None):
    print("\n" + "=" * 60)
    print(f"▶▶▶ START FLOW: {flow_name}")
    if child_name:
        print(f"👤 Dieťa: {child_name}")
    print("=" * 60)

def flow_end(flow_name):
    print("-" * 60)
    print(f"◀◀◀ END FLOW: {flow_name}\n")

def step_idx(prefix, idx, label, status):
    print(f"[{prefix}][{idx:02d}] {label:<35} {status}")
