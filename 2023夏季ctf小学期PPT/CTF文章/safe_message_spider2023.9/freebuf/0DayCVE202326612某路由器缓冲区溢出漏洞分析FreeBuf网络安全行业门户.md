## Part1 漏洞状态

  

![?url=http%3A%2F%2Fdingyue.ws.126.net%2F2023%2F0810%2Ff65a6a0fp00rz5uwz0009c000tl003im.png&thumbnail=660x2147483647&quality=80&type=jpg](https://image.3001.net/images/20230831/1693444947_64efeb5324d1947bff3e8.png!small)

## Part2 漏洞描述

![?url=http%3A%2F%2Fdingyue.ws.126.net%2F2023%2F0810%2F9b6851ccj00rz5uwz001xc000tm00bcm.jpg&thumbnail=660x2147483647&quality=80&type=jpg](https://image.3001.net/images/20230831/1693444957_64efeb5d4be089c1b0efc.png!small)

## Part3 漏洞验证

1\. 验证环境  
路由器模拟器：192.168.0.1  
2\. 验证过程  
运行PoC，浏览器出现崩溃现象

![?url=http%3A%2F%2Fdingyue.ws.126.net%2F2023%2F0810%2Fed04bb73j00rz5uwz002pc000gu00gqm.jpg&thumbnail=660x2147483647&quality=80&type=jpg](https://image.3001.net/images/20230831/1693444966_64efeb668afa1e7f8c04b.png!small)

## Part4 漏洞分析

C语言存在许多危险函数，如strcpy、strcat等，随后通过IDA发现web程序使用了高危函数函数strncpy。

![?url=http%3A%2F%2Fdingyue.ws.126.net%2F2023%2F0810%2F066f3dd6j00rz5uwz0035c000p000evm.jpg&thumbnail=660x2147483647&quality=80&type=jpg](https://image.3001.net/images/20230831/1693444975_64efeb6fb5e2996009b43.png!small)点击函数名，查看交叉引用，发现sub_469F78函数调用了strncpy函数。

![?url=http%3A%2F%2Fdingyue.ws.126.net%2F2023%2F0810%2F93497ef1j00rz5ux0006rc000p000eum.jpg&thumbnail=660x2147483647&quality=80&type=jpg](https://image.3001.net/images/20230831/1693444984_64efeb78586774417134a.png!small)sub_469F78函数320行调用了strncpy函数。查看309至320行代码，可以得知v60为xml中的HostName元素的值，v11为v60字符串的大小，v62为申请的330大小的堆空间。320行代码调用strncpy函数时，并未检查v11大小，而直接使用v11+1作为目标缓冲区的大小，此时如果可以控制v45字符串则将导致缓冲区溢出。

![?url=http%3A%2F%2Fdingyue.ws.126.net%2F2023%2F0810%2Faf337218j00rz5ux10050c000p000etm.jpg&thumbnail=660x2147483647&quality=80&type=jpg](https://image.3001.net/images/20230831/1693444997_64efeb8594398479c783c.png!small)点击函数名，按x查看引用，发现sub_469F78函数由sub_46B6E8函数调用。

![?url=http%3A%2F%2Fdingyue.ws.126.net%2F2023%2F0810%2Fa3655542j00rz5ux1005jc000p000eum.jpg&thumbnail=660x2147483647&quality=80&type=jpg](https://image.3001.net/images/20230831/1693445007_64efeb8f800aca5087f64.png!small)sub_46B6E8函数检查了SetParentsControlInfo和UsersInfo元素，并且由00588E0C地址引用。

![?url=http%3A%2F%2Fdingyue.ws.126.net%2F2023%2F0810%2Fd2e6ed60j00rz5ux1006pc000p000esm.jpg&thumbnail=660x2147483647&quality=80&type=jpg](https://image.3001.net/images/20230831/1693445015_64efeb97450bb962eb53d.png!small)对表的首地址00588D80，按下x，可以得知sub_42383C函数引用该表。

![?url=http%3A%2F%2Fdingyue.ws.126.net%2F2023%2F0810%2Fb69953f8j00rz5ux10086c000p000evm.jpg&thumbnail=660x2147483647&quality=80&type=jpg](https://image.3001.net/images/20230831/1693445024_64efeba0aa77180e31ec6.png!small)追踪sub_42383C的引用，得到sub_423F90函数。

![?url=http%3A%2F%2Fdingyue.ws.126.net%2F2023%2F0810%2F215e9840j00rz5ux1005zc000p000eam.jpg&thumbnail=660x2147483647&quality=80&type=jpg](https://image.3001.net/images/20230831/1693445032_64efeba81d871efbfee17.png!small)观察sub_423F90函数的第50行，发现/HNAP1路径的与处理程序sub_42383C进行关联。

![?url=http%3A%2F%2Fdingyue.ws.126.net%2F2023%2F0810%2F82ab540aj00rz5ux0004qc000p000f4m.jpg&thumbnail=660x2147483647&quality=80&type=jpg](https://image.3001.net/images/20230831/1693445039_64efebaff407888501744.png!small)sub_42383C函数中使用for循环依次比较off_588D80数值

![?url=http%3A%2F%2Fdingyue.ws.126.net%2F2023%2F0810%2F31f56ed5j00rz5ux1005uc000p000hcm.jpg&thumbnail=660x2147483647&quality=80&type=jpg](https://image.3001.net/images/20230831/1693445048_64efebb82120df4ac9ee6.png!small)查看地址off_588D80，可以确定为功能名和对应函数的数组。

![?url=http%3A%2F%2Fdingyue.ws.126.net%2F2023%2F0810%2F7ec3a109j00rz5ux200jxc000p000phm.jpg&thumbnail=660x2147483647&quality=80&type=jpg](https://image.3001.net/images/20230831/1693445055_64efebbfdacbd8df223d0.png!small)

## Part5 修复缓解建议

厂商暂未发布修复措施解决此安全问题，建议使用此设备的用户随时关注厂商主页或参考网址以获取解决办法：  
https://www.dlink.com/en/security-bulletin

