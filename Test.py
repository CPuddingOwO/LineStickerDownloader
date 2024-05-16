from led import *

if __name__ == '__main__':
    # TmpURL = "https://store.line.me/emojishop/product/6309c424f1289d7e58de7523/zh-Hant"
    # DownloadZIP(HTMLParser(URLParser(TmpURL, True)), DownloadDIR="./", ConvertAnime=True)
    # Animation Emoji
    TmpURL = "https://store.line.me/emojishop/product/65c871dab6eca402da3ffa35/zh-Hant"
    DownloadZIP(HTMLParser(URLParser(TmpURL, True)), DownloadDIR="./", ConvertAnime=True)

    # TmpURL = "https://store.line.me/stickershop/product/21802595/zh-Hant?qwqwqwq"
    # DownloadZIP(HTMLParser(URLParser(TmpURL, True)))
