## 0x1 Info

  * Tag:  
MSSQL，Privilege Escalation，Kerberos，域渗透，RDP  
![image](https://image.3001.net/images/20221212/1670830648_6396da3894da13cf53deb.png!small)  
靶场地址：https://yunjing.ichunqiu.com/ranking/summary?id=BzMFNFpvUDU

## 0x2 Recon

  1. Target external ip  
`47.92.82.196`

  2. nmap  
![image](https://image.3001.net/images/20221212/1670830662_6396da46934c5c45a4015.png!small)

  3. MSSQL 弱口令爆破，爆破出有效凭据，权限为服务账户权限（MSSQLSERVER）  
`sa:1qaz!QAZ`  
![image](https://image.3001.net/images/20221212/1670831232_6396dc808db2d69ef3a8a.png!small)

## 0x3 入口点 MSSQL - 172.22.8.18

  * 前言，该机器不在域内

  1. 直接MSSQL shell（这里做完了忘记截图了..）  
![image](https://image.3001.net/images/20221212/1670831243_6396dc8b0112e93f890b4.png!small)

  2. 提权，这里直接获取Clsid暴力怼potato（前面几个clsid是用不了的）  
  
修改GetClsid.ps1，添加执行potato  
![image](https://image.3001.net/images/20221212/1670831254_6396dc9678bd4f497200d.png!small)  
Potato和GetClsid.ps1  
![image](https://image.3001.net/images/20221212/1670831304_6396dcc87490d2d06b149.png!small)  
执行GetClsid.ps1  
![image](https://image.3001.net/images/20221212/1670831318_6396dcd6716a936f02e24.png!small)  
获取到有效clsid以及命令执行结果  
![image](https://image.3001.net/images/20221212/1670831329_6396dce1844845a2a7961.png!small)

  3. 导出SAM，SYSTEM，Security  
![image](https://image.3001.net/images/20221212/1670831346_6396dcf2c84701ac73c58.png!small)  
解出凭据，用administrator + psexec 139横向（外网没有开445）就能获取到 flag01  
`administrator 2caf35bb4c5059a3d50599844e2b9b1f`  
![image](https://image.3001.net/images/20221212/1670831386_6396dd1ac05af51173c7f.png!small)

  4. qwinsta和端口连接看到有机器rdp过来  
![image](https://image.3001.net/images/20221212/1670831399_6396dd27953486127b85c.png!small)  
![image](https://image.3001.net/images/20221212/1670831410_6396dd32a4c300278b8db.png!small)

  5. 这边使用administrator psexec后上msf（system权限），使用incognito模块，模拟至john（本人实测，只有msf的incognito能完成后续操作，f-secure lab等其他的模拟令牌工具没成功）  
![image](https://image.3001.net/images/20221212/1670831423_6396dd3f15f5ca0c9fd26.png!small)

  6. 使用john的token执行 net use 看到 \\\tsclient\C 共享  
![image](https://image.3001.net/images/20221212/1670831435_6396dd4b6751e14684a9f.png!small)

  7. 直接获取 \\\tsclient\C 下面的 credential.txt，同时提示 hijack image (镜像劫持)  
`xiaorang.lab\Aldrich:Ald@rLMWuy7Z!#`  
![image](https://image.3001.net/images/20221212/1670831447_6396dd57291b5d46ad3ce.png!small)

  * 快进，略过搭建代理过程

  8. CME 扫描 172.22.8.0/24，有三个机器提示密码过期了  
![image](https://image.3001.net/images/20221212/1670831497_6396dd89625855c8fd100.png!small)

  9. 测试一下 DC01 88端口是否开启（测是否域控），DC01为域控

  10. smbpasswd.py 远程修改一下过期密码，改成111qqq...  
![image](https://image.3001.net/images/20221212/1670831548_6396ddbc2d79d95d48a9d.png!small)

  11. ldapshell.py 验证，登录域成功  
![image](https://image.3001.net/images/20221212/1670831569_6396ddd1be6244553e5e8.png!small)

  12. CME 枚举 RDP，显示能登录进入 172.22.8.46（用CME官方的RDP模块不会扫出有效RDP凭据，这边自己写了一个基于xfreerdp的CME模块）  
[XiaoliChan/CrackMapExec-Extension](https://github.com/XiaoliChan/CrackMapExec-Extension)  
![image](https://image.3001.net/images/20221212/1670831623_6396de078c9bb4bc60022.png!small)

## 0x4 域渗透 - 入口 - 172.22.8.46

  1. 登录进入，查看到 xiaorang.lab\Aldrich 不是这台机器的管理员，只是普通用户  
![image](https://image.3001.net/images/20221212/1670831638_6396de16b15bc3d0b673e.png!small)

  * 提权，两种方法  
  
Priv-ESC1：镜像劫持提权（常规）  
  
Get-ACL查看到任何用户都可以对注册表 "HKLM:\SOFTWARE\Microsoft\Windows
NT\CurrentVersion\Image File Execution Options" 进行写入，创建操作  
![image](https://image.3001.net/images/20221212/1670831654_6396de269585150b24bad.png!small)  
创建一个劫持magnify.exe（放大镜）的注册表，执行CMD.exe  
![image](https://image.3001.net/images/20221212/1670831670_6396de3682328bb0558c4.png!small)  
锁定用户  
![image](https://image.3001.net/images/20221212/1670831690_6396de4a8b12cf822f564.png!small)  
点击放大镜  
![image](https://image.3001.net/images/20221212/1670831704_6396de58ce3d1eaa603a4.png!small)  
提权至system  
![image](https://image.3001.net/images/20221212/1670831724_6396de6c08277423ffc39.png!small)  
Priv-ESC2：krbrelayup提权  
  
域普通权限用户在域内机器，直接带走（非常规，推荐）  
![image](https://image.3001.net/images/20221212/1670831736_6396de7875ece19fc70c1.png!small)  
![image](https://image.3001.net/images/20221212/1670831746_6396de82667425844800e.png!small)

  5. 快进mimikatz，获取到当前机器的机器账户 win2016$

    
    
    xiaorang.lab\WIN2016$ 4ba974f170ab0fe1a8a1eb0ed8f6fe1a
    

## 0x5 域渗透 - DC Takeover

  * 两种方法

  1. 观察 WIN2016$ 的组关系，发现处于 Domain Admins 组，直接使用 Dcsync 带走 DC01 （过程略）  
![image](https://image.3001.net/images/20221212/1670831757_6396de8df3029995a9cf8.png!small)

  2. 约束委派（非常规）  
  
Bloodhound收集域信息，分析，发现存在约束委派  
![image](https://image.3001.net/images/20221212/1670831771_6396de9b5975568da0198.png!small)  
使用 getST.py 进行约束委派攻击  
![image](https://image.3001.net/images/20221212/1670831781_6396dea549b5b3d8cedde.png!small)  
带走 DC01  
![image](https://image.3001.net/images/20221212/1670831793_6396deb17b612731b92c5.png!small)

## 0x6 Outro

  * 个人比较手残，不懂C，incognito那个部分，按照作者解释来说，常规是要自己写一个impersonate token的工具（还是没脱离MSF.. TAT）

