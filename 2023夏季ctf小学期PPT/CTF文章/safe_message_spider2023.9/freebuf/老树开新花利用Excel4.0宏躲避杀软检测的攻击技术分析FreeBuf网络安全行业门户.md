背景  

2018年10月18日，360威胁情报中心首次捕获到一例利用Excel 4.0宏传播Imminent
Monitor远控木马的在野攻击样本。而这离2018年10月6日国外安全厂商Outflank的安全研究人员首次公开使用Excel
4.0宏执行ShellCode的利用代码仅仅过去了10余天。虽然Excel
4.0宏技术已经发布超过20年，并且在该技术出现早期就被经常用于制作宏病毒，但事实上，由于Microsoft很早就使用VBA宏（Visual Basic
for Applications）来代替Excel 4.0宏技术，这导致Excel 4.0宏并不为大众所熟知。并且由于Excel 4.0宏存放在Excel
97 - 2003格式（.xls，复合二进制文件格式）的Workbook OLE流中，这使得杀毒软件解析并检测Excel 4.0宏变得非常困难。

360威胁情报中心详细分析了Excel 4.0宏在Excel文档中的存储方式，并通过深入研究发现：在使用一些技巧隐藏Excel
4.0宏并配合执行一些经过特殊处理的ShellCode后，可以完美的躲避几乎所有杀毒软件的静态和动态查杀并执行任意恶意代码。由于基于Excel
4.0宏的新型利用技术已经被公开，且已经出现了利用该技术传播远控木马的在野利用，所以360威胁情报中心发布该分析报告并提醒预防此类攻击。

## 极强的免杀能力

360威胁情报中心通过深入分析Excel
4.0宏在复合二进制文件格式中的存储方式，构造了可以执行远程任意恶意代码的Exploit样本。经测试，国内外多款著名杀毒软件均无法对这类样本实现查杀：

### 卡巴斯基静态免杀

  

![image.png](https://image.3001.net/images/20181030/1540872877_5bd7daadee2f6.png!small)

### 卡巴斯基动态免杀

  

![image.png](https://image.3001.net/images/20181030/1540872893_5bd7dabdeafa9.png!small)

### ESET-NOD32静态免杀

  

![image.png](https://image.3001.net/images/20181030/1540872900_5bd7dac49041a.png!small)

### ESET-NOD32动态免杀

  

![image.png](https://image.3001.net/images/20181030/1540872906_5bd7daca23f5f.png!small)

## POC分析

Outflank的安全研究人员公开的POC样本在VirusTotal上查杀效果如下，截止目前未有杀软可以查杀，如果配合一些特殊的技巧还可以躲过杀软的动态查杀：

  

![image.png](https://image.3001.net/images/20181030/1540872913_5bd7dad107a7f.png!small)

### 执行过程分析

下图是Outflank的安全研究人员给出的测试Excel4.0宏的样本内容：

  

![image.png](https://image.3001.net/images/20181030/1540872918_5bd7dad64a8e9.png!small)

由于第一行第一列单元格名称被设置成“Auto_Open”，所以当打开此表格并点击了启用宏内容按钮时，Excel将会自动将此表格中的内容当成Excel
4.0宏执行。如果需要分析其执行过程，可以选中第一行第一列数据，右键选择“执行”菜单：

  

![image.png](https://image.3001.net/images/20181030/1540872923_5bd7dadbc412f.png!small)

然后在弹出的对话框中“位置”处选择本Excel文件，然后点击“单步执行”按钮：

  

![image.png](https://image.3001.net/images/20181030/1540872930_5bd7dae228769.png!small)

最后在弹出的对话框中可以看到公式内容，以及“单步执行”、“单步跳过”、“求值”等按钮：

  

![image.png](https://image.3001.net/images/20181030/1540872936_5bd7dae856511.png!small)

从调试过程来看，Excel首先执行第一行第一列中的宏代码，即=EXEC(“calc.exe”)，该指令执行完成后将会弹出计算器，同理可调试剩余两个公式，以下是三个公式的具体含义：

**公式内容** |  **功能**  
---|---  
=EXEC(“calc.exe”)  |  内部调用WinExec函数打开计算器  
=ALERT(“Hello, World”)  |  内部调用MessageBox函数打开对话框  
=HALT()  |  标识Excel 4.0宏结束，类似C语言return指令  
  
样本执行结果是打开计算器并弹出内容为“Hello, World”的对话框：

  

![image.png](https://image.3001.net/images/20181030/1540872941_5bd7daed6d087.png!small)

### 使用Excel 4.0宏执行ShellCode

由于Excel
4.0宏语言包括函数调用以及上百个内建函数，攻击者可以编写子程序或调用内建函数实现同VBA提供相同功能的恶意代码，下图是Outflank的安全研究人员提供的例子：

  

![image.png](https://image.3001.net/images/20181030/1540872946_5bd7daf27de92.png!small)

下表是各个宏公式具体含义：

**公式内容** **** |  **功能** ****  
---|---  
=REGISTER("Kernel32", "VirtualAlloc", "JJJJJ", "VAlloc", , 1, 9) |
设置kernel32!VirtualAlloc别名为VAlloc  
=VAlloc(0,1000000,4096,64) |
调用VAlloc函数分配大小为1000000，内存属性为PAGE_EXECUTE_READWRITE的内存  
=REGISTER("Kernel32", "WriteProcessMemory", "JJJCJJ", "WProcessMemory", , 1,
9) |  设置kernel32!WirteProcessMemory别名为WProcessMemory  
=SELECT(R1C2:R999:C2,R1C2) |  选择第一行第二列所有数据  
=SET.VALUE(R1C3, 0) |  设置第一行第三列数据为0  
=WHILE(ACTIVE.CELL()<>"END") |  循环读取刚刚选择的数据直到“END”标识  
=WProcessMemory(-1, R2C1 + R1C3 * 255,ACTIVE.CELL(), LEN(ACTIVE.CELL()), 0) |
将刚刚读取的内容写入由VAlloc分配的内存地址  
=SET.VALUE(R1C3, R1C3 + 1) |  将表格R1C3的值加一  
=SELECT(, "R[1]C") |  
=NEXT() |  下一次循环  
=REGISTER("Kernel32", "CreateThread", "JJJJJJJ", "CThread", , 1, 9) |
设置kernel32!CreateThread别名为CThread  
=CThread(0, 0, R2C1, 0, 0, 0) |  调用CThread函数创建线程并设置线程入口为由VAlloc分配的内存  
=HALT() |  标识子过程结束，类似C语言的return  
  
总体来说，该Excel 4.0宏代码实现的功能逻辑是：

第1步：调用kernel32!VirtualAlloc分配一段大小为1000000的可读可写可执行内存

第2步：循环读取第二列的数据并调用kernel32!WriteProcessMemory函数写入第1步分配的内存直到END标志

第3步：调用kernel32!CreateThread函数创建线程，并设置线程入口为第1步分配的内存

经过这3步操作，已然实现利用Excel4.0宏执行ShellCode的目的。

## 解析XLS中的Excel 4.0宏

### Execl文件（.xls）解析

Execl 4.0宏样本使用的XLS文件其实是一个MS-CFB(Microsoft Compound File Binary File)文件，而MS-CFB文件采用类似FAT文件系统的结构保存数据。很多现有工具可以解析该结构，比如OffVis、oletools、Structured Storage
eXplorer等。学习MS-CFB文件结构推荐使用OffVis，以下是用该工具打开的效果图：

  

![image.png](https://image.3001.net/images/20181030/1540872956_5bd7dafca67a9.png!small)

读取文件内容推荐使用StructuredStorage eXplorer，以下是用该工具打开的效果图：

  

![image.png](https://image.3001.net/images/20181030/1540872962_5bd7db027c20b.png!small)

如需手工解析请参考：

<https://msdn.microsoft.com/en-us/library/dd953721(v=office.12).aspx>。

### Book/Workbook解析

如上图所示，XLS文件中的公式内容均保存到Workbook中，要想从中读取公式就需要解析该结构。根据Microsoft提供的MS-XLS文档可知该Workbook结构由一个个顺序排列的record组成：

  

![image.png](https://image.3001.net/images/20181030/1540872969_5bd7db09b4d6b.png!small)

Record由三个字段构成，分别是记录类型、记录大小和记录数据，以下是MS-XLS文档所记录：

  

![image.png](https://image.3001.net/images/20181030/1540872976_5bd7db101b134.png!small)

记录类型和记录大小各占2个字节，记录数据由记录大小决定，如下图所示该记录类型为0x0809、记录大小为0x0010(16bytes)、记录数据为00 06
05 00 54 38 CD 07 C1 C0 01 00 06 07 00 00

  

![image.png](https://image.3001.net/images/20181030/1540872981_5bd7db15418b9.png!small)

其中，记录类型必须为Microsoft提供的RecordEnumeration类型，类型表格请参考<https://msdn.microsoft.com/en-us/library/dd945945(v=office.12).aspx>。

Recode type为133(BoundSheet8)的recode包含了表格(sheet)的类型信息，包括表格名称、隐藏状态和表格类型等

  

![image.png](https://image.3001.net/images/20181030/1540872986_5bd7db1ab755f.png!small)

以下是BoundSheet8的结构：

  

![image.png](https://image.3001.net/images/20181030/1540872990_5bd7db1e82b96.png!small)

lbPlyPos占4bytes，指定了表格BOF记录开始的book/workbook流偏移。

dt占1byte，指定了表格类型。

Value  |  Meaning  
---|---  
0x00  |  Worksheet or dialog sheet  
0x01  |  Macro sheet(Execl 4.0宏)  
0x02  |  Chart sheet  
0x06  |  VBA module(VBA宏)  
  
stName标识表格名称，包含2bytes长度和字符串。

以本次分析的样本为例：

sha256：ac6f6a9463dabeb485973a0bc440e740627e3d2a0593f1e6c26dbd116d6b2e3e

下图标识了2个表格，其中第一个表格为可见、带有Execl 4.0宏且名称为Macro1，第二个表格属性为可见、类型为Worksheet或dialog
sheet且名称为Sheet1。

  

![image.png](https://image.3001.net/images/20181030/1540872997_5bd7db25a902a.png!small)

由上图可知，Execl 4.0宏表格BOF
recode流偏移为0x001AF6，定位到流偏移为0x00001AF6的recode如下图所示，其类型为2057，对应确实是BOF记录：

  

![image.png](https://image.3001.net/images/20181030/1540873003_5bd7db2b8086a.png!small)

  

![image.png](https://image.3001.net/images/20181030/1540873011_5bd7db33af517.png!small)

  

![image.png](https://image.3001.net/images/20181030/1540873016_5bd7db38ab836.png!small)

  

![image.png](https://image.3001.net/images/20181030/1540873025_5bd7db419bef9.png!small)

然后从BOF recode开始遍历，寻找记录类型为6(Execl 4.0宏公式)的recode直到EOF recode：

  

![image.png](https://image.3001.net/images/20181030/1540873029_5bd7db45b051e.png!small)

### Excel 4.0宏对象解析

记录类型为6的recode包含了宏公式对象，其格式如下图所示：

  

![image.png](https://image.3001.net/images/20181030/1540873035_5bd7db4bafcb1.png!small)

Cell占6字节，指定公式所在单元格。

FormulaValue占8字节，指定公式的值。

CellParsedFormula结构用于指定公式。

如下图所示，包含2个Formula，第一个由数据0F 0017 08 00 63 61 6C 63 2E 65 78 65 42 01 6E

00指定公式，第二个由数据04 00 4200 36 00指定公式。

  

![image.png](https://image.3001.net/images/20181030/1540873041_5bd7db511752a.png!small)

CellParsedFormula结构如下：

  

![image.png](https://image.3001.net/images/20181030/1540873046_5bd7db5607585.png!small)

ccb占2字节，指定rgce大小。

rgce指定至少一个公式数据，包含函数号，参数等。

rgce结构大致如下图所示

  

![image.png](https://image.3001.net/images/20181030/1540873050_5bd7db5a436f3.png!small)

rgceType占2bytes，指定公式数据类型，类型请参考<https://msdn.microsoft.com/en-us/library/dd948654(v=office.12).aspx>。

下图灰色背景16进制数据为样本公式数据：

  

![image.png](https://ti.360.net/uploads/2018/10/30/c64126bc0c21ab3adf7579623b158137.png)

第一处公式数据解析结果如下：

l 0x000F表示公式数据长度，即ccb。

l 0x17表示公式数据类型，即rgceType，此处0x17表示PtgStr，即后面紧跟字符串。

l 0x0008表示公式数据长度，即sLen。

l calc.exe表示数据，即data。

l 0x42表示公式数据类型，即rgceType，此处0x42表示PtgFuncVar。

l 0x01表示函数参数个数，即NumberOfArg，此处为0x01代表仅一个参数。

l 0x006E ^ 0x0001=0表示FuncID将从Ftab表中查询，而不是从Cetab表中查询

  

![image.png](https://ti.360.net/uploads/2018/10/30/30e7783750168067c78714bb8430bdff.png)

PtgFuncVar定义参考<https://msdn.microsoft.com/en-us/library/dd907478(v=office.12).aspx>。

l
0x006E表示调用函数的ID，即FuncID，此处为0x6E，查询Ftab表可该调用EXEC函数，查询参考<https://msdn.microsoft.com/en-us/library/dd904817(v=office.12).aspx>。

总体来说，第一处公式数据确定了调用EXEC函数，参数为”calc.exe”。同理，第二处公式调用Ftab表中的0x36号函数，查询可知此处为调用HALT函数。

依次，则可以逐个解析Excel中的所有公式函数及相关数据。

## 在野样本分析

### 传播Imminent Monitor远控木马的攻击样本分析

360威胁情报中心在2018年10月18日首次捕获到利用Excel 4.0宏传播Imminent
Monitor远控木马的攻击样本，在VirusTotal上仅有一家杀毒软件能够查杀：

  

![image.png](https://image.3001.net/images/20181030/1540873091_5bd7db831dc74.png!small)

Excel 4.0恶意宏代码隐藏在表格中，选择取消隐藏则可看到Excel 4.0宏代码：

  

![image.png](https://image.3001.net/images/20181030/1540873096_5bd7db88be26b.png!small)

该宏代码会从：

hxxps://jplymell.com/dmc/InvoiceAug5e1063535cb7f5c06328ac2cd66114327.pdf下载后缀为PDF的文件并执行。而该文件实际为一个恶意的msi文件，通过msiexec执行后会在%temp%目录下解密释放一个.NET类型的可执行文件，命名为033ventdata.exe并执行：

  

![image.png](https://image.3001.net/images/20181030/1540873102_5bd7db8e8f940.png!small)

#### 033ventdata.exe分析

该程序是经过混淆的.NET程序，代码主要结构如下：

  

![image.png](https://ti.360.net/uploads/2018/10/30/5e832bbe6543161ae5fccb3a15015c7d.png)

Form1中vBM=会调用gRQ=函数：

  

![image.png](https://image.3001.net/images/20181030/1540873120_5bd7dba06fdb7.png!small)

gRQ=函数会首先获取一些配置信息，包括需要连接的CC地址：linkadrum.nl，并判断当前进程路径是否为”%temp%\ProtectedModuleHost.exe"，若不是则移动当前文件到该目录下，并删除当前进程文件：

  

![image.png](https://ti.360.net/uploads/2018/10/30/090aae04e09dc68310f7b58609fbedfc.png)

若进程路径符合，则在启动目录下生成对应的LNK自启动文件，实现自启动：

  

![image.png](https://image.3001.net/images/20181030/1540873140_5bd7dbb4bbb9e.png!small)

之后启动傀儡进程InstallUtil.exe，注入木马程序的主控PE文件：

  

![image.png](https://ti.360.net/uploads/2018/10/30/cd95b169d4728d1fd8d0dac37687f620.png)

#### 木马主控部分分析

注入的木马主控PE文件也是.NET程序，运行后会内存加载7z的LZMA的库DLL，接着调用lzma库去解压自身携带的木马主控EXE加载到内存执行。该EXE具有强混淆，内存加载执行后会通过linkadrum.nl上线并接受指令实现完整的远控功能：

  

![image.png](https://image.3001.net/images/20181030/1540873158_5bd7dbc648091.png!small)

通过反编译后还可以看到明显的字符串特征：“Imminent-Monitor-Client-Watermark”

  

![image.png](https://ti.360.net/uploads/2018/10/30/0baeda22d7a9ff433c94a98001f061c9.png)

而ImminentMonitor RAT是一款商业远控软件，官方售卖网站为：imminentmethods.net，基本囊括了所有远控功能：

  

![image.png](https://image.3001.net/images/20181030/1540873177_5bd7dbd98fcea.png!small)

### 早期利用Excel 4.0宏的宏病毒样本

通过大数据关联，360威胁情报中心还发现大量早期利用Excel 4.0宏进行传播的宏病毒样本：

  

![image.png](https://image.3001.net/images/20181030/1540873184_5bd7dbe040aa4.png!small)

MD5：66bceee6748d720dc6910f8cac7991da

该类宏病毒样本在互联网至少存活了数年，样本是被Excel 4.0宏病毒感染了的Excel文件，以其中一个样本作为示例分析，打开后如下图：

  

![image.png](https://image.3001.net/images/20181030/1540873192_5bd7dbe83d22c.png!small)

右键点击标签栏，会发现该样本隐藏了一个表(m1)_(m2)_(m3)：

  

![image.png](https://image.3001.net/images/20181030/1540873198_5bd7dbee591f8.png!small)

取消隐藏后，会发现在(m1)_(m2)_(m3)表里，还隐藏了列，取消隐藏列后会发现如下Excel 4.0宏代码：

  

![image.png](https://image.3001.net/images/20181030/1540873203_5bd7dbf3a3914.png!small)

其中第一列就是Excel4.0宏的代码，其功能为在C盘创建一个excel.txt文件，然后将表中C1:C108区域的内容写入该文件。最后再利用VBA.INSERT.FILE把该excel.txt文件加载到当前运行环境中。最后利用run函数调用VBA里的createcabfile函数。createcabfile函数的作用是把B列的数据写到C盘，然后解压并隐藏，最后修改其Excel的模板文件，实现蠕虫传播功能。

## 防护及总结

从近年来的高级攻击事件分析中可以看出，由于利用Office 0day等漏洞进行攻击的成本较高，多数攻击者更趋向于利用Office
VBA宏执行恶意代码。而对于本次公开的Excel
4.0宏利用技术则会对杀软查杀带来新的挑战。企业用户应尽可能小心打开来源不明的文档，如有需要可通过打开Office Excel中的：文件-选项-信任中心-信任中心设置-宏设置，来禁用一切宏代码执行：

  

![image.png](https://image.3001.net/images/20181030/1540873210_5bd7dbfa0020a.png!small)

目前，基于360威胁情报中心的威胁情报数据的全线产品，包括360威胁情报平台（TIP）、天眼高级威胁检测系统、360
NGSOC等，都已经支持对此类攻击以及对该类免杀漏洞利用样本的精确检测。360威胁情报中心的自研查杀引擎也可以独家静态提取攻击样本中的宏以及ShellCode利用代码：

  

![image.png](https://image.3001.net/images/20181030/1540873214_5bd7dbfe8bb0f.png!small)

## IOC

**MD5**  
---  
f4f785cc911925b8a2dd2bd2b2d1b6ef  
**URL**  
https://jplymell.com/dmc/InvoiceAug5e1063535cb7f5c06328ac2cd66114327.pdf  
**CC**  
linkadrum.nl  
  
## 参考

[1].https://outflank.nl/blog/2018/10/06/old-school-evil-excel-4-0-macros-xlm/

[2].https://msdn.microsoft.com/en-us/library/cc313154(v=office.12).aspx

[3].https://imminentmethods.net

  

