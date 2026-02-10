import subprocess
import re
import sys
import os
import time

def parse_prompts(filename):
    """Parse numbered prompts from file"""
    prompts = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # Match numbered prompts like "1. prompt text" or "1) prompt text"
        pattern = r'^\s*(\d+)[\.\)]\s*(.+)$'
        for line in content.split('\n'):
            line = line.strip()
            if line:
                match = re.match(pattern, line)
                if match:
                    num = int(match.group(1))
                    prompt = match.group(2).strip()
                    prompts.append((num, prompt))

        prompts.sort(key=lambda x: x[0])
        return [p[1] for p in prompts]

    except FileNotFoundError:
        print(f"Error: {filename} not found!")
        return []
    except Exception as e:
        print(f"Error reading prompts: {e}")
        return []


def run_codex_prompt(prompt, is_first, approval_flag, timeout_sec):
    """Run a single codex exec call, resuming previous session if not first.
    Uses stdin ('-') to pass the prompt, avoiding shell escaping issues."""
    if is_first:
        cmd = f'codex exec {approval_flag} --skip-git-repo-check -'
    else:
        cmd = f'codex exec resume --last {approval_flag} --skip-git-repo-check -'

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            encoding='utf-8',
            errors='replace',
            cwd=os.getcwd()
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", f"Timed out after {timeout_sec} seconds", -1
    except Exception as e:
        return "", str(e), -1


def main():
    prompt_file = "codex_prompt.txt"
    timeout_sec = 300  # 5 minutes per prompt

    # Parse CLI args for custom settings
    approval_flag = "--full-auto"
    for arg in sys.argv[1:]:
        if arg == "--yolo" or arg == "--dangerously":
            approval_flag = "--dangerously-bypass-approvals-and-sandbox"
        elif arg == "--full-auto":
            approval_flag = "--full-auto"
        elif arg.startswith("--timeout="):
            timeout_sec = int(arg.split("=")[1])
        elif arg.startswith("--file="):
            prompt_file = arg.split("=")[1]

    # Parse prompts
    prompts = parse_prompts(prompt_file)
    if not prompts:
        print(f"No prompts found in {prompt_file}")
        print("Format: one numbered prompt per line")
        print("  1. first prompt")
        print("  2. second prompt")
        print("  3. third prompt")
        sys.exit(1)

    print("=" * 60)
    print("CODEX SEQUENTIAL PROMPT RUNNER")
    print("=" * 60)
    print(f"  Prompt file : {prompt_file}")
    print(f"  Prompts     : {len(prompts)}")
    print(f"  Mode        : {approval_flag}")
    print(f"  Timeout     : {timeout_sec}s per prompt")
    print(f"  Method      : codex exec + resume (session context preserved)")
    print("=" * 60)
    print()

    for i, prompt in enumerate(prompts, 1):
        print(f"  {i}. {prompt}")
    print()

    all_output = []
    max_retries = 10

    for i, prompt in enumerate(prompts):
        is_first = (i == 0)
        prompt_num = i + 1
        attempt = 0

        while True:
            attempt += 1

            print("=" * 60)
            label = "new session" if is_first else "resume"
            retry_label = f" (retry {attempt - 1})" if attempt > 1 else ""
            print(f"[{prompt_num}/{len(prompts)}] SENDING ({label}{retry_label}): {prompt}")
            print("=" * 60)

            stdout, stderr, returncode = run_codex_prompt(prompt, is_first, approval_flag, timeout_sec)

            # Check if it was a timeout
            is_timeout = returncode == -1 and "Timed out" in stderr

            # Print the output
            if stdout:
                print(stdout)
            if stderr and returncode != 0:
                print(f"[STDERR] {stderr}")

            if is_timeout:
                if attempt >= max_retries:
                    print(f"[FAILED] Prompt {prompt_num} timed out {max_retries} times. Giving up.")
                    all_output.append({
                        'prompt_num': prompt_num,
                        'prompt': prompt,
                        'stdout': stdout,
                        'stderr': stderr,
                        'returncode': returncode
                    })
                    break

                print(f"[RETRY] Timed out. Retrying prompt {prompt_num} (attempt {attempt + 1}/{max_retries})...")
                print()
                time.sleep(3)
                continue

            # Success or non-timeout error - move on
            all_output.append({
                'prompt_num': prompt_num,
                'prompt': prompt,
                'stdout': stdout,
                'stderr': stderr,
                'returncode': returncode
            })

            if returncode != 0 and returncode != -1:
                print(f"[WARNING] Codex returned exit code {returncode}")

            break

        # Small delay between prompts to avoid rate limiting
        if i < len(prompts) - 1:
            print("[Waiting 2 seconds before next prompt...]")
            print()
            time.sleep(2)

    # Summary
    print()
    print("=" * 60)
    print("SESSION COMPLETE")
    print("=" * 60)
    succeeded = sum(1 for o in all_output if o['returncode'] == 0)
    print(f"  Prompts sent : {len(prompts)}")
    print(f"  Succeeded    : {succeeded}")
    print(f"  Failed       : {len(prompts) - succeeded}")
    print("=" * 60)

    # Save full output to file
    try:
        with open("codex_output.txt", "w", encoding="utf-8") as f:
            for o in all_output:
                f.write(f"{'='*60}\n")
                f.write(f"PROMPT {o['prompt_num']}: {o['prompt']}\n")
                f.write(f"{'='*60}\n")
                f.write(o['stdout'] + "\n")
                if o['stderr']:
                    f.write(f"[STDERR] {o['stderr']}\n")
                f.write("\n")
        print(f"  Full output saved to: codex_output.txt")
    except Exception as e:
        print(f"  Could not save output file: {e}")

    sys.exit(0 if succeeded == len(prompts) else 1)


if __name__ == "__main__":
    main()
