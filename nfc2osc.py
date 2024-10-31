from pythonosc import udp_client
from smartcard.util import toHexString
from smartcard.System import readers as get_readers
import time

def read_block(conn, block_number):
    cmd = [0xFF, 0xB0, 0x00, block_number, 0x10]
    data, sw1, sw2 = conn.transmit(cmd)
    return data if (sw1, sw2) == (0x90, 0x00) else None

def merge_ascii_strings(ascii_strings):
    merged_string = ascii_strings[0]
    for i in range(1, len(ascii_strings)):
        overlap_length = min(len(merged_string), len(ascii_strings[i]))
        for j in range(overlap_length, 0, -1):
            if merged_string[-j:] == ascii_strings[i][:j]:
                merged_string += ascii_strings[i][j:]
                break
        else:
            merged_string += ascii_strings[i]
    return merged_string

# OSCクライアントの設定
osc_client = udp_client.SimpleUDPClient("127.0.0.1", 8000)

readers = get_readers()
print(readers)

while True:
    try:
        conn = readers[0].createConnection()
        conn.connect()

        # カードIDの読み取り
        send_data = [0xFF, 0xCA, 0x00, 0x00, 0x00]
        recv_data, sw1, sw2 = conn.transmit(send_data)
        card_id = toHexString(recv_data)
        print(f"カードID: {card_id}")

        # ASCIIデータを収集
        ascii_strings = []
        for block in range(7, 128):
            block_data = read_block(conn, block)
            if block_data:
                ascii_data = ''.join(chr(x) for x in block_data if 32 <= x <= 126)
                ascii_strings.append(ascii_data)
                # print(f"ブロック {block:02d}: {toHexString(block_data)} (ASCII: {ascii_data})")
                # print("-" * 40)
        
        # 重複を排除して結合
        combined_ascii = merge_ascii_strings(ascii_strings).replace("RgH", "")
        print(f"結合されたASCII文字列: {combined_ascii}")

        # OSCメッセージの送信
        osc_client.send_message("/nfc/data", [card_id, combined_ascii])
        print("OSCメッセージを送信しました。")
        
        time.sleep(0.1)
        
    except Exception as e:
        print("カードを待っています...")
        time.sleep(1)
