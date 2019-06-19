# Библиотеки
import vk_api
import re

STOP_PART = ["PARENTH", "PR", "CONJ", "PART", "INTJ"]


def get_word(text):
    text = text.lower()
    text = text.replace("\n", " ").replace("-", " ")
    text = text.replace(",", "").replace(".", "").replace("?", "")
    text = text.replace("!", "").replace("–", "")
    words = text.split()
    return words

def vk_clean(text):
    new_text = ""
    i = 0
    while(i < len(text)):
        try:
            if text[i] == '[':
                while(text[i] != '|'):
                    i += 1
                f = i
                while(text[i] != ']'):
                    i += 1
                g = i
                new_text += text[f + 1:g]
            else:
                try:
                    new_text += re.findall('[\w ,.!?"-]', text[i])[0]
                except:
                    pass
        except:
            try:
                new_text += re.findall('[\w\s,.!?"-]', text[i])[0]
            except:
                pass
        i += 1
    return new_text

def normal_path(gr):
    global STOP_PART
    for part in STOP_PART:
        if len(part) < len(gr):
            if gr[0:len(part)] == part:
                return False
    return True

# Авторизация по токену
TEACHER_TOKEN = "1248eda31248eda31248eda33a1222b0fb112481248eda34e842ee0b852c387ea51b303"
version = "5.95"
MAX = 10

def search(GROUP):
    result = 2
    text_mas = []
    people = {}

    vk_session = vk_api.VkApi(app_id=6000000, token=TEACHER_TOKEN)
    vk = vk_session.get_api()

    # Скачиваем все посты
    print("Cкачиваем все посты") #Один
    try:
        response = vk.wall.get(owner_id=GROUP, count=0, offset=0)
        #Счётчик записей
        post_count = response["count"]
        post_counter = 0

        while (post_counter < post_count and post_counter < MAX):
            response = vk.wall.get(owner_id=GROUP, count=1, offset=post_counter)
            for post in response["items"]:

                text_mas.append(post["text"])

                try:
                    response = vk.wall.getComments(owner_id=GROUP, post_id=post["id"], count=0, offset=0)
                    comment_count = response["count"]
                    comment_counter = 0

                    while (comment_counter < comment_count):
                        response = vk.wall.getComments(owner_id=GROUP, post_id=post["id"], count=100, offset=comment_counter)
                        for comment in response["items"]:
                            try:
                                text_mas.append(comment["text"])
                                people[comment["from_id"]] = {}
                            except:
                                print("Сломанный комментарий")
                            comment_counter += 1
                except:
                    result = 1

                post_counter += 1
                print("Пост " + str(post_counter))

        #Работа с данными
        id_mas = []
        for id in people:
            id_mas.append(id)

            people_num = len(id_mas)
            people_counter = 0

            while (people_counter < people_num):
                response = vk.users.get(user_ids=id_mas[people_counter:people_counter + 500], fields="sex, city, bdate")
                for item in response:
                    people[item["id"]]["sex"] = item.get("sex")
                    people[item["id"]]["city"] = item.get("city")
                    people[item["id"]]["bdate"] = item.get('bdate')
                    people_counter += 1

        print(people)

    except:
        return 0

    #Частота слов
    import sys
    sys.platform = "win64"
    from pymystem3 import Mystem

    #Cобираем текст
    text = ""
    for note in text_mas:
        for word in get_word(vk_clean(note)):
            text += word + " "

    m = Mystem()
    lemmas = m.lemmatize(text)

    right_words = {}
    for obj in m.analyze(text):
        if obj.get("analysis"):
            if normal_path(obj["analysis"][0]["gr"]):
                #Доавляем слово
                if right_words.get(obj["analysis"][0]["lex"]):
                    right_words[obj["analysis"][0]["lex"]] += 1
                else:
                    right_words[obj["analysis"][0]["lex"]] = 1

    sorted_by_value = sorted(right_words.items(), key=lambda kv: kv[1] * (-1))

    #Графики
    sys.platform = "win32"
    import plotly
    import plotly.graph_objs as go
    import plotly.io as pio

    plotly.tools.set_credentials_file(username='Foxride', api_key='uxDQM5bTXC63OMRqoWm2')

    print(sorted_by_value[0:20])

    x = []
    y = []
    for word in sorted_by_value[0:20]:
        print(word)
        x.append(word[0])
        y.append(word[1])
    data = [go.Bar(x=x,y=y)]
    layout = go.Layout(
        title=go.layout.Title(
            text='Частота слов',
            xref='paper',
            x=0
        ),
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(
                text='Сколько раз встретились',
                font=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            )
        ),
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(
                text='Слова',
                font=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            )
        )
    )
    fig = go.Figure(data=data, layout=layout)
    pio.write_image(fig, 'static/img/plot1.png')

    from datetime import date

    def calculate_age(i):
        if not i:
            i = ''
        today = date.today()
        i = i.split('.')
        if len(i) < 3:
            return 0
        else:
            day = int(i[0])
            month = int(i[1])
            year = int(i[2])
        return today.year - year - ((today.month, today.day) < (month, day))

    #Люди
    for id in people:
        if id > 0:
            people[id]["age"] = calculate_age(people[id]["bdate"])

    #Возраст
    x = []
    y = []
    age = {}
    for id in people:
        if id > 0:
            if age.get(people[id]["age"]):
                age[people[id]["age"]] += 1
            else:
                age[people[id]["age"]] = 1

    for key in age:
        x.append(key)
        y.append(age[key])

    data = [go.Bar(x=x, y=y, marker=dict(color='rgb(84,57,100)'))]
    layout = go.Layout(
        title=go.layout.Title(
            text='Возраст',
            xref='paper',
            x=0
        ),
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(
                text='Возраст пользователя',
                font=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            )
        ),
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(
                text='Количество пользователей',
                font=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            )
        )
    )
    fig = go.Figure(data=data, layout=layout)
    pio.write_image(fig, 'static/img/plot2.png')


    #Город
    x = []
    y = []
    city = {}

    for id in people:
        if id > 0:
            try:
                if city.get(people[id]["city"]["title"]):
                    city[people[id]["city"]["title"]] += 1
                else:
                    city[people[id]["city"]["title"]] = 1
            except:
                pass


    for key in city:
        x.append(key)
        y.append(city[key])

    data = [go.Bar(x=x, y=y, marker=dict(color='rgb(156,2,167)'))]
    layout = go.Layout(
        title=go.layout.Title(
            text=('Город'),
            xref='paper',
            x=0
        ),
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(
                text='Город пользователя',
                font=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            )
        ),
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(
                text='Количество людей из города',
                font=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            )
        )
    )
    fig = go.Figure(data=data, layout=layout)
    pio.write_image(fig, 'static/img/plot3.png')

    #Пол
    x = []
    y = []
    sex = [0,0,0]
    for id in people:
        if id > 0:
            temp = people[id]["sex"]
            if temp:
                sex[temp] += 1
            else:
                sex[0] += 1

    x.append("Женский")
    x.append("Мужской")

    y.append(sex[1])
    y.append(sex[2])


    data = [go.Bar(x=x, y=y, marker=dict(color='rgb(26,22,42)'))]
    layout = go.Layout(
        title=go.layout.Title(
            text='Пол',
            xref='paper',
            x=0
        ),
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(
                text='Пол',
                font=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            )
        ),
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(
                text='Количество людей указанного пола',
                font=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            )
        )
    )
    fig = go.Figure(data=data, layout=layout)
    pio.write_image(fig, 'static/img/plot4.png')

    return result

if __name__ == "__main__":
    search(43777444)
