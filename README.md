# First_site
Разработка сайта на Flask с БД. 
Делаю тестовое задание на собес...
Техническое задание на реализацию блога

1. Технический стек
	- ЯП - Python 3.9 или 3.10 (на выбор) ✔
	- Стек технологий для реализации бэкенд (на выбор): ✔
		- Django + Django Rest Framework --
		- Flask + SQLAlchemy ✔
		- FastAPI + SQLAlchemy ---
	- База данных - PostgreSQL ✔
	- Развертывание проекта с помощью Docker (Docker-Compose) ✔

2. Задание
Реализовать блог со следующими возможностями
- создание, изменение и удаление постов
	- создание поста ✔
		- входные данные ✔
			- автор поста ✔
			- тема поста ✔
			- содержимое поста ✔
		- выходные данные ✔
			- успешность выполнения ✔
	- изменение поста
		- входные данные ✔
			- идентификатор поста ✔
			- автор поста ✔
			- тема поста ✔
			- содержимое поста ✔
		- выходные данные ✔
			- успешность выполнения ✔
	- удаление поста
		- входные данные ✔
			- идентификатор поста ✔
		- выходные данные ✔
			- успешность выполнения ✔
- отображение постов на странице веб-браузера ✔
- отображение лайков, поставленных конкретному посту ✔
- модификация количества лайков ✔
	- увеличение количества лайков ✔
		- входные данные ✔
			- идентификатор поста ✔
		- выходные данные ✔
			- успешность выполнения ✔
	- уменьшение количества лайков ✔
		- входные данные ✔
			- идентификатор поста ✔
		- выходные данные ✔
			- успешность выполнения ✔
Фронтенд (работа с браузером) реализовывается средствами бэкенда (например, с использованием Jinja ✔)

Данные в БД должны содержать
- идентификатор поста ✔
- тему поста ✔
- содержимое поста ✔
- количество лайков ✔
- автора поста ✔
- дату публикации ✔

Блог должен быть развернут в Docker — т. е. должна быть конфигурация для выполнения данной операции ✔

Приветствуется:
- реализация дополнительного функционала за пределами указанного ТЗ
- использование сериализаторов/десериализаторов
- использование миграций

