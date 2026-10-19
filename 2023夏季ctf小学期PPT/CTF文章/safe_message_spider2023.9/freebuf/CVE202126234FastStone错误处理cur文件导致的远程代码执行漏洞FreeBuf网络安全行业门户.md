FastStone Image Viewer是一款快速、小巧、功能强大的综合图像浏览软件。

## Part1 漏洞状态

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 有| 无  
  
## Part2 漏洞描述

‍漏洞名称|

FastStone错误处理cur文件导致的远程代码执行  
  
---|---  
CVE编号| CVE-2021-26234  
漏洞类型| 远程代码执行  
漏洞等级| 7.8 高危 (High）  
公开状态| 公开  
漏洞描述|

FastStone Image Viewer <= 7.5 受到用户模式写入访问冲突的影响，当用户打开或查看由 FSViewer.exe
错误处理的格式错误的 CUR 文件时触发。攻击者可以利用此问题进行拒绝服务 (DoS) 或可可以实现远程代码执行。  
  
时间线|

2021-03-18漏洞提交

2021-03-21 CVE发布  
  
受影响版本|

FastStone Image Viewer <= 7.5  
  
###  **分析环境:**

Win10

FastStone Image Viewer 7.5

## Part3 漏洞复现

### 1.测试文件放到桌面exp文件夹下

![图片](https://image.3001.net/images/20230705/1688535561_64a502090d311ab698138.png!small)

2\. 打开FastStone Viewwer

![图片](https://image.3001.net/images/20230705/1688535577_64a50219c58a66a9b6313.png!small)

3\. 当前浏览目录切换到Desktop，这样就会解析到Desktop目录下exp里面的所有图片文件

![图片](https://image.3001.net/images/20230705/1688535587_64a50223a7def2c9b75b3.png!small)

4.弹出calc，复现成功！

![图片](https://image.3001.net/images/20230705/1688535597_64a5022de53dce19816da.png!small)

## Part4 漏洞分析

正常cur文件的BitCount值

![图片](https://image.3001.net/images/20230705/1688535615_64a5023fa4c311593564b.png!small)

测试cur文件BitCount值

![图片](https://image.3001.net/images/20230705/1688535631_64a5024f11fd386f33b75.png!small)

关键漏洞流程

![图片](https://image.3001.net/images/20230705/1688535641_64a502597d8d749bf1b38.png!small)

可以看到，这里从ebp-34读取BItcount到ecx，后根据cl向左位移eax当作读取大小数据。又在0x5BDF35位置再次左移两位读取大小数据。在0x5BDF43位置读取文件，读取指针在堆栈上，因此当测试文件BitCount数值过大时，会覆盖堆栈上的SEH。0x5BDF49位置在被堆栈上获取数值，触发异常，然后导致代码流程被控制。

![图片](https://image.3001.net/images/20230705/1688535651_64a50263340c383c51490.png!small)

执行readFile之后

![图片](https://image.3001.net/images/20230705/1688535661_64a5026dc3bae451778ae.png!small)

可以看到，堆栈被破坏，seh handler被覆盖

![图片](https://image.3001.net/images/20230705/1688535674_64a5027a2484241a8ecd8.png!small)

最后触发异常，可以看到，最终走到异常代码被劫持的位置。

## Part5 修复建议

1\. 软件升级到最新版本

2\. 检测读取函数是否溢出

