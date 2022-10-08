import secmail
from requests import Session
import json
import os
import hmac

import base64
from hashlib import sha1
from nickname_generator import generate
from time import sleep
from bs4 import BeautifulSoup
from time import time as timestamp
from threading import Thread
from PIL import Image
import httplib2

import MainTrainer

val_test, val_train = MainTrainer.generate_data_set()
model = MainTrainer.trainer(val_test, val_train)

session = Session()

h = httplib2.Http('.cache')

PREFIX = bytes.fromhex("42")
SIG_KEY = bytes.fromhex("F8E7A61AC3F725941E3AC7CAE2D688BE97F30B93")
DEVICE_KEY = bytes.fromhex("02B258C63559D8804321C5D5065AF320358D366F")

heads = {
    'Accept-Language': 'en-US',
    'Content-Type': 'application/json; charset=utf-8',
    'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1; LG-UK495 Build/MRA58K; com.narvii.amino.master/3.3.33180)',
    'Host': 'service.narvii.com',
    'Accept-Encoding': 'gzip',
    'Connection': 'Keep-Alive'}


def sig(data: str) -> str:
    data = data if isinstance(data, bytes) else data.encode("utf-8")
    return base64.b64encode(PREFIX + hmac.new(SIG_KEY, data, sha1).digest()).decode("utf-8")


def generate_device(data: bytes = None) -> str:
    if isinstance(data, str): data = bytes(data, 'utf-8')
    identifier = PREFIX + (data or os.urandom(20))
    mac = hmac.new(DEVICE_KEY, identifier, sha1)
    return f"{identifier.hex()}{mac.hexdigest()}".upper()


def gen_email():
    mail = secmail.SecMail()
    email = mail.generate_email()
    return email


def get_message(email):
    try:
        sleep(2)
        mail = secmail.SecMail()
        inbox = mail.get_messages(email)
        for Id in inbox.id:
            msg = mail.read_message(email=email, id=Id).htmlBody
            bs = BeautifulSoup(msg, 'html.parser')
            images = bs.find_all('a')[0]
            url = (images['href'] + '\n')
            if url is not None:
                print(url)
                return url
    except:
        pass


def register(nickname: str, email: str, password: str, deviceId: str, verificationCode: str):
    data = {
        "secret": f"0 {password}",
        "deviceID": deviceId,
        "email": email,
        "clientType": 100,
        "nickname": nickname,
        "latitude": 0,
        "longitude": 0,
        "address": None,
        "clientCallbackURL": "narviiapp://relogin",
        "validationContext": {
            "data": {
                "code": verificationCode
            },
            "type": 1,
            "identity": email
        },
        "type": 1,
        "identity": email,
        "timestamp": int(timestamp() * 1000)
    }
    data = json.dumps(data)
    heads["NDC-MSG-SIG"] = sig(data)
    heads["Content-Length"] = str(len(data))
    heads["NDCDEVICEID"] = deviceId
    response = session.post(f"https://service.narvii.com/api/v1/g/s/auth/register", data=data, headers=heads,
                            timeout=12, verify=True)
    return response.status_code


def request_verify_code(email: str, deviceId: str):
    data = {
        "identity": email,
        "type": 1,
        "deviceID": deviceId
    }
    data = json.dumps(data)
    heads["Content-Length"] = str(len(data))
    heads["NDCDEVICEID"] = deviceId
    heads["NDC-MSG-SIG"] = sig(data)
    response = session.post(f"https://service.narvii.com/api/v1/g/s/auth/request-security-validation", data=data,
                            headers=heads, timeout=12, verify=True)
    if response.status_code != 200:
        print(response.text)


def generate_account(count: int, password: str):
    accounts_list = []

    itteration = 0

    def create_account(itteration):
        deviceid = generate_device()
        email = gen_email()
        request_verify_code(email=email, deviceId=deviceid)
        url = get_message(email)
        if url == None:
            return
        response, content = h.request(url)
        with open("captcha.png", "rb") as file_img:
            file_img.write(content)

        vcode = MainTrainer.resolve("captcha.png")

        print(email, password, deviceid)

        response = register(nickname=generate('en'), email=email, password=password, deviceId=deviceid,
                            verificationCode=vcode)
        if response == 400:
            print("Incorrect code.")
            return
        elif response == 200:
            print()
            with open('../../../internet/accountss.txt', 'a') as file:
                acc_data = f"{email} {password} {deviceid}\n"
                file.write(acc_data)

            accounts_list.append([email, password, deviceid])
            print(f"-- Generated {itteration} Accounts:\n{email} ...")
        else:
            print(response)

    while len(accounts_list) < count:
        itteration += 1
        thread = Thread(target=create_account, args=(itteration,))
        thread.start()
        thread.join()


if __name__ == '__main__':
    password = input("Password for accounts: ")
    count = int(input("How account to generate: "))
    generate_account(count=count, password=password)
