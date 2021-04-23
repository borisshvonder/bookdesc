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
    
def translate(phrase):
    text = None
    phrase_translations = _TRANSLATIONS.get(phrase)
    if phrase_translations:
        text = phrase_translations.get(_MAJOR_LOCALE)
        if not text: text = phrase_translations.get('')
    if not text: text = phrase
    return text

_TRANSLATIONS = {}
_TRANSLATIONS['an output file or folder to put CSVs to'] = {
    'ru': "Выходной CSV файл или каталог куда класть CSV файлы"
}
_TRANSLATIONS['an input (file or folder) to parse .fb2 from'] = {
    'ru': "Входной файл или каталог где искать .fb2 файлы"
}
_TRANSLATIONS['Display program infomration (long)'] = {
    'ru': "Отобразить информацию о программе (длинную)"
}
_TRANSLATIONS["BOOKDESC_SHORTDESCRIPTION"] = {
    '': """Parses .fb2 files into CSVs. 
There are two main modes in which this tool works:
* The "library" mode (default). In this mode tools parses .fb2 files and 
  incrementally updates CSVs found at the output location, deduping the 
  files by SHA-1
* The "dumb" mode (turned on using --dumb switch). In this mode the tool simply
  parses the .fb2 files and dumps them into output CSV (must NOT be a directory,
  must be a single file). It is possible to turn on deduping in this mode using
  the --dedup switch
""",
  'ru': """Парсит .fb2 файлы в CSV файлы. 
Есть два основных режима работы:
* Режим "библиотеки" (включен по умолчанию). В этом режиме программа парсит .fb2
  файлы и инкрементально обновляет CSV файлы в выходном каталоге. Производится
  дедуплицирование .fb2 файлоы по SHA-1 сумме.
* "Тупой" режим (включается ключом --dumb). В этом режиме программа просто 
  парсит указанные ей .fb2 файлы и складывает результаты в CSV (это не может 
  быть каталогом, это должен быть один CSV файл). Дедуплицирование все-таки
  может быть включено и в этом режиме при помощи ключа --dedup
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

