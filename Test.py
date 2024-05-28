from led import *
from pathlib import Path

if __name__ == '__main__':
    print(f"Current directory: {Path.cwd()}")
    _PathObject = Paths()
    print(f"Saving Directory: {_PathObject.SaverPath}")
    print(f"Tmp Directory: {_PathObject.TmpPath}")


    # TmpURL = "https://store.line.me/emojishop/product/6309c424f1289d7e58de7523/zh-Hant"
    # DownloadZIP(HTMLParser(URLParser(TmpURL, True)), _PathObject)
    # Animation Emoji
    TmpURL = "https://store.line.me/emojishop/product/65c871dab6eca402da3ffa35/zh-Hant"
    DownloadZIP(HTMLParser(URLParser(TmpURL, True)), PathOptions=_PathObject, RewriteSuffix=".abcc", )

    # TmpURL = "https://store.line.me/stickershop/product/21802595/zh-Hant?qwqwqwq"
    # DownloadZIP(HTMLParser(URLParser(TmpURL, True)), _PathObject)
