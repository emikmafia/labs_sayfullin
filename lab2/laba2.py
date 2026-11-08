import math

while True:
    try:
        menu = int(input('Выберите тип сечения (1-прямоугольное, 2-круглое, 3-двутавр): '))
        if menu in (1, 2, 3):
            break
        print('Повторите ввод (1-3)')
    except ValueError:
        print('Ошибка: введите число')

def read_value(prompt, lo, hi, cast=float):
    while True:
        try:
            v = cast(input(prompt))
            if lo <= v <= hi:
                return v
            print(f'Неверное значение, введите число от {lo} до {hi}')
        except ValueError:
            print('Ошибка: введите число')


sech = read_value('Введите ширину/диаметр сечения (10-1000): ', 10, 1000)
iz   = read_value('Введите изгибающий момент (0.1-500): ', 0.1, 500)
nap  = read_value('Введите допускаемое напряжение (50-400): ', 50, 400)
vis  = read_value('Введите высоту сечения (10-1000): ', 10, 1000)


if menu == 1:      
    W = sech * vis**2 / 6
elif menu == 2:  
    W = math.pi * sech**3 / 32
else:            
    W = vis**3 / 12

# Считаем фактическое напряжение (переводим кН*м в Н*мм -> *1_000_000)
sigma = (iz * 1_000_000) / W      


n = nap / sigma

if n < 0.5:
    klass = 'большой запас'
elif n <= 1.0:
    klass = 'допустимо'
else:
    klass = 'перегрузка'

print('\n--- Результаты ---')
print(f'Тип сечения: {menu}')
print(f'Момент сопротивления W = {W:.2f} мм³')
print(f'Фактическое напряжение σ = {sigma:.2f} МПа')


if sigma <= nap:
    print("Проверка прочности: ВЫПОЛНЕНА (σ ≤ [σ])")
else:
    print("Проверка прочности: НЕ ВЫПОЛНЕНА (σ > [σ])")

print(f'Коэффициент запаса n = {n:.3f} — {klass}')
