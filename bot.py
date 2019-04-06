#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot
import time, datetime
import paramiko
from telebot import types


API_TOKEN = "XXXXXXXXXX:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"     # токен бота
user_id = 000000000     # id администратора
no_admin_enabled = False    #вход с любого user_id
active_tunnel = False       #флаг активного туннеля


'''
USER STATES | состояния пользователя
0 = старт бота / запрос имени
1 = ввод имени
2 = приветствие / запрос настроек SSH(хост|ip)
3 = ввод имя хоста|ip-адрес SSH
4 = ввод порт SSH
5 = ввод имя пользователя SSH
6 = ввод пароля SSH / подключение
7 = ввод названия IPSec подключения
8 = ввод имя хоста|ip IPSec
9 = ввод секретного ключа
10 = ввод ip-адрес локальной сети
11 = ввод ip-адрес удаленной сети
12 = проверка введенных данных / доступны команды подключения 
'''

#paramico
host = ''
port = ''
user = ''
passw = ''

#script
namevpn = ''
servervpn = ''
keyvpn = ''
subnetvpn = ''
lanvpn = ''

state = 0   # "стартовое" cостояние    //7 для Debug IPSec
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=["start"])
def cmd_start(message):
    global state
    if (user_id == message.chat.id) or (no_admin_enabled):  # проверяем, что пишет именно владелец
        bot.send_message(message.chat.id, "Привет! Я Бот помощник 😊\nКак я могу к тебе обращаться?")
        state = 1
        print(state)
    else:
        bot.send_message(message.from_user.id, "В детстве мне говорили, что плохо отвечать незнакомцам ...\nПростите😅")
        print('Not registered detected')



@bot.message_handler(commands=["settings"])
def cmd_settings(message):
    global state
    if (user_id == message.chat.id) or (no_admin_enabled):
        bot.send_message(message.chat.id, "Что ж, давай c начала.\nВведи имя хоста или IP-адрес : ")
        state = 3
        print(state)



@bot.message_handler(commands=["help"])         #помощь
def help(message):
    global state
    if (user_id == message.chat.id) or (no_admin_enabled):
        print("help to user")
        print(state)
        bot.send_message(message.chat.id,"Вот мои команды :\n/help - Вызвать это меню\n/start - Стереть мне память и начать сначала\n/settings - Настроить SSH подключение\n/create - Создать туннель IPSec\n/terminate - Разорвать туннель IPSec\n/about - Об Авторе")


@bot.message_handler(commands=["about"])        # :)
def cmd_about(message):
    global state
    bot.send_message(message.chat.id, "Моего создателя зовут ********, вот ссылка на него :\nt.me/*********")
    print(state)


@bot.message_handler(commands=["ipsec"])
def cmd_ipsec(message):
    global state
    if (user_id == message.chat.id) or (no_admin_enabled):
        if state < 7:
            bot.send_message(message.chat.id, "Данная команда еще недоступна, не найдено SSH подключение.\n/settings - настроить SSH подключение")
            print(state)
        else:
            bot.send_message(message.chat.id, "Что ж, давай c начала.\nИмя IPSec подключения : ")
            state = 7
            print(state)

@bot.message_handler(commands=["create"])
def cmd_create(message):
    global state
    global active_tunnel
    global client
    global chan
    print(active_tunnel)
    if (user_id == message.chat.id) or (no_admin_enabled):
        if state < 7:
            bot.send_message(message.chat.id, "Данная команда еще недоступна, не найдено SSH подключение.\n/settings - настроить SSH подключение")
            print(state)
        elif state >= 7 and state < 12:
            bot.send_message(message.chat.id,"Данная команда еще недоступна, необходимо произвести настройки.\n/settings - настроить SSH подключение\n/ipsec - это запустит процесс настройки IPSec")
            print(state)
        elif state >= 12:
            if not active_tunnel :
                bot.send_message(message.chat.id, "Создаем туннель.")
                bot.send_message(message.chat.id, "Ожидайте...")

                print('Подключаемся и создаем туннель')

                '''
                                #код создания подключения Paramico
                '''
                client.connect(hostname=host, username=user, password=passw, port=port)     # подключились
                chan = client.invoke_shell()  # открыли сокет
                time.sleep(2)
                print("Открыли сокет!")
                chan.send('access-list _WEBADMIN_IPSEC_' + namevpn + ' \n')
                chan.send('permit ip ' + lanvpn + ' 255.255.255.0 ' + subnetvpn + ' 255.255.255.0\n')
                chan.send('exit\n')
                time.sleep(0.4)
                chan.send('crypto ike key ' + namevpn + ' ' + keyvpn + ' email *************@example.com\n')
                chan.send('crypto ike proposal ' + namevpn + ' \n')
                chan.send('encryption des\n')
                chan.send('encryption aes-cbc-128\n')
                chan.send('encryption 3des\n')
                chan.send('dh-group 1\n')
                chan.send('integrity md5\n')
                chan.send('integrity sha1\n')
                chan.send('exit \n')
                time.sleep(0.4)
                chan.send('crypto ike policy ' + namevpn + ' \n')
                chan.send('proposal ' + namevpn + ' \n')
                chan.send('lifetime 3600 \n')
                chan.send('mode ikev2 \n')
                chan.send('exit \n')
                time.sleep(0.4)
                chan.send('crypto ipsec transform-set ' + namevpn + ' \n')
                chan.send('cypher esp-des\n')
                chan.send('cypher esp-3des\n')
                chan.send('cypher esp-aes-128\n')
                chan.send('hmac esp-md5-hmac\n')
                chan.send('hmac esp-sha1-hmac\n')
                chan.send('dh-group 1 \n')
                chan.send('lifetime 3600 \n')
                chan.send('exit \n')
                time.sleep(0.4)
                chan.send('crypto ipsec profile ' + namevpn + ' \n')
                chan.send('dpd-interval 30 \n')
                chan.send('identity-local email *************@example.com \n')
                chan.send('match-identity-remote email *************@example.com \n')
                chan.send('authentication-local pre-share \n')
                chan.send('mode tunnel \n')
                chan.send('policy ' + namevpn + ' \n')
                chan.send('exit \n')
                time.sleep(0.4)
                chan.send('crypto map ' + namevpn + ' \n')
                chan.send('set-peer ' + servervpn + ' \n')
                chan.send('set-profile ' + namevpn + ' \n')
                chan.send('set-transform ' + namevpn + ' \n')
                chan.send('match-address _WEBADMIN_IPSEC_' + namevpn + ' \n')
                chan.send('set-tcpmss pmtu \n')
                chan.send('connect \n')
                time.sleep(1.5)
                chan.send('nail-up \n')
                chan.send('reauth-passive \n')
                chan.send('virtual-ip no enable \n')
                time.sleep(2.5)
                chan.send('enable \n')
                time.sleep(2.5)
                chan.send('enable \n')
                chan.send('exit \n')
                chan.send('exit \n')
                # chan.send('system configuration save \n')
                # в тестовом окружении нет смысла сохранять настройки в энергонезависимую память
                client.close()      #   отключились
                time.sleep(1)
                bot.send_message(message.chat.id, "Осталось совсем немного😌\nРаботаю над шифрованием ...")
                time.sleep(10)
                #client.connect(hostname=host, username=user, password=passw, port=port)  # подключились
                #chan = client.invoke_shell()  # открыли сокет
                #time.sleep(1)
                #chan.send('crypto map ' + namevpn + ' \n')
                #chan.send('enable \n')
                #time.sleep(1.5)
                #chan.send('exit \n')
                #chan.send('exit \n')
                #client.close()      #   отключились
                print(state)
                active_tunnel = True
                bot.send_message(message.chat.id, "Туннель создан! Теперь ваша локальная сеть объединена с сетью "+servervpn+"")
                time.sleep(2)
                bot.send_message(message.chat.id, "Приятного использования 😎")
            else:
                bot.send_message(message.chat.id, "Уже имеем туннель 😎\nЛокальная сеть объединена с сетью "+servervpn+"")
                print('Уже имеем туннель')
                print(state)
        else:
            bot.send_message(message.chat.id, "Что-то не так, проверьте настройки бота...")
            print('Что-то не так, проверьте настройки бота...')
            print(state)

@bot.message_handler(commands=["terminate"])
def cmd_terminate(message):
    global state
    global active_tunnel
    global client
    global chan
    print(active_tunnel)
    if (user_id == message.chat.id) or (no_admin_enabled):
        if state < 7:
            bot.send_message(message.chat.id, "Данная команда еще недоступна, не найдено SSH подключение.\n/settings - настроить SSH подключение")
            print(state)
        elif state >= 7 and state < 12:
            bot.send_message(message.chat.id,"Данная команда еще недоступна, необходимо произвести настройки.\n/settings - настроить SSH подключение\n/ipsec - это запустит процесс настройки IPSec")
            print(state)
        elif state >= 12:
            if active_tunnel :
                bot.send_message(message.chat.id, "Разрываем туннель.")
                bot.send_message(message.chat.id, "Ожидайте...")
                print('Подключаемся и разрываем туннель')

                '''
                            #код разрыва Paramico    
                '''
                client.connect(hostname=host, username=user, password=passw, port=port)  # подключились
                chan = client.invoke_shell()  # открыли сокет
                time.sleep(1)
                print("Открыли сокет!")
                print('STOP TUNNEL')
                chan.send('no access-list _WEBADMIN_IPSEC_' + namevpn + ' \n')
                chan.send('no crypto ike key ' + namevpn + ' \n')
                chan.send('no crypto ike proposal ' + namevpn + ' \n')
                chan.send('no crypto ike policy ' + namevpn + ' \n')
                chan.send('no crypto ipsec transform-set ' + namevpn + ' \n')
                chan.send('no crypto ipsec profile ' + namevpn + ' \n')
                chan.send('no crypto map ' + namevpn + ' \n')
                chan.send('\n')
                # chan.send('system configuration save \n')
                print('STOPPED')
                time.sleep(1)
                client.close()  # отключились
                print(state)
                active_tunnel = False
                bot.send_message(message.chat.id,"Туннель успешно закрыт!")
                time.sleep(1.5)
                bot.send_message(message.chat.id, "Спасибо за использование 😌")
            else:
                bot.send_message(message.chat.id, "Нет активного туннеля\nНевозможно выключить то, чего нет 🤷‍♀")
                print('Нечего разрывать ')
                print(state)
        else:
            bot.send_message(message.chat.id, "Что-то не так, проверьте настройки бота...")
            print('Что-то не так, проверьте настройки бота...')
            print(state)




@bot.message_handler(func=lambda message: state == 1)
def user_entering_name(message):
    if (user_id == message.chat.id) or (no_admin_enabled):

        global state
        global username
        username = message.text
        username = username.strip()
        # В случае с именем не будем ничего проверять, это Имя пользователя (может использоваться для доп. аутентификации)
        bot.send_message(message.chat.id, "Отличное имя, "+username+", Очень приятно познакомиться!\nА меня создал один программист, чтобы помогать людям создавать IPSec VPN туннели для объединения локальных сетей, я могу тебе с этим помочь.")
        bot.send_message(message.from_user.id,"Давай откроем настройки SSH и заполним нужные данные для подключения к системе.\nОтправь любое сообщение чтобы продолжить 😉")
        state = 2
        print(state)

@bot.message_handler(func=lambda message: state == 2)
def user_entering_host_msg(message):
    if (user_id == message.chat.id) or (no_admin_enabled):

        global state
        buf = message.text
        bot.send_message(message.from_user.id,"Для подключения по SSH введи Имя хоста или IP-адрес : ")
        state = 3
        print(state)

@bot.message_handler(func=lambda message: state == 3)
def user_entering_host(message):
    if (user_id == message.chat.id) or (no_admin_enabled):

        global state
        global host
        host = message.text
        host = host.strip()
        bot.send_message(message.from_user.id,"Теперь введи порт подключения (Port) : ")
        state = 4
        print(state)

@bot.message_handler(func=lambda message: state == 4)
def user_entering_port(message):
    if (user_id == message.chat.id) or (no_admin_enabled):

        global state
        global port
        # А вот тут сделаем проверку
        if not message.text.isdigit():
            # Состояние не меняем, поэтому только выводим сообщение об ошибке и ждём дальше
            bot.send_message(message.chat.id, "Порт это число 0 - 65535.")
            return
        # На данном этапе мы уверены, что message.text можно преобразовать в число, поэтому ничем не рискуем
        if int(message.text) < 1 or int(message.text) > 65535:
            bot.send_message(message.chat.id, "Какой-то странный порт, " + username + ". Проверь еще раз! Введи число от 0 - 65535.")
            return
        else:
            port = message.text
            port = port.strip()
            # Порт введён корректно, можно идти дальше
        bot.send_message(message.from_user.id,"Осталось совсем немного.\nИмя пользователя : ")
        state = 5
        print(state)

@bot.message_handler(func=lambda message: state == 5)
def user_entering_sshuser(message):
    if (user_id == message.chat.id) or (no_admin_enabled):

        global state
        global host
        global port
        global user
        global username
        user = message.text
        user = user.lower()
        user = user.strip()
        bot.send_message(message.from_user.id, "Давай проверим настройки\n"+user+"@"+host+":"+port+"\n\nЕсли ты где то видишь ошибку в данных нажми /settings - это запустит процесс настройки ещё раз.\nЕсли всё верно давай введём пароль : ")
        state = 6
        print(state)

@bot.message_handler(func=lambda message: state == 6)
def user_entering_password(message):
    if (user_id == message.chat.id) or (no_admin_enabled):

        global state
        global passw
        global client
        global chan
        passw = message.text
        passw = passw.strip()
        buf = len(passw)
        hide = '*'*buf
        bot.send_message(message.from_user.id, "Пытаюсь подключиться... \n"+user+"@"+host+":"+port+" "+hide+"")
        try:
            client.connect(hostname=host, username=user, password=passw, port=port)
        except TimeoutError:
            bot.send_message(message.from_user.id, "Очень долго 😔\nМоя попытка установить соединение была безуспешной, т.к. от другого компьютера за требуемое время не получен нужный отклик, или было разорвано уже установленное соединение из-за неверного отклика уже подключенного компьютера!")
            print("Попытка установить соединение была безуспешной, т.к. от другого компьютера за требуемое время не получен нужный отклик, или было разорвано уже установленное соединение из-за неверного отклика уже подключенного компьютера!")
            time.sleep(1)
            bot.send_message(message.from_user.id,"На твоём месте я бы еще раз всё проверил.\n\n"+user+"@"+host+":"+port+" "+hide+"\n\nИспользуй /settings - для настройки.")
        except paramiko.ssh_exception.AuthenticationException:
            bot.send_message(message.from_user.id, "Ошибка Аутентификации 😬\nВозможно неверно введены данные для входа.\nИспользуй /settings - для настройки\nИли попробуй ввести пароль ещё раз : ")
            print("Authentication failed!")
        except paramiko.ssh_exception.NoValidConnectionsError:
            bot.send_message(message.from_user.id,"Не могу подключиться по указанному порту '"+port+"'\nИспользуй /settings - для настройки.")
            print("Unable to connect to port!")
        except:
            bot.send_message(message.from_user.id,"Что-то со мной не так 😰\nИспользуй /settings - для настройки.\nПопробуй еще...")
            print("Something wrong...")
        else:
            print("No error found:")
            chan = client.invoke_shell()  # открыли сокет
            bot.send_message(message.from_user.id, "Подключено 😎\nСоздадим IPSec туннель.")
            print("Подключено!")
            bot.send_message(message.from_user.id, "Имя подключения IPSec : ")
            state = 7
            print(state)
        finally:
            client.close()      #закрываем подключение после проверки
            print("Thanks for Using © Andrew Denisow 2019")


@bot.message_handler(func=lambda message: state == 7)
def user_entering_namevpn(message):
    if (user_id == message.chat.id) or (no_admin_enabled):

        global state
        global namevpn
        namevpn = message.text
        namevpn = namevpn.strip()
        bot.send_message(message.from_user.id,"Теперь введи Имя хоста или IP-адрес удаленного сервера : ")
        state = 8
        print(state)

@bot.message_handler(func=lambda message: state == 8)
def user_entering_servervpn(message):
    if (user_id == message.chat.id) or (no_admin_enabled):

        global state
        global servervpn
        servervpn = message.text
        servervpn = servervpn.lower()
        servervpn = servervpn.strip()
        bot.send_message(message.from_user.id,"Секреный ключ : ")
        state = 9
        print(state)

@bot.message_handler(func=lambda message: state == 9)
def user_entering_keyvpn(message):
    if (user_id == message.chat.id) or (no_admin_enabled):

        global state
        global keyvpn
        if len(message.text) < 8 :
            bot.send_message(message.from_user.id,"Слишком короткий ключ! Введи не менее 8 символов : ")
            return
        else:
            keyvpn = message.text
            keyvpn = keyvpn.strip()
            bot.send_message(message.from_user.id,"Ещё чуть-чуть.\nВведи IP-адрес ЛОКАЛЬНОЙ подсети : \nПомни это подсеть, на конце '0'")
            state = 10
            print(state)

@bot.message_handler(func=lambda message: state == 10)
def user_entering_lanvpn(message):
    if (user_id == message.chat.id) or (no_admin_enabled):

        global state
        global lanvpn
        lanvpn = message.text
        lanvpn = lanvpn.strip()
        bot.send_message(message.from_user.id,"IP-адрес УДАЛЁННОЙ подсети : \nЭто тоже подсеть, на конце '0'")
        state = 11
        print(state)

@bot.message_handler(func=lambda message: state == 11)
def user_entering_subnetvpn(message):
    if (user_id == message.chat.id) or (no_admin_enabled):

        global state
        global subnetvpn
        subnetvpn = message.text
        subnetvpn = subnetvpn.strip()
        bot.send_message(message.from_user.id, "Давай проверим настройки IPSec\n\nНазвание подключения : "+namevpn+"\nУдаленный шлюз : "+servervpn+"\nКлюч PSK : "+keyvpn+"\nIP-адрес локальной сети : "+lanvpn+"\nIP-адрес удаленной сети : "+subnetvpn+"\n\nЕсли ты где-то видишь ошибку в данных нажми /ipsec - это запустит процесс настройки IPSec ещё раз.")
        bot.send_message(message.from_user.id,"Доступны команды :\n/create - Создать туннель IPSec\n/terminate - Разорвать туннель IPSec")
        state = 12
        print(state)
        print("Готовы создавать туннель")






client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

if __name__ == '__main__':
    while True:
        try:  # добавляем try для бесперебойной работы
            bot.polling(none_stop=True)  # запуск бота
        except:
            time.sleep(10)  # в случае падения
