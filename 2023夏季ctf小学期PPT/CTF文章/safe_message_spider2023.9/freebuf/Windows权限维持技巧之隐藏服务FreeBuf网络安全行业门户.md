## 0x01注册服务

将后门注册为windows自启动服务是常见的后门维持手法，使用命令sc或者powershell命令都可以将自己的后门程序注册为自启动服务。

使用sc命令将后门程序注册为自启动服务，并以LocalSystem的身份运行：

![1604049689_5f9bdb19171b9d0f9023f.png!small?1604049688589](https://image.3001.net/images/20201030/1604049689_5f9bdb19171b9d0f9023f.png!small?1604049688589)

手动启动服务或重启计算机，后门执行。虽然手动执行时提示启动失败，但实际上后门已经成功执行：

![1604049810_5f9bdb927915655f79bad.png!small?1604049810024](https://image.3001.net/images/20201030/1604049810_5f9bdb927915655f79bad.png!small?1604049810024)

msf成功建立新会话，查看权限为system

![1604049598_5f9bdabec5d50ebdfc63a.png!small?1604049598411](https://image.3001.net/images/20201030/1604049598_5f9bdabec5d50ebdfc63a.png!small?1604049598411)

虽然成功实现了服务自启动，但是这个权限维持的方法很容易被检测。因为创建新的服务后可以检索到这个服务，如果防御者看到名字不熟悉的服务就会怀疑这是恶意的服务。通过sc命令或者get-service命令可以查看该服务的信息。

使用sc查看指定名字的服务信息状态：

![1604050191_5f9bdd0f542befeadc55e.png!small?1604050190893](https://image.3001.net/images/20201030/1604050191_5f9bdd0f542befeadc55e.png!small?1604050190893)

或使用sc命令查看服务的配置信息，后门文件直接保留：

![1604050291_5f9bdd7361101f06eb3ee.png!small?1604050290923](https://image.3001.net/images/20201030/1604050291_5f9bdd7361101f06eb3ee.png!small?1604050290923)

使用powershell中的get-service 也可以查看服务信息

![1604050145_5f9bdce15e9a1d51c6e59.png!small?1604050144925](https://image.3001.net/images/20201030/1604050145_5f9bdce15e9a1d51c6e59.png!small?1604050144925)

## 0x02 隐藏服务

为了不被防御者发现用于权限维持的服务，可以考虑将服务隐藏。[Joshua
Wright](https://www.sans.org/profiles/joshua-wright?msc=blog-author)提供了一种方法，通过SDDL(安全描述符语言)修改服务的安全描述符，文章附在文末的参考文献中。Windows系统中服务和文件一样，都使用了安全描述符(SD)配置该安全对象对于哪些访问对象都允许哪些权限。

[Joshua Wright](https://www.sans.org/profiles/joshua-wright?msc=blog-author)提供的方法使用sc 命令的sdset模块可以修改服务的安全描述符，命令如下:

    
    
    sc.exe sdset test "D:(D;;DCLCWPDTSD;;;IU)(D;;DCLCWPDTSD;;;SU)(D;;DCLCWPDTSD;;;BA)(A;;CCLCSWLOCRRC;;;IU)(A;;CCLCSWLOCRRC;;;SU)(A;;CCLCSWRPWPDTLOCRRC;;;SY)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)S:(AU;FA;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;WD)"

![1604052014_5f9be42e37933d4261505.png!small?1604052013754](https://image.3001.net/images/20201030/1604052014_5f9be42e37933d4261505.png!small?1604052013754)

再次使用get-service命令查看服务信息，服务不存在

![1604052043_5f9be44b91a64f8087037.png!small?1604052043129](https://image.3001.net/images/20201030/1604052043_5f9be44b91a64f8087037.png!small?1604052043129)

使用sc.exe查看服务信息拒绝访问

![1605451222_5fb13dd633ac752195041.png!small?1605451223148](https://image.3001.net/images/20201115/1605451222_5fb13dd633ac752195041.png!small?1605451223148)

使用sc.exe查询所有服务信息并过滤名为“test”的服务，结果为空

![1605451153_5fb13d9108b4a909c0061.png!small?1605451153276](https://image.3001.net/images/20201115/1605451153_5fb13d9108b4a909c0061.png!small?1605451153276)

## 0x03 原理

### SDDL

Windows服务支持使用安全描述符定义语言（Security Descriptor Definition Language |
SDDL）控制服务权限的功能。通过修改SDDL可以修改对象（文件或者服务）的DACL（自主访问控制列表），从而修改用户对对象的访问控制。通过对服务的SDDL进行编辑，拒绝所有用户对该服务的读取权限，即实现服务隐藏的效果。

SDDL语法：

    
    
    符号描述
    
    O: -  Owner
    G: -  Primary Group
    D: -  Discretionary ACL (DACL) 
    S: -  System ACL (SACL) 
    
    ACE 类型描述
    
    A: -  Access Allowed
    D: -  Access Denied
    OA: - Object  Access Allowed
    OD: - Object  Access Denied
    AU: - System Auidt
    AL: - System Alarm
    OU: - System Object Audit
    OL: - System Object Alarm
    ML: - System MAndatory Label
    
    服务相关符号权限
    
    CC：- 服务配置查询
    LC: - 服务状态查询
    SW: - SERVICE_ENUMERATE_DEPENDENTS
    RP: - 服务启动
    WP: - 服务停止
    DT: - 服务暂停
    DC: - 服务配置更改
    
    SD: - 删除
    
    继承标志位
    OI：- 表示该ACE可以被子对象继承
    CI：- 表示该ACE可以被子容器继承
    IO：- 仅作用于子对象
    NP：- 仅被直接子容器继承，不继续向下继承
    
    对象
    
    "IU"：- 交互登陆用户
    
    "AU"：- 认证用户
    
    "SU"：- 服务登陆用户
    
    
    
    
    格式(允许/拒绝;继承;权限列表;;对象)

使用powershell 命令查看文件夹的SSDL：

get-acl [c:\windows] | fl

![image.png](https://image.3001.net/images/20201030/1604071890.png!small)

那么分析之前隐藏服务的命令，隐藏服务主要用到的SDDL为：

    
    
    D:(D;;DCLCWPDTSD;;;IU)  //拒绝交互登陆用户的服务配置、查询、状态查询、暂停和删除权限  
    (D;;DCLCWPDTSD;;;SU)    //拒绝登陆用户的服务配置、查询、状态查询、暂停和删除权限  
    (D;;DCLCWPDTSD;;;BA)    //拒绝认证用户的服务配置、查询、状态查询、暂停和删除权限

### 组策略实现服务隐藏

在了解了原理之后，发现实际隐藏服务的操作实际是修改服务权限，使服务对所有用户的查询等权限拒绝。

在【组策略管理编辑器->计算机配置->策略->Windows配置->安全设置->系统服务】中同样可以修改服务的权限

通过组策略编辑器取消所有用户对服务DHCP Client 服务的读取权限

![image.png](https://image.3001.net/images/20201030/1604071891.png!small)

使用get-service 查看DHCP Client 查看该服务，发现服务不存在

![image.png](https://image.3001.net/images/20201030/1604071893.png!small)

## 0x04 防御

在通过本文的方法隐藏后，下列方法都无法查询到服务的信息

    
    
    PS C:\WINDOWS\system32> Get-Service | Select-Object Name | Select-String -Pattern 'test'
    PS C:\WINDOWS\system32> Get-WmiObject Win32_Service | Select-String -Pattern 'test'
    PS C:\WINDOWS\system32>sc.exe query | Select-String -Pattern 'test'

如果事先知道服务的名称并拥有服务停止权限，使用Get-Service停止服务会提示无法打开

![image.png](https://image.3001.net/images/20201030/1604071894.png!small)

如果服务不存在，则停止服务时会提示服务不存在

或使用sc查询服务信息，会提示没有权限

![1605455580_5fb14edc4237ffb365921.png!small?1605455580495](https://image.3001.net/images/20201115/1605455580_5fb14edc4237ffb365921.png!small?1605455580495)

但是使用sc查询服务配置信息可以查到，因为没有拒绝用户的服务配置查询权限

![1605455700_5fb14f54eda4364e0cb2a.png!small?1605455701666](https://image.3001.net/images/20201115/1605455700_5fb14f54eda4364e0cb2a.png!small?1605455701666)

上述方法还拒绝了停止权限，因此无法停止，但依然会提示与服务相关的信息

![image.png](https://image.3001.net/images/20201030/1604071895.png!small)

所以为了更好的隐藏服务信息，可以对上述方法的SDDL进行更改，增加查询服务配置信息拒绝项（CC）：

    
    
    sc.exe sdset test "D:(D;;DCLCWPDTSDCC;;;IU)(D;;DCLCWPDTSDCC;;;SU)(D;;DCLCWPDTSDCC;;;BA)(A;;CCLCSWLOCRRC;;;IU)(A;;CCLCSWLOCRRC;;;SU)(A;;CCLCSWRPWPDTLOCRRC;;;SY)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)S:(AU;FA;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;WD)"

## 0x05 还原

通过删除拒绝相关的SDDL语句，即可让服务正常被查询

    
    
    & $env:SystemRoot\System32\sc.exe sdset auto_calc "D:(A;;CCLCSWRPWPDTLOCRRC;;;SY)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCLCSWLOCRRC;;;IU)(A;;CCLCSWLOCRRC;;;SU)S:(AU;FA;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;WD)"

![image.png](https://image.3001.net/images/20201030/1604071896.png!small)

## 0x06 参考文章

> <https://cqureacademy.com/blog/windows-internals/sddl>
>
> <https://www.sans.org/blog/red-team-tactics-hiding-windows-services/>

