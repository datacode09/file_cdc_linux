import os
import subprocess
import hashlib
import shutil

def run_command(command):
    """Runs a command on the local machine and returns the output."""
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = result.stdout.decode('utf-8')
    stderr = result.stderr.decode('utf-8')
    if result.returncode != 0:
        print(f"Error: {stderr}")
    return stdout, stderr

def calculate_checksum(file_path):
    """Calculates the MD5 checksum of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def sync_folders(src_user, src_ip, src_dir, dest_user, dest_ip, dest_dir, compress, delete_extra_files):
    """Synchronizes folders between two servers with enhanced features."""
    for root, dirs, files in os.walk(src_dir):
        relative_path = os.path.relpath(root, src_dir)
        dest_path = os.path.join(dest_dir, relative_path)

        create_remote_directory(dest_user, dest_ip, dest_path)

        for file in files:
            src_file_path = os.path.join(root, file)
            dest_file_path = os.path.join(dest_path, file)
            print(f"Processing {src_file_path}...")

            if not should_transfer_file(src_user, src_ip, src_file_path, dest_user, dest_ip, dest_file_path):
                print(f"Skipping {src_file_path} as it has not changed.")
                continue

            if compress:
                temp_compressed_file = compress_file(src_file_path)
                transfer_file(src_user, src_ip, temp_compressed_file, dest_user, dest_ip, dest_file_path + ".gz")
                decompress_file(dest_user, dest_ip, dest_file_path + ".gz", dest_file_path)
                os.remove(temp_compressed_file)
            else:
                transfer_file(src_user, src_ip, src_file_path, dest_user, dest_ip, dest_file_path)

            set_file_ownership(dest_user, dest_ip, dest_file_path)

        if delete_extra_files:
            delete_files_not_in_source(dest_user, dest_ip, root, dest_path, files)

def should_transfer_file(src_user, src_ip, src_file_path, dest_user, dest_ip, dest_file_path):
    """Determines whether a file should be transferred by comparing checksums."""
    src_checksum = calculate_checksum(src_file_path)
    dest_checksum = get_remote_checksum(dest_user, dest_ip, dest_file_path)
    return src_checksum != dest_checksum

def get_remote_checksum(dest_user, dest_ip, file_path):
    """Gets the checksum of a file on the remote server."""
    command = f"ssh {dest_user}@{dest_ip} 'md5sum {file_path} 2>/dev/null || echo \"\"'"
    stdout, _ = run_command(command)
    return stdout.split()[0] if stdout else None

def create_remote_directory(dest_user, dest_ip, directory_path):
    """Ensures the destination directory exists on the remote server."""
    command = f"ssh {dest_user}@{dest_ip} 'sudo -u prieappatom mkdir -p {directory_path}'"
    run_command(command)

def transfer_file(src_user, src_ip, src_file_path, dest_user, dest_ip, dest_file_path):
    """Transfers a file from the source to the destination server."""
    command = f"scp {src_user}@{src_ip}:{src_file_path} {dest_user}@{dest_ip}:{dest_file_path}"
    run_command(command)

def compress_file(file_path):
    """Compresses a file using gzip."""
    compressed_file = file_path + ".gz"
    with open(file_path, 'rb') as f_in, open(compressed_file, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    return compressed_file

def decompress_file(dest_user, dest_ip, compressed_file, dest_file_path):
    """Decompresses a file on the remote server."""
    command = f"ssh {dest_user}@{dest_ip} 'gunzip -c {compressed_file} > {dest_file_path}'"
    run_command(command)

def set_file_ownership(dest_user, dest_ip, file_path):
    """Sets the file ownership to 'prieappatom' on the destination server."""
    command = f"ssh {dest_user}@{dest_ip} 'sudo -u prieappatom chown prieappatom:prieappatom {file_path}'"
    run_command(command)

def delete_files_not_in_source(dest_user, dest_ip, src_dir, dest_dir, files_in_source):
    """Deletes files from the destination that are not present in the source directory."""
    command = f"ssh {dest_user}@{dest_ip} 'ls {dest_dir}'"
    stdout, _ = run_command(command)
    files_in_dest = stdout.split()
    
    for file in files_in_dest:
        if file not in files_in_source:
            command = f"ssh {dest_user}@{dest_ip} 'sudo -u prieappatom rm -f {os.path.join(dest_dir, file)}'"
            run_command(command)
            print(f"Deleted {os.path.join(dest_dir, file)} from destination.")

