### 项目地址

> https://github.com/Cl0udG0d/HXnineTails

### 关于该项目

之前看到很多跟`xray`联动的工具或方法，如`fofa2xray`或者`AWVS2Xray`，前者是将`fofa`搜索到的结果通过`api`使用`xray`进行扫描，后者是开启`xray`被动代理，使用`awvs`爬虫爬取后进行扫描，但两者都有一些不足的地方，如`fofa2xray`需要使用`fofa`的`api`，`awvs`搭建又太重，而且没有域名收集的功能。

由此开发 **花溪九尾**

### 项目简介

 **平凡** , **暴力** , **强大** , **可自行扩展的缝合怪物**

### 功能简介

 **梦幻联动：**

多工具域名收集，页面URL动态爬取，xray漏洞扫描， C段扫描，JS敏感信息提取，Server酱消息推送

该项目中目前集成：[crawlergo](https://github.com/0Kee-Team/crawlergo)，[OneForAll](https://github.com/shmilylty/OneForAll)，[subDomainsBrute](https://github.com/lijiejie/subDomainsBrute)，[Subfinder](https://github.com/projectdiscovery/subfinder)，[Sublist3r](https://github.com/aboul3la/Sublist3r)，[Xray](https://github.com/chaitin/xray)，[JSfinder](https://github.com/Threezh1/JSFinder)，[pppXray](https://github.com/Cl0udG0d/pppXray)，[Server酱](http://sc.ftqq.com/3.version)

下一个想要集成的项目是[ARL资产灯塔系统](https://github.com/TophantTechnology/ARL)

项目的成果在于将这些单独强大的组件融合到一个单一的应用中，适用于SRC批量扫描，CNVD垂直上分等

### 安装

安装`python3`（暂不支持`python2`

下载本项目代码:

> git clone https://github.com/Cl0udG0d/HXnineTails

安装相应的库文件

> pip3 install -r requirements.txt

> 为方便国内用户，在`requirements.txt`第一行使用了阿里云镜像
>
> 如果是国外服务器进行`python`库文件安装，为提速请删除`requirements.txt`第一行

需要安装下列项目，并将路径配置在`config.py`文件中

[谷歌浏览器](https://www.google.com/intl/zh-CN/chrome/)

[Xray](https://github.com/chaitin/xray/releases)（配合高级版食用更佳

[crawlergo](https://github.com/0Kee-Team/crawlergo/releases)

[OneForAll](https://github.com/shmilylty/OneForAll/releases)

[subDomainsBrute](https://github.com/lijiejie/subDomainsBrute)

[subfinder](https://github.com/projectdiscovery/subfinder/releases)

例如在我的个人笔记本电脑上，`config.py`中的路径信息为：

    
    
    '''
    各个项目所在路径：
    '''
    Chrome_Path='C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
    Xray_Path='D:\\Xray\\xray.exe'
    crawlergo_Path='C:\\Users\\Administrator\\Desktop\\test_tools\\crawlergo.exe'
    OneForAll_Path='C:\\Users\\Administrator\\Desktop\\test_tools\\OneForAll-master\\'
    subDomainsBrute_Path='C:\\Users\\Administrator\\Desktop\\test_tools\\subDomainsBrute-master\\'
    subfinder_Path='C:\\Users\\Administrator\\Desktop\\test_tools\\subfinder\\'
    

在`HXnineTails`文件夹下打开命令行输入扫描参数进行使用

### 使用说明

命令行使用，参数详情为：

    
    
    -h --help 输出帮助信息 如python3 scan.py --help
    -a --attone 对单个URL，只进行crawlergo动态爬虫+xray扫描 例如 百度官网 python3 scan.py -a https://www.baidu.com
    -s --attsrc 对SRC资产，进行信息搜集+crawlergo+xray , 例如 百度SRC python3 scan.py -s baidu.com
    -d --attdetail 对SRC资产,进行信息搜集+crawlergo+xray+C段信息搜集+js敏感信息搜集 , 例如 百度SRC 输入 python3 scan.py -d baidu.com
    -t --thread 线程数量，默认线程为5 如 python3 scan.py -t 10 -a http://testphp.vulnweb.com/ 
    -r 读取待扫描txt文件，每行一个URL 对取出的每个URL进行 -a 扫描，如 python3 scan.py -t 10 -r target.txt
    -c 对保存的漏洞相关报告进行清理，即清理save文件夹下的文件
    

建议使用`-a`或`-s`参数进行扫描

另外有一些全局配置在`config.py`中，可以自行修改，如：

    
    
    SERVERKEY=''
    
    portlist=['80','8080','8000','8081','8001']
    blacklist=["spider","org"]
    
    ThreadNum=5
    PYTHON="python3"
    

`SERVERKEY`是Server酱 你注册使用的`key`值

`portlist`是C段扫描时的默认扫描端口列表

`blacklist`中的字符串，若出现在待扫描URL中，该URL不会被扫描

`ThreadNum`默认的线程数量

`PYTHON`主机python解释器的名称，默认为`python3`

 **上面提到了一些外部程序或配置，如果在你的扫描中不需要用到的话，可以不进行安装，在程序运行过程中会自行pass掉**

### 项目架构

![](https://image.3001.net/images/20210123/1611414044_600c3a1cc040f71b9127a.png!small)

### 使用截图

> python3 scan.py -h

![](https://image.3001.net/images/20210123/1611414045_600c3a1d231d68037f20c.png!small)

项目配置完成后对`http://testphp.vulnweb.com/`进行扫描

> python3 scan.py -t 6 -a http://testphp.vulnweb.com/

![](https://image.3001.net/images/20210123/1611414045_600c3a1d5a2d1318a7ac9.png!small)

漏洞自动合并为一个报告存储在`saveXray`文件夹下

![](https://image.3001.net/images/20210123/1611414045_600c3a1da4107cfbdec25.png!small)

查看去重后的漏洞报告

![](https://image.3001.net/images/20210123/1611414045_600c3a1def82b93aa2430.png!small)

