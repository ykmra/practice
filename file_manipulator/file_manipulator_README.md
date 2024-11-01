# File Manipulator

ファイル操作を行うシンプルなコマンドラインツールです。テキストファイルの内容を様々な方法で操作することができます。

## 機能

このツールは以下の4つの機能を提供します：

1. **reverse** - ファイルの内容を逆順に書き出し
2. **copy** - ファイルのコピー
3. **duplicate-contents** - ファイルの内容を指定回数複製
4. **replace-string** - ファイル内の文字列を置換

## 使用方法

```bash
python file_manipulator.py <command> <arguments>
```

### コマンド一覧

#### reverse
ファイルの内容を逆順にして新しいファイルに書き出します。
```bash
python file_manipulator.py reverse <input_path> <output_path>
```

#### copy
ファイルを別の場所にコピーします。
```bash
python file_manipulator.py copy <input_path> <output_path>
```

#### duplicate-contents
ファイルの内容を指定した回数だけ複製し、元のファイルに追加します。
```bash
python file_manipulator.py duplicate-contents <input_path> <n>
```
- `n`: 複製する回数（整数）

#### replace-string
ファイル内の特定の文字列を新しい文字列に置換します。
```bash
python file_manipulator.py replace-string <input_path> <needle> <newstring>
```
- `needle`: 置換対象の文字列
- `newstring`: 置換後の文字列

## エラーハンドリング

プログラムは以下の場合にエラーメッセージを表示して終了します：

- コマンドライン引数の数が正しくない場合
- 指定されたファイルが存在しない場合
- duplicate-contentsコマンドで数値以外が指定された場合
- 不正なコマンドが指定された場合

## 注意事項

- ファイルの操作は取り消しできません。特にreplace-stringやduplicate-contentsコマンドは元のファイルを直接変更するため、使用前にファイルのバックアップを取ることを推奨します。
- テキストファイルを対象としています。バイナリファイルでの動作は保証されません。