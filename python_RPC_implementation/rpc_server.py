import socket
import json
import threading
import math
import time
from typing import Callable, Dict, Tuple

class RPCServer:
    """RPCサーバークラス
    
    このクラスでは、TCP/IPソケットを使用してRPCサーバーを実装する。
    また、クライアントからの接続を受け付け、登録された関数を実行して結果を返す。
    タイムアウト機能により、一定時間アクティビティがない場合は自動的にシャットダウンする。
    
    クラスの属性（Attributes）:
        host (str): サーバーのホスト名またはIPアドレス
        port (int): サーバーが待ち受けるポート番号
        functions (Dict[str, Callable]): 登録された関数のディクショナリ
        socket (socket.socket): サーバーソケット
        running (bool): サーバーの実行状態を示すフラグ
        last_activity (float): 最後のクライアントアクティビティのタイムスタンプ
        timeout (int): タイムアウトまでの秒数
        client_sockets (List[socket.socket]): アクティブなクライアント接続のソケットリスト
    """

    def __init__(self, host: str = 'localhost', port: int = 8000, timeout: int = 60) -> None:
        self.host = host
        self.port = port
        self.functions: Dict[str, Callable] = {} # 利用可能な関数名と、その説明や引数情報を登録
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # ソケットが同じアドレスとポートを再利用することを許可
        self.running = False
        self.last_activity = time.time()  # 最後のアクティビティ時刻を記録
        self.timeout = timeout  # タイムアウト時間（秒）
        self.client_sockets = []  # アクティブなクライアントソケットを管理するためのリスト

    def register_function(self, name: str, function: Callable) -> None:
        """関数をRPCサーバーに登録する。
        
        引数（Args）:
            name (str): 関数の名前（クライアントからの呼び出しに使用）
            function (Callable): 登録する関数オブジェクト
        """
        self.functions[name] = function

    def handle_client(self, client_socket: socket.socket, client_address: Tuple[str, int]) -> None:
        """クライアントとの接続を処理する。
        
        各クライアント接続に対して別スレッドで実行し、
        クライアントからのリクエストを処理し、結果を返す。
        
        引数（Args）:
            client_socket (socket.socket): クライアントとの通信用ソケット
            client_address (Tuple[str, int]): クライアントのアドレス情報 (host, port)
        """
        self.client_sockets.append(client_socket)  # クライアントソケットを登録
        try:
            while True:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    print(f"クライアント{client_address}が切断しました")
                    break
                
                # クライアントからデータを受信したら、最終アクティビティ時刻を更新
                self.last_activity = time.time()
                
                try:
                    request = json.loads(data)
                    response = self.process_request(request)
                except json.JSONDecodeError:
                    response = {
                        "error": "Invalid JSON format",
                        "id": None
                    }                
                client_socket.send(json.dumps(response).encode(('utf-8')))
        except Exception as e:
            print(f"クライアントとの接続・リクエスト処理中にエラーが発生しました: {e}")
        finally:
            self.client_sockets.remove(client_socket)  # クライアントソケットの登録解除
            client_socket.close()


    def process_request(self, request: dict) -> dict:
        """RPCリクエストを処理し、結果を返す。
        
        引数（Args）:
            request (dict): クライアントからのRPCリクエスト
                          {'method': str, 'params': list, 'id': int}の形式
        
        戻り値（Returns）:
            dict: 処理結果を含むレスポンス
                 成功時: {'result': Any, 'result_type': str, 'id': int}
                 失敗時: {'error': str, 'id': int}
        """
        method = request.get("method")
        params = request.get("params", [])
        request_id = request.get("id")

        if not method or method not in self.functions:
            return {
                "error": f"Method '{method}' not found",
                "id": request_id
            }

        try:
            result = self.functions[method](*params)
            return {
                "result": result,
                "result_type": type(result).__name__,
                "id": request_id
            }
        except Exception as e:
            return {
                "error": str(e),
                "id": request_id
            }

    def check_timeout(self) -> None:
        """クライアントアクティビティのタイムアウトを監視する。
        
        一定時間（self.timeout秒）クライアントからのアクティビティがない場合、
        サーバーを自動的にシャットダウンする。
        
        このメソッドは別スレッドで実行され、以下の処理を行う：
        1. 最後のアクティビティからの経過時間を計算
        2. タイムアウト条件をチェック
        3. 残り時間に基づいて次のチェックまでの待機時間を動的に計算
        
        タイムアウトが検出された場合、サーバーは停止され、全ての接続が閉じられる。
        """
        while self.running:
            current_time = time.time()
            elapsed_time = current_time - self.last_activity
            
            if elapsed_time > self.timeout:
                print(f"{self.timeout}秒間応答がなかったため、サーバーを停止します")
                self.stop()
                break
                
            # 次のチェックまでの待機時間を動的に計算
            next_check = min(1, self.timeout - elapsed_time)
            time.sleep(next_check)

    def start(self) -> None:
        """RPCサーバーを起動し、クライアントからの接続を待ち受ける。
        
        各クライアント接続に対して新しいスレッドを作成し、
        handle_client メソッドを実行する。
        また、タイムアウトを監視する別スレッドも起動する。
        """
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.running = True
        self.last_activity = time.time()  # サーバー起動時に初期化
        print(f"サーバーが{self.host}:{self.port}で起動しました")

        # タイムアウトチェック用のスレッドを開始
        timeout_thread = threading.Thread(target=self.check_timeout)
        timeout_thread.daemon = True
        timeout_thread.start()

        try:
            while self.running:
                try:
                    client_socket, addr = self.socket.accept()
                    print(f"クライアント({addr})が接続しました")
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except OSError: 
                    # タイムアウトなどでサーバーソケットが閉じられた場合は、ループを抜ける
                    break
                except Exception as e:
                    print(f"サーバー稼働中に予期せぬエラーが発生しました: {e}")
                    break
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self) -> None:
        """RPCサーバーを停止する。
        以下の処理を実行する：
        1. サーバーの実行状態フラグがTrueであれば、Falseに設定
        2. すべてのクライアント接続を閉じる
        3. サーバーソケットを閉じる
        """
        if self.running:
            self.running = False
            # すべてのクライアントソケットを閉じる
            for client_socket in self.client_sockets:
                client_socket.close()
            self.socket.close() #サーバーソケットを閉じる
            print("サーバーを終了します")


# RPCの関数を定義する
def floor(x: float) -> int:
    """数値の小数点以下を切り捨てる。
    
    引数（Args）:
        x (float): 切り捨てる数値
        
    戻り値（Returns）:
        int: 切り捨て後の整数
    """
    return math.floor(x)

def nroot(x: float, n: int) -> float:
    """数値xのn乗根を計算する。
    
    引数（Args）:
        x (float): 底の数値
        n (int): 根の次数
        
    戻り値（Returns）:
        float: x の n 乗根
    """
    return x ** (1/n)

def reverse(s: str) -> str:
    """文字列を逆順にする。
    
    引数（Args）:
        s (str): 逆順にする文字列
        
    戻り値（Returns）:
        str: 逆順にした文字列
    """
    return s[::-1]

def valid_anagram(str1: str, str2: str) -> bool:
    """2つの文字列がアナグラムかどうかを判定する。
    
    引数（Args）:
        str1 (str): 1つ目の文字列
        str2 (str): 2つ目の文字列
        
    戻り値（Returns）:
        bool: アナグラムの場合True、そうでない場合False
    """
    return sorted(str1.lower()) == sorted(str2.lower())

def sort_strings(str_arr: list) -> list:
    """文字列のリストをソートします。
    
    引数（Args）:
        str_arr (List[str]): ソートする文字列のリスト
        
    戻り値（Returns）:
        List[str]: ソート済みの文字列リスト
    """
    return sorted(str_arr)

if __name__ == "__main__":
    # サーバーを作成し、設定する
    server = RPCServer()
    
    # サーバーに関数を登録する
    server.register_function("floor", floor)
    server.register_function("nroot", nroot)
    server.register_function("reverse", reverse)
    server.register_function("validAnagram", valid_anagram)
    server.register_function("sort", sort_strings)
    
    # サーバーを稼働する
    server.start()