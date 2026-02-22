import re
import requests
import sys

class SolasRuntime:
    def __init__(self):
        self.context = {}

    def run(self, code):
        # 1. Strip comments
        code = re.sub(r'//.*', '', code)

        # 2. Transpilation Rules (Solas -> Python)
        rules = [
            # Keyword: emit
            (r'emit "(.*)"', r'print(f"\1")'),
            (r'emit (.*)', r'print(\1)'),

            # Keyword: grow (Fibonacci/Sequence Logic)
            (r'grow (\w+) to (\d+) \{ init \[(.*)\] step: (.*) \}',
             self._handle_grow),

            # Keyword: stream (API/Net Logic)
            (r'stream (\w+) from @net\.api\("(.*)"\) \{ (.*) \}',
             self._handle_stream),
        ]

        py_code = code
        for pattern, replacement in rules:
            if callable(replacement):
                py_code = re.sub(pattern, replacement, py_code)
            else:
                py_code = re.sub(pattern, replacement, py_code)

        # 3. Execution
        try:
            exec(py_code, {"requests": requests, "self": self}, self.context)
        except Exception as e:
            print(f"Solas Drift encountered: {e}")

    def _handle_grow(self, match):
        var, limit, start, step = match.groups()
        # Convert 'tail(2).sum' to Python logic
        step_py = step.replace("tail(2).sum", "data[-1] + data[-2]")
        return (f"data = [{start}]\n"
                f"for _ in range({limit}):\n"
                f"    data.append({step_py})\n"
                f"{var} = data")

    def _handle_stream(self, match):
        var, url, block = match.groups()
        # Basic drift/error handling logic
        return (f"try:\n"
                f"    res = requests.get('{url}')\n"
                f"    {var} = res.json()\n"
                f"    {block.strip()}\n"
                f"except:\n"
                f"    print('Drifting to fallback...')")

# --- EXECUTION ---
if __name__ == "__main__":
    solas_engine = SolasRuntime()

    # Test Script
    test_script = """
    // Testing the Light
    emit "Initializing Solas..."

    grow fib to 10 {
        init [0, 1]
        step: tail(2).sum
    }
    emit fib
    """

    solas_engine.run(test_script)