import re
import requests
import os

class SolasRuntime:
    def __init__(self):
        # Simulated environment variables for @env
        self.env = {"api_key": "SOLAS_DEMO_TOKEN_123"}
        self.context = {}
        self.storage = {}

    def _handle_net_logic(self, block):
        """Extracts security and retry metadata from a Solas block."""
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
        """Translates store/recall intents into dictionary persistence."""
        store_pattern = r'store (\w+) as (\w+)'
        recall_pattern = r'recall (\w+) into (\w+)'

        script = re.sub(store_pattern, r'self.storage["\2"] = \1', script)
        script = re.sub(recall_pattern, r'\2 = self.storage.get("\1")', script)
        return script

    def _handle_grow(self, match):
        """Translates growth patterns into iterative logic."""
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

        # Clean metadata lines to prevent Python SyntaxErrors
        cleaned_block = re.sub(r'(secure with|retry).*', '', block).strip()

        return (f"for _ in range({retries}):\n"
                f"    try:\n"
                f"        res = requests.get('{url}', headers={headers})\n"
                f"        res.raise_for_status()\n"
                f"        {var} = res.json()\n"
                f"        {cleaned_block}\n"
                f"        break\n"
                f"    except Exception as e:\n"
                f"        if _ == {retries} - 1:\n"
                f"            print(f'Drifting from @net error: {{e}}')")

    def run(self, script):
        """The core transpilation and execution engine."""
        # 1. Cleanse: Strip comments
        script = re.sub(r'//.*', '', script)

        # 2. Transpile: Order matters here
        script = self._handle_data(script)

        script = re.sub(r'grow (\w+) to (\d+) \{ init \[(.*)\] step: (.*) \}',
                        self._handle_grow, script)

        script = re.sub(r'stream (\w+) from @net\.(?:api|stream)\("(.*)"\) \{(.*?)\}',
                        self._handle_stream, script, flags=re.DOTALL)

        # Handle 'emit' (supports strings and variables)
        script = re.sub(r'emit "(.*)"', r'print(f"\1")', script)
        script = re.sub(r'emit ([^"\s]+)', r'print(\1)', script)

        # 3. Execute
        try:
            # We pass 'self' so the script can access self.storage and self.env
            exec(script, {"requests": requests, "self": self}, self.context)
        except Exception as e:
            print(f"Solas Critical Failure: {e}")

# --- DEMONSTRATION ---
if __name__ == "__main__":
    engine = SolasRuntime()

    solas_code = """
    // Intent: Initialize and store author
    emit "Solas Engine v1.0 Active"
    store "Paul Naughton" as creator

    // Intent: Fetch external data
    stream todo from @net.api("https://jsonplaceholder.typicode.com/todos/1") {
        retry(2)
        emit "Task: {todo['title']}"
    }

    // Intent: Recall and display author
    recall creator into user
    emit "Architect: {user}"

    // Intent: Generate sequence
    grow sequence to 5 {
        init [1, 1]
        step: tail(2).sum
    }
    emit sequence
    """

    engine.run(solas_code)