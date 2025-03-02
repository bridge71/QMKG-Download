import requests
import re
import os
from bs4 import BeautifulSoup

num = 1
songlist = []
url = 'https://node.kg.qq.com/fcgi-bin/kg_ugc_get_homepage'
param = {
    'outCharset': 'utf-8',
    'from': '1',
    # 'nocache': '', # 换成你自己的 comment: 注释了，好像没影响
    'format': 'json',
    'type': 'get_uinfo',
    'start': str(num),
    'num': '15',
    'share_uid': '', # 换成你要找的那个歌手的
    'g_tk': '5381',
    'g_tk_openkey': '5381'
}
head = {
    'Host': 'node.kg.qq.com',
    'Cookie': '', # 换成你自己的  comment: 好像没影响？
    'Sec-Ch-Ua': '"Chromium";v="111", "Not(A:Brand";v="8"',
    'Accept': 'application/json, text/plain, */*',
    'Sec-Ch-Ua-Mobile': '?1',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.65 Mobile Safari/537.36',
    'Sec-Ch-Ua-Platform': '"Android"',
    'Origin': 'https://static-play.kg.qq.com',
    'Sec-Fetch-Site': 'same-site',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.baidu.com', # 换成你自己的 comment: 好像有就行？ 
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}


username=""
total=0

resp=requests.get(url,params=param,headers=head)
obj1=re.compile(r'.*?"nickname": (?P<nickname>.*?),'
               r'.*?"ugc_total_count": (?P<total>.*?),',re.S)
res1=obj1.finditer(resp.text)
for it in res1:
    username=it.group("nickname")
    total=int(it.group("total"))
resp.close()

print("用户名为：",username)
print("用户作品：",total)
def findsongs(i):
    global songlist

    param['start'] = str(i)
    resp=requests.get(url,params=param,headers=head)
    obj1=re.compile(r'.*?"nickname": (?P<nickname>.*?),'
                r'.*?"ugc_total_count": (?P<total>.*?),',re.S)
    res1=obj1.finditer(resp.text)
    for it in res1:
        username=it.group("nickname")
        total=int(it.group("total"))
    obj2=re.compile(r'.*?"shareid": "(?P<shareid>.*?)".*?"title": "(?P<title>.*?)",',re.S)
    res2=obj2.findall(resp.text)
    songlist += res2
    resp.close()

for i in range(total//15 + 1):
    findsongs(i + 1)

# print(len(songlist))
# for item in songlist:
#     print(item)

def extract_content_between_strings(text, start_string, end_string):
    pattern = re.escape(start_string) + r"(.*?)" + re.escape(end_string)
    match = re.search(pattern, text, re.DOTALL)
    if match:
        content = match.group(1)
        return content
    else:
        return None
    
def download_music(url, save_path, siz):
    response = requests.get(url, stream=True)
    if response.status_code == 200:

        file_size = response.headers.get('Content-Length')

        if file_size is not None:
            print(f"文件大小: {file_size} 字节")
        else:
            print("无法确定文件大小")

        # print(siz, "  ", file_size)
        # print(type(siz))
        # print(type(file_size))

        if str(siz) != file_size:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=128):
                    file.write(chunk)
            print("Download complete!")
    else:
        print("Failed to download music.")

for i in range(len(songlist)):
    base_url="https://node.kg.qq.com/play?s="
    url_first=base_url+str(songlist[i][0])
    print(f"{i + 1}:\t", end='')
    print(f"{songlist[i][1]}".replace("/", "_") + f"\t:{songlist[i][0]}")
    response = requests.get(url_first)

    soup = BeautifulSoup(response.text, 'html.parser')
    script_tags = soup.find_all('script')

    music_url = ""

    for script in script_tags:
        script_content = str(script)
        content = extract_content_between_strings(script_content, "playurl", "playurl_video")
        if content:
            music_url = content[3:-3]
            break
            
    pre = "./music/"
    mypath = pre + f"{songlist[i][1]}.m4a".replace("/", "_")
    is_exists = os.path.exists(mypath)

    if is_exists:  #假设最多两个同名歌曲
        size1 = os.path.getsize(mypath)
        mypath2 = pre + f"{songlist[i][1]}-2.m4a".replace("/", "_")

        if music_url:
            download_music(music_url, mypath2, size1)
        else:
            print(f"{songlist[i][1]}.m4a downlown failed!")
    else:
        if music_url:
            download_music(music_url, mypath, 0)
        else:
            print(f"{songlist[i][1]}.m4a downlown failed!")
