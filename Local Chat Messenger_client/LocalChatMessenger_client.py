import json
import socket
import sys
from typing import Optional, Dict, Any


class Client:
    """
    ソケット通信を使用したクライアントクラス。
    サーバーに接続し、メッセージの送受信を行う。

    クラスの属性（Attributes）:
        ENCODING (str): 通信で使用する文字エンコーディング
        BUFFER_SIZE (int): 受信バッファサイズ
        host (str): 接続先サーバーのホストアドレス
        port (int): 接続先サーバーのポート番号
        client_socket (Optional[socket.socket]): クライアントソケットオブジェクト
    """
    
    ENCODING: str = 'utf-8'
    BUFFER_SIZE: int = 1024

    def __init__(self, host: str = '127.0.0.1', port: int = 5001) -> None:
        """
        クライアントの初期化を行う。

        引数（Args）:
            host: 接続先サーバーのホストアドレス（デフォルト: '127.0.0.1'）
            port: 接続先サーバーのポート番号（デフォルト: 5001）
        """
        self.host: str = host
        self.port: int = port
        self.client_socket: Optional[socket.socket] = None

    def connect(self) -> bool:
        """
        サーバーへの接続を試みる。

        戻り値（Returns）:
            bool: 接続成功時はTrue、失敗時はFalse
        """
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            print(f"サーバー {self.host}:{self.port} に接続しました")
            return True
        except Exception as e:
            print(f"サーバーへの接続に失敗しました: {e}")
            return False

    def send_receive(self) -> None:
        """
        サーバーとのメッセージの送受信を処理する。
        ユーザーからの入力を受け取り、サーバーに送信し、
        サーバーからのレスポンスを受信して表示する。
        'quit'が入力されるまで継続する。
        """
        try:
            while True:
                # ユーザーからの入力を受け取る
                message = input("今日一日の意気込みを入力してください！ (終了する場合は'quit'と入力): ")
                # 空入力のチェック
                if not message:
                    continue
                
                if message.lower() == 'quit':
                    self.client_socket.send(message.encode(Client.ENCODING))
                    break
                # メッセージをサーバーに送信
                self.client_socket.send(message.encode(Client.ENCODING))
                # サーバーからの応答を受信
                response = self.client_socket.recv(Client.BUFFER_SIZE).decode(Client.ENCODING)
                response_data: Dict[str, Any] = json.loads(response)
                # 受信したデータを整形して表示
                print("\n==== 今日の意気込み ====")
                for key, value in response_data.items():
                    print(f"{key}: {value}")
                print("========================\n")
        except KeyboardInterrupt:
            print("クライアントを終了中...")
        finally:
            self.client_socket.close()
            print("クライアントを終了しました")


if __name__ == '__main__':
    client = Client()
    if not client.connect():
        print("サーバーへの接続に失敗したため、プログラムを終了します。")
        if client.client_socket:
            client.client_socket.close()
        sys.exit(1)
    else:
        try:
            client.send_receive()
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e}")
            sys.exit(1)