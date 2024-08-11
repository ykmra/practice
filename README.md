# practice

## Guess the number game.py
ユーザーが指定した数値範囲内で生成されたランダムな数字を、制限された回数内で推測するゲームプログラム。  
制限回数は、デフォルトでは5回となっている。

ユーザーに 2 つの数字、最小数（n）と最大数（m）を入力してもらう。  
ユーザーが最小数と最大数を入力すると、プログラムが n から m の範囲内でランダムな数字を生成する。  
ユーザーは、生成されたランダムな数字を推測して入力する。  
制限回数内で、正解するまで繰り返し回答できる。



## file-converter.py
markdownファイルををhtmlファイルに変換するプログラム。  

ターミナル上で、以下コマンドによって実行できる。  
以下において、markdownは実行するコマンド、inputfile は .mdファイルへのパス、outputfileはプログラムを実行した後に作成される .htmlファイルへのパス。  
```
python3 file-converter.py markdown inputfile outputfile
```  

以下は関連ファイル。  
sample.md: markdownのサンプルファイル  
index.html: file-converter.pyによって、sample.mdをhtmlに変換したファイル  

## file_manipulator.py
ファイル操作を行うプログラム。  
reverse, copy, duplicate-contents, replace-stringの4種類のコマンドで実行できる。  
例えば、ターミナル上で、以下コマンドによって実行できる。  
以下において、reverseは実行するコマンド、inputpathは 読み込むファイルへのパス、outputpathはプログラムを実行した後に作成されるファイルへのパスを表す。  
```
python3 file_manipulator.py reverse inputpath outputpath
```  


各コマンドと引数は、以下の通り。  
```
reverse inputpath outputpath
```
 inputpath にあるファイルを受け取り、outputpath に inputpath の内容を逆にした新しいファイルを作成する。
```
copy inputpath outputpath
```
 inputpath にあるファイルのコピーを作成し、outputpath として保存する。
```
duplicate-contents inputpath n
```
inputpath にあるファイルの内容を読み込み、その内容を複製し、複製された内容を inputpath に n 回複製する。
```
replace-string inputpath needle newstring
```
inputpath にあるファイルの内容から文字列 'needle' を検索し、'needle' の全てを 'newstring' に置き換える。


