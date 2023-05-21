import os

def count_lines_in_files(directory, file_extension):
    total_lines = 0

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(file_extension):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    lines = sum(1 for _ in f)
                    total_lines += lines
                    print(f"File: {file_path}\tLines: {lines}")

    print(f"\nTotal lines in files with '{file_extension}' extension: {total_lines}")


# Usage example
directory_path = 'D:/Programmieren/Python/ShellshockBot'
file_extension = '.py'
count_lines_in_files(directory_path, file_extension)
