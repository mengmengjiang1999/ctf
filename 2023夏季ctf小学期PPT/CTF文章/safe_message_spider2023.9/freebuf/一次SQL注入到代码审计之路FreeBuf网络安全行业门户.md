***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。** **
**本文中出现的所有敏感信息已做打码处理** **

##  **一、找网站SQL注入点**

 **在测试时后发现有一个信息查询框，就是下面这个图片显示的。一般信息查询框会和数据库存在交互。**

![](https://image.3001.net/images/20200420/1587371246_5e9d5cee9263b.png!small)

我输入数字1，会正常提示木查询到相关信息。

![](https://image.3001.net/images/20200420/1587371507_5e9d5df39fd8e.png!small)

那我们使用1'测试一下，发现不弹未查询到相关信息的提示框，也没有任何数据输出，大致判断这个点存在sql注入，并且不对输出报错信息。

大概猜测出SQL语句为 ：

    
    
    select * from A where id ='$_POST['id']';

没有对用户输入的数据做任何过滤。

构造一个闭合语句再次确认一些是否确认存在sql注入。

payload：1' #

![](https://image.3001.net/images/20200420/1587376279_5e9d709764201.png!small)

通过上面简单测试，已经确定了，肯定存在sql注入。

##  **二、sqlmap跑一下**

将数据包保存到一个文件，直接用sqlmap跑。非常震惊，居然有51个库。

![](https://image.3001.net/images/20200420/1587376339_5e9d70d374e9d.png!small)

经过查询，查到后台的账号密码，那我就开始找后台的艰辛路程了。

##  **三、找后台**

没有找到后台，但是发现robots文件。

![](https://image.3001.net/images/20200420/1587376381_5e9d70fdc9060.png!small)

从robots上看到是PHPCMS系统![](https://image.3001.net/images/20200420/1587376399_5e9d710fc6af4.png!small)

使用PHPCMS系统通用后台地址admin.php，m=admin&c=index&a=login，都不行，测了好就发admin模型下的index控制器是存在，当我们访问的时候就会自动跳到首页，这也该是开发者后来做了修改，专门做防黑的。

##  **四、找通用漏洞**

这个步骤就不多说了，我测了已暴光的漏洞，都是不行，说明开发者还是有安全意识的，把漏洞都给修复了。

##  **五、返回sqlmap**

还有一种思路就是使用sqlmap --os-shell直接获取shell，但是这个基本上不行的，因为网站的文件基本上都是755权限，没有写的权限就会失败。那我还是抱着一丝丝希望去测试了。

使用sqlmap --os-shell需要知道网站的绝对路径，网站绝对路径可以通过中间件配置文件查看。

首先需要知道网站用了什么中间件，我没有用nmap跑，只用404看到是nginx ,nginx的配置文件
/usr/local/nginx/conf/ngixn.conf

用sqlmap --file-read 去读nginx配置文件。通过配置文件只看到一条默认的配置信息

![](https://image.3001.net/images/20200420/1587382310_5e9d8826c173e.png!small)需要注意的是如果在nginx.conf文件没有看到有价值的信息，有一种可能是存在，/usr/local/nginx/conf/vhost/网站域名.conf
这个位置，果不其然就是它。

![](https://image.3001.net/images/20200420/1587382572_5e9d892c8aef2.png!small)找到了真实的路径，就可以使用
sqlmap --os-shell了，但是正式我当时预料的没有写入权限导致拿shell失败。

![](https://image.3001.net/images/20200420/1587382766_5e9d89ee3bb73.png!small)

##  **六、使用sqlmap读取网站源码**

通过上面的思路我们已经知道网站的真实路径，知道了是PHPCMS系统，那我们可以读取网站的文件了。

1、读取路由文件 caches\configs\route.php 查看路由文件没有问题。

![](https://image.3001.net/images/20200420/1587383120_5e9d8b50d432d.png!small)2、查看系统文件
caches\configs\system.php （这个文件能看是否开启了域名访问后台）

![](https://image.3001.net/images/20200420/1587383213_5e9d8bad9b963.png!small)3、在上面我们说到admin模型下index控制器是能访问，知识在访问的时候会跳转到主页，那我们下载index控制器文件看下。
phpcms\modules\admin\index.php ,查看index控制器下的login方法是没有做任何修改的。

![](https://image.3001.net/images/20200420/1587383490_5e9d8cc283807.png!small)

##  **七、侧面渗透测试**

上面说了一共有51个网站，我随机看了几个，数据库的结构是一样的，说明是同一个建站系统。

那我们用nmap扫一下服务发现有8080服务，这个网站8080端口的网站时dedecms系统搭建的，我正好有后台密码，这样能通过dedecms上传文件。

![](https://image.3001.net/images/20200420/1587383995_5e9d8ebb87c3c.png!small)

##  **八、代码审计**

通过上面们大概判断是admin模块index控制器有问题。

查看admin模块多了一个MY_index.php控制器，

![](https://image.3001.net/images/20200420/1587385141_5e9d93353f521.png!small)查看MY_index.php
发现里面有一个构造函数，这个函数大概意思就是会打开这个方法会判断你的right_enter的session值是否为空，若果为空，那么就回到首页，这这是我们刚开始一直打不开后台的原因。

![](https://image.3001.net/images/20200420/1587385220_5e9d9384b06e6.png!small)

经过看phpcms开发手册（我对这看系统二次开发不太熟悉，我只知道是一个MVC结构的php程序），如果需要对控制器进行二次开发需要在同级目录创建一个MY_*.php文件，大概意思就是创建这个文件后程序在运行index模块时会运行MY_index.php里面的代码。

![](https://image.3001.net/images/20200420/1587390357_5e9da795b04c8.png!small)到这了明白了，因为没有$_SESSION['right_enter']值，所以导致登陆不了，所以打开后台首先需要给$_SESSION['right_enter']赋值。经过不懈努力找到了一个正确文件。

![](https://image.3001.net/images/20200420/1587390632_5e9da8a8d7f8f.png!small)

这个文件大概意思就是当我运行改文件时会将$_SESSION['right_enter']=1，然后跳转到登陆界面。

 ***本文作者： lesssafe，转载请注明来自FreeBuf.COM**  
  

