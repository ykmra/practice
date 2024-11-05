# Python RPC (Remote Procedure Call) Implementation: PythonによるRPCの実装

TCP/IPソケット通信を使用したシンプルなRPC（Remote Procedure Call）の実装です。サーバー側で定義された関数をクライアント側からリモートで呼び出すことができます。自動タイムアウト機能を備え、一定時間未使用の場合は自動的にシャットダウンします。

## 必要要件
- Python 3.6以降
- 標準ライブラリのみを使用（追加パッケージ不要）

## システム構成

本システムは以下の2つのPythonファイルで構成されています。
1. **rpc_server.py**: RPCサーバーの実装
2. **rpc_client.py**: RPCクライアントの実装

## 利用可能な関数

サーバーには以下の関数が実装されています。

1. **floor(x: float) → int**
   - 数値の小数点以下を切り捨てる

2. **nroot(x: float, n: int) → float**
   - 数値xのn乗根を計算する

3. **reverse(s: str) → str**
   - 文字列を逆順にする

4. **validAnagram(str1: str, str2: str) → bool**
   - 2つの文字列がアナグラムかどうかを判定する

5. **sort(str_arr: list) → list**
   - 文字列のリストをソートする（ひらがな、アルファベット対応）


## 使用方法

### サーバーの起動
```bash
python rpc_server.py
```
サーバーはデフォルトで以下の設定で起動します。
- ホスト: localhost
- ポート: 8000
- タイムアウト: 60秒

### クライアントの実行

```bash
python rpc_client.py
```
クライアントを起動すると、以下の状態になります。
1. 自動的にサーバーに接続する
2. 利用可能な関数の一覧が表示される
3. 対話型インターフェースで関数を呼び出すことができる


### クライアントコマンド

- `help`: 利用可能な関数の一覧と使用方法を表示する
- `exit`: プログラムを終了する
- 関数名: 関数名を入力すると、必要な引数の入力を求められる


## 特徴

### サーバー側の特徴
- 複数クライアントからの接続を同時に受け付けることができる
- クライアントからのリクエストに基づいて関数を処理し、クライアントに結果を返す
- 各クライアントが切断した時には、どのクライアントが切断したかをサーバーに表示する
- 設定した時間内にクライアントからのアクティビティがない場合、自動でサーバープログラムを終了する
- タイムアウト時間を設定することができる

### クライアント側の特徴
- 対話型のコマンドライン操作でサーバーから関数を呼び出せる
- 関数名と求められた引数を入力すると、サーバーから結果が返ってくる
- `help`コマンドで関数一覧を表示できる
- `exit`コマンドでクライアントを終了できる
- 不正な値が入力された場合は、再度入力プロンプトを表示する
- サーバーとの接続が切断された場合は、切断されたことを表示して自動的にクライアントプログラムを終了する

## 通信プロトコル

JSON形式でデータを送受信します。

### リクエスト形式 (クライアント→サーバー)
```json
{
    "method": "関数名",
    "params": [引数1, 引数2, ...],
    "id": リクエストID
}
```

### レスポンス形式 (サーバー→クライアント)
```json
{
    "result": 実行結果,
    "result_type": 結果の型,
    "id": リクエストID
}
```

### エラーレスポンス (サーバー→クライアント)
```json
{
    "error": "エラーメッセージ",
    "id": リクエストID
}
```

## 制限事項
- サーバーとクライアントは同一ネットワーク上にある必要があります
- バイナリデータの送受信には対応していません
- 引数の型は基本的なPythonの型（int, float, str, list）に限定されます
- タイムアウト時間はサーバーを起動する前に設定する必要があります

## 工夫した点

### サーバー側の工夫

#### 1. 新しい関数を容易に追加できる仕組み
`register_function`メソッドを使うことで、新しい関数をサーバーに簡単に追加できる。例えば、新しい計算方法や文字列処理を追加したい場合、このメソッドで関数を登録するだけでクライアントからその関数を呼び出せるようになる。
```python
def register_function(self, name: str, function: Callable) -> None:
    self.functions[name] = function
```

#### 2. タイムアウト機能の実装
   - 一定時間(デフォルトは60秒)クライアントからの応答がない場合、自動的にシャットダウンするようにした。
   - 独立したスレッドでクライアントの最終アクティビティ時刻の監視することで、メインの処理に影響を与えないようにした。
   - 最後のクライアントアクティビティからの経過時間を基に、動的に監視間隔を調整し、効率的にタイムアウトを監視するようにした。
   - サーバー停止時には、全てのソケットを閉じ、確実にリソースを解放するようにした。

```python
def check_timeout(self) -> None:
    while self.running:
        current_time = time.time()
        elapsed_time = current_time - self.last_activity # self.last_activityは、クライアントの最終アクティビティ時刻
        if elapsed_time > self.timeout:
            print(f"{self.timeout}秒間応答がなかったため、サーバーを停止します")
            self.stop()  # すべてのソケットを閉じる関数
            break
        # 次のチェックまでの待機時間を動的に計算
        next_check = min(1, self.timeout - elapsed_time)
        time.sleep(next_check)
```
```python
# start関数内のタイムアウトチェック用のスレッド
timeout_thread = threading.Thread(target=self.check_timeout)
timeout_thread.daemon = True
timeout_thread.start()
```

#### 3. 複数のクライアントへの同時対応
サーバーに接続してきた各クライアントに対して別々のスレッドを立ち上げて対応するようにした。これにより、複数のユーザーが同時にリクエストを送っても、スムーズに処理できるようになる。例えば、同時に複数の計算や文字列操作を依頼しても、別々のスレッドで対応するため、並行して処理することができる。
```python
# startメソッド内
while self.running:
    try:
        # クライアントからの接続の待ち受けは、メインスレッドで行う
        client_socket, addr = self.socket.accept()
        # クライアント処理は別のスレッドを立ち上げて行う
        print(f"クライアント({addr})が接続しました")
        thread = threading.Thread(
            target=self.handle_client,
            args=(client_socket, addr)
        )
        thread.daemon = True
        thread.start()
```

#### 4. 必要に応じたクライアント接続の切断と、サーバーシャットダウン時の全ての接続の切断
ユーザーが`exit`コマンドを送信した場合や、クライアントのリクエスト処理実行中に何らかのエラーが起きた場合、該当のクライアントソケットとスレッドのみを閉じるようにした。サーバーソケットは開いたままなので、他のクライアントの接続には影響がない。サーバーがCtrl+Cによりシャットダウンするときは、全てのスレッド・クライアントソケット・サーバーソケットが閉じるようになっている。
このように、必要な時に必要な接続だけを閉じ、かつ、最終的にすべての接続を確実に閉じるようにすることで、コンピュータのリソースを無駄に使い続けることを防いでいる。
```python
# サーバーを停止する時のメソッド
def stop(self) -> None:
    if self.running:
        self.running = False
        for client_socket in self.client_sockets:
            client_socket.close()
        self.socket.close()
        print("サーバーを終了します")
```
--------------

### クライアント側の工夫

#### 1. 関数情報の一元管理
`self.functions`ディクショナリに利用可能な関数の説明や引数情報を登録し、`show_help`メソッドでそれらを基に関数情報を表示するようにしている。
```python
# 関数を管理するディクショナリ
self.functions = {
    'floor': ('数値xの小数点以下を切り捨てます', [('数値x', float)]),
    'nroot': ('数値xのn乗根を計算します', [('数値x', float), ('根n(n=2なら平方根)', int)]),
    # ...以下略...
}
```
```python
# 利用可能な関数の一覧を表示する関数
def show_help(self) -> None:
    print("\n=== 利用可能な関数一覧 ===")
    # self.functionsの情報を基に、関数一覧を表示している
    for name, (desc, args) in self.functions.items():
        print(f"\n関数名: {name}")
        print(f"説明: {desc}")
        # ...以下略...
```
以下の`get_input`メソッドでも、`self.functions`ディクショナリの情報に基づいてユーザーからの入力バリデーションを行ったり、各関数に必要な引数の型に自動的に変換するようにしている。

このため、`self.functions`ディクショナリに新たな関数の情報を追加するだけで、ヘルプの表示やユーザー入力処理が新たな関数に自動的に対応するようになっている。このように関数情報を一元管理することで、プログラムの拡張やメンテナンスが容易になる。
```python
# get_inputメソッドの一部
# self.functionsの情報を基に、ユーザーに適切なデータ型の値の入力を促している
for arg_name, arg_type in self.functions[cmd][1]:
    while True:
        cmd = input("\n実行する関数名を入力してください('help'でヘルプ表示, 'exit'で終了): ").strip()
        # ...省略...
        
        if cmd not in self.functions:
            print(f"エラー: 関数'{cmd}'は存在しません")
            continue
    while True:
        try:
            value = input(f"{arg_name}を入力 ({arg_type.__name__}型): ")
            # ユーザーからの入力を適切なデータ型に変換(arg_type(value))
            args.append(arg_type(value))
            break
        except ValueError:
            print(f"エラー: {arg_type.__name__}型で入力してください")
            # ...以下略...
```
また、上記の`get_input`メソッドでは、ユーザーが不正な入力をした場合は具体的なエラーメッセージを表示して再度入力プロンプトを表示するようにし、正しい形式の値のみを受け入れるようにしている。

#### 2. 接続の適切な管理
ソケットの状態（接続の有無）をself.socketで管理し、サーバーからの切断時やエラー発生時に適切にソケットを閉じるようにしている。
これにより、ソケットのリソースリークを防いでいる。
```python
if not data:
    print("サーバーが正常に切断しました")
    self.socket.close()
    self.socket = None
    return None
```
```python
except OSError as e:
    print(f"エラーが発生したため、サーバーとの接続が切断されました: {e}")
    self.socket.close()
    self.socket = None
    return None
```

#### 3. メインループでの柔軟なエラーハンドリングと終了処理
`main`関数内では、`KeyboardInterrupt`を使ってユーザーの`exit`コマンドを処理し、最終的に全てのソケットを閉じてプログラムを終了するようにしている。
これにより、ユーザーがいつでも安全にプログラムを終了できるとともに、リソースが適切に解放される。
```python
#main関数内
except KeyboardInterrupt:
    break
finally:
    if client.socket:
        client.socket.close()
    print("プログラムを終了します")
```


