# coding=UTF-8
import random
import mysql.connector
from config import sql_user, sql_pass, sql_host, sql_base, admin_ids
from string import split, lower
import requests


info_message = 'Для вывода информации введите "!инфо"'


def register_user(vk_id, payload, gbot):
    conn = mysql.connector.connect(user=sql_user, password=sql_pass, host=sql_host, database=sql_base)
    cur = conn.cursor()
    cur.execute('SELECT id FROM users WHERE id=%s', (vk_id,))
    user = cur.fetchall()
    if (len(user) != 0):
        gbot.messages.send(peer_id=vk_id, message='Вы уже были зарегистрированы ранее!', random_id=random.randint(0, 200000))
        return
    sex = requests.get('https://api.vk.com/method/users.get?user_id={0}&v=5.52&fields=sex'.format(vk_id)).json()['response'][0]['sex']
    cur.execute('INSERT INTO `users` (`id`, `sex`) VALUES(%s,%s)', (vk_id,sex))
    conn.commit()
    
    gbot.messages.send(peer_id=vk_id, message='Вы успешно зарегистрированы!',random_id=random.randint(0, 200000))


def delete_user(vk_id, payload, gbot):
    conn = mysql.connector.connect(user=sql_user, password=sql_pass, host=sql_host, database=sql_base)
    cur = conn.cursor()
    cur.execute('SELECT id FROM users WHERE id=%s', (vk_id,))
    user = cur.fetchall()
    if (len(user) == 0):
        gbot.messages.send(peer_id=vk_id, message='Вашего id нет в системе!',
                           random_id=random.randint(0, 200000))
        return
    cur.execute("DELETE FROM users WHERE id=%s", (vk_id,))
    conn.commit()
    gbot.messages.send(peer_id=vk_id, message='Ваш id был удален из базы', random_id=random.randint(0, 200000))


command_str_list = u'\n!инфо\n!группа <группа>\n!получателю <сообщение>\n!санте <сообщение>'


def show_info(vk_id, payload, gbot):
    conn = mysql.connector.connect(user=sql_user, password=sql_pass, host=sql_host, database=sql_base)
    cur = conn.cursor()
    cur.execute('SELECT `id`, `group`, `id_next` FROM `users` WHERE `id`=%s', (vk_id,))
    user = cur.fetchall()
    msg = u''
    if (len(user) != 0):
        msg += u'Вы участвуете в игре\n'
        if (user[0][1] != ''):
            msg += u'Указана группа: ' + unicode(user[0][1])
        else:
            msg += u'Информация о группе не указана'
        if (user[0][2] > 0):
            msg += u'\nНадо сделать подарок для vk.com/id' + unicode(user[0][2]) + u' из группы '
            cur.execute('SELECT `group` FROM `users` WHERE `id`=%s', (user[0][2],))
            user1 = cur.fetchall()
            msg += unicode(user1[0][0])
    else:
        msg += u'Вы не участвуете в игре'
    msg += u'\n\nСписок доступных команд:' + command_str_list
    gbot.messages.send(peer_id=vk_id, message=msg, random_id=random.randint(0, 200000))


def set_group(vk_id, payload, gbot):
    conn = mysql.connector.connect(user=sql_user, password=sql_pass, host=sql_host, database=sql_base)
    cur = conn.cursor()
    cur.execute('SELECT id FROM users WHERE id=%s', (vk_id,))
    user = cur.fetchall()
    if (len(user) == 0):
        gbot.messages.send(peer_id=vk_id, message='Вы не участвуете в игре', random_id=random.randint(0, 200000))
        return
    cur.execute("UPDATE `users` SET `group`=%s WHERE `id`=%s", (payload if payload else u'нет информации', vk_id,))
    conn.commit()
    gbot.messages.send(peer_id=vk_id, message='Информация о группе была обновлена', random_id=random.randint(0, 200000))


def write_recv(vk_id, payload, gbot):
    msg = u'Ваш Тайный Санта пишет:\n' + payload
    conn = mysql.connector.connect(user=sql_user, password=sql_pass, host=sql_host, database=sql_base)
    cur = conn.cursor()
    cur.execute('SELECT `id_next` FROM `users` WHERE `id`=%s', (vk_id,))
    user = cur.fetchall()
    gbot.messages.send(peer_id=user[0][0], message=msg, random_id=random.randint(0, 200000))
    gbot.messages.send(peer_id=vk_id, message=u'Сообщение отправлено', random_id=random.randint(0, 200000))


def write_ts(vk_id, payload, gbot):
    msg = u'Ваш получатель пишет:\n' + payload
    conn = mysql.connector.connect(user=sql_user, password=sql_pass, host=sql_host, database=sql_base)
    cur = conn.cursor()
    cur.execute('SELECT `id_prev` FROM `users` WHERE `id`=%s', (vk_id,))
    user = cur.fetchall()
    gbot.messages.send(peer_id=user[0][0], message=msg, random_id=random.randint(0, 200000))
    gbot.messages.send(peer_id=vk_id, message=u'Сообщение отправлено', random_id=random.randint(0, 200000))


def mass_mesg(vk_id, payload, gbot):
    if vk_id not in admin_ids:
        gbot.messages.send(peer_id=vk_id, message=info_message, random_id=random.randint(0, 200000))
        return
    conn = mysql.connector.connect(user=sql_user, password=sql_pass, host=sql_host, database=sql_base)
    cur = conn.cursor()
    cur.execute('SELECT `id` FROM `users`', ())
    users = cur.fetchall()
    for user in users:
        gbot.messages.send(peer_id=user[0], message=payload, random_id=random.randint(0, 200000))


def get_stat(vk_id, payload, gbot):
    if vk_id not in admin_ids:
        gbot.messages.send(peer_id=vk_id, message=info_message, random_id=random.randint(0, 200000))
        return
    conn = mysql.connector.connect(user=sql_user, password=sql_pass, host=sql_host, database=sql_base)
    cur = conn.cursor()
    cur.execute('SELECT `id`, `id_next`,`id_prev` FROM `users`', ())
    users = cur.fetchall()
    #conn.commit()
    a = [0,0]
    mas = [[],[]]
    for user in users:
        sex = requests.get('https://api.vk.com/method/users.get?user_id={0}&v=5.52&fields=sex'.format(user[0])).json()['response'][0]['sex']
        a[sex-1] += 1
        if sex == 2:
            mas[0].append(user)
        else:
            mas[1].append(user)
    gbot.messages.send(peer_id=vk_id, message='Зарегистрировано всего: '+str(a[0]+a[1]), random_id=random.randint(0, 200000))
    gbot.messages.send(peer_id=vk_id, message='Зарегистрировано девушек: '+str(a[0]), random_id=random.randint(0, 200000))
    gbot.messages.send(peer_id=vk_id, message='Зарегистрировано парней: '+str(a[1]), random_id=random.randint(0, 200000))


def start_game(vk_id, payload, gbot):
    if vk_id not in admin_ids:
        gbot.messages.send(peer_id=vk_id, message=info_message, random_id=random.randint(0, 200000))
        return
    conn = mysql.connector.connect(user=sql_user, password=sql_pass, host=sql_host, database=sql_base)
    cur = conn.cursor()
    cur.execute('SELECT `id`, `id_next`,`id_prev` FROM `users`', ())
    users = cur.fetchall()

    mas = [[],[]]
    for user in users:
        sex = requests.get('https://api.vk.com/method/users.get?user_id={0}&v=5.52&fields=sex'.format(user[0])).json()['response'][0]['sex']
        if sex == 2:
            mas[0].append(user)
        else:
            mas[1].append(user)

    if len(mas[0]) > len(mas[1]):
        mas[0], mas[1] = mas[1], mas[0]

    final_mas = []
    for i in xrange(len(mas[1])):
        if i < len(mas[0]):
            final_mas.append(mas[0][i][0])
        final_mas.append(mas[1][i][0])
    for i in xrange(len(final_mas)):
        conn = mysql.connector.connect(user=sql_user, password=sql_pass, host=sql_host, database=sql_base)
        cur = conn.cursor()
        cur.execute('UPDATE `users` set `id_next`=%s WHERE `id`=%s', (final_mas[(i+1)%len(final_mas)],final_mas[i]))
        cur.execute('UPDATE `users` set `id_prev`=%s WHERE `id`=%s', (final_mas[i],final_mas[(i+1)%len(final_mas)]))
        conn.commit()

    #conn = mysql.connector.connect(user=sql_user, password=sql_pass, host=sql_host, database=sql_base)
    #cur = conn.cursor()
    #cur.execute('SELECT `id`, `id_next` FROM `users`', ())
    #users = cur.fetchall()
    #for user in users:
    #    msg = u'Игра началась. Надо сделать подарок для vk.com/id' + unicode(user[1])
    #    cur.execute('SELECT `group` FROM `users` WHERE `id`=%s', (user[1],))
    #    user1 = cur.fetchall()
    #    if user1[0][0] != '' :
    #        msg += u' из группы ' + unicode(user1[0][0])
    #    gbot.messages.send(peer_id=user[0], message=msg, random_id=random.randint(0, 200000))


def no_action(vk_id, payload, gbot):
    a=0


def parse_message(msg):
    msg = lower(msg)
    if msg[0] == '!':
        return split(msg[1:], None, 1)
    elif msg[0] == '/':
        return [u'self_message', '']
    else:
        return [u'***', '']


commands = ((u'инфо',show_info),
            (u'self_message',no_action),
            (u'группа',set_group),
            (u'стат',get_stat),
            (u'получателю',write_recv),
            (u'санте',write_ts),
            (u'мм',mass_mesg),)


def run_msg(mesg, gbot):
    if (mesg[0] != 4):
        return
    res = parse_message(mesg[6])
    for command in commands:
        if (res[0] == command[0]):
            try:
                command[1](mesg[3], res[1] if len(res)>1 else None, gbot)
                return

            except Exception as error:
                err_m = u'Что то пошло не так. Попробуйте повторить запрос или свяжитесь с администратором'
                gbot.messages.send(peer_id=mesg[3], message=err_m, random_id=random.randint(0, 200000))
                print(error)
    gbot.messages.send(peer_id=mesg[3], message=info_message, random_id=random.randint(0, 200000))
