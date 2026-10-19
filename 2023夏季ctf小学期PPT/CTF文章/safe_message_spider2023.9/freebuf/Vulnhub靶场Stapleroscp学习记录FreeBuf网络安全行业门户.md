#### 之前曾经做过一遍的靶机，拿来复习一下，有误之处请斧正，感谢各位大佬们

* * *

##### 正文开始

* * *

扫描ip  
![image](https://image.3001.net/images/20220224/1645670445_6216f02dc2bcb940c524e.png!small)

扫描端口

![image](https://image.3001.net/images/20220224/1645670423_6216f01707bf19c97ef1e.png!small)

试试ftp是否开始匿名登录,发现存在一个note文件,没什么有价值的内容

    
    
    ftp 192.168.133.218
    用户名:anonymous
    密码为空
    get 文件名
    

访问80端口直接404

![image](https://image.3001.net/images/20220224/1645670364_6216efdc8b54edb3427f0.png!small)

扫目录发现有两个文件

![image](https://image.3001.net/images/20220224/1645670313_6216efa940dded9716a38.png!small)

下载下来,也没发现什么有价值的内容

刚才扫端口发现`139`时开启的,然后用[enum4linux](https://www.ctolib.com/topics-82798.html)扫描一下SMB的相关信息,发现有两个活动的用户  
![image](https://image.3001.net/images/20220224/1645670275_6216ef83cae0e8887ec9e.png!small)

然后使用`smbclient //192.168.133.218/kathy -I 192.168.133.218 -N`连接对应的用户

![image](https://image.3001.net/images/20220224/1645670245_6216ef653b6d788e4b1af.png!small)

发现有两个目录,分别把里面的文件下载下来  
`get todo-list.txt`

然后登录到另外一个用户`smbclient //192.168.133.218/tmp -I 192.168.133.218 -N`

![image](https://image.3001.net/images/20220224/1645670216_6216ef48466adc03cde7c.png!small)

发现里面有一个名为`ls`的文件,一起下载下来,看了看下载的文件都没什么有用的线索,其中还有一套WordPress的源码,但是里面没有mysql的账号密码...没什么用

最后还剩下一个12380端口,竟然把网站开在这个端口上....

用`nikto`扫一波,发现两个目录

![image](https://image.3001.net/images/20220224/1645670132_6216eef4aced9e981250e.png!small)

访问一下也是没什么反应

扫描结果显示,这个网站上有ssl,那也就说明https是存在的

![image](https://image.3001.net/images/20220224/1645670106_6216eeda1a61c61757121.png!small)

接着访问上面那两个目录  
![image](https://image.3001.net/images/20220224/1645670069_6216eeb5c95eddf79b109.png!small)

第一个会显示一个弹窗如图,然后会重定向到一个网站上

![image](https://image.3001.net/images/20220224/1645670034_6216ee9224ef6d9e0c1a7.png!small)

第二个是一个WordPress的博客

然后顺势的想到用`wpscan`扫描一波,这里要注意一下,因为对应的网站ssl证书有问题,所以需要加上一个`--disable-tls-checks`的参数

扫描发现`https://192.168.133.218:12380/blogblog/wp-content/`存在一个目录遍历

![image](https://image.3001.net/images/20220224/1645670004_6216ee74ced2542def65f.png!small)

挨个目录翻一下

![image](https://image.3001.net/images/20220224/1645669982_6216ee5e054af5012ec1c.png!small)

然后发现一个视频播放器的目录

![image](https://image.3001.net/images/20220224/1645669963_6216ee4b2c602e35c5ef5.png!small)

里面的readme文件,有版本号,直接去searchsploit搜一下

![image](https://image.3001.net/images/20220224/1645669938_6216ee325a6e5acb9ff3d.png!small)

修改对应的exp,添加相应的内容,我们这个是https,所以需要在脚本中添加

    
    
    import ssl 
    ssl._create_default_https_context = ssl._create_unverified_context#取消全局证书验证
    

![image](https://image.3001.net/images/20220224/1645669915_6216ee1b1fe42ca4c319c.png!small)

脚本执行成功后我们去访问upload目录  
`https://192.168.133.218:12380/blogblog/wp-content/uploads/`把里面的对应的图片文件下载下来,查看图片得到mysql账号密码

![image](https://image.3001.net/images/20220224/1645669890_6216ee0264f7c02b1eb49.png!small)

![image](https://image.3001.net/images/20220224/1645669867_6216edeb2389b17a647fc.png!small)

查询数据库

    
    
    show databases;
    show tables;
    select * from wp_users;
    

![image](https://image.3001.net/images/20220224/1645669839_6216edcf830d80da19d79.png!small)

直接扔到网上解密一下

![image](https://image.3001.net/images/20220224/1645669820_6216edbc53a3c0f690900.png!small)

拿到密码登录后台

![image](https://image.3001.net/images/20220224/1645669794_6216eda20bb89d2e325ff.png!small)

适应对应的installed功能把我们的webshell传上去,上传成功之后shell文件放在upload目录下

![image](https://image.3001.net/images/20220224/1645669762_6216ed823f18293081f93.png!small)

在自己本地用nc开启监听,在浏览器里访问

![image](https://image.3001.net/images/20220224/1645669735_6216ed67a5f236a4848dc.png!small)

剩下的提权很难受,提权多次都不成功,后来上网上借鉴了一下大佬的wp,才成功

* * *

`uname -a`

![image](https://image.3001.net/images/20220224/1645669688_6216ed3817d1114b478b2.png!small)

`https://github.com/kkamagui/linux-kernel-exploits`

> 提权脚本下载:https://github.com/offensive-security/exploitdb-bin-> sploits/raw/master/bin-sploits/39772.zip

使用里面的exploit.tar进行提权

    
    
    ./compile.sh
    ./doubleput
    

![image](https://image.3001.net/images/20220224/1645669627_6216ecfb0b423699946af.jpg!small)

拿到root权限.  
END

