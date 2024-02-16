
import os
import hashlib
import csv

def hash_file(file_path):
    """Calculate the MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def update_progress(progress, total_files, folder_name):
    """Update progress information."""
    print(f"{folder_name} - {progress:.1f}% complete ({total_files} files processed)")

def find_duplicates(path1, path2, progress_csv):
    """Find duplicate files between two paths."""
    hashes_path1 = {}
    hashes_path2 = {}
    total_files = 0
    processed_files = 0
    duplicate_files = []

    # Check if there's a progress CSV file
    if os.path.exists(progress_csv):
        with open(progress_csv, 'r') as progress_file:
            reader = csv.reader(progress_file)
            for row in reader:
                if row:
                    folder_name, progress_str, total_files_str = row
                    if folder_name == 'Total Progress':
                        processed_files = int(total_files_str)

    # Count the total number of files in path1
    for root, _, files in os.walk(path1):
        total_files += len(files)

    # Check if there are no files in path1 to avoid division by zero
    if total_files == 0:
        print("No files found.")
        return 0, []

    # Generate file hashes for the first path
    print("Hashing Files (1/2):")
    for root, _, files in os.walk(path1):
        folder_name = os.path.relpath(root, path1)
        for i, file in enumerate(files, start=1):
            if i <= processed_files:
                continue  # Skip files that were already processed
            file_path = os.path.join(root, file)
            file_hash = hash_file(file_path)
            hashes_path1[file_hash] = file_path

            # Print progress every 10% completion
            progress = (i + processed_files) / total_files * 100
            update_progress(progress, total_files, folder_name)

            # Dump progress to CSV file
            with open(progress_csv, 'w', newline='') as progress_file:
                csv_writer = csv.writer(progress_file)
                csv_writer.writerow([folder_name, f"{progress:.1f}", f"{i + processed_files}"])

    # Count the total number of files in path2
    total_files = 0
    processed_files = 0
    for root, _, files in os.walk(path2):
        total_files += len(files)

    # Check if there are no files in path2 to avoid division by zero
    if total_files == 0:
        print("No files found.")
        return 0, []

    # Generate file hashes for the second path
    print("Hashing Files (2/2):")
    for root, _, files in os.walk(path2):
        folder_name = os.path.relpath(root, path2)
        for i, file in enumerate(files, start=1):
            if i <= processed_files:
                continue  # Skip files that were already processed
            file_path = os.path.join(root, file)
            file_hash = hash_file(file_path)
            hashes_path2[file_hash] = file_path

            # Print progress every 10% completion
            progress = (i + processed_files) / total_files * 100
            update_progress(progress, total_files, folder_name)

            # Dump progress to CSV file
            with open(progress_csv, 'w', newline='') as progress_file:
                csv_writer = csv.writer(progress_file)
                csv_writer.writerow([folder_name, f"{progress:.1f}", f"{i + processed_files}"])

    # Compare hashes from both paths
    for hash_value, file_path in hashes_path1.items():
        if hash_value in hashes_path2:
            duplicate_files.append((file_path, hashes_path2[hash_value]))

    # Dump final progress to CSV file
    with open(progress_csv, 'w', newline='') as progress_file:
        csv_writer = csv.writer(progress_file)
        csv_writer.writerow(['Total Progress', '100.0', f"{total_files}"])

    return total_files, duplicate_files

def write_to_csv(output_file, total_files, duplicate_files):
    """Write information to a CSV file."""
    with open(output_file, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Total Files', 'Duplicate Files', 'Percentage Duplicate'])
        csv_writer.writerow([total_files, len(duplicate_files), (len(duplicate_files) / total_files) * 100])
        csv_writer.writerow([])  # Add an empty row for better readability
        csv_writer.writerow(['File 1', 'File 2'])
        csv_writer.writerows(duplicate_files)

if __name__ == "__main__":
    # Replace these paths with the actual paths
    path1 = "/Users/satyamanikrishna/Downloads/f1"
    path2 = "/Users/satyamanikrishna/Downloads/f2"
    output_csv_file = "duplicate_files_info.csv"
    progress_csv_file = "hashing_progress.csv"

    # Find duplicate files between two paths
    total_files, duplicate_files = find_duplicates(path1, path2, progress_csv_file)

    if total_files > 0:
        # Write information to a CSV file
        write_to_csv(output_csv_file, total_files, duplicate_files)
        print(f"Information written to {output_csv_file}")
    else:
        print("No files found.")
