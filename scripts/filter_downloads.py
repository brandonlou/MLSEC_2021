import argparse
import os
import re
import shutil
import tempfile
import time


MAX_FILE_SIZE = 2097152 # 2 MiB
PE_FILE_EXTS =  ('.acm', '.ax', '.cpl', '.dll', '.drv', '.efi', '.exe', '.mui', '.ocx', '.scr', '.sys', '.tsp')
CMP_FILE_EXTS = ('.zip', '.tar.gz') # Note: .rar, .7z, etc. will have to be manually extracted


def copy_file(src_file: str, dst_dir: str):
    file_size = os.path.getsize(src_file)
    if file_size <= MAX_FILE_SIZE:
        shutil.copy2(src_file, dst_dir)
        print(f'Copied {src_file}')
    else:
        print(f'{src_file} is too large ({file_size} bytes)')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', type=str, help='Input directory to filter')
    parser.add_argument('output_dir', type=str, help='Output directory containing filtered PE files')
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    prog = re.compile(r"\(\d+\)") # Opening parenthesis, any number of digits, closing parenthesis
    skipped_files = []

    for filename in os.listdir(input_dir):
        # Skip duplicate downloads
        if prog.match(filename) is not None:
            skipped_files.append(filename)
            print(f'Skipping {filename}')
        elif os.path.getsize(f'{input_dir}/{filename}') > MAX_FILE_SIZE:
            print(f'File too large: {filename}')
        # Directly copy PE files
        elif filename.lower().endswith(PE_FILE_EXTS):
            copy_file(f'{input_dir}/{filename}', output_dir)
        # Extract compressed files into a temporary directory. Then look
        # through that directory for PE files.
        elif filename.lower().endswith(CMP_FILE_EXTS):
            sup = []
            with tempfile.TemporaryDirectory() as tmpdir:
                try:
                    shutil.unpack_archive(f'{input_dir}/{filename}', tmpdir)
                except Exception as e:
                    print(f'ERROR unpacking {input_dir}/{filename}: {e}')
                    continue
                for root, _, extracted_files in os.walk(tmpdir):
                    for extracted_file in extracted_files:
                        if extracted_file.lower().endswith(PE_FILE_EXTS):
                            copy_file(f'{root}/{extracted_file}', output_dir)
                            sup.append(extracted_file)
            print(f"Extracted {','.join(sup)} from {filename}")
        # Skip all other files.
        else:
            skipped_files.append(filename)
            print(f'Skipping {filename}')

    print(f"Skipped files: {','.join(skipped_files)}")
    print('Done')


if __name__ == '__main__':
    main()
