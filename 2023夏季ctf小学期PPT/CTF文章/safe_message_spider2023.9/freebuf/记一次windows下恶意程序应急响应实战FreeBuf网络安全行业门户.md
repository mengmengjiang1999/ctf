本机火绒爆出大量安全日志

![1639754115_61bca983ad4443bc7b7b1.png!small](https://image.3001.net/images/20211217/1639754115_61bca983ad4443bc7b7b1.png!small)

登录10.99.99.160这台pc，发现大量朝445端口的连接

![1639754121_61bca989e583ad31e170d.png!small](https://image.3001.net/images/20211217/1639754121_61bca989e583ad31e170d.png!small)

使用火绒剑查看进程，发现4个恶意进程和进程所在位置

![1639754127_61bca98f6ed70c8054d3a.png!small](https://image.3001.net/images/20211217/1639754127_61bca98f6ed70c8054d3a.png!small)

查看启动项，发现两个恶意启动项

![1639754133_61bca99593f38352e9990.png!small](https://image.3001.net/images/20211217/1639754133_61bca99593f38352e9990.png!small)

查看两个启动项的注册表

发现这两个恶意程序通过注册表自启，删除。

![1639754139_61bca99b6d9b41573d33e.png!small](https://image.3001.net/images/20211217/1639754139_61bca99b6d9b41573d33e.png!small)![1639754139_61bca99ba48e2683653d2.png!small](https://image.3001.net/images/20211217/1639754139_61bca99ba48e2683653d2.png!small)

查看计划任务，发现三个恶意计划任务，删除

![1639754145_61bca9a1a2795fa0e3f14.png!small](https://image.3001.net/images/20211217/1639754145_61bca9a1a2795fa0e3f14.png!small)

再查看有无自启服务，发现一个恶意服务

![1639754150_61bca9a6e60269b687c71.png!small](https://image.3001.net/images/20211217/1639754150_61bca9a6e60269b687c71.png!small)

关闭恶意服务，失败。

查看这一恶意服务的注册表，删除，然后服务可以禁用。

![1639754158_61bca9ae31c496d3164a8.png!small](https://image.3001.net/images/20211217/1639754158_61bca9ae31c496d3164a8.png!small)

目前位置，发现四个恶意程序

    
    
    C:\Windows\Temp\svchost.exe  
    C:\Windows\SysWOW64\drivers\svchost.exe  
    C:\Windows\SysWOW64\drivers\taskmgr.exe  
    C:\Windows\SysWOW64\wmiex.exe

删除四个恶意程序

    
    
    C:\Windows\SysWOW64\drivers\taskmgr.exe  
    C:\Windows\Temp\svchost.exe

这两个无法删除，显示使用中

这边在结束进程，再删除，成功。

发现还是存在大量445连接

![1639754166_61bca9b6b3ada4a0ded54.png!small](https://image.3001.net/images/20211217/1639754166_61bca9b6b3ada4a0ded54.png!small)

tasklist查找，发现还有一个svchost.exe进程，找到文件位置，删除

![1639754172_61bca9bc692c24c38e20c.png!small](https://image.3001.net/images/20211217/1639754172_61bca9bc692c24c38e20c.png!small)

发现无445的连接

![1639754178_61bca9c24d6b6e083e23c.png!small](https://image.3001.net/images/20211217/1639754178_61bca9c24d6b6e083e23c.png!small)![1639754182_61bca9c65cf69bc3aa255.png!small](https://image.3001.net/images/20211217/1639754182_61bca9c65cf69bc3aa255.png!small)

