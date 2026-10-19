## 一、工具

PyCharm 2020.3.3 （Community Edition）  
W13scan 主被动式安全扫描器

下载地址：<https://github.com/w-digital-scanner/w13scan>

## 二、Debug方式开启

### 1\. 注

直接运行w13scan.py是无法正确启动该工具的，需要配置一点东西

### 2\. 进行配置

![](https://image.3001.net/images/20210920/1632133029_61485fa5293784a36046f.png!small)

这里用最简单的主动扫描方式进行站点![](https://image.3001.net/images/20210920/1632133161_6148602963d3417908f03.png!small)扫描，该站点是存在备份文件泄露漏洞的。

### 3\. 设置断点

![](https://image.3001.net/images/20210920/1632133231_6148606fe34d82fa2695e.png!small)

### 4\.
点击调试![](https://image.3001.net/images/20210920/1632133269_61486095bb7ea44937322.png!small)

可以看见在控制台中运行了以下代码，其中-u http://www.xxxx.cn便是前面设置的参数：

    
    
    E:\python\python.exe "E:\PyCharm Community Edition 2020.3.3\plugins\python-ce\helpers\pydev\pydevd.py" --multiproc --qt-support=auto --client 127.0.0.1 --port 32300 --file E:/xxxxxxx/W13SCAN/w13scan.py -u http://www.xxxx.cn

## 三、分析过程

### 1\. 实例化两个对象KB、conf

注：class AttribDict(dict):

![](https://image.3001.net/images/20210920/1632133353_614860e95427836af3463.png!small)

### 2\. 按F7继续

进入main函数，第一步就是version_check()函数  
函数作用：该工具集成了sqlmap，故要支持sqlmap，则python版本需>=3.6。

### 3\. F7继续

进入root =
modulePath()，经过函数内部一系列处理得到入口文件路径![](https://image.3001.net/images/20210920/1632133438_6148613e3cc9f93cc1b55.png!small)

### 4\. F7继续

进入cmdline =
cmd_line_parser()，该函数解析了命令行携带的参数![](https://image.3001.net/images/20210920/1632133479_61486167b211ff3cb9c7a.png!small)

### 5\. F7继续

进入init(root,
cmdline)，目的是初始化执行，如下图可以发现许多功能均已初始化。![](https://image.3001.net/images/20210920/1632133518_6148618e4b85352cb25f3.png!small)

### 6\. F7继续

进入判断，

    
    
    if conf.url or conf.url_file:

此时我们conf实例中url已有值。

### 7\. 判断是单个域名还是一个域名文件

if conf.url:
urls.append(conf.url)![](https://image.3001.net/images/20210920/1632133572_614861c4bd483ed01f0a4.png!small)

if conf.url_file: 不是文件故不符合条件

### 8\.
循环处理域名列表![](https://image.3001.net/images/20210920/1632133723_6148625b760f5bfdc0b44.png!small)

### 9\. 通过域名/IP 尝试访问目标

返回200![](https://image.3001.net/images/20210920/1632133758_6148627ebc1be460ea420.png!small)

### 10\. 对目标进行分析

fake_req = FakeReq(domain, {}, HTTPMETHOD.GET,
"")![](https://image.3001.net/images/20210920/1632133793_614862a14865730031a47.png!small)

### 11\. 启动线程

    
    
    def start():
       run_threads(conf.threads, task_run)

### 12\. 进入漏扫插件

备份好scanners文件夹，我将扫描插件库中除了备份文件扫描插件，其余的都删除，这里三个备份文件扫描插件，分别是：基于文件；常见通用备份文件；基于域名的备份文件。从这三个角度来构造payload可以说是非常全面的。

![](https://image.3001.net/images/20210920/1632133924_61486324aa00485537170.png!small)

### 13\. 在backup_file.py的开头设置断点

开启调试，根据左下角来分析大致流程，![](https://image.3001.net/images/20210920/1632133975_61486357e92e83b6c89fc.png!small)

第一步：进main()![](https://image.3001.net/images/20210920/1632134010_6148637a2d210a7ebd377.png!small)

第二步：root是文件路径，cmdline是命令参数![](https://image.3001.net/images/20210920/1632134032_6148639068b30b659ffaa.png!small)

第三步：执行函数，函数作用是加载漏扫插件![](https://image.3001.net/images/20210920/1632134053_614863a5a2a4ad746ca7c.png!small)

第四步：启动模块，在第三步中函数内部的操作![](https://image.3001.net/images/20210920/1632134073_614863b97f20737808606.png!small)

第五步：加载漏扫插件![](https://image.3001.net/images/20210920/1632134097_614863d1018c5b2062a6c.png!small)

第六步：执行漏扫插件![](https://image.3001.net/images/20210920/1632134116_614863e4927b5c600a190.png!small)

### 14\. 进入漏洞插件类内部

所有的插件都有两个方法：  
def _check(self, content): 对内部的，不需要过于关注  
def audit(self): 对外部的，核心代码

### 15\. 分析payload

1)
基于文件的备份文件:![](https://image.3001.net/images/20210920/1632134188_6148642c4681dcc809cea.png!small)

2) 常见备份文件:

这里list太少了，可以改进一下，读取一个文件进行fuzz。

    
    
    list =['bak.rar', 'bak.zip', 'backup.rar', 'backup.zip', 'www.zip', 'www.rar', 'web.rar', 'web.zip','wwwroot.rar','wwwroot.zip', 'log.zip', 'log.rar']

http://www.xxxx.cn/list[i]

3) 基于域名的备份文件:

可以加一些，如xxxx.cn.rar、www.xxxx.cn.rar  
'http://www.xxxx.cn/cn.rar'  
'http://www.xxxx.cn/cn.zip'  
'http://www.xxxx.cn/xxxx.zip'  
'http://www.xxxx.cn/xxxx.rar'  
'http://www.xxxx.cn/www.rar'  
'http://www.xxxx.cn/www.zip'

### 16\. 最终结果保存在json文件中

![](https://image.3001.net/images/20210920/1632134262_61486476b99f77d8c5c5d.png!small)

  

