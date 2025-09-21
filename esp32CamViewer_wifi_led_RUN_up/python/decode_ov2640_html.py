import re
import gzip

def decode_html(input_file, output_file):
    with open(input_file, 'r') as f:
        content = f.read()

    # OV2640の配列のみを対象とする正規表現
    match = re.search(r'const uint8_t index_ov2640_html_gz\[\] = \{([^\}]+)\}', content)

    if not match:
        print("Could not find index_ov2640_html_gz array in the input file.")
        return

    data = match.group(1)

    # 16進数の文字列をバイトに変換
    hex_values = data.strip().split(',')
    byte_data = bytearray()
    for hex_val in hex_values:
        cleaned_hex = hex_val.strip()
        if cleaned_hex:
            byte_data.append(int(cleaned_hex, 16))

    # Gzip解凍
    try:
        decompressed_data = gzip.decompress(bytes(byte_data))

        # HTMLファイルとして保存
        with open(output_file, 'wb') as out_f:
            out_f.write(decompressed_data)
        print(f"Successfully decoded and saved {output_file}")

    except gzip.BadGzipFile:
        print(f"Error: Bad Gzip file for index_ov2640_html_gz")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    decode_html('../lib/Sketch_06.1_CameraWebServer/camera_index.h', 'index_ov2640.html')