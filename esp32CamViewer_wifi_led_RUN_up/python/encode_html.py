import gzip
import os

def encode_html(input_file, output_file):
    with open(input_file, 'rb') as f:
        content = f.read()

    compressed_data = gzip.compress(content)

    with open(output_file, 'w') as f:
        f.write(f'#define index_ov2640_html_gz_len {len(compressed_data)}\n')
        f.write('const uint8_t index_ov2640_html_gz[] = {\n  ')
        for i, byte in enumerate(compressed_data):
            f.write(f'0x{byte:02X}, ')
            if (i + 1) % 16 == 0:
                f.write('\n  ')
        f.write('\n};\n')

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    input_path = os.path.join(project_root, 'index_ov2640.html')
    output_path = os.path.join(project_root, 'camera_index.h')
    encode_html(input_path, output_path)