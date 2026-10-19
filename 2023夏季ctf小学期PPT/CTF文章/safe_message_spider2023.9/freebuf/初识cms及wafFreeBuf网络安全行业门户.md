## **一.CMSmap工具**  

CMSmap是一个Python编写的针对开源CMS（内容管理系统）的安全扫描器，它可以自动检测当前国外最流行的CMS的安全漏洞。

其功能：

1.可以检测网站的cms基本类型，自带wordPress,Joomla与Drupal插件列表，可以检测各种插件；  
2.多线程扫描工具，默认线程数为5；  
3.简单易操场

## 二.Web应用程序防火墙指纹识别工具WAFw00f**

> 本机安装位置：cd C:\Users\MCY\AppData\Local\Programs\Python\Python38-32\Lib\site-> packages\wafw00f

安装教程：如下  
安装环境：python3环境 ----> 使用pip install WAFwoof 直接安装；  
安装成功后，找到其安装目录下，在cmd命令中打开；比如我的  
![image.png](https://image.3001.net/images/20210526/1621998358_60adbb167fb2b8f506cdd.png!small)  
安装完成后就是上图的样子，然后根据提示打开wafw00f目录  
![image.png](https://image.3001.net/images/20210526/1621998389_60adbb35e28fcac7259eb.png!small)  
![image.png](https://image.3001.net/images/20210526/1621998461_60adbb7de6fbc553c22bd.png!small)  
探测web网站是否存在WAF

输入命令 python main.py 网站域名/IP

举例：python main.py www.baidu.com 存在防火墙  
![image.png](https://image.3001.net/images/20210526/1621998506_60adbbaa5e3028c5e00e3.png!small)  
这个网站不存在WAF  
python main.py
http://127.0.0.1/login/![image.png](https://image.3001.net/images/20210526/1621998589_60adbbfdcb5522785ad06.png!small)

