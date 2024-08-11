import os
import sys


def validate_args_count(expected_count):
    # 引数の数が正しいかチェック
    if len(sys.argv) != expected_count + 2:
        print(f"エラー: 引数の数が違います。引数の個数は{expected_count}個です")
        sys.exit(1)


def validate_file_exists(filepath):
    #ファイルパスが正しいかチェック
    if not os.path.exists(filepath):
        print(f"エラー: ファイル {filepath}が存在しません。正しいパスを入力してください")
        sys.exit(1)

def reverse(inputpath, outputpath):
    validate_file_exists(inputpath)
    with open(inputpath, 'r') as f:
        contents = f.read()

    with open(outputpath, 'w') as f:
        f.write(contents[::-1])


def copy(inputpath, outputpath):
    validate_file_exists(inputpath)
    with open(inputpath, 'r') as f:
        contents = f.read()

    with open(outputpath, 'w') as f:
        f.write(contents)


def duplicate_contents(inputpath, n):
    validate_file_exists(inputpath)
    try:
        n = int(n)
    except ValueError:
        print("エラー: 第2引数は数値を入力してください")
        sys.exit(1)
    with open(inputpath, 'r') as f:
        contents = f.read()

    with open(inputpath, 'a') as f:
        f.write(contents * (n - 1))


def replace_string(inputpath, needle, newstring):
    validate_file_exists(inputpath)
    with open(inputpath, 'r') as f:
        contents = f.read()

    with open(inputpath, 'w') as f:
        f.write(contents.replace(needle, newstring))


func_dict = {'reverse': lambda: reverse(sys.argv[2], sys.argv[3]), 'copy': lambda: copy(sys.argv[2], sys.argv[3]), 'duplicate-contents': lambda: duplicate_contents(sys.argv[2], sys.argv[3]), 'replace-string': lambda: replace_string(sys.argv[2], sys.argv[3], sys.argv[4])}
command = sys.argv[1]

if command in func_dict:
    if sys.argv[1] == 'replace-string':
        validate_args_count(3)
    else:
        validate_args_count(2)

    func_dict[command]()

else:
    print("エラー: 正しいコマンドを入力して下さい")
    sys.exit(1)




