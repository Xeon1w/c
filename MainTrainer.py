import cv2 as cv
import tensorflow as tf
import numpy as np
import os

try:
    from .imageConverter import process
except Exception:
    from imageConverter import process

filenameConvert = "imagesProcessed"

data = tf.keras.datasets.mnist
(x_trainer, y_trainer), (x_tester, y_tester) = data.load_data()


def convert(image):
    listImg = []

    img = cv.imread(image, 0)
    img = img - 255

    cutx = 9999
    cuty = 9999

    cutzx = 0
    cutzy = 0

    imgCopy = img.tolist()

    for i in range(len(imgCopy)):
        if 1 not in imgCopy[i]:
            continue

        if i < cuty:
            cuty = i

        if imgCopy[i].index(1) < cutx:
            cutx = imgCopy[i].index(1)

        if i > cutzy:
            cutzy = i

        val = [j for j in range(len(imgCopy[i])) if imgCopy[i][j]][-1]
        if val > cutzx:
            cutzx = val

    # plt.imshow(img)
    # plt.show()
    img = img[cuty:cutzy, cutx:cutzx]

    # plt.imshow(img)
    # plt.show()

    pth = 0
    plh = int(len(img[0]) / 6)
    imgs = []

    for i in range(6):
        imgs = img[0:-1, pth:pth + plh]
        imgs = cv.resize(imgs, (28, 28), interpolation=cv.INTER_AREA)
        listImg.append(imgs)
        # plt.imshow(imgs)
        # plt.show()

        pth += plh

    return listImg


def convert_image(image):
    process(image, f"{filenameConvert}/processed.png", 60)
    values = convert(f"{filenameConvert}/processed.png")
    return np.array(values)


def get_data_set(dir="cset"):
    val_test = []
    val_train = []

    for elem in os.listdir(dir):
        val_test.append(convert(f"{dir}/{elem}"))
        val = elem.replace(".png", "").replace("", " ").split()
        val_train.append([np.uint8(int(iter)) for iter in val])

    val_test = np.array(val_test)
    val_train = np.array(val_train)

    return val_test, val_train


def generate_data_set(dir="cset"):
    val_test = []
    val_train = []

    for elem in os.listdir(dir):
        val_test.extend(convert(f"{dir}/{elem}"))
        val = elem.replace(".png", "").replace("", " ").split()
        val_train.extend([np.uint8(int(iter)) for iter in val])

    val_test = np.array(val_test)
    val_train = np.array(val_train)

    val_test = np.append(val_test, x_trainer, 0)
    val_train = np.append(val_train, y_trainer, 0)

    return val_test, val_train


def trainer(x_train, y_train):
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Flatten())

    for i in range(2):
        model.add(tf.keras.layers.Dense(128, activation=tf.nn.relu))

    model.add(tf.keras.layers.Dense(10, activation=tf.nn.softmax))
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    os.system("cls")
    model.fit(x_train, y_train, epochs=15)
    model.save("captchat.model")
    return model


def get_model(dataset):
    return tf.keras.models.load_model(dataset)


def resolve(image, dataset="cset"):
    val = convert_image(image)

    try:
        model = get_model("captchat.model")
    except OSError:
        val_test, val_train = generate_data_set(dataset)
        model = trainer(val_test, val_train)

    predictions = model.predict(val)

    val = ""
    for i in range(len(predictions)):
        res = np.argmax(predictions[i])
        val = val + f"{res}"

    return val


if __name__ == "__main__":
    val_test, val_train = generate_data_set()
    model = trainer(val_test, val_train)
    # model = get_model("captchat.model")

    v1 = resolve("890533.png")
    v2 = resolve("062867.png")
    v3 = resolve("captcha.png")
    print("890533 : ", v1)
    print("062867 : ", v2)
    print("298790 : ", v3)
