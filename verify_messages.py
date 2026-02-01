import asyncio
from main import run_backend

def test_messages():
    print("Running procurement...")
    _, _, _, _, _, res = run_backend(100)
    print(f"\nCaptured {len(res.agent_messages)} messages:")
    for m in res.agent_messages:
        print(f"[{m['agent']}] {m['message']}")

if __name__ == "__main__":
    test_messages()
