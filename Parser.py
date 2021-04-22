try:
    import requests
    from bs4 import BeautifulSoup as bs
    from const import HEADERS, PWD_DATA
except ImportError as Error:
    print("Произошла ошибка при импортировании модуля. Возможно, один из них отсутствует")


class Parser:            

    def __init__(self, log_url, data_url):
        self.__log_url = log_url
        self.data_url = data_url
        try:
            # при инициализации объекта Parser сразу авторизируемся через сессию
            self.__session = requests.Session()
            self.__session.post(
                self.__log_url, data=PWD_DATA,
                headers=HEADERS, allow_redirects=False
            )
        except Exception as Error:
            pass

    def __str__(self):
        return f"Страница авторизации: {self.__log_url}, \nСтраница оценок: {self.__data_url}"

    def checkNull(self, string, res):
        """ 
        Метод, возвращающий строку, если проверяемая является пустой 
        string [str] ---> проверяемая строка
        res [str] ---> релузьтирующая строка
        """
        if string != "":
            return string
        else:
            return res

    def getPageContent(self, link: str):
        """
        Метод, получающий веб-страницу и возвращающий
        <class 'bs4.BeautifulSoup'>
        """
        try:
            response = self.__session.get(
                link, headers=HEADERS
            )
        except requests.exceptions.ConnectionError:
            print("Произошла ошибка при подключении. Проверьте правильность введённых ссылок / покдлючение к Интернету")

        if response.status_code == 200:
            return response
        else:
            print("Произошла ошибка во время получения страницы")

    def return_timetable(self):
        """
        Метод, возвращающий ниформацию по звонкам в виде словаря
        Звонки одинаковы во все дни, кроме вторника, так что не имеет смысле парсить данную
        информацию. 
        """
        return [
            {
                "1й урок": "8:00 - 8:40",
                "2й урок": "8:45 - 9:25",
                "3й урок": "9:40 - 10:20",
                "4й урок": "10:40 - 11:20",
                "5й урок": "11:40 - 12:20",
                "6й урок": "12:25 - 13:05",
                "7й урок": "13:10 - 13:50"
            }, 
            {
                "1й урок": "8:00 - 8:40",
                "Классный час": "8:45 - 9:05",
                "2й урок": "9:10 - 9:50",
                "3й урок": "10:05 - 10:45",
                "4й урок": "11:05 - 11:45",
                "5й урок": "11:55 - 12:35",
                "6й урок": "12:40 - 13:20",
                "7й урок": "13:25 - 14:05"
            }
        ]

    def prettify_data(self, string):
        """
        Метод, заменяющий составные названия школьных предметов на более простые
        string [str] ---> строка, которую мы проверяем (предмет)
        """
        words = {
            "англ. язык": "английский",
            "индивид. проект": "проект",
            "инф. и икт": "информатика",
            "рус. язык": "русский",
            "сл. задачи по физике": "задачи физика",
            "решение нестандартны": "задачи математика",
            "практ. по русс.яз.": "практика русский"
        }
        if string in words:
            return words[string]
        else:
            return string

    def parse_marks(self, web_page):
        """
        Метод, который парсит оценки и возвращает словарь с ними
        web_page [Soup] ---> объект супа, являющийся страницей сайта
        """
        marks_dict = dict()
        try:
            marks = bs(web_page.text, "html.parser").find_all("tr")
            marks.pop(0)
            marks.pop(0)

            for mark in marks:
                marks_dict.update(
                    {
                        self.prettify_data(mark.find("td", class_="s2").get_text().lower()): 
                        [
                            self.checkNull(mark.find("td", attrs={"style": "text-align:left;"}).get_text(), "Нет оценок"), 
                            mark.find("td", attrs={"style": "text-align:left;"}).find_next("td", class_="tac").get_text()
                        ]
                    }
                )    
            return marks_dict
            
        except IndexError:
            pass
