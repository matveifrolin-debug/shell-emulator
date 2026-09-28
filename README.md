# Эмулятор командной строки UNIX (вариант 18)

GUI-эмулятор оболочки ОС на Python + tkinter.

## Этап 1. REPL
- Заголовок окна: `Эмулятор - [user@host]` по данным реальной ОС.
- Раскрытие переменных окружения: `$HOME`, `${USERNAME}`.
  Неизвестная переменная заменяется пустой строкой.
- Команды-заглушки `ls`, `cd` выводят имя и аргументы.
- `exit` закрывает эмулятор.

## Запуск
```
run.bat          # Windows
./run.sh         # Linux / Git Bash
```

## Тесты
```
python -m unittest discover -s tests -v
```

## Примеры
```
user@host$ ls -l $HOME
ls: args=['-l', 'C:\\Users\\user']
user@host$ foo
Ошибка: foo: command not found
```