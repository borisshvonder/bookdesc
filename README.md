h1. Russian: Генератор метаинформации для электронных книг.

h2. История возникновения
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

h2. Цели
* Нужно уметь парсить .fb2 файлы (в том числе упакованные в архивах .zip).
* Инкрементальное обновление CSV файлов. Очень желательно дедуплицировать 
  файлы по их SHA1 подписи.
* Возможность разрезать CSV на более удобные для работы куски (возможно, по
  первой букве автора, т.е. a.csv, б.csv и так далее).
* bookdesc должно быть удобно использовать как библиотеку в других проектах на
  Питоне.
* Простой в сопровождении код, как можно меньше зависимостей.

h2. Не-цели
* Никакого полнотекстового поиска.
* Вообще никакого поиска, на самом деле.
* Никакого импорта из существующих баз и/или CSV

h1. English: Book descriptions CSV generator.

h2. History and Why
This is a successor to Jabot project https://github.com/borisshvonder/jabot).
I have no time to properly support the project and it does not seem to be easy
for new developers to pick up since the project was primarilly written as
retrospective on what I have learned in a few previous years. It was not built
for people to pick up easilly since it contains some uncommon features which
might not be easy to grasp. It also wasn't easy to operate since it required
Apache Solr and running retroshare node.

The bookdesc project, on the other hand, is supposed to be much simplier, 
easilly understood and operate. Thus:

* Python was chosen as the implementation language.
* bookdesc will NOT generate fulltext index.
* In fact, bookdesc will not have any indexing support whatsoever.
* Instead, it will simply generate one or more CSV files which will contain 
  books metadata (book name, ISBN, authors AND SHA1/MD5 book checksums). 
  Therefore, the user can search simply using grep.
* There will be no extra dependencies required whatsoever.

h2. Goals
* Ability to parse fb2 files directly or inside .zip archives.
* Incremental CSV updates. It is very much desirable that files will be deduped
  based on their SHA-1 signature.
* Ability to split CSV files into sizeable chunks (perhaps, by author first 
  letter, a.csv, b.csv and so on).
* It should be possible to use the bookdesc module as a library in other
  python projects.
* Simple to support code, minimal number of dependencies

h2. Non-goals
* No fulltext seach.
* In fact, no search at all.
* No import from existing databases and/or CSVs.

