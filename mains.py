# regbot by kvorder
import hmac
import json
import os
import time
from base64 import b64encode
from hashlib import sha1

import httplib2

import MainTrainer
import requests
import secmail
from bs4 import BeautifulSoup

session = requests.Session()
h = httplib2.Http('.cache')
heads = {
    'Accept-Language': 'en-US',
    'Content-Type': 'application/json; charset=utf-8',
    'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1; LG-UK495 Build/MRA58K; com.narvii.amino.master/3.3.33180)',
    'Host': 'service.narvii.com',
    'Accept-Encoding': 'gzip',
    'Connection': 'Keep-Alive'}


def generate_signature(data) -> str:
    try:
        d = data.encode("utf-8")
    except Exception:
        d = data

    mac = hmac.new(bytes.fromhex("F8E7A61AC3F725941E3AC7CAE2D688BE97F30B93"), d, sha1)
    return b64encode(bytes.fromhex("42") + mac.digest()).decode("utf-8")


def generate_device_id() -> str:
    identifier = os.urandom(20)
    key = bytes.fromhex("02B258C63559D8804321C5D5065AF320358D366F")
    mac = hmac.new(key, bytes.fromhex("42") + identifier, sha1)
    return f"42{identifier.hex()}{mac.hexdigest()}".upper()


def generate_email():
    return secmail.SecMail().generate_email()


def get_link(email):
    try:
        time.sleep(2)
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
        "timestamp": int(time.time() * 1000)
    }
    data = json.dumps(data)
    heads["NDC-MSG-SIG"] = generate_signature(data)
    heads["Content-Length"] = str(len(data))
    heads["NDCDEVICEID"] = deviceId
    response = session.post(f"https://service.narvii.com/api/v1/g/s/auth/register", data=data, headers=heads,
                            verify=True)
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
    heads["NDC-MSG-SIG"] = generate_signature(data)
    response = session.post(f"https://service.narvii.com/api/v1/g/s/auth/request-security-validation", data=data,
                            headers=heads, verify=True)
    if response.status_code != 200:
        print(response.text)


def create_account():
    deviceid = generate_device_id()
    email = generate_email()
    password = "suewq@321Iwq"
    request_verify_code(email=email, deviceId=deviceid)
    url = get_link(email)
    if url == None:
        return
    response = requests.get(url)
    with open("captcha.png", "wb") as file_img:
        file_img.write(response.content)

    vcode = MainTrainer.resolve("captcha.png")

    print(email, password, deviceid)
    print(vcode)
    response = register(nickname="SUPERSUSER", email=email, password=password, deviceId=deviceid,
                        verificationCode=vcode)
    if response == 400:
        print("Incorrect code.")
        return
    elif response == 200:
        with open('../../../internet/accountss.txt', 'a') as file:
            acc_data = f"{email} {password} {deviceid}\n"
            file.write(acc_data)

        print(f"Accounts:\n{email} ...")
    else:
        print(response)


for i in range(5):
    print(i)
    create_account()
