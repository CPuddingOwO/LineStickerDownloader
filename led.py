import sys
import requests
from bs4 import BeautifulSoup as bs
import os
import zipfile
from io import BytesIO

from pathlib import Path


class Paths:
    """
    Path Options Class
    """
    # Entrypoints #1: Path Options Class
    TmpPath: Path = Path(Path.cwd().joinpath("./Tmp"))
    SaverPath: Path = Path(Path.cwd().joinpath("./"))

    def __init__(self):
        pass
        # self.TmpPath.mkdir(parents=True, exist_ok=True)
        # self.SaverPath.mkdir(parents=True, exist_ok=True)

    def setTmpPath(self, path: str):
        self.TmpPath = Path(path)

    def setSaverPath(self, path: str):
        self.SaverPath = Path(path)


def URLParser(URL: str, RemoveHASH: bool = False) -> dict:
    """
    URL Parser
    :param URL: ``MUST`` | LINE Product URL ``EmojiShop`` | LINE Product URL ``StickerShop``
    :param RemoveHASH: DEF ``False`` | Boolean | Remove HASH from URL
    :return: ``Dict``: ``ID`` - str, ``Type`` - int (1: Emoji, 2: Sticker)
    """
    # Entrypoints #2: URL Parser
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
    """
    HTML Parser
    :param Info: ``MUST`` | ``Dict``: ``ID`` - str, ``Type`` - int (1: Emoji, 2: Sticker)
    :return: ``Dict``: ``Name`` - str, ``ID`` - str, ``Type`` - int (1: Emoji, 2: Sticker)
    """
    # Entrypoints #3: HTML Parser
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


def DownloadZIP(Info: dict, PathOptions: Paths, RewriteSuffix: str = ".png") -> bool:
    """
    Download ZIP & Rewrite Suffix Name
    :param Info: ``MUST`` | ``Dict``: ID - str, ``Type`` - int (1: Emoji, 2: Sticker)
    :param PathOptions: ``MUST`` | Path Options SMP:`` Paths()``
    :param RewriteSuffix: DEF ``.png`` | Rewrite Suffix Name & Build a New ZIP SMP: .apng
    :return: ``Boolean`` True Success | False Failed
    """
    # Entrypoints #4: Download ZIP & Rewrite Suffix Name
    # APIs
    _API_ANIME_EMOJI = "https://stickershop.line-scdn.net/sticonshop/v1/sticon/{ID}/iphone/package_animation.zip"
    _API_PKG_EMOJI = "https://stickershop.line-scdn.net/sticonshop/v1/sticon/{ID}/iphone/package.zip"

    _API_PKG_STICKER = "https://dl.stickershop.line.naver.jp/products/0/0/1/{ID}/iphone/stickerpack@2x.zip"
    _API_ANIME_STICKER = "https://dl.stickershop.line.naver.jp/products/0/0/1/{ID}/iphone/stickers@2x.zip"

    ID = Info["ID"]
    _Current_PKG_API = _API_PKG_EMOJI if Info["Type"] == 1 else _API_PKG_STICKER
    _Current_ANIME_API = _API_ANIME_EMOJI if Info["Type"] == 1 else _API_ANIME_STICKER
    _Flag_RewriteSuffixName = False
    try:
        # Entrypoint #5: Get Animation Ver ZIP
        resp = requests.get(_Current_ANIME_API.format(ID=ID))
        if resp.status_code == 200:
            _Flag_RewriteSuffixName = True
        # Entrypoint #6: Get Package Ver ZIP
        if resp.status_code == 404:
            resp = requests.get(_Current_PKG_API.format(ID=ID))
        if resp.status_code == 404:
            print("[ERROR] Get Zip Failed")
        if _Flag_RewriteSuffixName & (RewriteSuffix.lower() == ".png"):
            # Entrypoints #7: Save Original Zip
            PathOptions.TmpPath.mkdir(parents=True, exist_ok=True)
            with open(PathOptions.SaverPath.joinpath(Info["Name"] + ".zip"), 'wb') as f:
                f.write(resp.content)
                return True
        else:
            # Entrypoints #8: Extract Zip
            os.makedirs(PathOptions.TmpPath, exist_ok=True)
            with zipfile.ZipFile(BytesIO(resp.content), "r") as zf:
                zf.extractall(PathOptions.TmpPath)

            # Entrypoint #9: Rewrite Suffix Name
            for root, dirs, files in os.walk(PathOptions.TmpPath):
                for file in files:
                    # Delete File if "key" in Filename
                    if "key" in file:
                        os.remove(os.path.join(root, file))
                        continue
                    if not file.endswith(RewriteSuffix):
                        os.rename(os.path.join(root, file), os.path.join(root, file.replace(".png", RewriteSuffix)))

            # Entrypoint #10: Build Zip
            with zipfile.ZipFile(PathOptions.SaverPath.joinpath(Info["Name"] + ".zip"), 'w') as new_zip:
                for root, dirs, files in os.walk(PathOptions.TmpPath):
                    for file in files:
                        new_zip.write(os.path.join(root, file),
                                      arcname=os.path.relpath(os.path.join(root, file), PathOptions.TmpPath))

            # Entrypoint: Remove Temp Files
            for root, dirs, files in os.walk(PathOptions.TmpPath):
                for file in files:
                    os.remove(os.path.join(root, file))
            os.rmdir(PathOptions.TmpPath)
            return True
        print(f"Download Success: {Info['Name']}.zip at {PathOptions.SaverPath.joinpath(Info['Name'] + '.zip')}")
    except requests.exceptions.RequestException as e:
        print(f"Download Failed\n{e}")
        return False


if __name__ == "__main__":
    # Entrypoints #0: New PathsClass
    print(f"Current directory: {Path.cwd()}")
    _PathObject = Paths()
    print(f"Saving Directory: {_PathObject.SaverPath}")
    print(f"Tmp Directory: {_PathObject.TmpPath}")
    if len(sys.argv) != 2:
        print("Using: python led.py <url>")
    else:
        DownloadZIP(HTMLParser(URLParser(sys.argv[1], True)), _PathObject)
