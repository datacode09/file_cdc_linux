from sync_module import sync_folders
import config

def main():
    # Call the sync function with the necessary configuration
    sync_folders(
        src_user=config.SRC_USER,
        src_ip=config.SRC_IP,
        src_dir=config.SRC_DIR,
        dest_user=config.DEST_USER,
        dest_ip=config.DEST_IP,
        dest_dir=config.DEST_DIR,
        compress=config.COMPRESS,
        delete_extra_files=config.DELETE_EXTRA_FILES
    )

if __name__ == "__main__":
    main()
