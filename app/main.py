import subprocess
import sys

def main():
   
    command = sys.argv[3]
    args = sys.argv[4:]

    # Run the command and capture both stdout and stderr
    completed_process = subprocess.run([command, *args], capture_output=True)

    # Print stdout and stderr
    print(completed_process.stdout.decode("utf-8"), end='')
    print(completed_process.stderr.decode("utf-8"), end='', file=sys.stderr)

if __name__ == "__main__":
    main()