>
> 最近博主在研究如何通过行为分析的方式进行溯源，结果发现这方面的知识在网上很少找得到。所以博主决定来分享一下如何通过对PE中的时间、日志、发帖时间等推理攻击者活动时区。因为这方面的资料比较少，所以博主会尽量讲的细一些。

咱们先从PE中的时间讲起 ，有些基础的小伙伴可能知道PE中存在着编译时间的字段。但是有经验的黑客一般会混淆掉编译时间的字段，让安全人员无从下手。

不过还好，PE文件中不止存在一个时间戳。应该说，至少有“IMAGE_FILE_HEADER”、“IMAGE_IMPORT_DESCRIPTOR”、“IMAGE_EXPORT_DIRECTORY”、“RESOURCE_DIRECTORY_TABLE”、“IMAGE_DEBUG_DIRECTORY”中的五个时间戳。

不过在日常研究中，一般很少会遇到某个样本同时存在五个时间戳的情况，不过通过对时间戳的分析会有助于我们开展溯源的工作。

## PE头 时间戳

那么我们来讲解一下如何查看这些时间戳。首先我们打开010Editor，随便选择一个exe将其拖入010Editor，会弹出提示安装一个模板，我们点击“安装”。  
![image](https://image.3001.net/images/20221223/1671769308_63a52cdc119c6c07e2514.png!small)

于是我们便可以在下面看到新弹出了一个“模板结果”的窗口  
![image](https://image.3001.net/images/20221223/1671769270_63a52cb62dd5dfb5f7863.png!small)

我们先看一下“IMAGE_FILE_HEADER”中的时间戳。我们选择“struct IMAGE_NT_HEADERS NtHeader”->“struct
IMAGE_FILE_HEADER FileHeader”->“time_t
TimeDateStamp”可以看到这里存在一个时间戳，这个时间戳就是样本的编译时间戳，一般正常的程序是不会修改这个地方的，但是一些木马样本会对这个地方进行混淆，使用一个虚假的时间戳来迷惑研究人员。  
![image](https://image.3001.net/images/20221223/1671769261_63a52cad5b20d53db9b57.png!small)

我们在看第二个，“IMAGE_IMPORT_DESCRIPTOR”中的时间戳，首先我们展开“struct IMAGE_IMPORT_DESCRIPTOR
ImportDescriptor[0]”->“ULONG
TimeDateStamp”，这个字段便是导入表的时间戳，通常一个PE会有多个导入表，所以也会存在多个导入表的时间戳。在本次的样本中，这个地方显示的是0，表示编译时未写入导入表时间戳。

第三个时间戳是“IMAGE_EXPORT_DIRECTORY”中的时间戳，也就是导出表时间戳，而一般exe是不存在导出表的，所以这一步建议更换为dll进行测试，本次使用“cmdial32.dll”进行演示。

我们展开“struct IMAGE_EXPORT_DIRECTORY ExportDir”->“time_t
TimeDateStamp”字段，这个地方就是导出表时间戳，一般黑客也不会作出修改。  
![image](https://image.3001.net/images/20221223/1671769236_63a52c9421c24c26388d2.png!small)

第四个时间戳是“RESOURCE_DIRECTORY_TABLE”中的时间戳，我们展开“struct RESOURCE_DIRECTORY_TABLE
ResourceDirectoryTable”->“time_t
TimeDateStamp”字段，这个就是资源表的时间戳。在本次的演示中，该字段为”01/01/1970
00:00:00″这个时间为无效时间，表示该字段未写入。  
![image](https://image.3001.net/images/20221223/1671769223_63a52c87ea4febb68d6ba.png!small)

第五个时间戳是“IMAGE_DEBUG_DIRECTORY”中的时间戳，我们展开“struct IMAGE_DEBUG_DIRECTORY
DebugDirectory”->“time_t TimeDateStamp”字段，该字段就是调试表时间。  
![image](https://image.3001.net/images/20221223/1671769212_63a52c7cb6c4af4b0dbe9.png!small)

> 以上便是PE文件中的五个时间字段，那么我们掌握了这些字段或者其他日志、流量中的时间后又该如何去分析呢？

## 通过时间推理时区

下面我们就来讲一下，如何通过这些时间去推理时区。

首先我们需要先了解一下全球上班时间，全球上班时间可以在
[http://t.90.re](http://t.90.re/)查看，我们点击左侧的“全球上班时间对照表”，便可以在右侧看到已经转换为“北京(UTC+08:00)时间”的全球上班、下班时间了。  
![image](https://image.3001.net/images/20221223/1671769196_63a52c6c331c554be8379.png!small)

接着，我们来处理时间，首先的打开Excel，将我们掌握的时间输入进去，（此处为测试数据）。  
![image](https://image.3001.net/images/20221223/1671769155_63a52c4356bc3d326e490.png!small)

我们输入后，点击时间所在列“A”来选中这一列，然后点击“数据”选项卡，选择“分列”功能，在弹出的分列功能中选择“分隔符号”，点击“下一步”。  
![image](https://image.3001.net/images/20221223/1671769145_63a52c394091654f832b6.png!small)

接着，我们在分隔符号栏选择“其他”，输入分隔符“:”，点击“完成”。  
![image](https://image.3001.net/images/20221223/1671769134_63a52c2e02ee7f38e475c.png!small)

我们再点击时间所在列“A”来选中这一列，按下快捷键“Ctrl+1”打开“设置单元格格式”窗口，选择“文本”，点击确定。  
![image](https://image.3001.net/images/20221223/1671769122_63a52c22e8f5c47bd06ac.png!small)

此时，时间便被分成了三列，分别是：时、分、秒。  
![image](https://image.3001.net/images/20221223/1671769111_63a52c17a4604d5a64ee3.png!small)

在不需要特别高精度的情况下，我们默认以小时为基本单位，我们继续操作，我们找一个新列，输入0~23作为小时参考。  
![image](https://image.3001.net/images/20221223/1671769102_63a52c0e65d870064762c.png!small)

然后我们在旁边一列，输入公式“=COUNTIF(A:A,F1)”。我简单解释下这个公式。

开头的“=”表示这是这个公式，“COUNTIF”函数可以用来在一个范围统计有多少数据符合条件，“A:A”表示的是一个范围，即从“A”列到“A”列，也就是整个“A”列，“F1”则是参考标准。

简单理解，这条命令会在“A”列去寻找有多少条“F1”单元格的数据。  
![image](https://image.3001.net/images/20221223/1671769089_63a52c0161804bd9a7ea0.png!small)

输入完公式后，我们双击公式所在单元格“G2”的右下角  
![image](https://image.3001.net/images/20221223/1671769076_63a52bf4d31e1eee135e8.png!small)

这样公式便被填充到了F列最后一条。  
![image](https://image.3001.net/images/20221223/1671769061_63a52be53579ff83be2c5.png!small)

然后，我们在选择时间参考的“F”列和出现次数的“G”列，然后选择“插入”选项卡，选择“插入折线图”，选择“更多折线图(M)”。  
![image](https://image.3001.net/images/20221223/1671769043_63a52bd310293903c65ca.png!small)

然后，我们选择右面的这个折线图，点击确定。  
![image](https://image.3001.net/images/20221223/1671769033_63a52bc90554645f2d549.png!small)

这样我们便得到了一个时区折线图。  
![image](https://image.3001.net/images/20221223/1671768917_63a52b550b63d3c4fec7b.png!small)

从图中可以看出，本次数据中大约是从UTC+08:00的21点到次日的6点有活动的行为，说明攻击者会有较大可能在该时区活动。这里补充一个知识点，特殊情况下，攻击者可能会存在加班的情况，导致时间线较长。但是，攻击者一般不会出现提前上班的情况，所以各位小伙伴在研究时，可以对图表中的开始活动时间多多留意，加大可信权重。  
![image](https://image.3001.net/images/20221223/1671768978_63a52b920378111e5e63b.png!small)

我们继续，我们根据现在的数据，可以很明显的发现，北京时间（UTC+08:00）的21点左右是活动高峰期，我们打开
[http://t.90.re](http://t.90.re/)，选择“全球上班时间对照表”。  
![image](https://image.3001.net/images/20221223/1671768963_63a52b838008cdfb4c2a6.png!small)

然后找到上班时间在“21:00”下班时间在“06:00”范围内的几个国家，参照后发现，攻击者时区与“UTC-05:00”的工作时间较为匹配，对应北美时区。  
![image](https://image.3001.net/images/20221223/1671768943_63a52b6f98229c5765735.png!small)

