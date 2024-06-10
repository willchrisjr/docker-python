import tempfile
import os
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import json

def get_docker_token(image_name):
    # Get an authentication token for the specified Docker image from Docker Hub
    url = f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/{image_name}:pull"
    res = urllib.request.urlopen(url)
    res_json = json.loads(res.read().decode())
    return res_json["token"]

def build_docker_headers(token):
    # Generate HTTP headers for Docker API requests using the provided token
    return {
        "Accept": "application/vnd.docker.distribution.manifest.v2+json",
        "Authorization": f"Bearer {token}",
    }

def get_docker_image_manifest(headers, image_name):
    # Retrieve the image manifest from Docker Hub for the specified image
    manifest_url = f"https://registry-1.docker.io/v2/library/{image_name}/manifests/latest"
    request = urllib.request.Request(manifest_url, headers=headers)
    res = urllib.request.urlopen(request)
    res_json = json.loads(res.read().decode())
    return res_json

def get_image_layers(headers, image, layers):
    # Download and extract the layers of the Docker image
    dir_path = tempfile.mkdtemp()  # Create a temporary directory to store the layers

    for layer in layers:
        # Construct the URL to download the layer
        url = f"https://registry-1.docker.io/v2/library/{image}/blobs/{layer['digest']}"
        request = urllib.request.Request(url, headers=headers)
        res = urllib.request.urlopen(request)

        # Save the downloaded layer to a temporary file
        tmp_file = os.path.join(dir_path, "layer.tar")
        with open(tmp_file, "wb") as f:
            shutil.copyfileobj(res, f)

        # Extract the contents of the layer tarball
        with tarfile.open(tmp_file) as tar:
            def is_within_directory(directory, target):
                # Ensure the target path is within the specified directory to prevent path traversal attacks
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
                prefix = os.path.commonprefix([abs_directory, abs_target])
                return prefix == abs_directory

            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                # Safely extract the tarball contents to the specified path
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
                tar.extractall(path, members, numeric_owner=numeric_owner)

            safe_extract(tar, dir_path)

        os.remove(tmp_file)  # Remove the temporary file after extraction

    return dir_path  # Return the path to the directory containing the extracted layers

def main():
    if len(sys.argv) < 4:
        print("Usage: mydocker run <image:tag> <command> [args...]")
        sys.exit(1)

    image = sys.argv[2]
    command = sys.argv[3]
    args = sys.argv[4:]

    # Split the image name and tag (default to 'latest' if no tag is specified)
    if ':' in image:
        image_name, tag = image.split(':')
    else:
        image_name = image
        tag = 'latest'

    # Get an authentication token from Docker Hub
    token = get_docker_token(image_name=image_name)
    # Create HTTP headers for Docker API requests
    headers = build_docker_headers(token)
    # Retrieve the image manifest from Docker Hub
    manifest = get_docker_image_manifest(headers, image_name)
    # Download and extract the image layers
    dir_path = get_image_layers(headers, image_name, manifest["layers"])

    # Run the specified command in the isolated environment using 'unshare' and 'chroot'
    completed_process = subprocess.run(
        ["unshare", "-fpu", "chroot", dir_path, command, *args], capture_output=True
    )

    # Output the results of the command execution
    sys.stderr.write(completed_process.stderr.decode("utf-8"))
    sys.stdout.write(completed_process.stdout.decode("utf-8"))

    # Exit with the return code of the executed command
    sys.exit(completed_process.returncode)

if __name__ == "__main__":
    main()