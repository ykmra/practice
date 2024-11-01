import os
import sys
import markdown

def validate_args_count(expected_count):
    #引数の数が正しいかチェック
    if len(sys.argv) != expected_count + 2:
        print(f"エラー: 引数の数が違います。引数の数は{expected_count}個です")
        sys.exit(1)


def validate_file_exists(filepath):
    if not os.path.exists(filepath):
        print(f"エラー: ファイル {filepath}が存在しません。正しいパスを入力してください")
        sys.exit(1)


def convert_markdown(inputfile, outpufile):
    validate_file_exists(inputfile)
    with open(inputfile, 'r') as f:
        contents = f.read()

    with open(outpufile, 'w') as f:
        f.write(markdown.markdown(contents, extensions=['markdown.extensions.tables']))


if __name__ == "__main__":
    if sys.argv[1] != 'markdown':
        print("エラー: 正しいコマンドを入力して下さい")
        sys.exit(1)
    else:
        validate_args_count(2)
        convert_markdown(sys.argv[2], sys.argv[3])