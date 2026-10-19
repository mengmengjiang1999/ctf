**实验环境：**

 **web服务端：CentOS7外网+内网 ：192.168.1.13+192.168.52.121**

 **内网主机：客户端Windows Server 2019：192.168.52.12**

 **公网主机：Windows10：192.168.1.2**

服务端打开

![1615288562_604758f2a067110d6b2a0.png!small](https://image.3001.net/images/20210309/1615288562_604758f2a067110d6b2a0.png!small)

编辑frps.ini，输入以下内容

[common]

bind_port = 7000

bind_addr = 0.0.0.0

authenticate_hearbeats = true

authenticate_new_work_conns = true

authenticate_method = token

token = 'Nlz123'

dashboard_port = 7500

dashboard_user = admin

dashboard_pwd = admin888

![1615288581_604759050eaaba35e2275.png!small](https://image.3001.net/images/20210309/1615288581_604759050eaaba35e2275.png!small)

运行frps.ini

![1615288624_6047593018351aaf2ec5e.png!small](https://image.3001.net/images/20210309/1615288624_6047593018351aaf2ec5e.png!small)

然后在内网主机编辑frpc.ini

![1615288631_60475937bb6b022da4942.png!small](https://image.3001.net/images/20210309/1615288631_60475937bb6b022da4942.png!small)

用外网主机Windows10访问：

![1615288638_6047593e45313721a7d45.png!small](https://image.3001.net/images/20210309/1615288638_6047593e45313721a7d45.png!small)

在内网主机执行frpc.ini文件

![1615288645_60475945b12ddaaf47e51.png!small](https://image.3001.net/images/20210309/1615288645_60475945b12ddaaf47e51.png!small)

可以看到上线了

![1615288652_6047594c8b393945d4391.png!small](https://image.3001.net/images/20210309/1615288652_6047594c8b393945d4391.png!small)

用Windows10远程连接内网主机

![1615288663_60475957cb9d6e86bc7bd.png!small](https://image.3001.net/images/20210309/1615288663_60475957cb9d6e86bc7bd.png!small)

