import serial
import sys
import io
from PIL import Image, ImageTk
import tkinter as tk

# シリアルポートの設定
# COMポートは環境に合わせて変更してください
SERIAL_PORT = 'COM14'  # ESP32が接続されているCOMポート
BAUD_RATE = 921600

def display_camera_feed():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.01) # タイムアウトを短く設定
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        print("Please check if the ESP32 is connected and the correct COM port is selected.")
        sys.exit(1)

    root = tk.Tk()
    root.title("ESP32 CAM Viewer")

    label = tk.Label(root)
    label.pack()

    buffer = b'' # バッファをグローバルまたはクロージャ変数として定義

    def update_frame():
        nonlocal buffer
        try:
            # JPEGデータの開始マーカーと終了マーカーを検出
            start_marker = b'\xff\xd8'
            end_marker = b'\xff\xd9'
            
            # 利用可能なすべてのデータを読み込む
            new_data = ser.read_all()
            if new_data:
                buffer += new_data

            # バッファからJPEGフレームを抽出
            while True:
                start_index = buffer.find(start_marker)
                end_index = buffer.find(end_marker, start_index + len(start_marker)) # 開始マーカー以降で終了マーカーを探す

                if start_index == -1: # 開始マーカーが見つからない場合
                    # バッファの先頭にゴミデータがある可能性があるので、一定サイズを超えたら破棄
                    if len(buffer) > BAUD_RATE * 2: # 適当な閾値 (例: 2秒分のデータ)
                        print(f"No start marker found, clearing buffer. Buffer size: {len(buffer)}")
                        sys.stdout.flush()
                        buffer = b'' # バッファをクリア
                    break # 次のデータが来るを待つ
                
                if end_index == -1: # 終了マーカーが見つからない場合
                    # 開始マーカーは見つかったが、終了マーカーが見つからない場合は、次のデータが来るを待つ
                    # ただし、バッファが大きくなりすぎないように調整
                    if len(buffer) > BAUD_RATE * 2: # 適当な閾値
                        print(f"Start marker found but no end marker, clearing buffer. Buffer size: {len(buffer)}")
                        sys.stdout.flush()
                        buffer = buffer[start_index:] # 開始マーカーより前のデータを破棄
                        if len(buffer) > BAUD_RATE * 2: # さらに大きければ、最新のデータだけを保持
                            buffer = buffer[-BAUD_RATE:]
                    break # 不完全なフレームなので、次のデータが来るを待つ

                # 完全なJPEGフレームが見つかった場合
                if start_index != -1 and end_index != -1 and end_index > start_index:
                    # JPEGデータは開始マーカーから終了マーカーまでを含む
                    jpeg_data = buffer[start_index : end_index + len(end_marker)]
                    
                    try:
                        image = Image.open(io.BytesIO(jpeg_data))
                        photo = ImageTk.PhotoImage(image)
                        label.config(image=photo)
                        label.image = photo
                        root.update_idletasks()
                        root.update()
                        # print(f"Image updated. Size: {image.width}x{image.height}, Data length: {len(jpeg_data)}") # 通常の更新メッセージを削除
                        # sys.stdout.flush()
                    except Exception as e:
                        print(f"Error processing image: {e}. Data length: {len(jpeg_data)}")
                        sys.stdout.flush() # デバッグ出力をすぐに表示
                        # 不正なJPEGデータの場合、そのフレームを破棄して次のフレームを探す
                        buffer = buffer[end_index + len(end_marker):] # 不正なフレームをバッファから削除
                        continue # 次のフレームを探すためにループを継続
                
                # 処理が成功した場合、処理済みのデータをバッファから削除
                buffer = buffer[end_index + len(end_marker):]

        except serial.SerialException as e:
            print(f"Serial communication error: {e}")
            sys.stdout.flush() # デバッグ出力をすぐに表示
            ser.close()
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            sys.stdout.flush() # デバッグ出力をすぐに表示
            sys.exit(1)
        
        root.after(1, update_frame) # 可能な限り早く更新

    root.after(1, update_frame)
    root.mainloop()

    ser.close()

if __name__ == "__main__":
    display_camera_feed()