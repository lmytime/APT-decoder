# -*- encoding: utf-8 -*-
'''
@File    :   download.py
@Time    :   2021/12/24 03:16:23
@Author  :   Mingyu Li
@Version :   1.0
@Contact :   lmytime@hotmail.com
'''


def write_log(msg):
    from datetime import datetime
    from datetime import date
    current_day = date.today().strftime("%Y/%m/%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    with open("run.log", 'a') as f:
        f.write(f"{current_day} {current_time}\t {msg}\n")

def download_aptx(id):
    import requests
    url = f"https://www.stsci.edu/jwst/phase2-public/{id}.aptx"
    r = requests.get(url=url, allow_redirects=True)
    if(not r.content.decode("utf-8", "ignore").startswith("<!DOCTYPE HTML")):
        with open(f"aptx-data/{id}.aptx", 'wb') as f:
            f.write(r.content)
        print(f"OK {id}.aptx")
        write_log(f"OK {id}.aptx")
        return True
    else:
        print(f"NO {id}.aptx")
        write_log(f"NO {id}.aptx")
        return False

def extract_aptx(inpfile, outdir):
    from zipfile import ZipFile
    with ZipFile(inpfile, 'r') as zipObj:
        zipObj.extractall(outdir)

if __name__ == "__main__":
    from multiprocessing import Pool

    ids = list(range(0,3000))
    with Pool(processes=6) as p:
        p.map(download_aptx, ids)

    # extract_aptx(f"aptx-data/{id}.aptx", f"aptx-data/{id}")
