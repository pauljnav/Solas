import re
import requests
import textwrap
import sys

class SolasRuntime:
    def __init__(self):
        self.env = {"api_key": "SOLAS_DEMO_TOKEN_123"}
        self.context = {}
        self.storage = {}

    def _handle_net_logic(self, block):
        auth_match = re.search(r'secure with @env\.(\w+)', block)
        retry_match = re.search(r'retry\((\d+)\)', block)
        headers = {}
        if auth_match:
            env_key = auth_match.group(1)
            token = self.env.get(env_key, "MISSING_KEY")
            headers = {'Authorization': f'Bearer {token}'}
        retries = int(retry_match.group(1)) if retry_match else 1
        return headers, retries

    def _handle_data(self, script):
        script = re.sub(r'store (.*?) as (\w+)', r'self.storage["\2"] = \1', script)
        script = re.sub(r'recall (\w+) into (\w+)', r'\2 = self.storage.get("\1")', script)
        return script

    def _handle_grow(self, match):
        var, limit, start, step = match.groups()
        step_py = step.replace("tail(2).sum", "data[-1] + data[-2]")
        return (f"data = [{start}]\n"
                f"for _ in range({limit}):\n"
                f"    data.append({step_py})\n"
                f"{var} = data")

    def _handle_stream(self, match):
        """Translates network intents into resilient request blocks."""
        var, url, block = match.groups()
        headers, retries = self._handle_net_logic(block)

        # Split lines and strip ALL leading/trailing whitespace from each
        lines = [line.strip() for line in block.split('\n')]

        # Filter out keywords that are handled by the translator, keep the rest
        logic_lines = []
        for line in lines:
            if line and not any(k in line for k in ['secure with', 'retry']):
                # Force exactly 8 spaces of indentation for Python's try block
                logic_lines.append(f"        {line}")

        inner_logic = "\n".join(logic_lines)

        return (f"for _ in range({retries}):\n"
                f"    try:\n"
                f"        res = requests.get('{url}', headers={headers})\n"
                f"        res.raise_for_status()\n"
                f"        {var} = res.json()\n"
                f"{inner_logic}\n"
                f"        break\n"
                f"    except Exception as e:\n"
                f"        if _ == {retries} - 1:\n"
                f"            print(f'Drifting from @net error: {{e}}')")

    def run(self, script):
        # 1. Strip comments and normalize
        script = re.sub(r'//.*', '', script)

        # 2. Transpile
        script = self._handle_data(script)
        script = re.sub(r'grow (\w+) to (\d+) \{ init \[(.*)\] step: (.*) \}', self._handle_grow, script)
        script = re.sub(r'stream (\w+) from @net\.(?:api|stream)\("(.*)"\) \{(.*?)\}', self._handle_stream, script, flags=re.DOTALL)

        # Flexible emit: handles variables, dict access, and strings
        script = re.sub(r'emit "(.*)"', r'print(f"\1")', script)
        script = re.sub(r'emit ([^"\s]+)', r'print(\1)', script)

        # 3. Execute
        try:
            exec(script, {"requests": requests, "self": self}, self.context)
        except Exception as e:
            print(f"Solas Critical Failure: {e}")

if __name__ == "__main__":
    engine = SolasRuntime()

    # Check if a filename was provided: python SOLAS_RUN.py my_script.solas
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        try:
            with open(filename, 'r') as f:
                solas_code = f.read()
            print(f"--- Executing: {filename} ---")
            engine.run(solas_code)
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
    else:
        print("Usage: python SOLAS_RUN.py <filename.solas>")