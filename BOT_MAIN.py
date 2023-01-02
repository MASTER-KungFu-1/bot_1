from aiogram import Bot,Dispatcher,types
import asyncio
import logging
import config
import pymysql
from config import db_name,password,host,user
import datetime

from fake_useragent import UserAgent
import aiohttp
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command,Text
from aiogram import F
storage = MemoryStorage()
storage = MemoryStorage()

class FSMAdmin(StatesGroup):
    start = State()
    change = State()
    date = State()
    find = State()
    find_choice = State()


async def parser_for_groups():
    agent = UserAgent()
    headers = {
        "Accept":"*/*",
        "User-Agent":f"{agent.random}"
    }
    url = "https://edu.donstu.ru/api/raspGrouplist?year=2022-2023"
    async with aiohttp.ClientSession() as session:
        async with session.get(url,headers=headers) as response:
            data = await response.json()
    data = data.get("data")
    all_groups = data
    return all_groups

async def parser_find():
    agent = UserAgent()
    headers = {
        "Accept":"*/*",
        "User-Agent":f"{agent.random}"
    }

    url = "https://edu.donstu.ru/api/raspTeacherlist?year=2022-2023"
    async with aiohttp.ClientSession() as session:
        async with session.get(url,headers=headers) as response:
            data = await response.json()
    data = data.get("data")
    all_find = data
    return all_find


async def parser_prepod_info(prepod:int,date):

    info = f"{date.year}-{date.month}-{date.day}"
    url = f'https://edu.donstu.ru/api/Rasp?idTeacher={prepod}&sdate={info}'

    agent = UserAgent()
    headers = {
        "Accept":"*/*",
        "User-Agent":f"{agent.random}"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url,headers=headers) as response:
                data = await response.json()
    except: 
        date = date - datetime.timedelta(days=1)
        info = f"{date.year}-{date.month}-{date.day}"
        url = f'https://edu.donstu.ru/api/Rasp?idTeacher={prepod}&sdate={info}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url,headers=headers) as response:
                data = await response.json()
    all_days =  [[],[],[],[],[],[]]
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

async def parser(Mkis21:int,date):

    info = f"{date.year}-{date.month}-{date.day}"
    url = f'https://edu.donstu.ru/api/Rasp?idGroup={Mkis21}&sdate={info}'

    agent = UserAgent()
    headers = {
        "Accept":"*/*",
        "User-Agent":f"{agent.random}"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url,headers=headers) as response:
                data = await response.json()
    except: 
        date = date - datetime.timedelta(days=1)
        info = f"{date.year}-{date.month}-{date.day}"
        url = f'https://edu.donstu.ru/api/Rasp?idGroup={Mkis21}&sdate={info}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url,headers=headers) as response:
                data = await response.json()
    
    all_days =  [[],[],[],[],[],[]]
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



logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.token_1)
dp = Dispatcher(bot=bot,storage=storage)

info_1 = []
o = []
async def start_def(dispatcher):       
    global group
    group = []
    for i in await parser_for_groups():
        group.append(i.get("name"))

@dp.message(Command(commands=["start","now","change","help","tomorrow",'date',"notification","find"]))
async def cmd_start(message: types.Message,state:FSMContext):
    engine = pymysql.connect(host=host,user=user,password=password,db=db_name)
    engine.ping()
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
            await state.set_state(FSMAdmin.start)
            await message.answer("Приветствую, укажите свою группу, чтобы корректно использовать бота.\nТак же вы можете написать команду /help, чтобы узнать доступные команды")
        else:
            await message.answer(f"Вы уже вводили свою группу,\nЧтобы её изменить напишите /change группа\nЕсли вы хотите узнать команды бота введите /help")
    
    if "/date" in message.text.lower():
        d = datetime.datetime.now()
        await state.set_state(FSMAdmin.date)
        await message.answer(f"напишите дату в формате дд.мм, сегодня: {d.day}.{d.month}") 

    if message.text.lower() == "/now":
        info = []
        all_days = await parser(id_info,datetime.datetime.now())
        time = datetime.datetime.now()
        message_send = []
        send = ''
        f = 0
        if time.weekday() == 6:
            await message.answer("Сегодня воскресенье, пар нет")
        else:
            if all_days[time.weekday()] == []:
                await message.answer("Сегодня нет пар, хорошо вам отдохнуть :)")    
            else:
                for i in range(len(all_days[time.weekday()])):
                    info.append([])
                    a = all_days[time.weekday()][i]
                    info[i].append(a.get("дисциплина"))
                    info[i].append(a.get("преподаватель"))
                    info[i].append(a.get("начало"))
                    info[i].append(a.get("конец"))
                    info[i].append(a.get("аудитория"))
                    if info[i][2] == info[i-1][2] and i>0:
                        f +=1
                        message_send.append(f"Пара № {i}: {info[i][0]}\nПреподаватель: {info[i][1]}\nНачало в: {info[i][2]} До: {info[i][3]}\nАудитория: {info[i][4]}")
                    elif f!=0:
                        message_send.append(f"Пара № {i}: {info[i][0]}\nПреподаватель: {info[i][1]}\nНачало в: {info[i][2]} До: {info[i][3]}\nАудитория: {info[i][4]}")    
                    else:
                        message_send.append(f"Пара № {i+1}: {info[i][0]}\nПреподаватель: {info[i][1]}\nНачало в: {info[i][2]} До: {info[i][3]}\nАудитория: {info[i][4]}")
                for i in message_send:
                    send+=i
                    send+="\n\n"
                await message.answer(send) 
    
    if message.text.lower() == "/tomorrow":
        info = []
        all_days = await parser(id_info,datetime.datetime.now())
        message_send = []
        send = ''
        f = 0
        time = datetime.datetime.now()
        time = time + datetime.timedelta(days=1)
        if time.weekday() == 6 :
            await message.answer(" В воскресенье, пар нет")
        else:
            if all_days[time.weekday()] == []:
                await message.answer("В этот день нет пар, хорошо вам отдохнуть :)")    
            else:
                for i in range(len(all_days[time.weekday()])):
                    info.append([])
                    a = all_days[time.weekday()][i]
                    info[i].append(a.get("дисциплина"))
                    info[i].append(a.get("преподаватель"))
                    info[i].append(a.get("начало"))
                    info[i].append(a.get("конец"))
                    info[i].append(a.get("аудитория"))
                    if info[i][2] == info[i-1][2] and i>0:
                        f +=1
                        message_send.append(f"Пара № {i}: {info[i][0]}\nПреподаватель: {info[i][1]}\nНачало в: {info[i][2]} До: {info[i][3]}\nАудитория: {info[i][4]}")
                    elif f!=0:
                        message_send.append(f"Пара № {i}: {info[i][0]}\nПреподаватель: {info[i][1]}\nНачало в: {info[i][2]} До: {info[i][3]}\nАудитория: {info[i][4]}")    
                    else:
                        message_send.append(f"Пара № {i+1}: {info[i][0]}\nПреподаватель: {info[i][1]}\nНачало в: {info[i][2]} До: {info[i][3]}\nАудитория: {info[i][4]}")
                for i in message_send:
                    send+=i
                    send+="\n\n"
                await message.answer(send)  


    if   "/change" in message.text.lower():
        await state.set_state(FSMAdmin.change)
        await message.answer("Напишите свою группу")    
    
    if "/find" in message.text.lower():
        await state.set_state(FSMAdmin.find)
        await message.answer("Напишите фамилию преподавателя")
    
    if message.text.lower() == "/help":
        await message.answer("список команд:\n/change группа - чтобы сменить выбранную группу\n/now - для отображения расписания на сегодня, для выбранной группы\n/date 00.00 - для вывода даты (вместо нулей напишите нужную дату, например 01.01)\n/tomorrow - узнать расписание на завтра ")
@dp.message(F.text,FSMAdmin.start)
async def Group(message: types.Message,state:FSMContext):
    info = message.text.upper()
    info = info.replace(" ","")
    info = info.replace("-","")
    engine = pymysql.connect(host=host,user=user,password=password,db=db_name)
    if info in group: 
        for i in await parser_for_groups():
            if i.get("name") == info:
                info_2 = i.get("id")
        engine.ping()
        with engine.cursor() as cursor:                                   
            cursor.execute(f"insert into users(id,groupp,number_1) values('{message.from_user.id}','{info}',{info_2});")
            engine.commit()            
        await message.reply(f"я сохранил выбранную вами группу")
        await state.clear()
        await message.answer('Выберите один из вариантов:\nНапишите /now, чтобы получить расписание на сегодня\nНапишите дату, например: 01.01')
    else:
        await message.reply("Похоже вы допустили ошибку при вводе, проверьте название группы(пока вы не введёте название группы, команды не будут работать)!") 
@dp.message(F.text,FSMAdmin.change)
async def change_info(message: types.Message,state:FSMContext):
    group_change = message.text.lower()
    group_change = group_change.replace("/change", "")
    group_change = group_change.replace(" ","")
    group_change = group_change.upper()
    engine = pymysql.connect(host=host,user=user,password=password,db=db_name)
    engine.ping()
    with engine.cursor() as cursor:
        sql = f"SELECT id,groupp,number_1,notifications from users;"
        cursor.execute(sql)
    id_user = cursor.fetchall()
    id_main = []
    for i in id_user:
        id_main.append(i[0])
    await state.set_state(FSMAdmin.change)
    if group_change in group:
        for i in id_user:
            if i[0]==message.from_user.id:
                if i[1] == group_change:
                    await message.answer("Данная группа у вас уже выбрана!")
                else:    
                    for i in await parser_for_groups():
                        if i.get("name") == group_change:
                            info_2 = i.get("id")
                    with engine.cursor() as cursor:                                   
                        cursor.execute(f"UPDATE `rasp_db`.`users` SET `groupp` = '{group_change}' WHERE (`id` = '{message.from_user.id}');")
                        cursor.execute(f"UPDATE `rasp_db`.`users` SET `number_1` = '{info_2}' WHERE (`id` = '{message.from_user.id}');")
                        engine.commit()
                    await state.clear()
                    await message.answer(f"Ваша группа была изменена на {group_change}")  
    else:
        await message.answer(f"Мы не смогли найти группу: {group_change}, пожалуйста перепроверьте ввод")

@dp.message(F.text,FSMAdmin.date)
async def change_info(message: types.Message,state:FSMContext):
    data:str = message.text.lower()
    data = data.replace(" ","")
    if len(data)==5:
        info = []
        time = datetime.datetime(2023,int(data[3:]),int(data[:2]))
        engine = pymysql.connect(host=host,user=user,password=password,db=db_name)
        engine.ping()
        with engine.cursor() as cursor:
            sql = f"SELECT id,groupp,number_1,notifications from users;"
            cursor.execute(sql)
        id_user = cursor.fetchall()
        for i in id_user:
            if message.from_user.id == i[0]:
                id_info:int = i[2]
        message_send = []
        send = ''
        f = 0
        all_days = await parser(id_info,(datetime.datetime(2023,int(data[3:]),int(data[:2]))))         
        if time.weekday() == 6:
            await state.clear()
            await message.answer("В воскресенье пар нет")        
        else:
            if all_days[time.weekday()] == []:
                await state.clear()
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
                    if info[i][2] == info[i-1][2] and i>0:
                        f +=1
                        message_send.append(f"Пара № {i}: {info[i][0]}\nПреподаватель: {info[i][1]}\nНачало в: {info[i][2]} До: {info[i][3]}\nАудитория: {info[i][4]}")
                    elif f!=0:
                        message_send.append(f"Пара № {i}: {info[i][0]}\nПреподаватель: {info[i][1]}\nНачало в: {info[i][2]} До: {info[i][3]}\nАудитория: {info[i][4]}")    
                    else:
                        message_send.append(f"Пара № {i+1}: {info[i][0]}\nПреподаватель: {info[i][1]}\nНачало в: {info[i][2]} До: {info[i][3]}\nАудитория: {info[i][4]}")
                for i in message_send:
                    send+=i
                    send+="\n\n"
                await state.clear()
                await message.answer(send) 
    else: 
        await message.answer("Неправильно написана дата, напишите в формате дд.мм")
@dp.message(F.text,FSMAdmin.find)
async def change_info(message: types.Message,state:FSMContext):
    data:str = message.text.lower()
    data = data.replace(" ","")
    info = await parser_find()
    k = 0
    a = []
    n = ""
    global message_info 
    message_info = 0
    for i in info:
        if i.get("name") == None:
            continue
        else:
            if data in i.get("name").lower():
                k+=1
                message_info = i.get("id")
                a.append(i)
    if k == 0: 
        await message.answer("Данного преподавателя не удалось найти, проверьте правильность ввода!")
    elif k==1:
        keyboard = InlineKeyboardBuilder()
        a_else = await parser_prepod_info(message_info,datetime.datetime.now()) 
        count = 0
        for i in range(len(a_else)):
            if a_else[i] == []:
                continue
            else:
                s = a_else[i][0].get("день_недели")    
                count+=1
                keyboard.button(text=s,callback_data=f"callback_{s}")    
        keyboard.adjust(1)   
        if count == 0:
            await message.answer("На этой недели у преподавателя пар нет!")
        else:    
            await message.answer("Выберите день недели:", reply_markup=keyboard.as_markup())
        await state.clear()

    elif k>1:
        
        for  i in range(len(a)):
            n+=(f"/{i+1} "+ a[i].get("name")+ "\n")    
        global po 
        po = n
        await message.answer(n+"\n"+"Выберите одного из преподавателей,нажав на его номер")
        await state.set_state(FSMAdmin.find_choice)

@dp.message(F.text,FSMAdmin.find_choice)
async def one_more_find(message: types.Message,state:FSMContext):
    info1 = message.text
    o = await parser_find()
    p = po.find(f"{info1}")
    p1 = po[p:po.find("\n",p)]
    p1 = p1[p1.find(" ")+1:]
    count = 0
    global message_info
    message_info = 0
    for i in o:
        if p1 == i.get("name"):
            message_info = i.get("id")
            a = await parser_prepod_info(message_info,datetime.datetime.now())
            break
    else:
        await message.answer("Нажмите на номер преподавателя, чтобы узнать его расписание!")
        return 
    keyboard = InlineKeyboardBuilder()
    
    for i in range(len(a)):
        if a[i] == []:
            continue
        else:
            s = a[i][0].get("день_недели")    
            count+=1
            keyboard.button(text=s,callback_data=f"callback_{s}")  
    keyboard.adjust(1)
    if count ==0:
        await message.answer("На этой недели у преподавателя пар нет!")
    else:    
        await message.answer("Выберите день недели:",reply_markup=keyboard.as_markup())
    await state.clear()
    


@dp.callback_query(Text(startswith="callback"))
async def monday_callback(callback: types.CallbackQuery):
    print("yes")
    if callback.data == "callback_Понедельник":
        a_else = await parser_prepod_info(message_info,datetime.datetime.now())
        a_else = a_else[0]
        info = []
        message_send = []
        send = ""
        l = 0
        for j in range(len(a_else)):
            info.append([])
            b = a_else[j]
            info[j].append(b.get("дисциплина"))
            info[j].append(b.get("преподаватель"))  
            info[j].append(b.get("начало"))
            info[j].append(b.get("конец"))
            info[j].append(b.get("аудитория"))
            if info[j][2] == info[j-1][2] and j>0:
                l +=1
                message_send.append(f"{s}\nПара № {j}: {info[j][0]}\nПреподаватель: {info[j][1]}\nНачало в: {info[j][2]} До: {info[j][3]}\nАудитория: {info[j][4]}")
            elif l!=0:
                message_send.append(f"Пара № {j}: {info[j][0]}\nПреподаватель: {info[j][1]}\nНачало в: {info[j][2]} До: {info[j][3]}\nАудитория: {info[j][4]}")    
            else:
                message_send.append(f"Пара № {j+1}: {info[j][0]}\nПреподаватель: {info[j][1]}\nНачало в: {info[j][2]} До: {info[j][3]}\nАудитория: {info[j][4]}")
        for k in message_send:
                    send+=k
                    send+="\n\n"
        s = b.get("день_недели")
        await callback.message.answer(f"{s}\n\n"+send)
        await callback.answer()

    elif callback.data == "callback_Вторник":
        a_else = await parser_prepod_info(message_info,datetime.datetime.now())
        a_else = a_else[1]
        info = []
        message_send = []
        send = ""
        l = 0
        for j in range(len(a_else)):
            info.append([])
            b = a_else[j]
            info[j].append(b.get("дисциплина"))
            info[j].append(b.get("преподаватель"))
            info[j].append(b.get("начало"))
            info[j].append(b.get("конец"))
            info[j].append(b.get("аудитория"))
            if info[j][2] == info[j-1][2] and j>0:
                l +=1
                message_send.append(f"{s}\nПара № {j}: {info[j][0]}\nПреподаватель: {info[j][1]}\nНачало в: {info[j][2]} До: {info[j][3]}\nАудитория: {info[j][4]}")
            elif l!=0:
                message_send.append(f"Пара № {j}: {info[j][0]}\nПреподаватель: {info[j][1]}\nНачало в: {info[j][2]} До: {info[j][3]}\nАудитория: {info[j][4]}")    
            else:
                message_send.append(f"Пара № {j+1}: {info[j][0]}\nПреподаватель: {info[j][1]}\nНачало в: {info[j][2]} До: {info[j][3]}\nАудитория: {info[j][4]}")
        for k in message_send:
                    send+=k
                    send+="\n\n"
        s = b.get("день_недели")
        await callback.message.answer(f"{s}\n\n"+send)
        await callback.answer()

    elif callback.data == "callback_Среда":
        a_else = await parser_prepod_info(message_info,datetime.datetime.now())
        a_else = a_else[2]
        info = []
        message_send = []
        send = ""
        l = 0
        for j in range(len(a_else)):
            info.append([])
            b = a_else[j]
            info[j].append(b.get("дисциплина"))
            info[j].append(b.get("преподаватель"))
            info[j].append(b.get("начало"))
            info[j].append(b.get("конец"))
            info[j].append(b.get("аудитория"))
            if info[j][2] == info[j-1][2] and j>0:
                l +=1
                message_send.append(f"{s}\nПара № {j}: {info[j][0]}\nПреподаватель: {info[j][1]}\nНачало в: {info[j][2]} До: {info[j][3]}\nАудитория: {info[j][4]}")
            elif l!=0:
                message_send.append(f"Пара № {j}: {info[j][0]}\nПреподаватель: {info[j][1]}\nНачало в: {info[j][2]} До: {info[j][3]}\nАудитория: {info[j][4]}")    
            else:
                message_send.append(f"Пара № {j+1}: {info[j][0]}\nПреподаватель: {info[j][1]}\nНачало в: {info[j][2]} До: {info[j][3]}\nАудитория: {info[j][4]}")
        for k in message_send:
                    send+=k
                    send+="\n\n"
        s = b.get("день_недели")
        await callback.message.answer(f"{s}\n\n"+send)
        await callback.answer()

    elif callback.data == "callback_Четверг":
        a_else = await parser_prepod_info(message_info,datetime.datetime.now())
        a_else = a_else[3]
        info = []
        message_send = []
        send = ""
        l = 0
        for j in range(len(a_else)):
            info.append([])
            b = a_else[j]
            info[j].append(b.get("дисциплина"))
            info[j].append(b.get("преподаватель"))
            info[j].append(b.get("начало"))
            info[j].append(b.get("конец"))
            info[j].append(b.get("аудитория"))
            if info[j][2] == info[j-1][2] and j>0:
                l +=1
                message_send.append(f"{s}\nПара № {j}: {info[j][0]}\nПреподаватель: {info[j][1]}\nНачало в: {info[j][2]} До: {info[j][3]}\nАудитория: {info[j][4]}")
            elif l!=0:
                message_send.append(f"Пара № {j}: {info[j][0]}\nПреподаватель: {info[j][1]}\nНачало в: {info[j][2]} До: {info[j][3]}\nАудитория: {info[j][4]}")    
            else:
                message_send.append(f"Пара № {j+1}: {info[j][0]}\nПреподаватель: {info[j][1]}\nНачало в: {info[j][2]} До: {info[j][3]}\nАудитория: {info[j][4]}")
        for k in message_send:
                    send+=k
                    send+="\n\n"
        s = b.get("день_недели")
        await callback.message.answer(f"{s}\n\n"+send)
        await callback.answer()

    elif callback.data == "callback_Пятница":
        a_else = await parser_prepod_info(message_info,datetime.datetime.now())
        a_else = a_else[4]
        info = []
        message_send = []
        send = ""
        l = 0
        for j in range(len(a_else)):
            info.append([])
            b = a_else[j]
            info[j].append(b.get("дисциплина"))
            info[j].append(b.get("преподаватель"))
            info[j].append(b.get("начало"))
            info[j].append(b.get("конец"))
            info[j].append(b.get("аудитория"))
            if info[j][2] == info[j-1][2] and j>0:
                l +=1
                message_send.append(f"{s}\nПара № {j}: {info[j][0]}\nПреподаватель: {info[j][1]}\nНачало в: {info[j][2]} До: {info[j][3]}\nАудитория: {info[j][4]}")
            elif l!=0:
                message_send.append(f"Пара № {j}: {info[j][0]}\nПреподаватель: {info[j][1]}\nНачало в: {info[j][2]} До: {info[j][3]}\nАудитория: {info[j][4]}")    
            else:
                message_send.append(f"Пара № {j+1}: {info[j][0]}\nПреподаватель: {info[j][1]}\nНачало в: {info[j][2]} До: {info[j][3]}\nАудитория: {info[j][4]}")
        for k in message_send:
                    send+=k
                    send+="\n\n"
        s = b.get("день_недели")
        await callback.message.answer(f"{s}\n\n"+send)
        await callback.answer()

    elif callback.data == "callback_Суббота":
        a_else = await parser_prepod_info(message_info,datetime.datetime.now())
        a_else = a_else[5]
        info = []
        message_send = []
        send = ""
        l = 0
        for j in range(len(a_else)):
            info.append([])
            b = a_else[j]
            info[j].append(b.get("дисциплина"))
            info[j].append(b.get("преподаватель"))
            info[j].append(b.get("начало"))
            info[j].append(b.get("конец"))
            info[j].append(b.get("аудитория"))
            if info[j][2] == info[j-1][2] and j>0:
                l +=1
                message_send.append(f"{s}\nПара № {j}: {info[j][0]}\nПреподаватель: {info[j][1]}\nНачало в: {info[j][2]} До: {info[j][3]}\nАудитория: {info[j][4]}")
            elif l!=0:
                message_send.append(f"Пара № {j}: {info[j][0]}\nПреподаватель: {info[j][1]}\nНачало в: {info[j][2]} До: {info[j][3]}\nАудитория: {info[j][4]}")    
            else:
                message_send.append(f"Пара № {j+1}: {info[j][0]}\nПреподаватель: {info[j][1]}\nНачало в: {info[j][2]} До: {info[j][3]}\nАудитория: {info[j][4]}")
        for k in message_send:
                    send+=k
                    send+="\n\n"
        s = b.get("день_недели")
        await callback.message.answer(f"{s}\n\n"+send)
        await callback.answer()

async def main():
    dp.startup.register(start_def)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())    