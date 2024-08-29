import os
import paramiko

class SSHConnection:
    """Handles SSH connections and SFTP operations."""

    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.ssh_client = self._create_ssh_client()
        self.sftp_client = self.ssh_client.open_sftp()

    def _create_ssh_client(self):
        """Creates and returns an SSH client."""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.hostname, username=self.username, password=self.password)
        return client

    def execute_command(self, command):
        """Executes a command on the remote server."""
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        return stdout.read().decode(), stderr.read().decode()

    def close(self):
        """Closes the SSH and SFTP connections."""
        self.sftp_client.close()
        self.ssh_client.close()

    def sftp_get(self, remote_path, local_path):
        """Downloads a file from the remote server."""
        self.sftp_client.get(remote_path, local_path)

    def sftp_put(self, local_path, remote_path):
        """Uploads a file to the remote server."""
        self.sftp_client.put(local_path, remote_path)

def sync_folders(source_connection, destination_connection, src_dir, dest_dir):
    """Synchronizes folders between two servers."""
    for root, dirs, files in os.walk(src_dir):
        relative_path = os.path.relpath(root, src_dir)
        dest_path = os.path.join(dest_dir, relative_path)

        create_remote_directory(destination_connection, dest_path)
        transfer_files(source_connection, destination_connection, root, files, dest_path)

def create_remote_directory(ssh_connection, directory_path):
    """Ensures the destination directory exists on the remote server."""
    ssh_connection.execute_command(f'sudo -u prieappatom mkdir -p {directory_path}')

def transfer_files(source_connection, destination_connection, src_root, files, dest_path):
    """Transfers files from the source to the destination server."""
    for file in files:
        src_file_path = os.path.join(src_root, file)
        dest_file_path = os.path.join(dest_path, file)
        print(f"Transferring {src_file_path} to {dest_file_path}")
        
        source_connection.sftp_get(src_file_path, "/tmp/temp_file")
        destination_connection.sftp_put("/tmp/temp_file", dest_file_path)
        
        set_file_ownership(destination_connection, dest_file_path)

def set_file_ownership(ssh_connection, file_path):
    """Sets the file ownership to 'prieappatom' on the destination server."""
    ssh_connection.execute_command(f'sudo -u prieappatom chown prieappatom:prieappatom {file_path}')

def main():
    src_user = "qhg85bx"
    src_ip = "strplvarie0002.fg.rbc.com"
    src_dir = "/rbc/home/prieapptom"

    dest_user = "qhg85bx"
    dest_ip = "guerlvarie0002.fg.rbc.com"
    dest_dir = "/rbc/home/prieapptom"  # Same path on the destination server

    password = "qhg85bx_password"

    source_connection = SSHConnection(src_ip, src_user, password)
    destination_connection = SSHConnection(dest_ip, dest_user, password)

    try:
        sync_folders(source_connection, destination_connection, src_dir, dest_dir)
    finally:
        source_connection.close()
        destination_connection.close()

if you __name__ == "__main__":
    main()
