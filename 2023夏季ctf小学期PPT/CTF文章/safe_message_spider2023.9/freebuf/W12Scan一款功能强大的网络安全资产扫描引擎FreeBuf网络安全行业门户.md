**W12是一款功能强大的网络安全资产扫描引擎，它可以自动收集关于分析目标的相关资产信息，以供研究人员分析和使用。**

![1.jpg](https://image.3001.net/images/20190505/1557047309_5ccea80d7900c.jpg!small)

## 工具安装

我们可以使用Docker直接完成分析环境的搭建，操作命令如下：

    
    
    git clone <https://github.com/boy-hack/w12scan>
    
    cd w12scan
    
    docker -composeup –d

环境搭建完成后，我们可以直接在浏览器中访问地址：[http://127.0.0.1:8000](http://127.0.0.1:8000/)。

默认账号和密码均为：boyhack。

下面给出的是W12Scan的Web源程序接口：

![2.png](https://image.3001.net/images/20190505/1557047325_5ccea81d79df8.png!small)

本工具基于Python3+Django+Elasticsearch+Redis构建，并且使用了WebRestful API来添加扫描任务：

![3.png](https://image.3001.net/images/20190505/1557047338_5ccea82a95cf7.png!small)

## 功能介绍

### Web端

1、 功能强大的搜索语句

-搜索内容管理系统、服务、标题、国家地理位置等等，快速寻找相关目标信息：
    
    
    title=“abc”# 从标题中搜索
    
    header=“abc”# 从Http Header中搜索
    
    body=“123”# 从Body搜索
    
    url =“*.baidu.com” # 搜索目标域名”baidu.com”的子域名，”*”为通配符
    
    ip =‘1.1.1.1’ # 搜索IP地址，支持CIDR'192.168.1.0/24'和通配符搜索'192.168.1.*'
    
    port= ‘80’ # 搜索端口号
    
    app =’nginx’ # 搜索程序组件
    
    country= ‘cn’ # 搜索国家编码
    
    service= ‘mysql’ # 搜索服务
    
    bug ='xx' # 搜索可能存在的目标漏洞

2、 自定义资产

-通过自定义配置目标组织的相关域名以及网络资产，W12Scan可以自动搜索对应的资产分析目标。在查看目标分析数据时，程序还会提醒该目标的归属方信息。

3、自动关联

-查看目标详情时，若搜索目标为IP地址，程序会自动关联该IP地址上的所有域名以及子域名。

4、多节点管理

-程序的Web端每隔几分钟会自动检查节点的运行状况，并提供扫描节点数量以及相关日志信息。

5、任务添加接口

-程序自带了基于Web Restful API的任务添加接口，我们可以在Web端或其他应用程序端使用这个接口。

## 扫描客户端

1、PoC概念验证

-接入airbug的API，在线获取和调用最新版本的PoC验证脚本。

2、内置扫描脚本

-程序内置有常用的漏洞验证及扫描服务。

3、扫描任务

-端口扫描任务基于masscan实现，端口识别功能基于nmap实现。

4、分布式支持

-可直接在其他设备上执行扫描任务，也可基于Docker实现分布式扫描。

## Telegram讨论组

Telegram讨论组：【[点我访问](https://t.me/joinchat/MZ16xBd1HRD2Nq_o1T8XIQ)】

### 项目地址

W12Scan：【[GitHub传送门](https://github.com/boy-hack/w12scan)】

***参考来源：[boy-hack](https://github.com/boy-hack/w12scan)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

