# Лабораторная работа 5. Алгоритмическая обработка числовых рядов

## Запуск

Из папки `num_series_app`:

```bash
python main.py --kind sine --n 20 --window 3 --alpha 0.3 --seed 7
```

## Примеры

```bash
# генерация + анализ
python main.py --kind sine --n 20 --window 3 --seed 7

# генерация + сохранение в JSON
python main.py --kind random --n 50 --save data/random.json

# загрузка из файла + анализ
python main.py --load data/random.json --window 5
python main.py --load data/series.csv --window 5

# пайплайн: генерация → сохранение → чтение → анализ
python main.py --kind sine --n 30 --save data/s.json
python main.py --load data/s.json --window 3

# экспорт результата в CSV
python main.py --kind trend --n 30 --export out.csv
```

## Тесты

```bash
python -m pytest
python run_self_tests.py
```
