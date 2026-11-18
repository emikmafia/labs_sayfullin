# Разбор кода проекта num_series_app

Подробное объяснение каждого модуля и синтаксиса Python, который в них используется.
Документ описывает текущее состояние проекта: лабораторные 5 и 5.1 и вариант 8.

---

## 1. Общая картина

Проект — консольное приложение: генерирует или читает числовой ряд, считает статистику,
сглаживает его скользящими средними и умеет сохранять/загружать данные.

```
num_series_app/
├── num_series/            пакет (библиотека) с логикой
│   ├── __init__.py        публичный API пакета
│   ├── generator.py       формирование рядов
│   ├── stats.py           среднее, медиана, размах
│   ├── moving_average.py  SMA, центрированное MA, EMA, замер скорости
│   ├── deque_average.py   те же средние на collections.deque
│   ├── io_json.py         сохранение/чтение JSON
│   ├── io_file.py         чтение txt/csv
│   └── variant8.py        ряд с выбросами, усечённое среднее, скользящая медиана
├── tests/                 тесты для pytest
├── conftest.py            настройка путей для pytest
├── pytest.ini             конфигурация pytest
├── test/                  пустая папка-черновик (не используется)
├── pytest.py              пустой файл-черновик (мешает запуску pytest!)
├── main.py                CLI основной программы
├── variant8.py            CLI варианта 8
├── run_self_tests.py      проверки без pytest
└── readme.md              как запускать
```

Поток данных:

```
generator / io_file / io_json ──list[float]──▶ stats
                              └──list[float]──▶ moving_average / deque_average / variant8
                                                        │
                                                        ▼
                                                     main.py
```

Два общих соглашения по всему проекту:

1. **Один тип данных** для передачи между модулями: `list[float]` (иногда `Sequence[float]`).
2. **Один контракт ошибок**: неверный вход — это `ValueError`. Поэтому `main.py` ловит
   только `ValueError` и превращает его в понятное сообщение и код возврата 1.

---

## 2. `num_series/__init__.py` — витрина пакета

```python
from .generator import random_series, sine_series, trend_series
from .stats import mean, median, spread, summarize
from .moving_average import (
    simple_moving_average,
    simple_moving_average_deque,
    centered_moving_average,
    exponential_moving_average,
    benchmark_moving_average,
)
from .io_json import save_series_json, load_series_json
from .io_file import load_series_txt, load_series_csv, load_series_auto

__all__ = [
    "random_series", "sine_series", "trend_series",
    "mean", "median", "spread", "summarize",
    "simple_moving_average", "simple_moving_average_deque",
    "centered_moving_average", "exponential_moving_average",
    "benchmark_moving_average",
    "save_series_json", "load_series_json",
    "load_series_txt", "load_series_csv", "load_series_auto",
]

__version__ = "1.1.0"
```

Что здесь важно:

- Точка перед именем модуля (`.generator`) — **относительный импорт**: «модуль из этой же папки».
  Он работает только внутри пакета (папки с `__init__.py`).
- `__all__` — список имён, которые считаются публичными. Он влияет на `from num_series import *`
  и служит документацией: всё, чего нет в списке, считается внутренним.
- Благодаря этому файлу пользователь пишет `from num_series import sine_series`, не зная,
  в каком файле лежит функция. Внутреннюю раскладку можно менять.
- `__version__` — строка версии пакета.

---

## 3. `generator.py` — источники данных

### 3.1. `_validate_n`

```python
def _validate_n(n: int) -> None:
    """Проверка, что n — положительное целое число."""
    try:
        is_positive_int = (n > 0) and (int(n) == n)
    except (TypeError, ValueError) as err:
        raise ValueError(
            f"n должно быть положительным целым числом "
            f"(получено: {n!r}; причина: {err.args[0]})"
        ) from err

    if not is_positive_int:
        raise ValueError(
            f"n должно быть положительным целым числом (получено: {n!r})"
        )
```

- Подчёркивание в начале имени — соглашение «это внутренняя функция, снаружи не вызывать».
- `n > 0` для `None`, строки или списка бросает `TypeError` — его ловит `except`.
- `int(n) == n` проверяет «целое по значению»: `int(2.5) == 2`, и `2 != 2.5` → `False`.
  Значение `10.0` проходит: `int(10.0) == 10 == 10.0`.
- `raise ... from err` — цепочка исключений. В трейсбеке будет видно исходную причину
  и наше сообщение, связанные явно («The above exception was the direct cause...»).
- `{n!r}` — в f-строке `!r` означает «подставить `repr()`», то есть значение с кавычками
  для строк, чтобы в сообщении было видно, что именно пришло.

### 3.2. Три генератора

```python
def random_series(n: int, low: float = -100.0, high: float = 100.0,
                  seed: Optional[int] = None) -> List[float]:
    _validate_n(n)
    if low >= high:
        raise ValueError(f"low должно быть меньше high (получено: {low} >= {high})")
    rng = random.Random(seed)
    return [rng.uniform(low, high) for _ in range(n)]
```

- `low` и `high` — параметры со значениями по умолчанию: их можно не передавать.
- `Optional[int]` означает «`int` или `None`».
- `random.Random(seed)` — **локальный** генератор случайных чисел. Если написать
  `random.seed(seed)`, изменится глобальное состояние модуля `random`
  для всей программы. Локальный объект ни на что больше не влияет.
- `[rng.uniform(low, high) for _ in range(n)]` — списковое включение (list comprehension):
  создать список из n элементов. `_` — обычное имя переменной, означающее «значение не нужно».
- `uniform(a, b)` — равномерное распределение на отрезке `[a, b]`.

```python
def sine_series(n: int, amplitude: float = 1.0, frequency: float = 1.0,
                noise: float = 0.0, seed: Optional[int] = None) -> List[float]:
    _validate_n(n)
    rng = random.Random(seed)
    return [
        amplitude * math.sin(2 * math.pi * frequency * i / n)
        + (rng.uniform(-noise, noise) if noise else 0.0)
        for i in range(n)
    ]
```

- `2 * math.pi * frequency * i / n` — фаза синуса: за `n` точек `frequency` полных периодов.
- `... if noise else 0.0` — условное выражение (тернарный оператор): «если `noise`
  ненулевое, взять шум, иначе ноль». Побочный эффект: при `noise == 0` генератор
  не вызывается, и последовательность случайных чисел не сдвигается.
- Многострочное включение — просто перенос выражения на несколько строк внутри `[]`.

```python
def trend_series(n: int, start: float = 0.0, step: float = 1.0,
                 noise: float = 0.0, seed: Optional[int] = None) -> List[float]:
    _validate_n(n)
    rng = random.Random(seed)
    return [
        start + step * i + (rng.uniform(-noise, noise) if noise else 0.0)
        for i in range(n)
    ]
```

Линейный тренд: значение растёт на `step` на каждом шаге.

### 3.3. Замечание

В этом файле лежит копия `_ensure_not_empty`, хотя она относится к `stats.py`, и импортированы
неиспользуемые `Dict`, `Sequence`. Это следствие того, как собирался код по методичке;
на работу не влияет.

---

## 4. `stats.py` — статистика вручную

```python
def _ensure_not_empty(data: Sequence[float]) -> None:
    if not data:
        raise ValueError("Ряд пуст: расчёт статистики невозможен")
```

- `Sequence[float]` — тип «любая последовательность чисел»: список, кортеж, `range`.
  Функция ничего не меняет, поэтому конкретный тип не важен.
- `not data` истинно для пустого списка, кортежа, строки.

```python
def mean(data: Sequence[float]) -> float:
    _ensure_not_empty(data)
    return sum(data) / len(data)
```

`sum` — встроенная функция, `len` — длина. Одно прохождение, O(n).

```python
def median(data: Sequence[float]) -> float:
    _ensure_not_empty(data)
    s = sorted(data)
    k = len(s) // 2
    if len(s) % 2:
        return float(s[k])
    return (s[k - 1] + s[k]) / 2.0
```

- `sorted(data)` возвращает **новый** список; исходный не меняется.
- `len(s) // 2` — целочисленное деление: для 5 элементов даёт 2, для 4 — тоже 2.
- `if len(s) % 2:` — остаток от деления на 2; в условии это «нечётное количество».
  Ненулевое число в условии Python считает истиной.
- `float(s[k])` — приведение типа: даже если в списке были `int`, результат будет `float`.
- Индексация с нуля: `s[0]` — первый элемент, `s[k - 1]` — предыдущий центральному.
- Сложность O(n log n) из-за сортировки. Устойчивость к выбросам — главное свойство медианы.

```python
def spread(data: Sequence[float]) -> float:
    _ensure_not_empty(data)
    return float(max(data) - min(data))
```

`max` и `min` — встроенные функции, два прохода O(n).

```python
def summarize(data: Sequence[float]) -> Dict[str, float]:
    _ensure_not_empty(data)
    return {
        "count": len(data),
        "mean": mean(data),
        "median": median(data),
        "spread": spread(data),
        "min": float(min(data)),
        "max": float(max(data)),
    }
```

- `Dict[str, float]` — аннотация «словарь, где ключ — строка, значение — число».
- Литерал словаря `{ "ключ": значение, ... }`.
- Функция вызывает соседние функции повторно: каждая заново проверяет вход.
  Это дублирование вычислений, но код остаётся простым.

---

## 5. `moving_average.py` — сглаживание и замер

### 5.1. Валидация окна

```python
def check_window(window: int, n: int) -> None:
    """Валидация размера окна."""
    if not isinstance(window, int) or window < 1:
        raise ValueError(f"window должно быть целым >= 1 (получено: {window})")
    if window > n:
        raise ValueError(
            f"window не может быть больше длины ряда (получено: {window} > {n})"
        )
```

- `isinstance(window, int)` — проверка типа во время выполнения.
- `not ... or ...` — объединение двух условий: «не целое **или** меньше единицы».
- Логика `or`/`and` в Python «короткая»: если левая часть уже истинна, правая не вычисляется.

### 5.2. SMA через бегущую сумму

```python
def simple_moving_average(data: Sequence[float], window: int) -> List[float]:
    check_window(window, len(data))
    running = sum(data[:window])
    result = [running / window]
    for i in range(window, len(data)):
        running += data[i] - data[i - window]
        result.append(running / window)
    return result
```

- `data[:window]` — срез: элементы с 0 по `window - 1`, правый конец не включается.
- `running += x` — то же, что `running = running + x`.
- Идея: при сдвиге окна одно значение уходит (`data[i - window]`), одно приходит (`data[i]`).
  Поэтому на шаг нужны одно сложение и одно вычитание — O(n) вместо O(n·window).
- Длина результата: `len(data) - window + 1`.

### 5.3. Центрированное MA

```python
def centered_moving_average(data: Sequence[float], window: int) -> List[float]:
    if window % 2 == 0:
        raise ValueError(f"Для центрированной SMA window должно быть нечётным ...")
    check_window(window, len(data))
    half_window = window // 2
    result = []
    for i in range(half_window, len(data) - half_window):
        current_window = data[i - half_window : i + half_window + 1]
        result.append(sum(current_window) / window)
    return result
```

- `range(a, b)` — от `a` до `b - 1`.
- Срез `data[i - half : i + half + 1]` даёт ровно `window` элементов:
  правый конец среза не включается, поэтому `+ 1`.
- Значение приписывается центру окна, а не правому краю — в этом отличие от обычной SMA.
- Чётное окно запрещено: у него нет единственного центрального элемента.

### 5.4. EMA

```python
def exponential_moving_average(data: Sequence[float], alpha: float) -> List[float]:
    if not data:
        raise ValueError("Ряд пуст: расчёт статистики невозможен")
    if not (0 < alpha <= 1):
        raise ValueError(f"alpha должна быть в диапазоне (0, 1] (получено: {alpha})")
    result = [float(data[0])]
    for i in range(1, len(data)):
        ema_val = alpha * data[i] + (1 - alpha) * result[-1]
        result.append(ema_val)
    return result
```

- `result[-1]` — последний элемент списка (отрицательный индекс считается с конца).
- `0 < alpha <= 1` — цепочка сравнений; в Python это `(0 < alpha) and (alpha <= 1)`.
- Рекуррентная формула: доля `alpha` от новой точки плюс `(1 - alpha)` от прошлого значения.
- `alpha = 1` возвращает исходный ряд, `alpha → 0` — сильное сглаживание.

### 5.5. SMA на `deque` (добавлено в ЛР 5.1)

```python
from collections import deque

def simple_moving_average_deque(data: Sequence[float], window: int) -> List[float]:
    """SMA с использованием deque (двусторонней очереди)."""
    check_window(window, len(data))
    result = []
    d = deque()
    running_sum = 0.0
    for x in data:
        d.append(x)
        running_sum += x
        if len(d) > window:
            running_sum -= d.popleft()
        if len(d) == window:
            result.append(running_sum / window)
    return result
```

- `deque()` — двусторонняя очередь из модуля `collections`. `append` справа,
  `popleft` слева, оба O(1).
- Логика: добавили элемент, прибавили к сумме; если окно переполнилось — убрали
  самый старый и вычли его.
- Результат совпадает с `simple_moving_average` (различие только в порядке операций
  с плавающей точкой, порядка 1e-15).

### 5.6. Замер скорости

```python
def benchmark_moving_average(data: Sequence[float], window: int, repeats: int = 1000) -> dict:
    check_window(window, len(data))

    t0 = time.perf_counter()
    for _ in range(repeats):
        simple_moving_average(data, window)
    t_list = (time.perf_counter() - t0) / repeats

    t0 = time.perf_counter()
    for _ in range(repeats):
        simple_moving_average_deque(data, window)
    t_deque = (time.perf_counter() - t0) / repeats

    return {"list": t_list, "deque": t_deque}
```

- `time.perf_counter()` — монотонные часы высокого разрешения; правильный выбор для замеров
  (в отличие от `time.time()`, который может «прыгать» из-за синхронизации).
- Замер повторяется `repeats` раз, результат делится на число повторов — получается
  среднее время одного вызова.
- Обе реализации имеют сложность O(n), поэтому сравнение показывает разницу констант,
  а не асимптотики. На практике list-версия выходит быстрее: у `deque` на каждом шаге
  два обращения по индексу и вызов `popleft`.

---

## 6. `deque_average.py` — отдельный модуль на `deque`

Модуль не заменяет `moving_average.py`, а повторяет его контракт
(`Sequence[float]` на входе, `list[float]` на выходе), но через `deque(maxlen=...)`.

```python
def _check_window(window: int, n: int) -> None:
    if not isinstance(window, int) or isinstance(window, bool):
        raise ValueError(f"window должен быть целым, получено: {window!r}")
    ...
```

- `isinstance(window, bool)` — отдельная проверка, потому что `bool` является подклассом `int`:
  `True` прошёл бы как `1`. Это защита от неочевидной ошибки.

```python
buf: Deque[float] = deque(maxlen=window)
running = 0.0
result: List[float] = []
for i, x in enumerate(data):
    if len(buf) == window:
        running -= buf[0]
    buf.append(x)
    running += x
    if i >= window - 1:
        result.append(running / window)
```

- `deque(maxlen=window)` — очередь, которая сама выбрасывает самый старый элемент
  при переполнении.
- `buf[0]` — первый (самый старый) элемент; вычитается **до** `append`, потому что
  после `append` `deque` уже выкинул бы его.
- `enumerate(data)` даёт пары «индекс, значение» — поэтому в цикле доступны `i` и `x`.
- Условие `i >= window - 1` — «окно уже полное», только с этого момента пишем результат.

`centered_moving_average_deque` объявлена как центрированная, требует нечётное окно,
но фактически собирает обычное скользящее окно и делит на `window` — центрирования
(сдвига на `half`) в ней нет. Так написано в методичке, поведение оставлено как есть.

`exponential_moving_average_deque` считает EMA одной переменной `prev`;
`deque(maxlen=1)` в ней играет роль «буфера последнего значения» и на результат не влияет.

---

## 7. `io_json.py` — сохранение и чтение JSON

```python
PathLike = Union[str, Path]
```

Псевдоним типа: функция принимает и строку, и объект `Path`.

```python
def save_series_json(data, path, meta=None, indent=2) -> None:
    if not data:
        raise ValueError("Ряд пуст: нечего сохранять")

    for i, v in enumerate(data):
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            raise ValueError(f"Элемент data[{i}] = {v!r} не является числом")
```

- `isinstance(v, (int, float))` — второй аргумент может быть кортежем типов.
- `or isinstance(v, bool)` — исключение булевых значений (они тоже `int`).

```python
    payload = {
        "meta": {
            "n": len(data),
            "created": datetime.now().isoformat(timespec="seconds"),
            **(meta or {}),
        },
        "data": list(data),
    }
```

- `**(meta or {})` — распаковка словаря в литерал: его ключи добавляются к `"meta"`.
  `meta or {}` защищает от `None`.
- `isoformat(timespec="seconds")` — строка времени вида `2025-01-15T10:30:00`.
- `list(data)` — копия, чтобы в файл попал обычный список.

```python
    file_path = Path(path)
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=indent)
    except OSError as err:
        raise ValueError(f"Не удалось записать файл {file_path}: {err}") from err
```

- `Path(path)` — объект пути из `pathlib`; работает и с `/`, и с `\`.
- `.parent` — папка, `.mkdir(parents=True, exist_ok=True)` создаёт её со всеми
  промежуточными уровнями и не падает, если она уже есть.
- `with ... as f:` — контекстный менеджер: файл закроется автоматически, даже при ошибке.
- `ensure_ascii=False` — русский текст пишется читаемо, а не `\u0440\u0443`.
- `OSError` — базовый класс ошибок ввода-вывода (нет прав, нет диска).

```python
def load_series_json(path, with_meta=False):
    ...
    try:
        with file_path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as err:
        raise ValueError(
            f"Файл {file_path} не является корректным JSON: "
            f"{err.msg} (строка {err.lineno})"
        ) from err
```

- `JSONDecodeError` содержит `msg` (что не так) и `lineno` (где именно).
- `except` может идти несколько подряд — каждый ловит свой тип.

```python
    if isinstance(payload, list):
        data, meta = payload, {}
    elif isinstance(payload, dict):
        if "data" not in payload:
            raise ValueError(...)
        data = payload["data"]
        meta = payload.get("meta", {}) or {}
    else:
        raise ValueError(...)
```

- `elif` — сокращение от `else if`.
- `"data" not in payload` — проверка наличия ключа в словаре.
- `payload.get("meta", {})` — значение по ключу или значение по умолчанию; второе `or {}`
  защищает от `"meta": null`.
- Поддерживаются два формата: полный объект и «голый» список чисел.

```python
    result = [float(v) for v in data]
    return (result, meta) if with_meta else result
```

- Приведение всех элементов к `float`.
- Возврат кортежа или списка в зависимости от флага — одна строка вместо `if/else`.

---

## 8. `io_file.py` — текстовые форматы

```python
_SEPARATORS = re.compile(r"[,;\s]+")
```

- `re.compile` заранее собирает регулярное выражение — быстрее при многократном использовании.
- `[,;\s]+` — «одна или более запятых, точек с запятой или пробельных символов».
  Жадный `+` склеивает подряд идущие разделители.

```python
def load_series_txt(path: PathLike) -> List[float]:
    file_path = Path(path)
    if not file_path.exists():
        raise ValueError(f"Файл не найден: {file_path}")
    result: List[float] = []
    try:
        with file_path.open("r", encoding="utf-8") as f:
            for lineno, raw in enumerate(f, start=1):
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    result.append(float(line))
                except ValueError as err:
                    raise ValueError(f"{file_path}:{lineno}: '{line}' не является числом") from err
    except OSError as err:
        raise ValueError(f"Не удалось прочитать файл {file_path}: {err}") from err
```

- Файл — итерируемый объект: `for lineno, raw in enumerate(f, start=1)` читает построчно.
- `enumerate(..., start=1)` — нумерация строк с единицы, как в редакторах.
- `raw.strip()` убирает `\n` и пробелы по краям.
- `continue` — перейти к следующей итерации цикла.
- `line.startswith("#")` — проверка префикса.
- Вложенный `try` ловит ошибку конвертации именно этого числа.
- `f"{file_path}:{lineno}: ..."` — формат сообщения как в компиляторах: файл, строка, суть.

```python
def load_series_csv(path: PathLike) -> List[float]:
    ...
                tokens = [t for t in _SEPARATORS.split(line) if t]
                if not tokens:
                    continue
                try:
                    values = [float(t) for t in tokens]
                except ValueError:
                    if lineno == 1:
                        continue  # считаем это заголовком
                    raise ValueError(f"{file_path}:{lineno}: строка '{line}' содержит нечисловые значения")
                result.extend(values)
```

- `.split(...)` режет строку по регулярному выражению в список.
- `if t` в включении выбрасывает пустые токены.
- Если конвертация не удалась в первой строке — считаем её заголовком.
- `result.extend(values)` добавляет все элементы сразу (в отличие от `append`, который
  добавил бы один список как элемент).

```python
def load_series_auto(path: PathLike) -> List[float]:
    from .io_json import load_series_json
    suffix = Path(path).suffix.lower()
    if suffix == ".json":
        return load_series_json(path)
    if suffix in {".txt", ".dat"}:
        return load_series_txt(path)
    if suffix in {".csv", ".tsv"}:
        return load_series_csv(path)
    try:
        return load_series_csv(path)
    except ValueError:
        return load_series_txt(path)
```

- Импорт **внутри функции** — чтобы не создавать цикл импортов между модулями io.
- `.suffix` — расширение файла с точкой; `.lower()` — привести к нижнему регистру.
- `in {".txt", ".dat"}` — проверка принадлежности множеству (фигурные скобки без двоеточий
  создают `set`).
- Стратегия для неизвестного расширения: сначала csv, при ошибке — txt.

---

## 9. `variant8.py` (в пакете) — вариант 8

```python
def outlier_series(n: int = 1500, seed: Optional[int] = None,
                   positions: Optional[Sequence[int]] = None) -> List[float]:
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError(f"n должно быть целым >= 1 (получено: {n!r})")

    rng = random.Random(seed)
    data = [rng.gauss(0.0, 1.0) for _ in range(n)]

    if positions is None:
        positions = (n // 3, (2 * n) // 3)

    scale = max(abs(v) for v in data)
    for position in positions:
        ...
        data[position] = 10.0 * scale
    return data
```

- `rng.gauss(0.0, 1.0)` — нормальное распределение с μ = 0 и σ = 1.
- `max(abs(v) for v in data)` — генераторное выражение внутри `max`: значения
  не собираются в список, а вычисляются по одному.
- `positions` по умолчанию — кортеж из двух индексов: `n // 3` и `2 * n // 3`.
- `data[position] = ...` — замена элемента по индексу.
- Выброс в 10 раз больше типичного: `10.0 * scale`, где `scale` — максимальное
  отклонение шума.

```python
def trimmed_mean(data: Sequence[float], proportion: float = 0.10) -> float:
    _ensure_not_empty(data)
    if not (0 <= proportion < 0.5):
        raise ValueError(...)
    ordered = sorted(data)
    cut = int(len(ordered) * proportion)
    kept = ordered[cut:len(ordered) - cut] if cut else ordered
    if not kept:
        raise ValueError("После усечения ряд пуст")
    return sum(kept) / len(kept)
```

- `0 <= x < 0.5` — цепочка сравнений, читается как в математике.
- `int(...)` отбрасывает дробную часть.
- `ordered[cut : len(ordered) - cut]` — обрезаем `cut` элементов с начала и с конца.
- `if cut else ordered` — при нулевом усечении срез `[0:len]` и так дал бы весь список,
  но ветка делает намерение явным.

```python
def rolling_median(data: Sequence[float], window: int) -> List[float]:
    _ensure_not_empty(data)
    ...
    result: List[float] = []
    last_start = len(data) - window + 1
    for start in range(last_start):
        result.append(_median_sorted(sorted(data[start:start + window])))
    return result
```

- `range(last_start)` — все позиции, где окно целиком помещается в ряд.
- `_median_sorted` считает медиану уже отсортированного окна и корректно работает
  и для чётной, и для нечётной длины окна.
- Сложность O(n · window · log window): для учебных объёмов приемлемо.

---

## 10. `main.py` — основная программа

### 10.1. Источники данных

```python
def build_series(kind: str, n: int, seed: int) -> List[float]:
    if kind == "random":
        return random_series(n, low=-50, high=50, seed=seed)
    if kind == "sine":
        return sine_series(n, amplitude=10, frequency=2, noise=1.5, seed=seed)
    if kind == "trend":
        return trend_series(n, start=0, step=1.0, noise=0.5, seed=seed)
    raise ValueError(f"Неизвестный тип ряда: {kind!r}")
```

Фабрика: по строковому ключу выбирает генератор с готовыми пресетами.

```python
def obtain_series(args: argparse.Namespace) -> Tuple[List[float], str]:
    if args.load:
        data = load_series_auto(args.load)
        return data, f"файл: {args.load}"
    data = build_series(args.kind, args.n, args.seed)
    return data, f"сгенерирован ({args.kind}, n={args.n}, seed={args.seed})"
```

- `argparse.Namespace` — объект, в котором argparse хранит разобранные аргументы;
  `args.load` — значение `--load` или `None`.
- Возвращается кортеж «ряд + описание источника»; распаковка в две переменные
  происходит при вызове.
- `Tuple[List[float], str]` — аннотация кортежа из двух элементов.

### 10.2. Печать

```python
def print_series(title: str, values: List[float], fmt: str = "{:>10.3f}") -> None:
    print(f"\n{title} (n={len(values)}):")
    print(" " + " ".join(fmt.format(v) for v in values))
```

- `"{:>10.3f}"` — мини-язык форматирования: ширина 10, выравнивание вправо (`>`),
  три знака после точки (`f`).
- `"\n"` — перевод строки.
- `" ".join(генератор)` — склеивает строки через пробел; генератор вычисляет строки
  по одной, без создания списка.
- `fmt.format(v)` — подстановка значения в шаблон.

```python
def print_stats(stats: dict) -> None:
    print(f"Среднее арифметическое : {stats['mean']:>10.4f}")
    ...
```

- `{stats['mean']:>10.4f}` — в f-строке можно обращаться к элементам словаря;
  одинарные кавычки внутри двойных обязательны, чтобы не закрыть строку.
- `:>10.4f` — тот же мини-язык форматирования.

### 10.3. Экспорт CSV

```python
def export_series_csv(path: str, data: List[float]) -> None:
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["i", "value"])
            for i, v in enumerate(data):
                w.writerow([i, v])
    except OSError as err:
        raise ValueError(f"Не удалось записать CSV {path}: {err}") from err
```

- `csv.writer` сам экранирует разделители и кавычки.
- `newline=""` обязателен на Windows: без него между строками появятся пустые.

### 10.4. Аргументы командной строки

```python
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Алгоритмическая обработка числовых рядов",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Пример: python main.py --kind sine --n 20 --save data/s.json",
    )
    parser.add_argument(
        "--kind", choices=["random", "sine", "trend"], default="sine",
        help="тип генерируемого ряда",
    )
    parser.add_argument("--n", type=int, default=20, help="количество точек в ряде")
    ...
    parser.add_argument("--load", metavar="PATH", help="загрузить ряд из файла ...")
    parser.add_argument("--save", metavar="PATH", help="сохранить ряд в JSON-файл")
    parser.add_argument("--export", metavar="FILE", help="экспортировать ряд в CSV (i, value)")
    parser.add_argument("--benchmark", action="store_true",
                        help="замерить время выполнения SMA для list и deque")
    return parser
```

- `choices=[...]` — допустимые значения; иначе argparse выдаст ошибку и код 2.
- `type=int` — преобразование строки в число при разборе.
- `default=` — значение, если аргумент не передан.
- `metavar="PATH"` — как аргумент выглядит в справке.
- `action="store_true"` — флаг без значения: передан → `True`, иначе `False`.
- `ArgumentDefaultsHelpFormatter` — автоматически дописывает «(default: ...)» в `--help`.
- `epilog` — текст в конце справки.

### 10.5. Главная функция

```python
def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        data, source = obtain_series(args)
    except ValueError as err:
        print(f"Ошибка получения ряда: {err}", file=sys.stderr)
        return 1
    ...
    try:
        stats = summarize(data)
        sma = simple_moving_average(data, args.window)
        ema = exponential_moving_average(data, args.alpha)
        cma = (centered_moving_average(data, args.window)
               if args.window % 2 == 1 else None)
    except ValueError as err:
        print(f"Ошибка анализа: {err}", file=sys.stderr)
        return 1

    print_header(source)
    print_stats(stats)
    ...
    if args.benchmark:
        print("-" * 60)
        print("Замер времени выполнения SMA (среднее за 1000 повторов):")
        timings = benchmark_moving_average(data, args.window, repeats=1000)
        print(f"  list : {timings['list']:.8f} с")
        print(f"  deque: {timings['deque']:.8f} с")
        print(f"  отношение (list/deque): {timings['list'] / timings['deque']:.2f}")
    print_footer()
    return 0
```

- `argv=None` → argparse берёт `sys.argv[1:]`; список → можно вызвать
  `main(["--n", "5"])` из теста, не трогая аргументы процесса.
- `file=sys.stderr` — ошибки идут в поток ошибок, а не в обычный вывод.
- `return 1` — ненулевой код возврата означает неуспех для оболочки и CI.
- `if args.benchmark:` — флаг проверяется как обычное логическое значение.
- `{...:.8f}` — восемь знаков после точки, чтобы различать микросекунды.
- `{a / b:.2f}` — деление прямо внутри f-строки.

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

- `__name__` равно `"__main__"` только при запуске файла; при `import main` код не выполнится.
- `raise SystemExit(code)` завершает программу с переданным кодом.

---

## 11. `variant8.py` (в корне) — CLI варианта 8

```python
from num_series.moving_average import (
    simple_moving_average,
    simple_moving_average_deque,
)
from num_series.stats import mean, median, spread
from num_series.variant8 import outlier_series, rolling_median, trimmed_mean
```

- Импорт конкретных функций из модулей пакета; круглые скобки позволяют переносить список.
- `from num_series.variant8 import ...` — обращение к подмодулю пакета.

```python
def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = outlier_series(args.n, seed=args.seed)
        sma_list = simple_moving_average(data, args.window)
        sma_deque = simple_moving_average_deque(data, args.window)
        medians = rolling_median(data, args.window)
        trimmed = trimmed_mean(data, 0.10)
    except ValueError as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        return 1
    ...
    difference = max(abs(a - b) for a, b in zip(sma_list, sma_deque))
    print(f"Макс. расхождение SMA list/deque: {difference:.3e}")
```

- `zip(a, b)` идёт по двум спискам одновременно, выдавая пары.
- `abs(a - b)` — модуль разности.
- `max(...)` по генератору — наибольшее расхождение.
- `{difference:.3e}` — экспоненциальный формат с тремя знаками (например, `1.443e-15`).
- `median` из `stats` импортирован, но в выводе используется `median(data)` — функция
  из `stats`, а не встроенная.

---

## 12. Тестовая обвязка

### 12.1. `conftest.py`

```python
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
```

- `__file__` — путь к текущему файлу; `.resolve()` делает его абсолютным.
- `sys.path` — список папок, где Python ищет модули; `insert(0, ...)` ставит корень
  проекта первым, чтобы `import num_series` работал без установки пакета.
- pytest автоматически загружает `conftest.py` до тестов.

### 12.2. `pytest.ini`

```ini
[pytest]
testpaths = tests
```

- Секция `[pytest]` — обязательна.
- `testpaths` говорит pytest искать тесты только в папке `tests`.

### 12.3. Файлы тестов

```python
import pytest

from num_series.stats import mean

def test_mean():
    assert mean([1, 2, 3, 4]) == pytest.approx(2.5)
```

- `assert условие` — если ложно, тест падает.
- `pytest.approx(2.5)` — сравнение чисел с плавающей точкой с допуском
  (обычное `==` для float ненадёжно).
- `with pytest.raises(ValueError):` — проверка, что код бросил нужное исключение.
- `capsys` и `tmp_path` — встроенные фикстуры pytest: перехват вывода и временная папка.

### 12.4. `run_self_tests.py`

```python
def run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = cli.main(argv)
    return code, out.getvalue(), err.getvalue()
```

- `io.StringIO()` — файл в памяти; `.getvalue()` возвращает записанный текст.
- `contextlib.redirect_stdout` временно подменяет `sys.stdout` — так перехватывается вывод.
- Два менеджера в одном `with` — обычная практика.

```python
CHECKS = (check_generator, check_stats, check_moving_average, check_io, check_cli)

def main():
    failed = 0
    for check in CHECKS:
        try:
            check()
        except AssertionError as err:
            failed += 1
            print(f"[FAIL] {check.__name__}: {err}")
        else:
            print(f"[ OK ] {check.__name__}")
    ...
```

- Функции — объекты первого класса: их можно положить в кортеж и вызывать по имени.
- `check.__name__` — имя функции строкой.
- `except ... else:` — блок `else` выполняется, если исключения не было.

---

## 13. Синтаксис Python: сводка по конструкциям

### Аннотации типов

```python
def f(n: int, data: Sequence[float]) -> List[float]: ...
```

Типы после двоеточия и стрелки — **аннотации**, Python их не проверяет во время работы.
Они служат документацией и подсказкам редактора. Используются `List`, `Sequence`, `Dict`,
`Optional`, `Union`, `Tuple`, `Deque`, `Iterable`, `Any`.

`from __future__ import annotations` в начале файла делает так, что аннотации
не вычисляются при импорте, а хранятся строками. Это позволяет писать `list[float] | None`
даже в версиях, где такой синтаксис ещё не поддерживался во время выполнения.

### f-строки

```python
f"n = {n}, ошибка: {err!r}, значение: {x:>10.3f}"
```

- `{выражение}` — подстановка.
- `!r` — `repr()`, `!s` — `str()`.
- `:>10.3f` — формат: ширина 10, вправо, 3 знака после точки.
- `:.3e` — экспоненциальный формат.

### Исключения

```python
try:
    ...
except (TypeError, ValueError) as err:
    raise ValueError("...") from err
```

- `try/except` — обработка ошибок; `except` может перечислять несколько типов.
- `as err` — связать исключение с именем.
- `raise ... from err` — сохранить причину.
- `else` после `except` — код, который выполняется, если ошибки не было.
- `finally` — выполняется всегда (в проекте не используется).

### Циклы и итерация

```python
for i, x in enumerate(data, start=1): ...
for a, b in zip(xs, ys): ...
for i in range(1, len(data)): ...
for _ in range(n): ...
```

- `enumerate` — индекс и значение.
- `zip` — параллельный проход по нескольким последовательностям.
- `range(a, b)` — от `a` до `b - 1`.
- `_` — «переменная не нужна».
- `continue` — следующая итерация; `break` — выход (в проекте не используется).

### Списковые включения и генераторы

```python
[rng.uniform(low, high) for _ in range(n)]           # список
(t for t in tokens if t)                             # генераторное выражение
max(abs(v) for v in data)                            # генератор внутри функции
```

- Включение создаёт список целиком; генератор выдаёт значения по одному.
- `if` в конце — фильтр.

### Срезы и индексы

```python
data[:window]          # первые window элементов
data[i:i + window]     # окно
data[start:stop:step]  # общий вид
result[-1]             # последний элемент
```

Правый конец среза **не включается**. Отрицательные индексы считаются с конца.

### Словари

```python
payload.get("meta", {}) or {}
{**meta, "n": len(data)}
```

- `.get(key, default)` — значение или значение по умолчанию.
- `**` — распаковка словаря в литерал или в вызов функции.

### Функции

```python
def f(a, b=1, *, c=None): ...
```

- `b=1` — значение по умолчанию.
- `*` — аргументы после него только именованные (в проекте не используется, но полезно знать).
- Функция без `return` возвращает `None`.

### Модули и пакеты

```python
from .generator import random_series   # внутри пакета
from num_series import random_series   # снаружи
```

- Пакет — папка с `__init__.py`.
- Точка — «текущий пакет».
- `__all__` — публичный список имён.
- `if __name__ == "__main__":` — код только при запуске файла.

### `collections.deque`

```python
d = deque(maxlen=3)
d.append(x)      # справа, O(1)
d.popleft()      # слева, O(1)
d[0]             # первый, O(1)
```

Кольцевой буфер: при переполнении сам удаляет элемент с противоположного конца.

### `argparse`

```python
parser.add_argument("--n", type=int, default=20, choices=[1, 2, 3],
                    action="store_true", metavar="PATH", help="...")
args = parser.parse_args(argv)
```

- `type` — преобразование, `default` — значение по умолчанию, `choices` — допустимые значения,
  `action="store_true"` — флаг, `metavar` — подпись в справке, `help` — описание.

### Файлы и пути

```python
with open(path, "w", newline="", encoding="utf-8") as f: ...
file_path.parent.mkdir(parents=True, exist_ok=True)
file_path.suffix.lower()
file_path.exists()
```

- `with` закрывает файл автоматически.
- `encoding="utf-8"` — явная кодировка (иначе на Windows возможен cp1251).
- `pathlib` избавляет от ручной склейки путей.

### `json` и `csv`

```python
json.dump(payload, f, ensure_ascii=False, indent=2)
payload = json.load(f)
csv.writer(f).writerow(["i", "value"])
```

### `time`

```python
t0 = time.perf_counter()
...
time.perf_counter() - t0
```

Монотонные часы высокого разрешения — для замеров длительности.

### `assert`

```python
assert condition, "сообщение"
```

- В тестах: при ложном условии бросается `AssertionError`.
- При запуске с `python -O` проверки `assert` отключаются — поэтому в рабочем коде
  они не заменяют явные `raise`.

---

## 14. Как запускать

```bash
# основная программа
python main.py --kind sine --n 20 --window 3 --alpha 0.3 --seed 7

# замер скорости SMA
python main.py --kind random --n 5000 --window 20 --benchmark

# вариант 8 (чётное и нечётное окно)
python variant8.py --n 1500 --window 10 --seed 42
python variant8.py --n 1500 --window 9 --seed 42

# тесты
python -m pytest
python run_self_tests.py
```

---

## 15. Известные особенности кода

1. `centered_moving_average_deque` в `deque_average.py` центрирования не выполняет —
   возвращает обычную SMA. Так задано в методичке ЛР 5.1.
2. Функция с именем `simple_moving_average_deque` существует в двух модулях
   (`moving_average` и `deque_average`) — реализации разные, результаты совпадают.
   В `num_series/__init__.py` экспортирована версия из `moving_average`.
3. `_ensure_not_empty` продублирована в `generator.py`, хотя нужна только в `stats.py`;
   там же импортированы неиспользуемые `Dict`, `Sequence`.
4. В `main.py` импортирован `json`, но не используется.
5. `pytest.py` (0 байт) в корне перекрывает настоящий пакет `pytest`: при запуске
   `python -m pytest` из папки проекта Python найдёт этот пустой файл.
   Удалить его — и тесты запустятся.
6. Бенчмарк сравнивает две O(n)-реализации, поэтому показывает разницу констант:
   на n = 1000, k = 10 list-версия примерно в 1.6 раза быстрее deque-версии.
7. Варианты 4 и 17 в методичке ЛР 5.1 совпадают по содержанию.
