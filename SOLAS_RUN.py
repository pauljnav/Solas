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
        var, url, block = match.groups()
        headers, retries = self._handle_net_logic(block)

        # Clean and indent
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        logic = "\n".join(["        " + l for l in lines if not any(k in l for k in ['secure', 'retry'])])

        # Use triple quotes for the block to prevent any quote nesting errors
        return f"""
for _ in range({retries}):
    try:
        res = requests.get('{url}', headers={headers})
        res.raise_for_status()
        {var} = res.json()
{logic}
        break
    except Exception as e:
        if _ == {retries} - 1: print(f"Drifting: {{e}}")
"""

    def run(self, script):
        import textwrap
        script = textwrap.dedent(script).strip()
        script = re.sub(r'//.*', '', script)

        script = self._handle_data(script)
        script = re.sub(r'grow (\w+) to (\d+) \{ init \[(.*)\] step: (.*) \}', self._handle_grow, script)
        script = re.sub(r'stream (\w+) from @net\.(?:api|stream)\("(.*)"\) \{(.*?)\}', self._handle_stream, script, flags=re.DOTALL)

        # FIXED EMIT: Uses a safer template that doesn't care about internal quotes
        script = re.sub(r'emit "(.*)"', r'print(f"""\1""")', script)
        script = re.sub(r'emit ([^"\s]+)', r'print(\1)', script)

        try:
            # We must pass the current storage into the exec globals
            exec(script, {"requests": requests, "self": self}, self.context)
        except Exception as e:
            # If it fails, we need to see the "Iron" code it built
            print("--- GENERATED PYTHON (DEBUG) ---")
            print(script)
            print("--------------------------------")
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