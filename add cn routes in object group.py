# -*- coding: utf-8 -*-
import json
import client as cl
import csv
import requests
from ipaddress import IPv4Network
#from requests.packages.urllib3.exceptions import InsecureRequestWarning
#requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

## 输入相关信息
VCO_URL = ""
username = ""
password = ""
csv_file = "china_ip_list.csv"

# Login
client = cl.VcoRequestManager(VCO_URL, verify_ssl=True)
client.authenticate(username, password, is_operator=False)

result=[]
with open(csv_file, "rt") as f:
    reader = csv.reader(f)
    ## 将文件读取成为字典
    dict_reader = csv.DictReader(f)

    for row in dict_reader:
        dict={}
        for key,value in row.items():
            if value == '':
                dict[key] = None
            else:
                dict[key] = value
        result.append(dict)


all_data=[]
for i in range(0, len(result)):
    ## 获取国内路由网段的IP
    ip = str(result[i]['ip'])
    ## 获取国内路由网段的掩码，并将/24的掩码写法转换成255.255.255.0的写法
    mask = str(IPv4Network("%s/%s" % (result[i]['ip'],result[i]['prefix'])).netmask)
    data_dict = {'ip': ip, 'rule_type': 'prefix', 'mask': mask}
    all_data.append(data_dict)

j = 1
for i in range(0, len(all_data), 255):
    ## 由于一个Group只能添加255个路由条目，因此将所有的路由条目按照每255条拆分出一个Group来
    f = all_data[i:i+255]
    ## 通过API新建Group，并添加255条路由
    res = client.call_api("enterprise/insertObjectGroup",{
        "name": "CN Route Group %s" % j,
        "description": "",
        "type": "address_group",
        "data": f
    })
    print("Success Create CN Route Group %s" % j)
    j = j+1

