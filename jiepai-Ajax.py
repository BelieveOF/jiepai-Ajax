from urllib.parse import urlencode
import requests
import os
from hashlib import md5
from multiprocessing import Pool



# 先得到一张网页的 内容返回json形式
def get_page(offset):
    params ={
        'offset': offset,
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': '20',
        'cur_tab': '1',
        'from': 'gallery',
    }
    url = "https://www.toutiao.com/search_content/?" + urlencode(params)
    try:
        res1 = requests.get(url)
        if res1.status_code == 200:
            return res1.json()
    except requests.ConnectionError:
        return None

# 返回一个网页中的所有图片url
def get_images(json):
    if json.get('data'):
        for item in json.get('data'):
            title = item.get('title')
            images = item.get('image_list')
            for image in images:
                yield {
                    'image': image.get('url'),
                    'title': title
                }
# 根据提取的url下载图片
def save_image(item):
    if not os.path.exists(item.get('title')):
        os.mkdir(item.get('title'))
    try:
        response = requests.get('http:' +item.get('image').replace('list', 'large'))
        print(response)
        if response.status_code == 200:
            file_path = '{0}/{1}.{2}'.format(item.get('title'),md5(response.content).hexdigest(),'jpg')
            if not os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    f.write(response.content)
            else:
                print("Already Download", file_path)
    except requests.ConnectionError as e:
        print("Failed to Save Image")

# 主方法
def main(offset):
    json = get_page(offset)
    for item in get_images(json):
        print(item)
        save_image(item)


if __name__ == '__main__':
    start = 1
    end = 20
    pool = Pool()
    groups = ([x*20 for x in range(start, end+1)])
    # 利用 map 和 进程池 循环爬取
    pool.map(main, groups)
    pool.close()
    pool.join()
