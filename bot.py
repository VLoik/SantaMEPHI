# coding=UTF-8
import vk
import requests
import time
from commands import run_msg
from config import vk_token


def group_auth_vk(token):
    session = vk.Session(access_token=token)
    return vk.API(session, v='5.60')


def user_auth_vk(id, login, passwd, scope):
    session = vk.AuthSession(app_id=id, user_login=login, user_password=passwd, scope=scope)
    return vk.API(session, v='5.60')


def main():
    gbot = group_auth_vk(vk_token)

    print("Ready!")
    while (True):
        try:
            poll = gbot.messages.getLongPollServer()
            r = requests.request("GET", "http://" + poll['server'] + "?act=a_check&key=" + poll['key'] + "&ts=" + str(
                poll['ts']) + "&wait=10&mode=2", timeout=50)
            mesg_poll = r.json()
            for mesg in mesg_poll['updates']:
                run_msg(mesg, gbot)
        except Exception as e:
            print("Error: {0}".format(e))
            time.sleep(4)



if __name__ == '__main__':
    main()