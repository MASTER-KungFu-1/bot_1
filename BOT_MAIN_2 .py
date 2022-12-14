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
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()

class FSMAdmin(StatesGroup):
    start = State()
    change = State()
    date = State()
    find = State()
    find_choice = State()


def parser_for_groups():
    agent = UserAgent()
    headers = {
        "Accept":"*/*",
        "User-Agent":f"{agent.random}"
    }

    url = "https://edu.donstu.ru/api/raspGrouplist?year=2022-2023"
    req = requests.get(url,headers=headers)
    src = req.text
    with open("/etc/BOT/dict_1.json","w") as file:
        json.dump(src,file,indent=4,ensure_ascii=True)    

    with open("/etc/BOT/dict_1.json", "r") as read_file:
        data = json.load(read_file)
    data:dict = json.loads(data)
    data = data.get("data")
    all_groups = data
    return all_groups

def parser_find():
    agent = UserAgent()
    headers = {
        "Accept":"*/*",
        "User-Agent":f"{agent.random}"
    }

    url = "https://edu.donstu.ru/api/raspTeacherlist?year=2022-2023"
    req = requests.get(url,headers=headers)
    src = req.text
    with open("/etc/BOT/dict_2.json","w") as file:
            json.dump(src,file,indent=4,ensure_ascii=True)    

    with open("/etc/BOT/dict_2.json", "r") as read_file:
        data = json.load(read_file)
    data:dict = json.loads(data)
    data = data.get("data")
    all_find = data
    return all_find


def parser_prepod_info(prepod:int,date):

    info = f"{date.year}-{date.month}-{date.day}"
    url = f'https://edu.donstu.ru/api/Rasp?idTeacher={prepod}&sdate={info}'

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
        url = f'https://edu.donstu.ru/api/Rasp?idTeacher={prepod}&sdate={info}'
        req = requests.get(url,headers=headers)
        src = req.text
    with open("/etc/BOT/dict_3.json","w") as file:
            json.dump(src,file,indent=4,ensure_ascii=True)    

    with open("/etc/BOT/dict_3.json", "r") as read_file:
        data = json.load(read_file)
    data = json.loads(data)
    all_days = [[],[],[],[],[],[]]
    data = data.get("data").get("rasp")
    for i in data:
        if i.get("????????????????????") == 1:
            all_days[0].append(i)
        elif i.get("????????????????????") == 2:
            all_days[1].append(i)
        elif i.get("????????????????????") == 3:
            all_days[2].append(i)
        elif i.get("????????????????????") == 4:
            all_days[3].append(i)
        elif i.get("????????????????????") == 5:
            all_days[4].append(i)
        else :
            all_days[5].append(i)
    return all_days


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
    with open("/etc/BOT/dict.json","w") as file:
            json.dump(src,file,indent=4,ensure_ascii=True)    

    with open("/etc/BOT/dict.json", "r") as read_file:
        data = json.load(read_file)
    data = json.loads(data)
    all_days = [[],[],[],[],[],[]]
    data = data.get("data").get("rasp")
    for i in data:
        if i.get("????????????????????") == 1:
            all_days[0].append(i)
        elif i.get("????????????????????") == 2:
            all_days[1].append(i)
        elif i.get("????????????????????") == 3:
            all_days[2].append(i)
        elif i.get("????????????????????") == 4:
            all_days[3].append(i)
        elif i.get("????????????????????") == 5:
            all_days[4].append(i)
        else :
            all_days[5].append(i)
    return all_days



all_days = parser(44434,datetime.datetime.now())



logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.token_1)
dp = Dispatcher(bot=bot,storage=storage)

info_1 = []
o = []
group = []
for i in parser_for_groups():
    group.append(i.get("name"))

@dp.message_handler(commands=["start","now","change","help","tomorrow",'date',"find"],state=None)
async def cmd_start(message: types.Message):
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
            await FSMAdmin.start.set()
            await message.answer("??????????????????????, ?????????????? ???????? ????????????, ?????????? ?????????????????? ???????????????????????? ????????.\n?????? ???? ???? ???????????? ???????????????? ?????????????? /help, ?????????? ???????????? ?????????????????? ??????????????")
        else:
            await message.answer(f"???? ?????? ?????????????? ???????? ????????????,\n?????????? ???? ???????????????? ???????????????? /change ????????????\n???????? ???? ???????????? ???????????? ?????????????? ???????? ?????????????? /help")
    
    if "/date" in message.text.lower():
        d = datetime.datetime.now()
        await FSMAdmin.date.set()
        await message.answer(f"???????????????? ???????? ?? ?????????????? ????.????, ??????????????: {d.day}.{d.month}") 

    if message.text.lower() == "/now":
        info = []
        all_days = parser(id_info,datetime.datetime.now())
        time = datetime.datetime.now()
        message_send = []
        send = ''
        f = 0
        if time.weekday() == 6:
            await message.answer("?????????????? ??????????????????????, ?????? ??????")
        else:
            if all_days[time.weekday()] == []:
                await message.answer("?????????????? ?????? ??????, ???????????? ?????? ?????????????????? :)")    
            else:
                for i in range(len(all_days[time.weekday()])):
                    info.append([])
                    a = all_days[time.weekday()][i]
                    info[i].append(a.get("????????????????????"))
                    info[i].append(a.get("??????????????????????????"))
                    info[i].append(a.get("????????????"))
                    info[i].append(a.get("??????????"))
                    info[i].append(a.get("??????????????????"))
                    if info[i][2] == info[i-1][2] and i>0:
                        f +=1
                        message_send.append(f"???????? ??? {i}: {info[i][0]}\n??????????????????????????: {info[i][1]}\n???????????? ??: {info[i][2]} ????: {info[i][3]}\n??????????????????: {info[i][4]}")
                    elif f!=0:
                        message_send.append(f"???????? ??? {i}: {info[i][0]}\n??????????????????????????: {info[i][1]}\n???????????? ??: {info[i][2]} ????: {info[i][3]}\n??????????????????: {info[i][4]}")    
                    else:
                        message_send.append(f"???????? ??? {i+1}: {info[i][0]}\n??????????????????????????: {info[i][1]}\n???????????? ??: {info[i][2]} ????: {info[i][3]}\n??????????????????: {info[i][4]}")
        for i in message_send:
            send+=i
            send+="\n\n"
        await message.answer(send) 
    
    if message.text.lower() == "/tomorrow":
        info = []
        all_days = parser(id_info,datetime.datetime.now())
        message_send = []
        send = ''
        f = 0
        time = datetime.datetime.now()
        time = time + datetime.timedelta(days=1)
        if time.weekday() == 6 :
            await message.answer(" ?? ??????????????????????, ?????? ??????")
        else:
            if all_days[time.weekday()] == []:
                await message.answer("?? ???????? ???????? ?????? ??????, ???????????? ?????? ?????????????????? :)")    
            else:
                for i in range(len(all_days[time.weekday()])):
                    info.append([])
                    a = all_days[time.weekday()][i]
                    info[i].append(a.get("????????????????????"))
                    info[i].append(a.get("??????????????????????????"))
                    info[i].append(a.get("????????????"))
                    info[i].append(a.get("??????????"))
                    info[i].append(a.get("??????????????????"))
                    if info[i][2] == info[i-1][2] and i>0:
                        f +=1
                        message_send.append(f"???????? ??? {i}: {info[i][0]}\n??????????????????????????: {info[i][1]}\n???????????? ??: {info[i][2]} ????: {info[i][3]}\n??????????????????: {info[i][4]}")
                    elif f!=0:
                        message_send.append(f"???????? ??? {i}: {info[i][0]}\n??????????????????????????: {info[i][1]}\n???????????? ??: {info[i][2]} ????: {info[i][3]}\n??????????????????: {info[i][4]}")    
                    else:
                        message_send.append(f"???????? ??? {i+1}: {info[i][0]}\n??????????????????????????: {info[i][1]}\n???????????? ??: {info[i][2]} ????: {info[i][3]}\n??????????????????: {info[i][4]}")
        for i in message_send:
            send+=i
            send+="\n\n"
        await message.answer(send)  


    if   "/change" in message.text.lower():
        await FSMAdmin.change.set()
        await message.answer("???????????????? ???????? ????????????")    
    
    if "/find" in message.text.lower():
        await FSMAdmin.find.set()
        await message.answer("???????????????? ?????????????? ??????????????????????????")
    
    if message.text.lower() == "/help":
        await message.answer("???????????? ????????????:\n/change ???????????? - ?????????? ?????????????? ?????????????????? ????????????\n/now - ?????? ?????????????????????? ???????????????????? ???? ??????????????, ?????? ?????????????????? ????????????\n/date 00.00 - ?????? ???????????? ???????? (???????????? ?????????? ???????????????? ???????????? ????????, ???????????????? 01.01)\n/tomorrow - ???????????? ???????????????????? ???? ???????????? ")
@dp.message_handler(content_types="text",state=FSMAdmin.start)
async def Group(message: types.Message,state:FSMContext):
    info = message.text.upper()
    info = info.replace(" ","")
    info = info.replace("-","")
    engine = pymysql.connect(host=host,user=user,password=password,db=db_name)
    if info in group: 
        for i in parser_for_groups():
            if i.get("name") == info:
                info_2 = i.get("id")
        engine.ping()
        with engine.cursor() as cursor:                                   
            cursor.execute(f"insert into users(id,groupp,number_1) values('{message.from_user.id}','{info}',{info_2});")
            engine.commit()            
        await message.reply(f"?? ???????????????? ?????????????????? ???????? ????????????")
        await state.reset_state()
        await message.answer('???????????????? ???????? ???? ??????????????????:\n???????????????? /now, ?????????? ???????????????? ???????????????????? ???? ??????????????\n???????????????? ????????, ????????????????: 01.01')
    else:
        await message.reply("???????????? ???? ?????????????????? ???????????? ?????? ??????????, ?????????????????? ???????????????? ????????????(???????? ???? ???? ?????????????? ???????????????? ????????????, ?????????????? ???? ?????????? ????????????????)!") 
@dp.message_handler(content_types="text",state=FSMAdmin.change)
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
    await FSMAdmin.change.set()
    if group_change in group:
        for i in id_user:
            if i[0]==message.from_user.id:
                if i[1] == group_change:
                    await message.answer("???????????? ???????????? ?? ?????? ?????? ??????????????!")
                else:    
                    for i in parser_for_groups():
                        if i.get("name") == group_change:
                            info_2 = i.get("id")
                    with engine.cursor() as cursor:                                   
                        cursor.execute(f"UPDATE `rasp_db`.`users` SET `groupp` = '{group_change}' WHERE (`id` = '{message.from_user.id}');")
                        cursor.execute(f"UPDATE `rasp_db`.`users` SET `number_1` = '{info_2}' WHERE (`id` = '{message.from_user.id}');")
                        engine.commit()
                    await state.reset_state()
                    await message.answer(f"???????? ???????????? ???????? ???????????????? ???? {group_change}")  
    else:
        await message.answer(f"???? ???? ???????????? ?????????? ????????????: {group_change}, ???????????????????? ?????????????????????????? ????????")

@dp.message_handler(content_types="text",state=FSMAdmin.date)
async def change_info(message: types.Message,state:FSMContext):
    data:str = message.text.lower()
    data = data.replace(" ","")
    if len(data)==5:
        info = []
        time = datetime.datetime(2022,int(data[3:]),int(data[:2]))
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
        all_days = parser(id_info,(datetime.datetime(2022,int(data[3:]),int(data[:2]))))         
        if time.weekday() == 6:
            await state.reset_state()
            await message.answer("?? ?????????????????????? ?????? ??????")        
        else:
            if all_days[time.weekday()] == []:
                await state.reset_state()
                await message.answer("?? ???????? ???????? ?????? ??????, ?????????? ??????????????????")
            else:    
                for i in range(len(all_days[time.weekday()])):
                    info.append([])
                    a = all_days[time.weekday()][i]
                    info[i].append(a.get("????????????????????"))
                    info[i].append(a.get("??????????????????????????"))
                    info[i].append(a.get("????????????"))
                    info[i].append(a.get("??????????"))
                    info[i].append(a.get("??????????????????"))
                    if info[i][2] == info[i-1][2] and i>0:
                        f +=1
                        message_send.append(f"???????? ??? {i}: {info[i][0]}\n??????????????????????????: {info[i][1]}\n???????????? ??: {info[i][2]} ????: {info[i][3]}\n??????????????????: {info[i][4]}")
                    elif f!=0:
                        message_send.append(f"???????? ??? {i}: {info[i][0]}\n??????????????????????????: {info[i][1]}\n???????????? ??: {info[i][2]} ????: {info[i][3]}\n??????????????????: {info[i][4]}")    
                    else:
                        message_send.append(f"???????? ??? {i+1}: {info[i][0]}\n??????????????????????????: {info[i][1]}\n???????????? ??: {info[i][2]} ????: {info[i][3]}\n??????????????????: {info[i][4]}")
                for i in message_send:
                    send+=i
                    send+="\n\n"
                await state.reset_state()
                await message.answer(send) 
    else: 
        await message.answer("?????????????????????? ???????????????? ????????, ???????????????? ?? ?????????????? ????.????")
@dp.message_handler(content_types="text",state=FSMAdmin.find)
async def change_info(message: types.Message,state:FSMContext):
    data:str = message.text.lower()
    data = data.replace(" ","")
    info = parser_find()
    k = 0
    a = []
    n = ""
    message_info = 0
    for i in info:
        if data in i.get("name").lower():
            k+=1
            message_info = i.get("id")
            a.append(i)
    if k == 0: 
        await message.answer("?????????????? ?????????????????????????? ???? ?????????????? ??????????, ?????????????????? ???????????????????????? ??????????!")
    elif k==1:
        o = parser_find()
        a_else = parser_prepod_info(message_info,datetime.datetime.now()) 
        for i in range(len(a_else)):
            if a_else[i] == []:
                continue
            else:
                info = []
                message_send = []
                send = ""
                l = 0

                for j in range(len(a_else[i])):
                    info.append([])
                    b = a_else[i][j]
                    info[j].append(b.get("????????????????????"))
                    info[j].append(b.get("??????????????????????????"))
                    info[j].append(b.get("????????????"))
                    info[j].append(b.get("??????????"))
                    info[j].append(b.get("??????????????????"))
                    info[j].append(b.get("????????????"))
                    if " " in info[j][5]:
                        padej = "??????????"
                    else:
                        padej = "????????????"
                    if info[j][2] == info[j-1][2] and j>0:
                        l +=1
                        message_send.append(f"{s}\n???????? ??? {j}: {info[j][0]}\n??????????????????????????: {info[j][1]}\n???????????? ??: {info[j][2]} ????: {info[j][3]}\n??????????????????: {info[j][4]}\n???????? ???????? ?? {padej}: {info[j][5]}")
                    elif l!=0:
                        message_send.append(f"???????? ??? {j}: {info[j][0]}\n??????????????????????????: {info[j][1]}\n???????????? ??: {info[j][2]} ????: {info[j][3]}\n??????????????????: {info[j][4]}\n???????? ???????? ?? {padej}: {info[j][5]}")    
                    else:
                        message_send.append(f"???????? ??? {j+1}: {info[j][0]}\n??????????????????????????: {info[j][1]}\n???????????? ??: {info[j][2]} ????: {info[j][3]}\n??????????????????: {info[j][4]}\n???????? ???????? ?? {padej}: {info[j][5]}")
                for k in message_send:
                    send+=k
                    send+="\n\n"
                s = a_else[i][0].get("????????_????????????")    
                await message.answer(f"{s}\n\n"+send)
        await state.reset_state()

    elif k>1:
        
        for  i in range(len(a)):
            n+=(f"/{i+1} "+ a[i].get("name")+ "\n")    
        global po 
        po = n
        await message.answer(n+"\n"+"???????????????? ???????????? ???? ????????????????????????????,?????????? ???? ?????? ??????????")
        await FSMAdmin.find_choice.set()

@dp.message_handler(content_types="text",state=FSMAdmin.find_choice)
async def one_more_find(message: types.Message,state:FSMContext):
    info1 = message.text
    o = parser_find()
    p = po.find(f"{info1}")
    p1 = po[p:po.find("\n",p)]
    p1 = p1[p1.find(" ")+1:]
    time = datetime.datetime.now()
    message_send = []
    l = 0
    for i in o:
        if p1 == i.get("name"):
            f = i.get("id")
            a = parser_prepod_info(f,datetime.datetime.now())
            break
    else:
        await message.answer("?????????????? ???? ?????????? ??????????????????????????, ?????????? ???????????? ?????? ????????????????????!")
        return 

    for i in range(len(a)):
        if a[i] == []:
            continue
        else:
                info = []
                message_send = []
                send = ""
                l = 0
                for j in range(len(a[i])):
                    info.append([])
                    b = a[i][j]
                    info[j].append(b.get("????????????????????"))
                    info[j].append(b.get("??????????????????????????"))
                    info[j].append(b.get("????????????"))
                    info[j].append(b.get("??????????"))
                    info[j].append(b.get("??????????????????"))
                    if info[j][2] == info[j-1][2] and j>0:
                        l +=1
                        message_send.append(f"{s}\n???????? ??? {j}: {info[j][0]}\n??????????????????????????: {info[j][1]}\n???????????? ??: {info[j][2]} ????: {info[j][3]}\n??????????????????: {info[j][4]}")
                    elif l!=0:
                        message_send.append(f"???????? ??? {j}: {info[j][0]}\n??????????????????????????: {info[j][1]}\n???????????? ??: {info[j][2]} ????: {info[j][3]}\n??????????????????: {info[j][4]}")    
                    else:
                        message_send.append(f"???????? ??? {j+1}: {info[j][0]}\n??????????????????????????: {info[j][1]}\n???????????? ??: {info[j][2]} ????: {info[j][3]}\n??????????????????: {info[j][4]}")
                for k in message_send:
                            send+=k
                            send+="\n\n"
                s = b.get("????????_????????????")
                await message.answer(f"{s}\n\n"+send)
    await state.reset_state()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())    
