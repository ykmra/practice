import sys
import random

def input_number(str):
    while True:
        num = input(f'{str}を入力してください。: ')
        try:
            num = int(num)
            print(f'{str}は{num}です')
            break
        except ValueError:
            print('数字を入力してください。: ')
    return num

def generate_answer():
    min_num = input_number('最小数')
    max_num = input_number('最大数')

    if min_num > max_num:
        print(f"エラー: 最小数{min_num}が最大数{max_num}より大きいです。最大数より小さい最小数を入力してください。")
        sys.exit(1)

    return random.randint(min_num, max_num), min_num, max_num


def play_game(min_num, max_num, max_count=5):
    count = 0
    while count < max_count:
        answer = input(f'{min_num}から{max_num}の間で生成された数字を予測して入力してください。{max_count}回以内に正解してください。: ')
        count += 1
        try:
            answer = int(answer)
            print(f'回答{count}回目: あなたの回答は{answer}です。')
            if answer == correct_answer:
                print('おめでとうございます！正解です！')
                break
            else:
                print('不正解です。違う数字を入力してください。')
        except ValueError:
            print(f'回答{count}回目: 数字を入力してください。')
        if count == max_count:
            print(f'残念。。。{max_count}回以内に正解できませんでした…。')


if __name__ == "__main__":
    correct_answer, min_num, max_num = generate_answer()
    play_game(min_num, max_num, max_count=5)