import sys
import requests
from bs4 import BeautifulSoup as bs
import os
import zipfile
from io import BytesIO


def URLParser(URL: str, RemoveHASH: bool = False) -> dict:
    URL = URL.lower()
    HASHIndex = URL.find("?")
    HASHIndex = HASHIndex if HASHIndex != -1 else 0
    if RemoveHASH & HASHIndex:
        URL = URL[0:HASHIndex]
    # MatchID
    IPreIndex = URL.find("/product/")
    IPostIndex = URL.find("/zh-hant")
    ID = URL[IPreIndex + 9: IPostIndex]
    Type = -1
    if URL.find("emojishop") != -1:
        Type = 1
    if URL.find("stickershop") != -1:
        Type = 2
    return {"ID": ID, "Type": Type}


def HTMLParser(Info: dict) -> dict:
    # Build NAME API
    _API = "https://store.line.me/{Mode}/product/{ID}/en"
    if not Info["Type"]:
        raise "Get ID Failed"
    _Mode = "stickershop" if Info["Type"] == 2 else "emojishop"
    _API = _API.format(Mode=_Mode, ID=Info["ID"])
    # Fetch NAME
    try:
        resp = requests.get(_API)
        soup = bs(resp.text, 'html.parser')
        _Title = soup.find(name='p', class_="mdCMN38Item01Ttl").text
    except requests.exceptions.RequestException as e:
        print(f"Fetch Name Failed\n{e}")
        _Title = "UnknownName"
    return {"Name": _Title, "ID": Info["ID"], "Type": Info["Type"]}


def DownloadZIP(Info: dict, DownloadDIR: str = "./", TmpDIR: str = "./Tmp/", ConvertAnime: bool = True) -> None:
    # APIs
    _API_ANIME_EMOJI = "https://stickershop.line-scdn.net/sticonshop/v1/sticon/{ID}/iphone/package_animation.zip"
    _API_PKG_EMOJI = "https://stickershop.line-scdn.net/sticonshop/v1/sticon/{ID}/iphone/package.zip"

    _API_PKG_STICKER = "http://dl.stickershop.line.naver.jp/products/0/0/1/{ID}/iphone/stickerpack@2x.zip"
    _API_ANIME_STICKER = "http://dl.stickershop.line.naver.jp/products/0/0/1/{ID}/iphone/stickers@2x.zip"

    ID = Info["ID"]
    _Current_PKG_API = _API_PKG_EMOJI if Info["Type"] == 1 else _API_PKG_STICKER
    _Current_ANIME_API = _API_ANIME_EMOJI if Info["Type"] == 1 else _API_ANIME_STICKER
    CurrentPath = os.path.abspath(".")
    TmpDir = CurrentPath + TmpDIR
    FlagAnime = False
    try:
        resp = requests.get(_Current_ANIME_API.format(ID=ID))
        if resp.status_code == 200:
            FlagAnime = True
        if resp.status_code == 404:
            resp = requests.get(_Current_PKG_API.format(ID=ID))
        if resp.status_code == 404:
            print("[ERROR] Get Zip Failed")
        if not (FlagAnime & ConvertAnime):
            with open(DownloadDIR + "/" + Info["Name"] + ".zip", 'wb') as f:
                f.write(resp.content)
        else:
            os.makedirs(TmpDir, exist_ok=True)
            with zipfile.ZipFile(BytesIO(resp.content), "r") as zf:
                zf.extractall(TmpDir)

            # Entrypoint: Change File Extension
            for root, dirs, files in os.walk(TmpDir):
                for file in files:
                    # Delete File if "key" in Filename
                    if "key" in file:
                        os.remove(os.path.join(root, file))
                        continue
                    if file.endswith(".png"):
                        os.rename(os.path.join(root, file), os.path.join(root, file.replace(".png", ".webm")))
            # Entrypoint: Build Zip
            with zipfile.ZipFile(DownloadDIR + "/" + Info["Name"] + ".zip", 'w') as new_zip:
                for root, dirs, files in os.walk(TmpDir):
                    for file in files:
                        new_zip.write(os.path.join(root, file), arcname=os.path.relpath(os.path.join(root, file), TmpDir))

            # Entrypoint: Remove Temp Files
            for root, dirs, files in os.walk(TmpDir):
                for file in files:
                    os.remove(os.path.join(root, file))
            os.rmdir(TmpDir)
    except requests.exceptions.RequestException as e:
        print(f"Download Failed\n{e}")


if __name__ == "__main__":
    # # TmpURL = "https://store.line.me/emojishop/product/6309c424f1289d7e58de7523/zh-Hant"
    # # DownloadZIP(HTMLParser(URLParser(TmpURL, True)), DownloadDIR="./", ConvertAnime=True)
    # # Animation Emoji
    # TmpURL = "https://store.line.me/emojishop/product/65c871dab6eca402da3ffa35/zh-Hant"
    # DownloadZIP(HTMLParser(URLParser(TmpURL, True)), DownloadDIR="./", ConvertAnime=True)
    #
    # # TmpURL = "https://store.line.me/stickershop/product/21802595/zh-Hant?qwqwqwq"
    # # DownloadZIP(HTMLParser(URLParser(TmpURL, True)))

    if len(sys.argv) != 2:
        print("Using: python led.py <url>")
    else:
        DownloadZIP(HTMLParser(URLParser(sys.argv[1], True)), DownloadDIR="./", ConvertAnime=False)
