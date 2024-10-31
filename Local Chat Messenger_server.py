import socket
import threading
from faker import Faker
import json
import sys
from typing import Optional, Dict, Tuple


class Server:
    """
    ソケット通信を使用したサーバークラス。
    クライアントからメッセージを受信し、フェイクデータを生成して返信する。

    クラスの属性（Attributes）:
        ENCODING (str): 通信で使用する文字エンコーディング
        LISTEN_BACKLOG (int): 同時接続待ち数
        BUFFER_SIZE (int): 受信バッファサイズ
        host (str): サーバーのホストアドレス
        port (int): サーバーのポート番号
        server_socket (Optional[socket.socket]): サーバーソケットオブジェクト
        faker (Faker): フェイクデータ生成オブジェクト
    """

    ENCODING: str = 'utf-8'
    LISTEN_BACKLOG: int = 5
    BUFFER_SIZE: int = 1024

    def __init__(self, host: str = '127.0.0.1', port: int = 5001) -> None:
        """
        サーバーの初期化を行う。

        引数（Args）:
            host: サーバーのホストアドレス（デフォルト: '127.0.0.1'）
            port: サーバーのポート番号（デフォルト: 5001）
        """
        self.host: str = host
        self.port: int = port
        self.server_socket: Optional[socket.socket] = None
        self.faker: Faker = Faker('ja_JP') # 日本語のフェイクデータを生成

    def setup(self) -> None:
        """
        サーバーソケットの初期設定を行う。
        ソケットの作成、バインド、リッスン状態の設定を実施する。

        発生する可能性のある例外（Raises）:
            OSError: ソケットの作成やバインドに失敗した場合
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(Server.LISTEN_BACKLOG)
            print(f"サーバーが {self.host}:{self.port} で起動しました")
        except Exception as e:
            # 確実にリソースを解放
            if self.server_socket:
                self.server_socket.close()  
            # エラーを上位に伝播して適切な終了処理を促す
            raise

    def generate_fake_response(self, message: str) -> str:
        """
        クライアントのメッセージに基づいてフェイクデータを生成する。

        引数（Args）:
            message: クライアントから受信したメッセージ

        戻り値（Returns）:
            JSON形式のフェイクデータ（文字列）
        """
        response_data: Dict[str, str] = {
            'name': self.faker.name(),
            'address': self.faker.address(),
            'email': self.faker.email(),
            'company': self.faker.company(),
            'received_message': message
        }
        return json.dumps(response_data, ensure_ascii=False)
    


    def handle_client(self, client_socket: socket.socket, client_address: Tuple[str, int]) -> None:
        """
        個別のクライアントとの通信を処理する。

        引数（Args）:
            client_socket: クライアントとの通信用ソケット
            client_address: クライアントのアドレス情報 (host, port)
        """
        try:
            while True:
                message = client_socket.recv(Server.BUFFER_SIZE).decode(Server.ENCODING)
                if not message:
                    break
                if message.lower() == 'quit':
                    print(f"クライアント({client_address})が正常に切断しました")
                    break
                print(f"クライアント({client_address})からのメッセージ: {message}")
                # フェイクデータを生成して返信
                response = self.generate_fake_response(message)
                client_socket.send(response.encode(Server.ENCODING))
        except Exception as e:
            print(f"クライアントとの通信中にエラーが発生しました: {e}")
        finally:
            client_socket.close()

    def start(self) -> None:
        """
        サーバーを起動し、クライアントからの接続を待ち受ける。
        接続があった場合、別スレッドでクライアントの処理を開始する。
        """
        try:
            while True:
                client_socket, address = self.server_socket.accept()
                print(f"クライアント接続: {address}")
                # 各クライアントを別々のスレッドで処理
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, address), 
                    daemon=True
                )
                client_thread.start()
        except KeyboardInterrupt:
            print("\nサーバーを停止します...")
        finally:
            self.server_socket.close()



if __name__ == '__main__':
    try:
        server = Server()
        server.setup()
        server.start()
    except OSError as e:
        print(f"サーバーのセットアップ中にエラーが発生しました: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
        sys.exit(1)
