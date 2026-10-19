欢迎关注同名微信公众号！[狼蛛安全实验室](https://mp.weixin.qq.com/s/ccMQEhCoSwOaUV1RMFpFvg)！

## 正文

近期发现了一些恶意的Lnk样本，忽然想到之前研究过Lnk文件的结构，就在此向大家分享一些有用的知识点，希望大家有所收获。

在Lnk文件中有很多字段，其中有一些字段很有意思，包括：“MachineID”、“MAC
Address”、“SID”、“DriveSerialNumber”、“Item Type
Text”等等，这些字段对溯源是很有帮助的，可以结合VT等样本沙箱进行Hunter，扩展更多样本，从而梳理攻击者的攻击时间线、攻击目标等等。

以下篇幅作者主要讲解Lnk文件的结构，我会尽量写的详细一点，方便大家学习。

首先，我们先创建一个lnk文件，找到一个程序，右键创建快捷方式

![1668496308_63733bb499b9206141e65.jpg!small](https://image.3001.net/images/20221115/1668496308_63733bb499b9206141e65.jpg!small)

可以看到快捷方式的实际后缀为.lnk文件，大小1k字节。

![1668496317_63733bbd331e9929d2d77.jpg!small](https://image.3001.net/images/20221115/1668496317_63733bbd331e9929d2d77.jpg!small)

我们打开010Editor，选择左上角的文件->打开

![1668496325_63733bc5589173a0cdc79.jpg!small](https://image.3001.net/images/20221115/1668496325_63733bc5589173a0cdc79.jpg!small)

选择我们创建的快捷方式后会提示安装模板，点击安装。

![1668496334_63733bcec9f9ff86231f1.jpg!small](https://image.3001.net/images/20221115/1668496334_63733bcec9f9ff86231f1.jpg!small)

我们可以在下面看到安装完后，下面出现了一个窗口。

![1668496344_63733bd8527e1bf668bdb.jpg!small](https://image.3001.net/images/20221115/1668496344_63733bd8527e1bf668bdb.jpg!small)

我们可以通过展开“struct ExtraData sExtraData”->“struct TrackerDataBlock
sTrackerDataBlock”->“byte MachineID[16]”，查看MachineID（计算机名称）

![1668496352_63733be04f32068fc26b0.jpg!small](https://image.3001.net/images/20221115/1668496352_63733be04f32068fc26b0.jpg!small)

接着，我们展开“struct ExtraData sExtraData”->“struct TrackerDataBlock
sTrackerDataBlock”->“GUID VolumeDroid[16]”，可以从最后的6字节看到完整的MAC地址。

![1668496360_63733be8b59f018303a43.jpg!small](https://image.3001.net/images/20221115/1668496360_63733be8b59f018303a43.jpg!small)

紧接着，展开“struct ExtraData sExtraData”->“struct PropertyStoreDataBlock
sPropertyStoreDataBlock”->“struct PropertyStoreList
sPropertyStoreList[1]”->“struct PropertyIntegerValue
sPropertyIntegerValue”->“struct TypedPropertyValue Value”->“wchar_t
Value[44]”，查看创建lnk文件用户的SID。

![1668496367_63733bef8f50caa9dcc06.jpg!small](https://image.3001.net/images/20221115/1668496367_63733bef8f50caa9dcc06.jpg!small)

然后，我们展开“struct LinkInfo sLinkInfo”->“struct VolumeID sVolumeID”->“uint32
DriveSerialNumber”，并将其转换为16进制查看改卷的序列号。

![1668496377_63733bf9d32d8033309f2.jpg!small](https://image.3001.net/images/20221115/1668496377_63733bf9d32d8033309f2.jpg!small)

然后，展开“struct ExtraData sExtraData”->“struct PropertyStoreDataBlock
sPropertyStoreDataBlock”->“struct PropertyStoreList
sPropertyStoreList[0]”->“struct PropertyIntegerValue
sPropertyIntegerValue[1]”->“struct TypedPropertyValue Value”->“wchar_t
Value[6]”，可以看到存在文件类型字段

![1668496385_63733c01d6cb0482f11f0.jpg!small](https://image.3001.net/images/20221115/1668496385_63733c01d6cb0482f11f0.jpg!small)

该字段在其他系统中也是以系统语言的方式存在，例如JP。

![1668496396_63733c0c3b9548f71f3c7.jpg!small](https://image.3001.net/images/20221115/1668496396_63733c0c3b9548f71f3c7.jpg!small)

那么我们该如何扩线呢？

作者用mac地址和netbios名称举个例子，以上述样本为例，yara规则可以这么实现（也可以按照个人习惯添加其他字段等）：

    
    
    rule Lnk{strings:$mac = {00 0C 29 11 EB 76}$netbios = "work-pc" fullword ascicondition:uint16(0) == 0x4c and ($mac or $netbios)}

