from aiogram import Bot,Dispatcher,types
import asyncio
import logging
import config
import pymysql
from config import db_name,password,host,user
import datetime
import requests
from fake_useragent import UserAgent
import json

def parser_for_groups():
    agent = UserAgent()
    headers = {
        "Accept":"*/*",
        "User-Agent":f"{agent.random}"
    }

    url = "https://edu.donstu.ru/api/raspGrouplist?year=2022-2023"
    req = requests.get(url,headers=headers)
    src = req.text
    with open("Bot/dict_1.json","w") as file:
            json.dump(src,file,indent=4,ensure_ascii=True)    

    with open("Bot/dict_1.json", "r") as read_file:
        data = json.load(read_file)
    data:dict = json.loads(data)
    data = data.get("data")
    all_groups = data
    return all_groups



def parser(Mkis21:int,date):

    info = f"{date.year}-{date.month}-{date.day}"
    url = f'https://edu.donstu.ru/api/Rasp?idGroup={Mkis21}&sdate={info}'

    agent = UserAgent()
    headers = {
        "Accept":"*/*",
        "User-Agent":f"{agent.random}"
    }
    try:
        req = requests.get(url,headers=headers)
        src = req.text
    except: 
        date = date - datetime.timedelta(days=1)
        info = f"{date.year}-{date.month}-{date.day}"
        url = f'https://edu.donstu.ru/api/Rasp?idGroup={Mkis21}&sdate={info}'
        req = requests.get(url,headers=headers)
        src = req.text
    with open("Bot/dict.json","w") as file:
            json.dump(src,file,indent=4,ensure_ascii=False)    

    with open("Bot/dict.json", "r") as read_file:
        data = json.load(read_file)
    data = json.loads(data)
    all_days = [[],[],[],[],[],[]]
    data = data.get("data").get("rasp")
    for i in data:
        if i.get("деньНедели") == 1:
            all_days[0].append(i)
        elif i.get("деньНедели") == 2:
            all_days[1].append(i)
        elif i.get("деньНедели") == 3:
            all_days[2].append(i)
        elif i.get("деньНедели") == 4:
            all_days[3].append(i)
        elif i.get("деньНедели") == 5:
            all_days[4].append(i)
        else :
            all_days[5].append(i)
    return all_days



all_days = parser(44434,datetime.datetime.now())

engine = pymysql.connect(host=host,user=user,password=password,db=db_name)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.token_1)
dp = Dispatcher(bot=bot)

info_1 = []
o = []
group = []
# group = ["МКИС21","МКИС22","МКИС23","МКИС24","МКИС25"]
for i in parser_for_groups():
    group.append(i.get("name"))


@dp.message_handler(commands=["start","now","change","help","tomorrow",'date'])
async def cmd_start(message: types.Message):

    # kb = [
    #     [types.KeyboardButton(text="Мкис 21")],
    #     [types.KeyboardButton(text="Мкис 22")],
    #     [types.KeyboardButton(text="Мкис 23")]
    # ]
    # keyboard = types.ReplyKeyboardMarkup(
    #     keyboard=kb,
    #     resize_keyboard=True,
    #     input_field_placeholder="Выберите свою группу"
    #     )
    with engine.cursor() as cursor:
        sql = f"SELECT id,groupp,number_1 from users;"
        cursor.execute(sql)
    id_user = cursor.fetchall()
    id_main = []
    for i in id_user:
        id_main.append(i[0])
    for i in id_user:
        if message.from_user.id == i[0]:
            id_info:int = i[2]
    
    


    if message.text.lower() == "/start":    
        if message.from_user.id not in id_main:
            await message.answer("Приветствую, укажите свою группу, чтобы корректно использовать бота.\nТак же вы можете написать команду /help, чтобы узнать доступные команды")
        else:
            await message.answer(f"Вы уже вводили свою группу,\nЧтобы её изменить напишите /change группа\nЕсли вы хотите узнать команды бота введите /help")
    

    if "/date" in message.text.lower():
        data:str = message.text.lower()
        data = data.replace("/date","")
        data = data.replace(" ","")
        info = []
        all_days = parser(id_info,(datetime.datetime(2022,int(data[3:]),int(data[:2]))))
        time = datetime.datetime(2022,int(data[3:]),int(data[:2]))
        message_send = []
        send = ''
        if time.weekday() == 6:
            await message.answer("В этот день воскресенье, пар нет")
        else:
            if all_days[time.weekday()] == []:
                await message.answer("В этот день нет пар, можно отдохнуть")
            else:    
                for i in range(len(all_days[time.weekday()])):
                    info.append([])
                    a = all_days[time.weekday()][i]
                    info[i].append(a.get("дисциплина"))
                    info[i].append(a.get("преподаватель"))
                    info[i].append(a.get("начало"))
                    info[i].append(a.get("конец"))
                    info[i].append(a.get("аудитория"))
                    message_send.append(f"Пара № {i+1}: {info[i][0]}\nПреподаватель: {info[i][1]}\nНачало в: {info[i][2]} До: {info[i][3]}\nАудитория: {info[i][4]}")
        for i in message_send:
            send+=i
            send+="\n\n"
        await message.answer(send)  


    if message.text.lower() == "/now":
        info = []
        all_days = parser(id_info,datetime.datetime.now())
        time = datetime.datetime.now()
        message_send = []
        send = ''
        if time.weekday() == 6:
            await message.answer("Сегодня воскресенье, пар нет")
        else:
            if all_days[time.weekday()] == []:
                await message.answer("Сегодня нет пар, надеюсь вы хорошо отдохнули :)")    
            else:
                for i in range(len(all_days[time.weekday()])):
                    info.append([])
                    a = all_days[time.weekday()][i]
                    info[i].append(a.get("дисциплина"))
                    info[i].append(a.get("преподаватель"))
                    info[i].append(a.get("начало"))
                    info[i].append(a.get("конец"))
                    info[i].append(a.get("аудитория"))
                    message_send.append(f"Пара № {i+1}: {info[i][0]}\nПреподаватель: {info[i][1]}\nНачало в: {info[i][2]} До: {info[i][3]}\nАудитория: {info[i][4]}")
        for i in message_send:
            send+=i
            send+="\n\n"
        await message.answer(send)  


    if message.text.lower() == "/tomorrow":
        info = []
        all_days = parser(id_info,datetime.datetime.now())
        time = datetime.datetime.now()
        time = time + datetime.timedelta(days=1)
        message_send = []
        send = ""
        if time.weekday() == 6:
            await message.answer("В этот день воскресенье, пар нет")
        else:
            if all_days[time.weekday()] == []:
                await message.answer("В этот день нет пар, надеюсь вы хорошо отдохнули :)")    
            else:
                for i in range(len(all_days[time.weekday()])):
                    info.append([])
                    a = all_days[time.weekday()][i]
                    info[i].append(a.get("дисциплина"))
                    info[i].append(a.get("преподаватель"))
                    info[i].append(a.get("начало"))
                    info[i].append(a.get("конец"))
                    info[i].append(a.get("аудитория"))
                    message_send.append(f"Пара № {i+1}: {info[i][0]}\nПреподаватель: {info[i][1]}\nНачало в: {info[i][2]} До: {info[i][3]}\nАудитория: {info[i][4]}")
        for i in message_send:
            send+=i
            send+="\n\n"
        await message.answer(send)    



    if   "/change" in message.text.lower():
        group_change = message.text.lower()
        group_change = group_change.replace("/change", "")
        group_change = group_change.replace(" ","")
        group_change = group_change.upper()
        if group_change in group:
            for i in id_user:
                if i[0]==message.from_user.id:
                    if i[1] == group_change:
                        await message.answer("Данная группа у вас уже выбрана!")
                    else:    
                        for i in parser_for_groups():
                            if i.get("name") == group_change:
                                info_2 = i.get("id")
                        with engine.cursor() as cursor:                                   
                            cursor.execute(f"UPDATE `rasp_db`.`users` SET `groupp` = '{group_change}' WHERE (`id` = '{message.from_user.id}');")
                            cursor.execute(f"UPDATE `rasp_db`.`users` SET `number_1` = '{info_2}' WHERE (`id` = '{message.from_user.id}');")
                            engine.commit()
                        await message.answer(f"Ваша группа была изменена на {group_change}")  
        else:
            await message.answer(f"Мы не смогли найти группу: {group_change}, пожалуйста перепроверьте ввод")    
    
    if message.text.lower() == "/help":
        await message.answer("список команд:\n/change группа - чтобы сменить выбранную группу\n/now - для отображения расписания на сегодня, для выбранной группы\n/date 00.00 - для вывода даты (вместо нулей напишите нужную дату, например 01.01)\n/tomorrow - узнать расписание на завтра ")
@dp.message_handler(content_types="text")
async def Group(message: types.Message):
    info = message.text.upper()
    info = info.replace(" ","")
    info = info.replace("-","")

    if info in group:
        for i in parser_for_groups():
            if i.get("name") == info:
                info_2 = i.get("id")
        with engine.cursor() as cursor:                                   
            cursor.execute(f"insert into users(id,groupp,number_1) values('{message.from_user.id}','{info}',{info_2});")
            engine.commit()            
        await message.reply(f"я сохранил выбранную вами группу")

        await message.answer('Выберите один из вариантов:\nНапишите /now, чтобы получить расписание на сегодня\nНапишите дату, например: 01.01')
    else:
        await message.reply("Похоже вы допустили ошибку при вводе, перепроверьте название группы!") 
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())    