import re
import gzip
import os

def decode_html(input_file, output_dir):
    # camera_index.hが格納されているディレクトリを取得
    base_dir = os.path.dirname(input_file)
    
    with open(input_file, 'r') as f:
        content = f.read()

    # 正規表現ですべてのgz配列を検索
    gz_arrays = re.findall(r'const uint8_t (index_\w+_html_gz)\[\] = \{([^\}]+)\}', content)

    if not gz_arrays:
        print(f"No gzipped data found in {input_file}")
        return

    for name, data in gz_arrays:
        # OV2640のデータのみを対象とする
        if 'ov2640' not in name:
            continue

        output_filename = name.replace('_html_gz', '.html')
        output_path = os.path.join(output_dir, output_filename)
        
        # 16進数の文字列をバイトに変換
        hex_values = data.strip().split(',')
        byte_data = bytearray()
        for hex_val in hex_values:
            cleaned_hex = hex_val.strip()
            if cleaned_hex:
                try:
                    byte_data.append(int(cleaned_hex, 16))
                except ValueError:
                    # 変換できない値はスキップ (例: 空白やコメント)
                    pass
        
        # Gzip解凍
        try:
            decompressed_data = gzip.decompress(bytes(byte_data))
            
            # HTMLファイルとして保存
            with open(output_path, 'wb') as out_f:
                out_f.write(decompressed_data)
            print(f"Successfully decoded and saved {output_path}")

        except gzip.BadGzipFile:
            print(f"Error: Bad Gzip file for {name}")
        except Exception as e:
            print(f"An error occurred for {name}: {e}")

if __name__ == '__main__':
    # このスクリプトがある場所を基準にパスを指定
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    input_path = os.path.join(project_root, 'lib', 'Sketch_06.1_CameraWebServer', 'camera_index.h')
    output_dir = project_root # プロジェクトのルートにHTMLを保存

    decode_html(input_path, output_dir)
