## 一、前言

**最近在做着一些日志分析的活，刚好看到LogonTracer这款工具，于是就参考着网上仅有的文章去搭建了，搭建过程中会多少遇到一些问题，也就顺手将其记录到这篇文章中了，希望这篇文章能帮助到第一次搭建这款工具的小伙伴。**

LogonTracer这款工具是基于Python编写的，并使用Neo4j作为其数据库（Neo4j多用于图形数据库），是一款用于分析Windows安全事件登录日志的可视化工具。它会将登录相关事件中的主机名（或IP地址）和帐户名称关联起来，并将其以图形化的方式展现出来，使得在日志取证时直观清晰。

## 二、Docker搭建LogonTracer详细过程  

Docker安装过程就略过了。接下来将详细介绍如何使用Docker搭建LogonTracer：

1、开启docker服务

    
    
    service docker start  
    

2、拉取logontracer镜像  

    
    
    docker pull jpcertcc/docker-logontracer  
    

![2.png](https://image.3001.net/images/20191112/1573542562_5dca5aa22ab96.png!small)

3、运行镜像

    
    
    docker run --detach --publish=7474:7474 --publish=7687:7687 --publish=8080:8080 -e LTHOSTNAME=192.168.59.128 jpcertcc/docker-logontracer  
    

（其中LTHOSTNAME值对应修改为本地IP）

![3.png](https://image.3001.net/images/20191112/1573542609_5dca5ad117d74.png!small)

4、连接Neo4j数据库

    
    
    浏览器访问：http://[本地IP地址]:7474  
    

默认账号neo4j/neo4j，接着要求修改密码，输入新密码即可。

![4-1修改Neo4j密码.png](https://image.3001.net/images/20191112/1573542893_5dca5bed5ee3f.png!small)输入完密码连接成功后，在如下图的输入框中输入如下命令，点击右侧的按钮执行。

    
    
    MATCH(n)
    OPTIONAL MATCH (n)-[r]-()
    DELETE n,r  
    

![8-1.png](https://image.3001.net/images/20191112/1573543063_5dca5c97b35ba.png!small)

做到这一步时，可能会遇到即使正确输入默认密码后仍一直提示账号密码错误，这时可以修改neo4j.conf配置文件，取消验证机制，该文件在conf目录下。

    
    
    docker exec -it 7882c4e3dab1 /bin/sh     (其中7882c4e3dab1为容器ID号，通过docker ps -a可查看）  
      
    vi conf/neo4j.conf  
    

找到文件内容：#dbms.security.auth_enabled=false

将前面的#号去掉，修改为dbms.security.auth_enabled=false

（重启镜像才生效，当前可以暂时不重启，因为下面还有需要重启的地方，到时一次重启即可。）  

![5-1修改Neo4j配置文件.png](https://image.3001.net/images/20191112/1573543606_5dca5eb657676.png!small)

5、访问LogonTracer界面  

    
    
    http://[本机IP地址]:8080

此时，通过上述4步之后LogonTracer的Docker环境已经搭建好并可以正常运行，但是，由于打开的页面中有2个JS文件调用的是远程网址，这2个网址由于一些原因在国内无法正常访问，所以，在通过浏览器访问首页后，点击“Upload
Event Log”按钮是无反应的，那就无法上传日志文件，这就是需要解决的坑。

![1-5
问题1上传按钮点击不了.png](https://image.3001.net/images/20191112/1573544470_5dca6216358ae.png!small)

解决这个坑要对2处JS进行修改：

第一处JS：

<https://cdn.rawgit.com/neo4j/neo4j-javascript-driver/1.4.1/lib/browser/neo4j-web.min.js>

解决办法：直接修改系统的hosts文件，手动将域名cdn.rawgit.com解析到151.139.237.11上，该网址就可以正常访问了。

执行命令：

    
    
    vim /etc/hosts
    然后在hosts文件中添加一行：
    151.139.237.11 cdn.rawgit.com  
    

![1-6
修改hosts文件.png](https://image.3001.net/images/20191112/1573544578_5dca6282bf91d.png!small)

第二处JS：

<https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js>

解决方法：进入Docker镜像编辑index.html模板文件。

执行命令：

    
    
    docker exec -it 7882c4e3dab1 /bin/sh (其中7882c4e3dab1为容器ID)   
    

进入Docker镜像的终端内执行命令，编辑模板文件：

    
    
    vi /usr/local/src/LogonTracer/templates/index.html  
    

找到

<https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js>  

![1-8
修改模板文件index.png](https://image.3001.net/images/20191112/1573544890_5dca63baec531.png!small)

将该网址的改为

<https://ajax.loli.net/ajax/libs/jquery/3.2.1/jquery.min.js>

保存文件。

![1-9
（修改后）模板文件index.png](https://image.3001.net/images/20191112/1573544936_5dca63e8e6d43.png!small)

6、重启Docker镜像

    
    
    docker restart 7882c4e3dab1 (其中7882c4e3dab1为容器ID)

![3-1重启docker容器.png](https://image.3001.net/images/20191112/1573545079_5dca6477e9653.png!small)

7、再次访问LogonTracer界面

    
    
    http://[本地IP地址]:8080  
    

点击左侧的“UploadEvent
Log”上传保存在本机的evtx格式或者XML格式的Windows安全日志文件，点击“Browse”选择日志文件，然后点击“Upload”，进行上传。这时候就完美解决了上传按钮点不了的问题了。

![9-1成功上传日志.png](https://image.3001.net/images/20191112/1573545232_5dca6510cdf5f.png!small)

这样就已经成功运行并使用LogonTracer对日志文件进行分析了。  

![10-1图表模型grid.png](https://image.3001.net/images/20191112/1573545301_5dca6555eba54.png!small)

## 三、LogonTracer功能介绍

1、在LogonTracer界面左侧，就是对日志文件进行分析的功能选项。

![4-1功能区.png](https://image.3001.net/images/20191112/1573545551_5dca664f3c7b2.png!small)

All Users：查看所有用户的登录信息

SYSTEM Privileges：查看管理员账号的登录信息（一般登录类型3或10）

NTLM Remote Logon：查看NTLM远程登录信息（登录类型3）

RDP Logon：查看RDP远程桌面登录信息（登录类型10）

Network Logon：查看网络登录信息（登录类型3）

Batch Logon：查看批处理登录信息（登录类型4）

Service Logon：查看服务登录信息（登录类型5）

Ms14-068 Exploit Failure：MS14-068漏洞利用失败信息

Logon Failure:查看登录失败信息

Detect DCsync/DCShadow：查看删除 DCsync/DCShadow信息

Add/Detect Users：查看添加/删除用户信息

Domain Check：域检查信息

Audit Policy Change：查看审计策略变更信息

  

2、在界面右侧，显示着用户名及其重要性等级。

![1-1右侧功能.png](https://image.3001.net/images/20191112/1573545819_5dca675b3a34a.png!small)

对于此排名，LogonTracer会对事件日志图执行网络分析，并根据每个节点的“中心性”创建排名。中心性是指示每个节点与网络中心的接近度的索引。由于被攻击帐户用于对许多主机执行登录尝试，因此它们往往具有更高的中心性。因此，通过比较中心性，可以识别可能受影响的帐户/主机。

对于每个节点，链接到主机（绿点）并带有一行账户信息（红/蓝）表示已使用主机登陆。

> 红色：SYSTEM权限帐户
>
> 蓝色：标准用户帐户
>
> 绿色：主机/ IP地址

附上登录类型说明：

登录类型  
| 类型说明  
  
---|---  
Logon type 2 Interactive  
| 交互式登录（Interactive），就是指用户在计算机的控制台上进行的登录，也就是在本地键盘上进行的登录，是常见的登录方式。  
  
Logon type 3 Network  
|
网络登录（Network），最常见的是访问网络共享文件夹或打印机。另外大多数情况下通过网络登录IIS时也被记为这种类型，但基本验证方式的IIS登录是个例外，它将被记为类型8。  
  
Logon type 4 Batch  
|
批处理（Batch），当Windows运行一个计划任务时，“计划任务服务”将为这个任务首先创建一个新的登录会话以便它能在此计划任务所配置的用户账户下运行，当这种登录出现时，Windows在日志中记为类型4，对于其它类型的工作任务系统，依赖于它的设计，也可以在开始工作时产生类型4的登录事件，类型4登录通常表明某计划任务启动，但也可能是一个恶意用户通过计划任务来猜测用户密码，这种尝试将产生一个类型4的登录失败事件，但是这种失败登录也可能是由于计划任务的用户密码没能同步更改造成的，比如用户密码更改了，而忘记了在计划任务中进行更改。  
  
Logon Type 7 Unlock  
| 解除屏幕锁定（Unlock）  
当用户离开屏幕一段时间后，屏保程序会锁定计算机屏幕。解开屏幕锁定需要键入用户名和密码。此时产生的日志类型就是Type 7。  
  
Logon Type 8 NetworkCleartext  
| 网络明文登录（NetworkCleartext），通常发生在IIS 的 ASP登录，又如FTP。  
  
Logon Type 9 NewCredentials  
| 新凭证（NewCredentials） ，通常发生在RunAS方式（允许用户用其他权限运行指定的工具和程序）运行某程序时的登录验证。  
  
Logon Type 10 RemoteInteractive  
|
远程登录（RemoteInteractive），通过终端服务、远程桌面或远程协助访问计算机时，Windows将记为类型10，以便与真正的控制台登录相区别，注意XP之前的版本不支持这种登录类型，比如Windows2000仍然会把终端服务登录记为类型2，WindowsXP/2003起有Type
10。  
  
Logon Type 11 CachedInteractive  
|
缓存登录，在自己网络之外以域用户登录而无法登录域控制器时使用缓存登录。默认情况下，Windows缓存了最近10次交互式域登录成功的凭证HASH，如果以后当你以一个域用户登录而又没有域控制器可用时，Windows将使用这些HASH来验证你的身份。  
  
3、日志筛选过滤器

在界面顶部就是日志筛选过滤器，可以根据用户名、主机名和IP地址等对日志进行筛选。  

![2-1过滤器.png](https://image.3001.net/images/20191112/1573546795_5dca6b2b96b48.png!small)

也可以过滤显示时间段及事件ID，事件出现的次数。  

![2-2过滤器.png](https://image.3001.net/images/20191112/1573546998_5dca6bf6102e0.png!small)

4、Create Timeline（创建时间轴）

按时间顺序显示事件日志，以用户名及时间轴划分。

![9-2CreateTimeline时间表.png](https://image.3001.net/images/20191112/1573546477_5dca69eded30a.png!small)  

![9-3CreateTimeline时间表.png](https://image.3001.net/images/20191112/1573546489_5dca69f9a016f.png!small)

研究表明，监控以下事件对于调查未经授权的登录是有效的。基于此，LogonTracer还可以显示以下事件ID以进行可视化：

附登录事件ID及说明：

事件ID  
| 事件说明  
  
---|---  
4624  
| 登录成功  
  
4625  
| 登录失败  
  
4768  
| Kerberos身份验证（TGT请求）  
  
4769  
| Kerberos服务票据（ST请求）  
  
4776  
| NTLM身份验证  
  
4672  
| 分配特殊权限  
  
  
由于并非所有上述事件ID都使用默认设置进行记录，因此需要启用审核策略以保留此类日志，建议启用审核策略。

5、Diff Graph(差异扩散图)

选择要比较额2个不同的时间日期，以图形化对其进行差异分析。  

![3-1Diff
Graph差异.png](https://image.3001.net/images/20191112/1573546752_5dca6b00eedaa.png!small)

![3-2Diff
Graph差异.png](https://image.3001.net/images/20191112/1573547094_5dca6c56a23a5.png!small)

## 四、常见问题  

问题1：使用docker安装完LogonTracer运行时，界面一直处于加载状态。

![问题1-一直加载2.png](https://image.3001.net/images/20191112/1573547197_5dca6cbd0ba49.png!small)现象如下图：（360浏览器运行）  
![问题1-一直加载.png](https://image.3001.net/images/20191112/1573547281_5dca6d11c25b5.png!small)解决方法：不妨换个浏览器试试，如火狐或谷歌浏览器。

问题2：在使用docker安装运行后，访问LogonTracer界面时上传的日志文件成功后，却无法对日志加载分析。

![问题2-EXVT文件上传失败.png](https://image.3001.net/images/20191112/1573547367_5dca6d67d444a.png!small)原因：如果是上传文件按钮无法点击，原因是上面安装过程中提到的JS文件问题，按照上面安装过程的解决方法即可。

如果是上传的EVTX格式的日志文件在上传后无法加载分析的，现象如下图：

![问题2-EXVT文件上传失败2.png](https://image.3001.net/images/20191112/1573547544_5dca6e18d4b02.png!small)

原因一是Time Zone（时区）选项值选错了，中国的UTC为+8，因此Time Zone下拉选项框中选择8。

原因二是上传的EVTX日志文件的问题，如可能当前的日志文件没有记录到任何除了IP为127.0.0.1的其他IP地址。（下图为Log Parser
Lizard的分析截图）

![问题2-EXVT文件上传失败3.png](https://image.3001.net/images/20191112/1573547605_5dca6e559c33a.png!small)

## 五、结语

以上就是我在使用docker搭建LogonTracer时所记录下来的笔记，在遇到问题2时一直以为是搭的环境的问题，折腾后才发现是上传的日志文件问题，导致一直无法进行加载分析，网上也没有找到相关的问题解决文章，因此想通过记录一下这个过程来帮助正在搭建或将要搭建这个工具的小伙伴一些参考。

获取详细的介绍、安装使用说明以及相关软件，请访问：<https://github.com/JPCERTCC/LogonTracer>

 ***本文作者：yongsec，转载请注明来自FreeBuf.COM**

