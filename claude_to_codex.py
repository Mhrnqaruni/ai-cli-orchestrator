import json
import time
import sys

def check_status():
    """Check Codex bridge status"""
    try:
        with open('codex_status.json', 'r') as f:
            status = json.load(f)
        return status
    except:
        return None

def send_to_codex(message, max_wait=120):
    """Send a message to Codex via the bridge and wait for response"""
    print(f"[CLAUDE] Sending to Codex: {message}")

    # Write command to file
    with open('codex_command.txt', 'w', encoding='utf-8') as f:
        f.write(message)

    print("[CLAUDE] Message sent, waiting for response...")

    # Wait for response
    start_time = time.time()
    last_status = None

    while time.time() - start_time < max_wait:
        status = check_status()
        if status and status.get('status') == 'response_ready':
            # Read response
            try:
                with open('codex_response.txt', 'r', encoding='utf-8') as f:
                    response = f.read()
                print(f"\n[CLAUDE] Got response from Codex:")
                print("=" * 60)
                print(response)
                print("=" * 60)
                return response
            except:
                pass

        # Show status updates
        if status and status != last_status:
            print(f"[CLAUDE] Status: {status.get('status')} - {status.get('message')}")
            last_status = status

        time.sleep(1)

    print("[CLAUDE] Timeout waiting for response")
    return None

def get_last_response():
    """Get the last response from Codex"""
    try:
        with open('codex_response.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        message = ' '.join(sys.argv[1:])
        send_to_codex(message)
    else:
        # Interactive mode
        print("Claude to Codex Interface")
        print("Type your message and press Enter")
        print("Type 'quit' to exit")
        print()

        while True:
            message = input("[CLAUDE] > ")
            if message.lower() in ['quit', 'exit', 'q']:
                break

            if message.strip():
                send_to_codex(message)
                print()
