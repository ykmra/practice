import socket
import json
from typing import Any, Optional

class RPCClient:
    """RPCクライアントクラス
    
    このクラスでは、RPCサーバーに接続し、登録された関数を呼び出すためのインターフェースを提供する。
    
    クラスの属性（Attributes）:
        host (str): 接続先サーバーのホスト名
        port (int): 接続先サーバーのポート番号
        socket (Optional[socket.socket]): サーバーとの通信用ソケット
        request_id (int): リクエストを識別するためのID
        functions (Dict[str, Tuple[str, Union[List[Tuple[str, type]], str]]]): 
            利用可能な関数の情報を格納する辞書
    """
    def __init__(self, host: str = 'localhost', port: int = 8000):
        """RPCClientのインスタンスを初期化する。

        引数（Args）:
            host (str, optional): サーバーのホスト名。デフォルトは'localhost'
            port (int, optional): サーバーのポート番号。デフォルトは8000
        """
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.request_id = 0
        self.functions = {
            'floor': ('数値xの小数点以下を切り捨てます', [('数値x', float)]),
            'nroot': ('数値xのn乗根を計算します', [('数値x', float), ('根n(n=2なら平方根)', int)]),
            'reverse': ('文字列を逆順にします', [('文字列', str)]),
            'validAnagram': ('2つの文字列がアナグラムかどうかを判定します', [('文字列1', str), ('文字列2', str)]),
            'sort': ('入力された複数の文字列を配列化し、配列を昇順にソートします(対応文字: ひらがな、アルファベット)', 'list')
        }

    def connect(self) -> None:
        """サーバーに接続する。
        
        発生する可能性のある例外（Raises）:
            Exception: 接続に失敗した場合
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
        except ConnectionRefusedError:
            # ConnectionRefusedErrorをraiseして呼び出し元(main関数)に伝え、呼び出し元で適切なエラーメッセージを表示するようにする。
            # ConnectionRefusedErrorとして上位にraiseしないと、Exceptionとしてraiseされるので、エラーの原因が分かりにくくなってしまう。
            raise 
        except Exception as e:
            raise Exception(f"サーバーへの接続に失敗: {e}")


    def call(self, method: str, params: list) -> Any:
        """RPCメソッドを呼び出し、結果を取得する。
        
        引数（Args）:
            method (str): 呼び出すメソッドの名前
            params (list): メソッドに渡すパラメータのリスト
            
        戻り値（Returns）:
            Any: メソッドの実行結果
            None: サーバーが切断された場合、または不正なデータを受信した場合
            
        発生する可能性のある例外（Raises）:
            ConnectionError: サーバーに接続されていない場合
            Exception: サーバーがエラーを返した場合
        """
        if not self.socket:
            raise ConnectionError("サーバーに接続されていません")

        self.request_id += 1
        request = {
            "method": method,
            "params": params,
            "id": self.request_id
        }
        print(f'\n"{method}({params})" のリクエストを送信しました。リクエストID: {self.request_id}')

        # リクエストの送信とサーバーからの応答受信
        try:
            # リクエストを送信
            self.socket.send(json.dumps(request).encode('utf-8'))
            
            # サーバーからの応答を受信
            data = self.socket.recv(4096)
            if not data:
                # サーバーが正常に切断した場合
                print("サーバーが正常に切断しました")
                self.socket.close()
                self.socket = None
                return None
            
            response = json.loads(data.decode('utf-8'))
            # サーバーからの応答にエラーが含まれるか確認
            if "error" in response:
                raise Exception(response["error"])
            # サーバーからの応答にエラーがふくまれなければ、resultを返す
            return response.get("result")
        except OSError as e:
            # サーバーとの接続が異常に切断された場合
            print(f"エラーが発生したため、サーバーとの接続が切断されました: {e}")
            self.socket.close()
            self.socket = None
            return None
        except json.JSONDecodeError:
            # 不正なデータを受信した場合
            print("サーバーからの応答が不正です")
            return None

    def show_help(self) -> None:
        """利用可能な関数の一覧と説明を表示する。"""
        print("\n=== 利用可能な関数一覧 ===")
        # self.functionsのkeyにはstr型の関数名、valueにはタプル型の(説明文, 引数情報)が入っている
        # nameにはkey(関数名)、タプルの中のdescには説明文、argsには引数情報(リスト型)が入る。例えば、nroot関数のargsは[('数値x', float), ('根n', int)]となる。
        for name, (desc, args) in self.functions.items():
            print(f"\n関数名: {name}")
            print(f"説明: {desc}")
            # argsがリストの場合(floor関数, nroot関数など)と、そうでない場合(argsが文字列の場合(sort関数))で処理を分ける
            if isinstance(args, list):
                # arg[0]には引数名、arg[1]には引数のデータ型が入る。nroot関数の場合、arg_infoは["数値x (float型)", "根n (int型)"]となる。
                arg_info = [f"{arg[0]} ({arg[1].__name__}型)" for arg in args]
                # arg_infoをカンマで結合して表示する。nroot関数の場合は、"引数: 数値x(float型), 根n(int型)"となる。
                print(f"引数: {', '.join(arg_info)}")
            else:
                # sort関数の場合
                print("引数: 複数の文字列 (複数の文字列をlist型に変換)")
        print("\n=====================================")

    def get_input(self) -> tuple[str, list]:
        """ユーザーからの入力を取得し、関数名と引数のタプルを返す。
        
        戻り値（Returns）:
            Tuple[Optional[str], Optional[List[Any]]]: (関数名, 引数のリスト)のタプル
                                                    exitコマンドの場合は(None, None)
        
        発生する可能性のある例外（Raises）:
            KeyboardInterrupt: exitコマンドが入力された場合
        """
        while True:
            cmd = input("\n実行する関数名を入力してください('help'でヘルプ表示, 'exit'で終了): ").strip()
            
            if cmd.lower() == 'exit':
                raise KeyboardInterrupt
            if cmd.lower() == 'help':
                self.show_help()
                continue
            
            if cmd not in self.functions:
                print(f"エラー: 関数'{cmd}'は存在しません")
                continue

            # 引数の取得
            if cmd == 'sort':
                print("ソートする文字列をスペース区切りで入力してください")
                words = input("例 'apple banana cherry': ").split()
                return cmd, [words]
            
            # その他の関数の引数処理
            args = []
            for arg_name, arg_type in self.functions[cmd][1]:
                while True:
                    try:
                        value = input(f"{arg_name}を入力 ({arg_type.__name__}型): ")
                        args.append(arg_type(value))
                        break
                    except ValueError:
                        print(f"エラー: {arg_type.__name__}型で入力してください")

            return cmd, args

def main():
    """メインプログラムを実行する。"""
    client = RPCClient()
    
    try:
        print("サーバーに接続中...")
        client.connect()
        print("接続成功！")
        client.show_help()

        while True:
            try:
                func_name, args = client.get_input()
                result = client.call(func_name, args)
                if result is None:
                    print("サーバーが切断しました")
                    break
                print(f"\n結果: {result}")
            except ValueError as e:
                print(f"エラー: {e}")
            except KeyboardInterrupt:
                break
    except ConnectionRefusedError:
        print("サーバーと接続できませんでした。サーバーが起動しているか確認してください。")
    except ConnectionError as e:
        print(f"接続の問題によりエラーが発生しました: {e}")
    finally:
        if client.socket:
            client.socket.close()
        print("プログラムを終了します")

if __name__ == "__main__":
    main()