

---

# MyDocker

MyDocker is a simplified Docker implementation that can pull an image from Docker Hub and execute commands within it. This project demonstrates the use of chroot, PID namespaces, and the Docker registry API to create an isolated environment for running applications. The project is designed to provide a hands-on understanding of containerization concepts and the inner workings of Docker.

## Features

- **Fetch Docker Images**: Pull images from Docker Hub using the Docker registry API.
- **Extract Image Layers**: Download and extract image layers to a chroot directory.
- **Isolated Execution**: Execute commands within an isolated environment using chroot and PID namespaces.
- **Security**: Implement safe extraction to prevent path traversal attacks.

## Prerequisites

- Python 3.6 or higher
- `pip` (Python package installer)
- `unshare` command (available on most Unix-like systems)

## Setup

1. **Clone the repository**:

   ```sh
   git clone https://github.com/yourusername/mydocker.git
   cd mydocker
   ```

2. **Create and activate a virtual environment**:

   ```sh
   python -m venv myenv
   source myenv/bin/activate  # On Windows use `myenv\Scripts\activate`
   ```

3. **Install the required dependencies**:

   ```sh
   pip install requests
   ```

## Usage

### Running the Script

To run the script, use the following command:

```sh
python main.py run <image:tag> <command> [args...]
```

For example:

```sh
python main.py run alpine:latest /bin/echo hey
```

### Using the Shell Script

You can also use the provided `your_docker.sh` script to run the program:

1. **Make the script executable**:

   ```sh
   chmod +x your_docker.sh
   ```

2. **Run the script**:

   ```sh
   ./your_docker.sh run alpine:latest /bin/echo hey
   ```

## Project Structure

- `main.py`: The main Python script that implements the Docker functionality.
- `your_docker.sh`: A shell script to run the Python script with the virtual environment activated.

## Code Explanation

### `main.py`

The `main.py` script performs the following steps:

1. **Token Retrieval**: Obtains an authentication token from Docker Hub.
2. **Manifest Retrieval**: Retrieves the image manifest to get the list of layers.
3. **Layer Download and Extraction**: Downloads and extracts the image layers to a temporary directory.
4. **Command Execution**: Executes the specified command within the isolated environment using `unshare` and `chroot`.

#### Functions

- `get_docker_token(image_name)`: Retrieves an authentication token for the specified image.
- `build_docker_headers(token)`: Creates headers for Docker requests using the token.
- `get_docker_image_manifest(headers, image_name)`: Retrieves the image manifest from Docker Hub.
- `get_image_layers(headers, image, layers)`: Downloads and extracts the image layers to a temporary directory.
- `main()`: The main function that orchestrates the entire process.

### `your_docker.sh`

The `your_docker.sh` script ensures that the virtual environment is activated before running the `main.py` script:

```sh
#!/bin/sh

# Activate the virtual environment
source myenv/bin/activate

# Run the Python script using the virtual environment's Python interpreter
myenv/bin/python main.py "$@"
```

## Detailed Steps and Accomplishments

### 1. Token Retrieval

The script starts by obtaining an authentication token from Docker Hub. This token is necessary to access the image layers. The `get_docker_token` function constructs the URL for the token request and retrieves the token using `urllib.request`.

### 2. Manifest Retrieval

Once the token is obtained, the script retrieves the image manifest. The manifest contains metadata about the image, including the list of layers. The `get_docker_image_manifest` function constructs the URL for the manifest request and retrieves the manifest using the token for authentication.

### 3. Layer Download and Extraction

The script then downloads and extracts the image layers. Each layer is a tar file that contains part of the filesystem for the image. The `get_image_layers` function iterates over the layers, downloads each one, and extracts it to a temporary directory. The extraction process includes a safe extraction method to prevent path traversal attacks.

### 4. Command Execution

Finally, the script executes the specified command within the isolated environment. The `unshare` command is used to create a new PID namespace, and `chroot` is used to change the root directory to the temporary directory containing the extracted layers. The command is then executed within this isolated environment.

## Example

Here is an example of running the script to list the contents of the root directory in an Alpine Linux container:

```sh
./your_docker.sh run alpine:latest /bin/sh -c '/bin/ls /'
```

Expected output:

```
bin
dev
etc
home
lib
media
mnt
opt
proc
root
run
sbin
srv
sys
tmp
usr
var
```

## Security Considerations

The script includes a safe extraction method to prevent path traversal attacks when extracting tar files. This ensures that the extracted files stay within the target directory. The use of `unshare` and `chroot` also helps to isolate the execution environment, providing a degree of security and isolation from the host system.

## Future Improvements

- **Advanced Docker Features**: Add support for more advanced Docker features such as networking and volume management.
- **Enhanced Security**: Implement additional security measures to further isolate the containerized environment.
- **Error Handling and Logging**: Improve error handling and logging for better debugging and maintenance.
- **Performance Optimization**: Optimize the performance of the image download and extraction process.



