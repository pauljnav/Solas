import re
import requests
import os

class SolasRuntime:
    def __init__(self):
        # Simulated environment variables for @env
        self.env = {"api_key": "SOLAS_DEMO_TOKEN_123"}
        self.context = {}

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

        # Clean the block of the metadata lines so they don't cause Python errors
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
                f"            print(f'Drifting from error: {{e}}')")

    def run(self, script):
        # 1. Strip comments
        script = re.sub(r'//.*', '', script)

        # 2. Sequential Transpilation
        # Handle 'grow'
        script = re.sub(r'grow (\w+) to (\d+) \{ init \[(.*)\] step: (.*) \}',
                        self._handle_grow, script)

        # Handle 'stream'
        script = re.sub(r'stream (\w+) from @net\.(?:api|stream)\("(.*)"\) \{(.*?)\}',
                        self._handle_stream, script, flags=re.DOTALL)

        # Handle 'emit'
        script = re.sub(r'emit "(.*)"', r'print(f"\1")', script)
        script = re.sub(r'emit (\w+)', r'print(\1)', script)

        # 3. Final Execution
        try:
            exec(script, {"requests": requests, "self": self}, self.context)
        except Exception as e:
            print(f"Solas Critical Failure: {e}")

# --- DEMONSTRATION ---
if __name__ == "__main__":
    engine = SolasRuntime()

    solas_code = """
    // Intent: Securely fetch data and grow a sequence
    emit "Solas Engine v1.0 Active"

    stream data from @net.api("https://jsonplaceholder.typicode.com/todos/1") {
        secure with @env.api_key
        retry(2)
        emit "Network Success: {data['title']}"
    }

    grow sequence to 5 {
        init [1, 1]
        step: tail(2).sum
    }
    emit sequence
    """

    engine.run(solas_code)