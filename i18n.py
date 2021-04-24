# -*- coding: UTF-8 -*-
"""Internatialization support"""

import bookdesc
import locale

def _major_locale():
    loc = locale.getlocale()[0]
    underscore = loc.find('_')
    if underscore > 0:
        loc = loc[:underscore]
    return loc


_MAJOR_LOCALE = _major_locale()
_TRANSLATIONS = {}
    
def translate(phrase):
    text = None
    phrase_translations = _TRANSLATIONS.get(phrase)
    if phrase_translations:
        text = phrase_translations.get(_MAJOR_LOCALE)
        if not text: text = phrase_translations.get('')
    if not text: text = phrase
    return text

_TRANSLATIONS['an output file or folder to put CSVs to'] = {
    'ru': "Выходной CSV файл или каталог куда класть CSV файлы"
}
_TRANSLATIONS['DUMB_MODE_FILE_MUST_NOT_EXIST'] = {
    '': "in dumb mode must not exist and could not be a folder",
    'ru': " в 'тупом' режиме не должен существовать и не должен быть каталогом"
}
_TRANSLATIONS['an input (file or folder) to parse .fb2 from'] = {
    'ru': "Входной файл или каталог где искать .fb2 файлы"
}
_TRANSLATIONS['Display program infomration (long)'] = {
    'ru': "Отобразить информацию о программе (длинную)"
}
_TRANSLATIONS['dedup backend, (default: b+tree)'] = {
    'ru': "backend для дедупликации (по умолчанию b+tree)"
}
_TRANSLATIONS['coward mode: fail on any WARNING/ERROR/CRITICAL message'] = {
    'ru': "режим труса: аварийный выход при любом WARNING/ERROR/CRITICAL сообщении"
}
_TRANSLATIONS['logging level (NONE: no logging)'] = {
    'ru': "уровень логгирования (NONE: без ведения логов)"
}
_TRANSLATIONS["BOOKDESC_SHORTDESCRIPTION"] = {
    '': """Parses .fb2 files into CSVs. 
There are two main modes in which this tool works:
* The "dumb" mode (turned on using --dumb switch). In this mode the tool simply
  parses the .fb2 files and dumps them into output CSV. Output MUST be a 
  filename (not directory) and it should not exist. The deduping is not 
  performed.
* The "library" mode (default). In this mode tools parses .fb2 files and 
  incrementally updates CSVs found at the output location, deduping the 
  files by SHA-1
""",
  'ru': """Парсит .fb2 файлы в CSV файлы. 
Есть два основных режима работы:
* "Тупой" режим (включается ключом --dumb). В этом режиме программа просто 
  парсит указанные ей .fb2 файлы и складывает результаты в выходной файл (out).
  Выходной файл не должен существовать и не должен быть каталогом. Дедупликация
  не производится.
* Режим "библиотеки" (включен по умолчанию). В этом режиме программа парсит .fb2
  файлы и инкрементально обновляет CSV файлы в выходном каталоге (out). 
  Производится дедуплицирование .fb2 файлоы по SHA-1 сумме.
"""
}

_TRANSLATIONS["BOOKDESC_INFO"] = {
    '': bookdesc.__doc__,
    'ru': """Генератор метаинформации для электронных книг.

h1. История возникновения
Это развития идей проекта Jabot (https://github.com/borisshvonder/jabot).
К сожалению, у меня нет времени для должной поддержки проекта, а человеку новому
будет трудно в нем разобраться, поскольку проект, в основном, был создан в
качестве "работы над ошибками", ретроспективно описывающей то, чему я научился
за предыдущие несколько лет. Он не был рассчитан на то чтобы в него было легко
погрузиться, в частности, поскольку он содержит многие необычные функции, 
которые, возможно трудно будет понять. К тому же его довольно трудно 
сопровождать в продакшыне, так как он требует Apache Solr и запущенную 
retroshare ноду.

Проект bookdesc, наоборот, должен быть гораздо проще, понятнее и легче в 
использовании. Таким образом:

* Питон был выбран в качестве языка.
* bookdesc не будет создавать полнотекстовых индексов.
* На самом деле, вообще никаких поисковых индексов.
* Вместо этого, bookdesc создаст один или несколько CSV файлов, содержащих 
  метаданные книг (название книги, ISBN, авторов, и SHA1/MD5 подпись файла).
  Таким образом, для поиска нужной книги пользователь просто может использовать
  grep. 
* У bookdesc не будет никаких сторонних зависимостей.

h1. Цели
* Нужно уметь парсить .fb2 файлы (в том числе упакованные в архивах .zip).
* Инкрементальное обновление CSV файлов. Очень желательно дедуплицировать 
  файлы по их SHA1 подписи.
* Возможность разрезать CSV на более удобные для работы куски (возможно, по
  первой букве автора, т.е. a.csv, б.csv и так далее).
* bookdesc должно быть удобно использовать как библиотеку в других проектах на
  Питоне.
* Простой в сопровождении код, как можно меньше зависимостей.

h1. Не-цели
* Никакого полнотекстового поиска.
* Вообще никакого поиска, на самом деле.
* Никакого импорта из существующих баз и/или CSV
"""}

