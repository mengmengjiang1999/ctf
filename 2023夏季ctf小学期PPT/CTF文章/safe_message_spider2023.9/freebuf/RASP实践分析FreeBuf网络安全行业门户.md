## 一、RSAP简介

#### 1\. Waf

简介:
它采用请求特征检测攻击方式,waf和防火墙就好比如一座大厦门口的保安，你要进入大厦,waf和防火墙就会在你进入大厦时进行安检，检查到你携带违禁品，就会把你拦截下来，如果没有那就放你进入，至于你进入大厦后所做的一些行为就不会再去检测。

最近几年，攻击手段开始变得复杂，攻击面也越来越广。传统的安全防护手段，WAF、IDS(入侵检测系统)，大多是基于规则，已经不能满足企业对安全的基本需求。对所有的请求都匹配规则，拖慢服务器性能。

产品形态: 硬件、软件、云。

![](https://image.3001.net/images/20210322/1616342901_60576f758ddb40f8ddbc4.png!small)

#### 2\. RASP

简介:
好比给每个进入大厦的人都配了一名私人保镖，不仅仅是在入口处设置保安检测,当你进入这座大厦后,你的一举一动都会被它监测到,当你要挥起拳头,下一步准备打人时,他就会在你挥拳时把你拦截下来。

只对关键的请求点检测,不是所有请求都匹配所有规则，

产品形态: 软件，运行在应用程序内部，应用程序融为一体，实时监测、阻断攻击，使程序自身拥有自保护的能力。

## 二、功能清单

#### 1\. RASP可以检测那些漏洞

    
    
    攻击类型                  RASP支持               WAF支持 
    跨站脚本（XSS）              ✔ 		             	✔ 
    命令注入 	               	✔ 		            	✔ 
    ShellShock 	            	✔ 		            	✔ 
    未经处理的异常             	✔ 		               ❌ 
    缺少内容类型                 ✔		             	✔ 
    缺少Accept标头             	✔		            	✔ 
    不受支持的方法           	✔ 		            	✔ 
    漏洞扫描 	               	✔		            	✔ 
    方法调用失败               	✔		            	❌ 
    敏感数据泄露               	✔ 		            	❌ 
    

## 三、竞品分析

调研了一些国内做RASP的厂商,详情如下图:  
![](https://image.3001.net/images/20210322/1616342902_60576f760736487bf9826.png!small)

## 四、搭建流程

### 搭建OpenRASP做个小测试,先搭建一个用于测试的靶场,

#### 1\. 搭建测试环境

1、为了简化安装，使用docker方式进行

    
    
    curl -sSL https://get.daocloud.io/docker | sh
    

2、dockers安装mysql数据库

    
    
    docker run --name mysqlserver -e MYSQL_ROOT_PASSWORD=123 -d -i -p 3309:3306  mysql:5.6
    

3、此环境已经上传docker，无需提前下载直接运行即可。

    
    
    docker run --name permeate_test --link mysqlserver:db  -d -i  -p 8888:80 –p 8086:8086 daxia/websafe:latest	
    

4、通过浏览器访问http://localhost:8888，便可以打开安装协议页面，点击我同意此协议，填写安装配置，设置数据库地址为db，安装MySQL数据库时我们已经设置密码为123，这里也填写123，参考页面如下：

![](https://image.3001.net/images/20210322/1616342903_60576f777011877e4fa61.png!small)

![](https://image.3001.net/images/20210322/1616342903_60576f77f1e22bb37d4e0.png!small)

![](https://image.3001.net/images/20210322/1616342904_60576f785c7f025727104.png!small)

#### 2\. 安装OpenRASP

1、安装ES服务

    
    
    docker run --name elasticsearch -d -p 9200:9200 -p 9300:9300 elasticsearch:5.6
    

2、安装mongodb

    
    
    docker run -itd --name mongo -p 27017:27017 mongo 
    

3、下载rasp-cloud

    
    
    wget https://packages.baidu.com/app/openrasp/release/latest/rasp-cloud.tar.gz
    

4、修改配置文件，把127.0.0.1更换为本机IP

    
    
    vim rasp-cloud-2021-02-07/conf/app.conf
    

![](https://image.3001.net/images/20210322/1616342904_60576f78ae8398474d833.png!small)

5、启动后台管理系统

    
    
    ./rasp-cloud-2021-02-07/rasp-cloud -d
    

6、访问后台

    
    
    http://172.26.81.233:8086/
    

![](https://image.3001.net/images/20210322/1616342905_60576f791766f922a9e5c.png!small)

7、点击添加主机,然后选择你对应的语言去下载安装包,我这里是PHP,所以选择PHP服务器.

下载 PHP 安装包

    
    
    curl https://packages.baidu.com/app/openrasp/release/1.3.6/rasp-php-linux.tar.bz2 -o rasp-php-linux.tar.bz2  
    tar -xvf rasp-php-linux.tar.bz2  
    cd rasp-\*/
    

install.php 进行安装

    
    
    ./install.php
    

默认安装路径为 **/opt/rasp** ，可替换为其他路径

    
    
    php install.php -d /opt/rasp --heartbeat 90 --app-id c0c523ce311cef92c6f3e9eee306777c99010ce7 --app-secret 0njm1mPafaCGV3cyY15BnOauu4BeqqlC62auGpU8uJk --backend-url http://172.26.81.223:8086/
    

重启 PHP-FPM 或者 Apache 服务器

    
    
    service php-fpm restart
    
    apachectl -k restart
    

![](https://image.3001.net/images/20210322/1616342905_60576f798a540e65a0870.png!small)

## 五、实践案例

我们的靶场已经添加成功了,现在模拟黑客手段攻击靶场,检测一下OpenRASP的防护能力,这里我用工具burp
suite去扫描我的靶场,可以看到下图扫到了XSS跨站脚本,密码明文传输,SQL注入

![](https://image.3001.net/images/20210322/1616342905_60576f79ef04ac4515524.png!small)

OpenRASP的攻击事件中记录了3334条记录,

![](https://image.3001.net/images/20210322/1616342906_60576f7a552c1b462f6f1.png!small)

漏洞列表中可以看到它拦截到的漏洞,

![](https://image.3001.net/images/20210322/1616342906_60576f7ae87f3189249f6.png!small)

默认是只安装防护插件,还可以下载iast交互式扫描插件,

![](https://image.3001.net/images/20210322/1616342907_60576f7bd227498d06cdc.png!small)

* * *

作者: 陈婷

发布时间:2021年3月21日

