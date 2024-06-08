import os
import subprocess
import sys
import tempfile
import shutil
import stat

def copy_dependencies(binary_path, temp_dir):
    # Use ldd to find the shared libraries
    result = subprocess.run(['ldd', binary_path], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    
    for line in lines:
        parts = line.split()
        if '=>' in parts:
            lib_path = parts[2]
        else:
            lib_path = parts[0]
        
        if os.path.exists(lib_path):
            dest_path = os.path.join(temp_dir, lib_path.lstrip('/'))
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy(lib_path, dest_path)

def main():
    # Remove any debug print statements
    command = sys.argv[3]
    args = sys.argv[4:]

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Copy the binary to the temporary directory
            binary_path = shutil.copy(command, temp_dir)
            
            # Make the binary executable
            os.chmod(binary_path, os.stat(binary_path).st_mode | stat.S_IEXEC)
            
            # Copy the necessary shared libraries
            copy_dependencies(command, temp_dir)
            
            # Prepare the command to run in the new namespace and chroot
            command_in_chroot = os.path.join("/", os.path.basename(binary_path))
            unshare_command = ['unshare', '--pid', '--fork', '--mount-proc', '--']
            chroot_command = ['chroot', temp_dir, command_in_chroot, *args]
            
            # Run the command in the new PID namespace and chroot
            completed_process = subprocess.run(unshare_command + chroot_command, capture_output=True)
            
            # Print stdout and stderr
            print(completed_process.stdout.decode("utf-8"), end='')
            print(completed_process.stderr.decode("utf-8"), end='', file=sys.stderr)
            
            # Exit with the same code as the completed process
            sys.exit(completed_process.returncode)
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(2)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()