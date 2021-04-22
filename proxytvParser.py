from ftplib import FTP

from datetime import datetime as dt
from re import sub, findall, MULTILINE
from os import system, name as os_name

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys

clear_cmd = "cls" if os_name == "nt" else "clear"
flag_in = "https://proxytv.ru/iptv/img/flags/"

def get_plist(driver):
    print("Getting a list of playlists...")
    elem = driver.find_element_by_name("udpxyaddr")
    elem.send_keys("plist"+Keys.RETURN)
    elem.clear()
    while flag_in not in driver.page_source:
        pass
    return findall(r"плейлист \"(.*)\"", driver.page_source)


def get_channels_plist(driver, plist_names=[]):

    no_result = "Поиск по запросу не дал результата!"
    q_elem = driver.find_element_by_name("udpxyaddr")
    channels_pages = ""
    plc = len(plist_names)
    print(f"Started crawling {plc} playlists.")
    for i, v in enumerate(plist_names, 1):
        q_elem.send_keys("pl:"+v+Keys.RETURN)
        q_elem.clear()
        html = driver.page_source
        while flag_in not in html and no_result not in html:
            html = driver.page_source
        channels_pages += html
        print("Playlists:", v, f"{i}/{plc}")

    print(f"Finished crawling {plc} playlists")

    return ("#EXTM3U list-autor=\"PTP\"",)+tuple(findall(r"#EXTINF:.*:\d+",
                                                         channels_pages,
                                                         flags=MULTILINE))

def clear_parsed(rslt):
    return sub(r"<.*?>", "", "\n".join(rslt)
               .replace("<br>", "\n")
               .replace("ProxyBot", "PTP"))


driver = None
fn = "all.m3u8"

ftp_user = FTP("ftp.drivehq.com")
ftp_user.login("jigifaj653", "G4BqQQXrs96mnve")
ftp_user.cwd("wwwhome")

try:

    system(clear_cmd)
    print("Creating a browser...")
    options = Options()
    options.headless = True
    driver = Firefox(options=options)
    print("Browser created")
    print("Sending a request...")
    driver.get("https://proxytv.ru/")
    print("Request sent.")

    while True:
        with open(fn, "w", encoding="UTF-8") as f:
            f.write(clear_parsed(get_channels_plist(driver, get_plist(driver))))
        print("Uploading to FTP...")
        with open(fn, "rb") as fp:
            ftp_user.storbinary(f"STOR {fn}", fp)
        print(dt.now(), "Last updated.")

except Exception:
    pass
finally:
    if driver:
        driver.close()
    if os_name == "nt":
        system("pause")

    else:
        input("Press Enter to exit.")
