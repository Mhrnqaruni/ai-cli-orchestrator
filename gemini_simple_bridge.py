import subprocess
import time
import json
import os
from datetime import datetime

class SimpleGeminiBridge:
    def __init__(self):
        self.command_file = "gemini_command.txt"
        self.response_file = "gemini_response.txt"
        self.status_file = "gemini_status.json"
        self.running = False

    def _update_status(self, status, message=""):
        """Update status file"""
        data = {
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        with open(self.status_file, 'w') as f:
            json.dump(data, f, indent=2)
        return data

    def send_to_gemini(self, message, timeout=120):
        """Send message to Gemini CLI using pipe (Gemini accepts piped stdin)"""
        print(f"\n[BRIDGE] Sending to Gemini: {message[:80]}...")
        self._update_status("sending", f"Sending: {message[:50]}...")

        try:
            result = subprocess.run(
                'gemini --yolo',
                shell=True,
                input=message,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd(),
                encoding='utf-8',
                errors='replace'
            )

            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr

            # Save response
            timestamp = datetime.now().strftime('%H:%M:%S')
            response_text = f"[{timestamp}] QUESTION: {message}\n\nRESPONSE:\n{output}\n"

            with open(self.response_file, 'w', encoding='utf-8') as f:
                f.write(response_text)

            self._update_status("response_ready", "Response available")
            print(f"[BRIDGE] Response received and saved")

            return output

        except subprocess.TimeoutExpired:
            error_msg = f"Gemini response timed out after {timeout} seconds"
            print(f"[BRIDGE] {error_msg}")
            self._update_status("timeout", error_msg)
            return None

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"[BRIDGE] {error_msg}")
            self._update_status("error", error_msg)
            return None

    def watch_for_commands(self):
        """Watch for commands from Claude Code"""
        print(f"\n[BRIDGE] Starting watchdog mode...")
        print(f"[BRIDGE] Monitoring: {self.command_file}")
        print(f"[BRIDGE] Responses saved to: {self.response_file}")
        print(f"[BRIDGE] Status updates in: {self.status_file}")
        print(f"\n[BRIDGE] Ready! Waiting for commands from Claude...\n")

        self._update_status("ready", "Waiting for commands")
        self.running = True
        last_mtime = 0

        # Ensure command file exists
        if not os.path.exists(self.command_file):
            open(self.command_file, 'a').close()

        while self.running:
            try:
                current_mtime = os.path.getmtime(self.command_file)

                if current_mtime > last_mtime:
                    last_mtime = current_mtime

                    with open(self.command_file, 'r', encoding='utf-8') as f:
                        command = f.read().strip()

                    if command and len(command) > 0:
                        print(f"[BRIDGE] New command detected!")
                        self.send_to_gemini(command)

                        # Clear command file
                        with open(self.command_file, 'w') as f:
                            f.write("")

                        print(f"[BRIDGE] Ready for next command\n")

                time.sleep(0.5)

            except KeyboardInterrupt:
                print("\n[BRIDGE] Stopped by user")
                break
            except Exception as e:
                print(f"[BRIDGE] Error in watchdog: {e}")
                time.sleep(1)

        self._update_status("stopped", "Bridge stopped")
        print("[BRIDGE] Watchdog stopped")

def main():
    print("=" * 60)
    print("GEMINI SIMPLE BRIDGE - Watchdog Mode")
    print("=" * 60)
    print("\nThis bridge allows Claude Code to interact with Gemini CLI")
    print("using file-based messaging.\n")
    print("How it works:")
    print("  1. Claude writes a command to gemini_command.txt")
    print("  2. This bridge detects it and pipes it to Gemini CLI")
    print("  3. Gemini's response is saved to gemini_response.txt")
    print("  4. Claude reads the response and decides next step\n")

    bridge = SimpleGeminiBridge()

    # Initial test
    print("[BRIDGE] Running initial test...")
    test_response = bridge.send_to_gemini("Hello, respond with one sentence confirming you are working.")
    if test_response:
        print(f"[BRIDGE] Test successful!\n")
    else:
        print(f"[BRIDGE] Test failed - check that 'gemini' is in your PATH\n")

    # Enter watchdog mode
    try:
        bridge.watch_for_commands()
    except KeyboardInterrupt:
        print("\n[BRIDGE] Interrupted by user")

if __name__ == "__main__":
    main()
