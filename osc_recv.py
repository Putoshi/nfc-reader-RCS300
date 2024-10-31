from pythonosc import dispatcher
from pythonosc import osc_server

def print_nfc_data(unused_addr, card_id, ascii_data):
    print(f"受信したカードID: {card_id}")
    print(f"受信したASCIIデータ: {ascii_data}")

# ディスパッチャーの設定
disp = dispatcher.Dispatcher()
disp.map("/nfc/data", print_nfc_data)

# サーバーの設定
server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 8000), disp)

print("OSCサーバーを開始します。Ctrl+Cで停止します。")
try:
    server.serve_forever()
except KeyboardInterrupt:
    print("OSCサーバーを停止します。")