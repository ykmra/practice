import random

def input_number(str):
    while True:
        num = input(f'{str}を入力してください')
        try:
            num = int(num)
            print(f'{str}は{num}です')
            break
        except ValueError:
            print('数字を入力してください')
    return num

n = input_number('最小数')
m = input_number('最大数')

correct_answer = random.randint(n, m)

count = 0
max_count = 5
while count < max_count:
    answer = input(f'{n}から{m}の間で生成された数字を予測して入力してください。{max_count}回以内に正解してください。')
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