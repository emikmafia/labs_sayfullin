print("--- Задание 1.1 ---")
n = int(input('Введите количество чисел n: '))
print(f'Введите {n} чисел через пробел: ')

numbers = list(map(float, input().split()))

total_sum = 0
multiplier = 1

for x in numbers[:n]:
    is_odd = int(x) % 2 != 0  
    multiplier = multiplier * is_odd 
    total_sum += x * multiplier 

print(f'Сумма нечетных чисел в начале: {total_sum}')


print("\n--- Задание 1.2 ---")
is_valid_2 = False

while not is_valid_2:
    try:
        n1 = int(input("Введите целое число N (> 0): "))
        if n1 > 0:
            c = 0  
            digit_sum = 0  
            temp_n1 = n1 
            
            while temp_n1 > 0:
                chis = temp_n1 % 10       
                digit_sum += chis   
                c += 1          
                temp_n1 = temp_n1 // 10        
            
            print("Количество цифр:", c)
            print("Сумма цифр:", digit_sum)
            is_valid_2 = True
        else:
            print("Число должно быть больше 0.")
    except ValueError:
        print('Ошибка: введите целое число > 0')


print("\n--- Задание 2 ---")
s = input('Введите строку: ')
words = s.rstrip('.').split() 
print('Количество слов:', len(words))


print("\n--- Задание 3 ---")
is_valid_3 = False

while not is_valid_3:
    try:
        a = list(map(int, input('Введите элементы массива (через пробел): ').split()))
        obs_sum = sum(a)
        
        obs_umn = 1
        for x in a:
            obs_umn *= x
            
        print('Список:', a)
        print('Сумма элементов:', obs_sum)
        print('Произведение элементов:', obs_umn)
        is_valid_3 = True
    except ValueError:
        print("Ошибка: вводите только целые числа через пробел!")
