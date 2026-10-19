**近日，国内半导体行业爆发勒索病毒，造成业务大面积瘫痪，深信服安全团队率先接到情报并进行处置，发现其攻击手段与早期Petya勒索病毒有相似之处，但又有很大不同，其攻击方式包括控制域控服务器、钓鱼邮件、永恒之蓝漏洞攻击和暴力破解，威力巨大，可在短时间内造成内网大量主机瘫痪并弹出骷髅头！**

深信服已将其命名为GhostPetya骷髅头勒索病毒，并且制定了完善的防御措施和解决方案。

![1.png](https://image.3001.net/images/20181208/1544234405_5c0b25a58c1f1.png!small)

中招主机，其勒索信息如下，黑客索要0.1个比特币赎金。

![2.png](https://image.3001.net/images/20181208/1544234421_5c0b25b50b297.png!small)

##  **病毒分析**

1.以读写的模式，打开主机\\\\.\PhysicalDrive0、\\\\.\PhysicalDrive1、\\\\.\PhysicalDrive2、\\\\.\PhysicalDrive3、\\\\.\I等磁盘，如下所示：

![3.png](https://image.3001.net/images/20181208/1544234454_5c0b25d632cf1.png!small)

2.然后MBR勒索的数据写入到这些打开的磁盘空间中，如下所示：

![4.png](https://image.3001.net/images/20181208/1544234464_5c0b25e09f116.png!small)

写入的相关数据，如下所示：

![5.png](https://image.3001.net/images/20181208/1544234475_5c0b25eb12624.png!small)

显示的勒索信息，如下所示：

![6.png](https://image.3001.net/images/20181208/1544234485_5c0b25f52ae56.png!small)

3.然后执行重启系统命令，如下所示：

![7.png](https://image.3001.net/images/20181208/1544234494_5c0b25fe70bc1.png!small)

4.从感染的主机中提取出相应的MBR数据，如下所示：

![8.png](https://image.3001.net/images/20181208/1544234503_5c0b260788bd2.png!small)

5.感染后的主机，会先调用CHKDSK进行磁盘检测操作，如下所示：

![9.png](https://image.3001.net/images/20181208/1544234514_5c0b2612431eb.png!small)

调用磁盘检测信息，如下所示：

![10.png](https://image.3001.net/images/20181208/1544234525_5c0b261d1cd23.png!small)

完成之后会弹出勒索图片闪屏信息。

按任意健进入系统，显示如下所示的勒索信息：

![11.png](https://image.3001.net/images/20181208/1544234539_5c0b262bbf2ad.png!small)

要求受害客户支付0.1个BTC进行解锁操作,BTC地址：

    
    
    1Ex6qfkopZ5wgbiCrxpq4cALF56yr8gLhX

6.对感染后主机的MBR进行动态调试，如下所示：

![12.png](https://image.3001.net/images/20181208/1544234551_5c0b2637ede86.png!small)

7.经过调试分析，此感染后的MBR与之前Petya勒索病毒MBR代码非常相似，调用int
13中断，将扇区1-32从磁盘加载到内存0x8000开始的地址，然后转到0x8000执行指令，如下所示：

![13.png](https://image.3001.net/images/20181208/1544234563_5c0b2643ae3e5.png!small)

8.循环读取$等字符串信息，用于显示勒索信息图片，如下所示：

![14.png](https://image.3001.net/images/20181208/1544234574_5c0b264e94055.png!small)

9.显示勒索图片信息，如下所示：

![15.png](https://image.3001.net/images/20181208/1544234584_5c0b26589a88a.png!small)

设置屏幕的显示模式，如下所示：

![16.png](https://image.3001.net/images/20181208/1544234595_5c0b26636a169.png!small)

设置屏幕滚动参数，如下所示：

![17.png](https://image.3001.net/images/20181208/1544234607_5c0b266f06bde.png!small)

然后进行闪屏操作，如下所示：

![18.png](https://image.3001.net/images/20181208/1544234618_5c0b267a442a3.png!small)

10.检测是否有键盘按键信息，如下所示：

![19.png](https://image.3001.net/images/20181208/1544234630_5c0b268622cbd.png!small)

11.如果有按键信息，则读取相应的勒索信息，弹出信息勒索信息显示界面，如下所示：

![20.png](https://image.3001.net/images/20181208/1544234642_5c0b269235e7c.png!small)

相应的勒索信息数据，如下所示：

![21.png](https://image.3001.net/images/20181208/1544234652_5c0b269c1ad88.png!small)

12.循环检测用户输入的key，如下所示：

![22.png](https://image.3001.net/images/20181208/1544234664_5c0b26a8ea8f3.png!small)

##  **解决方案**

1.隔离感染主机：已中毒计算机尽快隔离，关闭所有网络连接，禁用网卡；

2.切断传播途径：关闭潜在终端的SMB 445等网络共享端口，关闭异常的外联访问。深信服下一代防火墙用户，可开启IPS和僵尸网络功能，进行封堵；

3.查找攻击源：借助深信服安全感知平台；

4.查杀病毒：推荐使用深信服EDR进行查杀；

5.修补漏洞：打上漏洞相关补丁，漏洞包括“永恒之蓝”漏洞等。

 **不幸中招的用户，可以尝试以下方式进行业务恢复：**

### 1：进入PE模式和制作启动U盘

 **工具:**

U盘启动制作软件；

U盘(制作启动盘时候格式化)；

测试PC为Windows。

![23_2.png](https://image.3001.net/images/20181208/1544234740_5c0b26f44d7d4.png!small)

制作好后U盘插入PC，开机进入PE模式 **有两种方法：**

(1) 开机后按F12，进入启动项选择U盘启动(不同的电脑按键不一样，可自行百度)；

(2) 进入BIOS系统中 （我这里选择FN+F12，可以去网上查的）选择U盘启动。  
![24.jpg](https://image.3001.net/images/20181208/1544234755_5c0b2703d8487.jpg!small)然后进入如下图界面，由于测试的PC是windows7系统，所以选择第[02]选项（根据中毒的PC情况来选项）。

![25_2.png](https://image.3001.net/images/20181208/1544234834_5c0b27527a7e2.png!small)

![26.png](https://image.3001.net/images/20181208/1544234851_5c0b2763d5f2f.png!small)

### 2：恢复数据

 **步骤1：** 接入运行桌面上的 DiskGenius软件，找到中毒PC的硬盘(一般为500G和1TB左右)。

![27.png](https://image.3001.net/images/20181208/1544234888_5c0b2788e8b1e.png!small)

 **步骤2：** 点击鼠标右键运行 **“** **搜索已丢失分区（** **重建分区表）”；**

![28.jpg](https://image.3001.net/images/20181208/1544234900_5c0b27948e3d7.jpg!small)

![29.jpg](https://image.3001.net/images/20181208/1544234917_5c0b27a575773.jpg!small)

 **步骤3：** 如果在搜索期间，弹出“搜索到分区框”记得点击保留：

![30.png](https://image.3001.net/images/20181208/1544234931_5c0b27b30fe41.png!small)

 **步骤4：** 最后可以看到数据恢复了，接着需要“点击保存”；

![31.png](https://image.3001.net/images/20181208/1544234943_5c0b27bf3ac21.png!small)

![32.jpg](https://image.3001.net/images/20181208/1544234957_5c0b27cd02d69.jpg!small)

### 3：重建MBR

 **步骤1:** 正常情况下数据恢复后重启系统的话，mbr还是不能正确引导系统启动，所以这个时候需要紧接着修复mbr，点击鼠标右键运行 **”**
**重建主导记录MBR”** **，这个时候会新建MBR；**

![33.png](https://image.3001.net/images/20181208/1544234970_5c0b27da15503.png!small)

![34.jpg](https://image.3001.net/images/20181208/1544234981_5c0b27e54d74c.jpg!small)

![35.png](https://image.3001.net/images/20181208/1544234999_5c0b27f7d8707.png!small)

 **这个时候就可以重新启动系统就可以恢复了。**

### 4：其它事项(注意)

 **2.** **恢复数据流程**

步骤2:运行在”搜索已丢失分区(重建分区表)”，当软件一直正在搜索情况下不要停止搜索后再次(重建分区表)，最好是一次性(重建分区表)，不然的话，第2次搜索完后丢失的数据可能会丢失部分；

步骤4:注意个别PC会存在系统C盘恢复不回来，这个时候可以直接插入备份U盘拷贝其它盘的数据出来后重装系统)。

 **3.** **重建MBR** **流程**

方法1:在DiskGenius上新建，上文已提到；

方法2:进入PE模式后，点击左下角的”引导修复--Bootice(引导扇区恢复工具)—主引导记录(M)-=选择Windows NT5.X/6.X MBR--点击安装/配置；

![36_2.png](https://image.3001.net/images/20181208/1544235051_5c0b282baf0c8.png!small)

![37.jpg](https://image.3001.net/images/20181208/1544235062_5c0b28360c597.jpg!small)

![38.png](https://image.3001.net/images/20181208/1544235071_5c0b283f86250.png!small)

然后根据系统点击Windows NT5.XMBR或者Windows NT6.X MBR后完成重启系统即可；

注意:存在个别情况就是数据恢复回来了，但是C盘的恢复不了或者新建MBR后正常开机不了，这个时候可以在PE模式下把其它盘的重要数据拷贝出来重装系统。

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

