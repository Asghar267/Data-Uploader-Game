import os
from concurrent.futures import ThreadPoolExecutor
import time

def create_large_file(file_name, size_in_mb):
    with open(file_name, 'wb') as file:
        file.write(b'0' * size_in_mb * 1024 * 1024)  # Write '0' bytes to fill the file
    print(f'{file_name} created with size {size_in_mb} MB.')

def create_files_until_full(directory, file_size_in_mb, num_threads):
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        file_index = 0
        while True:
            file_name = os.path.join(directory, f'file_{file_index}.bin')
            executor.submit(create_large_file, file_name, file_size_in_mb)
            file_index += 1

if __name__ == "__main__":
    directory = 'background_files'
    os.makedirs(directory, exist_ok=True)
    
    file_size_in_mb = 100  # Size of each file in MB
    num_threads = 5  # Number of threads to create files concurrently
    
    try:
        create_files_until_full(directory, file_size_in_mb, num_threads)
    except Exception as e:
        print(f"An error occurred: {e}")
