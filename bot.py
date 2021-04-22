import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.upload import VkUpload
from Parser import Parser
from time import time
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


session = vk_api.VkApi(token="4ddbc1b267c5801b297dd7e31988c4fcaad6a32741ca3786264b108ea70230a30300b49ff912523d8a71b")
upload = VkUpload(session)
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

def send_rings(user_id):
    list = parser.return_timetable()

    message = ""        
    message += "Понедельник - Суббота (без Вторника):\n"
    for key, val in list[0].items():
        message += f"⏱ {key}: {val}\n"
    message += "\nВторник (с классным часом):\n"
    for key, val in list[1].items():
        message += f"⏱ {key}: {val}\n"

    send_simple_message(user_id, message)

def send_commands(user_id):
    commands = "1. Команды - выводит список доступных команд \n2. Все оценки - выводит все полученные оценки \n3. Начать - добавляет интерактивную клавиатуру \
\n4. Оценки {предмет} - выводит оценки по выбранному предмету (фигурные скобки не указываются) \
    \n5. Звонки - выводит информацию о времени звонков (расписание)"
    send_simple_message(user_id, commands)

def info_marks(user_id):
    pass

def select_color(mark: float) -> tuple:
    if mark == "":
        pass
    else:
        if float(mark) >= 3.5:
            return ("#1ca020")
        elif float(mark) < 3.5 and float(mark) >= 2.5:
            return ("#f9a23b")
        else:
            return ("#f04708")

def select_mark(mark) -> str:
    if mark == "":
        return "нет"
    else:
        if float(mark) >= 4.5:
            return "5"
        elif float(mark) >= 3.5 and float(mark) < 4.5:
            return "4"
        elif float(mark) >= 2.5 and float(mark) < 3.5:
            return "3"
        elif float(mark) >= 1.5 and float(mark) < 2.5:
            return "2"
        else:
            return "1"

def send_mark_billboard(user_id, subject):
    dict = parser.parse_marks(parser.getPageContent(parser.data_url))
    if subject.lower() in dict:        
        image = Image.open("E:\\Games\\luvairo\\board.jpg")
        drawable = ImageDraw.Draw(image)
        width = image.size[0]
        font = ImageFont.truetype("E:\\Games\\luvairo\\neversmile.otf", 350)
        font_mark = ImageFont.truetype("E:\\Games\\luvairo\\neversmile.otf", 275)

        drawable.text(
            (width / 2 - len(subject) * 79, 400), subject, 
            font=font
        )

        drawable.text(
            (550, 1000), "·Ср. балл:", font=font_mark
        )
        drawable.text(
            (1570, 1000), dict[subject][1], font=font_mark,
            fill=select_color(dict[subject][1].replace(",", "."))
        )

        drawable.text(
            (550, 1400), "·Оценка:", font=font_mark
        )
        drawable.text(
            (1450, 1400), select_mark(dict[subject][1].replace(",", ".")), font=font_mark,
            fill=select_color(dict[subject][1].replace(",", "."))
        )

        drawable.line(
            (500, 820, width - 440, 820), fill='white',
            width=17
        )
        del drawable
        image.save("E:\\Games\\luvairo\\new_image.jpg")

        upload_image = upload.photo_messages(photos="E:\\Games\\luvairo\\new_image.jpg")[0]
        data = "photo{}_{}".format(upload_image['owner_id'], upload_image['id'])

        session.method(
            "messages.send", {
                "user_id": user_id,
                "message": "Ваш биллборд",
                "attachment": data,
                "random_id": 0
            }
        )
    else:
        send_simple_message(user_id, "Такого предмета не существует")

def send_marks(user_id, full, sub=None):
    if full:
        dict = parser.parse_marks(parser.getPageContent(parser.data_url))
        
        message = ""
        for key, val in dict.items():
            message += f"🖌 {key.capitalize()}: {val[0]} {'=> ' + val[1] if val[1] != '' else ''}\n"

        send_simple_message(user_id, message)
    else:
        try:
            dict = parser.parse_marks(parser.getPageContent(parser.data_url))

            try:
                message = f"🖌 {sub.capitalize()}: {dict[sub][0]} \n📈 Средний балл: {dict[sub][1] if dict[sub][1] != '' else 'z'}"
                send_simple_message(user_id, message)
            except KeyError as Error:
                send_simple_message(user_id, "Такого предмета не существует. Введи ПОМОЩЬ ОЦЕНКИ, чтобы получить справку по команде")

        except Exception as Error:
            send_simple_message(user_id, "Произошла ошибка на стороне сервера")

last_time = time()
for event in VkLongPoll(session).listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        user_id = event.user_id
        message = event.text.lower()

        if message == "все оценки":
            if time() > last_time + 3:
                last_time = time()
                send_marks(user_id, True)
            else:
                send_simple_message(user_id, f"Команда перезаряжается {round(last_time + 3 - time(), 2)} секунд. Подождите")

        elif message.split()[0] == "помощь" and message.split()[1] == "оценки":
            send_simple_message(
                user_id,
                "Синтаксис команды: оценки [предмет] (регистр не имеет значения, скобки писать не нужно) \
                    \nЕсли название предмета состоит из двух слов, то их нужно заключить в кавычки \
                    \nПример: оценки \"математические задачи\""
            )
        
        elif message.split()[0] == "балл":
            send_mark_billboard(user_id, message.split()[1]) 

        elif message == "звонки":
            send_rings(user_id)
        
        elif message == "команды":
            send_commands(user_id)

        elif message.split()[0] == "оценки":
            if time() > last_time + 3:
                last_time = time()
                if message.split("&quot;")[0] == message:
                    send_marks(user_id, False, message.split(" ")[1])
                else:
                    send_marks(user_id, False, message.split("&quot;")[1])
            else:
                send_simple_message(user_id, f"Команда перезаряжается {round(last_time + 3 - time(), 2)} секунд. Подождите")

        elif message == "начать":
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
