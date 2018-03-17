#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import sys
import json
import urllib.request
import urllib.parse
from urllib.error import URLError
from http.cookiejar import CookieJar
user = 'Admin'
password = 'zabbix'
hostgroup_list = [
  "恒信linux服务器",
  "恒信windows服务器",
  "高创内网服务器"
]
url = "http://192.168.3.204/zabbix/api_jsonrpc.php"
graph_url = "http://192.168.3.204/zabbix/chart2.php?graphid={}&period=86400&width=1782&height=150"
login_url = "http://192.168.3.204/zabbix/index.php"
header = {"Content-Type":"application/json", 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}

"""auth_data ={
  "jsonrpc": "2.0",
  "method": "user.login",
  "params": {
      "user": "Admin",
      "password": "zabbix"
  },
"id": 1,
"auth": None
}

hostgroup_data ={
"jsonrpc": "2.0",
"method": "hostgroup.get",
"params": {
    "output": [
		 "groupid",
	    "name"
	 ],
    "filter": {
        "name": [
            "恒信linux服务器",
            "恒信windows服务器",
            "高创内网服务器"
        ]
    }
},
#  "auth": "6f38cddc44cfbb6c1bd186f9a220b5a0",
  "id": 1
}"""

def postRequest(data):
    request = urllib.request.Request(url, json.dumps(data).encode())
    for k,v in header.items():
        request.add_header(k,v)
    try:
        result = urllib.request.urlopen(request)
    except URLError as e:
        if hasattr(e, 'reason'):
            print("Reason:{}".format(e.reason))
        if hasattr(e, 'code'):
            print("Code:{}".format(e.code))
    else:
        response = json.loads(result.read().decode())
        result.close()
        return response
    return

def userLogin(user, password):
    data ={
      "jsonrpc": "2.0",
      "method": "user.login",
      "params": {
          "user": user,
          "password": password
      },
      "id": 1,
      "auth": None
    }
    response = postRequest(data)
    return response["result"]

def getHostGroupId(token):
    data = {
      "jsonrpc": "2.0",
      "method": "hostgroup.get",
      "params": {
          "output": [
             "groupid",
             "name"
          ],
          "filter": {
              "name": hostgroup_list,
          }
      },
      "auth": token,
      "id": 1
    }
    # {'result': [{'groupid': '8', 'name': '恒信linux服务器'}, {'groupid': '9', 'name': '恒信windows服务器'}, {'groupid': '12', 'name': '高创内网服务器'}], 'jsonrpc': '2.0', 'id': 1}
    response = postRequest(data)
    return [group["groupid"] for group in response["result"]]

def getHostId(token, groupids, name):
    data = {
      "jsonrpc": "2.0",
      "method": "host.get",
      "params": {
          "output": [
              "hostid",
              "host",
              "name",
           ],
           "groupids": groupids,
           "selectGroups": ["groupid", "name"],
      },
      "auth": token,
      "id": 1
    }
    response = postRequest(data)
    for host in response["result"]:
        if host["name"] == name:
            host_id = host["hostid"]
    return host_id

def getItemId(token, hostid):
    data = {
      "jsonrpc": "2.0",
      "method": "item.get",
      "params": {
          "output": [
              "itemid",
              "key_",
              "name",
          ],
          "hostids": "10105",
          "sortfield": "name"
      },
      "auth": token,
      "id": 1
    }
    response = postRequest(data)
    return [item["itemid"] for item in response["result"]]

def getGraphId(token, hostid):
    data = {
      "jsonrpc": "2.0",
      "method": "graph.get",
      "params": {
          "output": "graphid",
#          "itemids": itemids,
#			 "selectItems": ["key_"],
          "hostids": hostid,
          "sortfield": "name"
      },
      "auth": token,
      "id": 1
    }
    response = postRequest(data)
#    print(response["result"])
    return {"_".join(graph["name"].split()):graph["graphid"] for graph in response["result"]}

def getGraphUrl(graphid_dict):
    graph_url_dict = {}
    for graphname,graphid in graphid_dict.items():
        graph_url_dict[graphname] = graph_url.format(graphid)
    return graph_url_dict

def downloadGraph(name,url):
#    print(url)
    if "/" in name:
        name = name.replace("/","")
    if name.endswith("_"):
        name = name + "root"
#    print(name)
    data = urllib.request.urlopen(url).read()
    path = "/".join([os.path.dirname(os.path.abspath(__file__)), "img"])
    filename = "{}.png".format(name)
    if not os.path.isdir(path):
        os.makedirs(path)
    with open("/".join([path,filename]), 'wb') as f:
        f.write(data)

def loginZabbix(user, password):      # 下载图片时，需要先模拟登陆zabbix，否则会没有权限
    data = {
        "name": user,
        "password": password,
        "autologin": 1,
        "enter": "Sign in"
    }
    # 设置一个cookie处理器，它负责从服务器下载cookie到本地，并且在发送请求时带上本地的cookie
    cj = CookieJar()
    cookie_support = urllib.request.HTTPCookieProcessor(cj)
    opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)
    urllib.request.install_opener(opener)
    # 打开登录主页面（他的目的是从页面下载cookie，这样我们在再送post数据时就有cookie了，否则发送不成功）
    h = urllib.request.urlopen(login_url)
    post_data = urllib.parse.urlencode(data).encode('utf-8')
    # 通过urllib2提供的request方法来向指定Url发送我们构造的数据，并完成登录过程
    request = urllib.request.Request(login_url, post_data)
    response = urllib.request.urlopen(request)

if __name__ == '__main__':
    try:
        token = userLogin(user, password)
    except TypeError as e:
        print("ErrorInfo:{}".format(e))
        sys.exit()
    groupids = getHostGroupId(token)
    hostid = getHostId(token, groupids, 'handan-116.251.230.72')
#    print(hostid)
#    itemids = getItemId(token, hostid)
#    print(itemids)
    graphid_dict = getGraphId(token, hostid)
#    print(graphid_dict)
    graphurl_dict = getGraphUrl(graphid_dict)
#    print(graphurl_dict)
    loginZabbix(user, password)
    for name,url in graphurl_dict.items():
        downloadGraph(name,url)
#    hostgroup_info = urlopen(url, hostgroup_data, header)
    
