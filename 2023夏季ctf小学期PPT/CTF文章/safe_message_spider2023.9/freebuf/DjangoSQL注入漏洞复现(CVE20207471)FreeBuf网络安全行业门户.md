## **漏洞简介：**

Django是高水准的由Python编程语言驱动的一个开源Web应用程序框架，起源于开源社区。使用Django，程序员可以方便、快捷地创建高品质、易维护、数据库驱动的应用程序，应用广泛。2月11日，绿盟科技监测发现此漏洞PoC已公开，请相关用户尽快升级Django至修复版本，修复此漏洞。

## **威胁类型**

SQL注入

## **威胁等级**

高

## **漏洞编号**

CVE-2020-7471

## **受影响系统及应用版本**

### 受影响版本：

Django 1.11.x

Django 2.2.x

Django 3.0.x

Django 主开发分支

### 不受影响产品版本

Django 1.11.28

Django 2.2.10

Django 3.0.3

## **漏洞复现：**

******搭建环境**

**(kali)安装 django 漏洞版本（测试使用版本为3.0.2）**

**使用pip命令安装**

    
    
    pip3 install django==3.0.2

**安装postgres 数据库**

    
    
    Sudo spt-get install postgresql postgresql-client

**初次安装postgres 数据库，系统会创建一个数据库超级用户 postgres，密码为空。使用命令（sudo -i -u
postgres）进入postgres数据库，并创建测试数据库（test）。**

    
    
    sudo /etc/init.d/postgresql start
    
    sudo -i -u postgres
    
    psql

**![](https://image.3001.net/images/20200803/1596432308.png!small)**

![](https://image.3001.net/images/20200803/1596432318.png!small)

**下载CVE-2020-7471到本地**

    
    
    git clone <https://github.com/SNCKER/CVE-2020-7471>.git

**()  
![](https://image.3001.net/images/20200803/1596432594.png!small)**

******修改配置文件**
**![](https://image.3001.net/images/20200803/1596432614.png!small)**

**利用CVE中的代码初始化测试数据库test中的表**

    
    
    python3 manage.py migrate

![](https://image.3001.net/images/20200803/1596432627.png!small)**这里No
changes可以不用在意**

    
    
    python3 manage.py migrate vul_app

![](https://image.3001.net/images/20200803/1596432642.png!small)**初始化环节全部完成**

****

### **2** **、攻击环节**

**进入数据库：**
**![](https://image.3001.net/images/20200803/1596432860.png!small)**

**\d** **看一下数据库中所有的表**
**![](https://image.3001.net/images/20200803/1596432876.png!small)**

**执行poc代码生成内容：**

    
    
    Python3 CVE-2020-7471.py

![](https://image.3001.net/images/20200803/1596432922.png!small)**查询：**

    
    
    select*fromvul_app_info;

**  
![](https://image.3001.net/images/20200803/1596432932.png!small)**

**注入成功！**

## **2** **、修复建议**

Django 官方已经发布新版本修复了上述漏洞，请受影响的用户尽快升级进行防护。

**Django 1.11.28下载地址：**

    
    
    https://www.djangoproject.com/m/releases/1.11/Django-1.11.28.tar.gz

**Django 2.2.10 下载地址**

    
    
    https://www.djangoproject.com/m/releases/2.2/Django-2.2.10.tar.gz

**Django 3.0.3下载地址：**

    
    
    https://www.djangoproject.com/m/releases/3.0/Django-3.0.3.tar.gz

参考链接：<https://github.com/SNCKER/CVE-2020-7471>

<https://blog.csdn.net/qq_41260930/article/details/104303146>

