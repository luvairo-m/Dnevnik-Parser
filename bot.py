import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from Parser import Parser
from time import time


session = vk_api.VkApi(token="4ddbc1b267c5801b297dd7e31988c4fcaad6a32741ca3786264b108ea70230a30300b49ff912523d8a71b")
parser = Parser(
    "https://login.dnevnik.ru/login/esia/kurgan",
    "https://schools.dnevnik.ru/children/marks.aspx?child=2176035&index=9&tab=period&homebasededucation=False"
)

def send_simple_message(user_id, message):
    session.method(
        "messages.send", {
            "user_id": user_id,
            "message": message,
            "random_id": 0
        }
    )

def send_commands(user_id):
    commands = "1. Команды - выводит список доступных команд \n2. Все оценки - выводит все полученные оценки \n3. Начать - добавляет интерактивную клавиатуру \
\n4. Оценки {предмет} - выводит оценки по выбранному предмету (фигурные скобки не указываются)"
    send_simple_message(user_id, commands)

def info_marks(user_id):
    pass

def send_marks(user_id, full, sub=None):
    if full:
        dict = parser.get_marks()
        
        message = ""
        for key, val in dict.items():
            message += f"{key.capitalize()}: {val[0]} {'=> ' + val[1] if val[1] != '' else ''}\n"

        send_simple_message(user_id, message)
    else:
        try:
            dict = parser.get_marks()

            try:
                message = f"{sub.capitalize()}: {dict[sub][0]} {'=> ' + dict[sub][1] if dict[sub][1] != '' else ''}"
                send_simple_message(user_id, message)
            except KeyError as Error:
                send_simple_message(user_id, "Такого предмета не существует. Введи ПОМОЩЬ ОЦЕНКИ, чтобы получить справку по команде")

        except Exception as Error:
            send_simple_message(user_id, "Произошла ошибка на стороне сервера")

last_time = time()
for event in VkLongPoll(session).listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        user_id = event.user_id

        if event.text.lower() == "все оценки":
            if time() > last_time + 3:
                last_time = time()
                send_marks(user_id, True)
            else:
                send_simple_message(user_id, f"Команда перезаряжается {round(last_time + 3 - time(), 2)} секунд. Подождите")

        elif event.text.lower().split()[0] == "помощь" and event.text.lower().split()[1] == "оценки":
            send_simple_message(
                user_id,
                "Синтаксис команды: оценки [предмет] (регистр не имеет значения, скобки писать не нужно) \
                    \nЕсли название предмета состоит из двух слов, то их нужно заключить в кавычки \
                    \nПример: оценки \"математические задачи\""
            )

        elif event.text.lower() == "команды":
            send_commands(user_id)

        elif event.text.lower().split()[0] == "оценки":
            if time() > last_time + 3:
                last_time = time()
                if event.text.lower().split("&quot;")[0] == event.text.lower():
                    send_marks(user_id, False, event.text.lower().split(" ")[1])
                else:
                    send_marks(user_id, False, event.text.lower().split("&quot;")[1])
            else:
                send_simple_message(user_id, f"Команда перезаряжается {round(last_time + 3 - time(), 2)} секунд. Подождите")

        elif event.text.lower() == "начать":
            user_data = session.method("users.get", {"user_id": user_id})
            keyboard = VkKeyboard(one_time=False)
            keyboard.add_button("Все оценки", color=VkKeyboardColor.POSITIVE)
            keyboard.add_line()
            keyboard.add_button("Средний балл", color=VkKeyboardColor.POSITIVE)
            keyboard.add_line()
            keyboard.add_openlink_button("Средний балл (приложение)", link="https://play.google.com/store/apps/details?id=ru.luvairo.markplus")
            keyboard.add_line()
            keyboard.add_button("Команды", color=VkKeyboardColor.PRIMARY)
            session.method(
                "messages.send", {
                    "user_id": user_id,
                    "message": f"Привет, {user_data[0]['first_name']} {user_data[0]['last_name']}! Я добавил внизу кнопки с командами для твоего удобства",
                    "keyboard": keyboard.get_keyboard(),
                    "random_id": 0
                }
            )

        else:
            send_simple_message(
                user_id, 
                "Такой команды не существует. Введите НАЧАТЬ или КОМАНДЫ, чтобы получить список доступных команд"
            )
