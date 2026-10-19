## **概述**

近期，奇安信病毒响应中心在日常威胁追踪中发现，一例针对俄罗斯鄂木斯克州，一家与石油相关的公司的攻击活动。攻击入口依旧为邮件，通过向公司公开邮箱中发送诱饵邮件获得攻击入口。攻击目的为植入后门程序以及获取目标机器上的浏览器本地凭证信息。

从样本中字符串分析来看攻击者做了充分的准备，对俄罗斯用户上网习惯较为熟悉，PE样本中列出大量与俄罗斯用户的用户习惯息息相关的字符串，并且多个字符串都与银行相关。从样本分析结果关联发现该木马为RTM家族木马。

## **样本分析**

###  **诱饵文件**

发送的诱饵邮件内容使用语言为俄文,内容与金额核对有关:

![ae01c751-a832-4ac6-97f9-d54cb04d8bfa.png](https://shanghai.lx.qianxin.com/bsafe/ae01c751-a832-4ac6-97f9-d54cb04d8bfa.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=87b00384e4292e5bfd6320f333f6c3c636c217302d21b8054650a905e7f8d6d9)

内容翻译如下:

![84d85b9b-462b-4f34-85cb-2b3d73a82149.png](https://shanghai.lx.qianxin.com/bsafe/84d85b9b-462b-4f34-85cb-2b3d73a82149.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=adb38f1c7ae1f3a1b03e48637b7d8bdf6f474cb3471ee3661623f2b40e251989)  

邮件中有一个名称为Сверка за сегодня的压缩文件,中文翻译名称为”今日核对”,压缩文件解压之后里面附带一个可执行文件,该文件为一个下载器:

![51d73e89-734a-4190-b5b9-3bbd0156f65b.png](https://shanghai.lx.qianxin.com/bsafe/51d73e89-734a-4190-b5b9-3bbd0156f65b.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=9c3675ce645d56b446aad0f89a4a6e8a2033d1e777b03e492259e4e65fbf87b4)

邮件发送人是俄罗斯罗斯可莫能源公司(Roskommunenergo),发件人为Елена Куликова pts@rcen-nt.ru。

收件人邮箱为” info@oms.transneft.ru”,该邮箱是俄罗斯鄂木斯克州一家与石油相关的公司:

![617b1ef9-fc93-4217-9ba9-ee8889320dea.png](https://shanghai.lx.qianxin.com/bsafe/617b1ef9-fc93-4217-9ba9-ee8889320dea.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=7a47917f5eca614d6979faaf4ee71f438da8db160943873bbd97c38f2dfb5b47)  

### **Loader分析**

名称| Сверка за сегодня.exe  
---|---  
MD5| CDA842C3115A**D25B89360E547DD79B  
  
该EXE在main函数中插入了一些无功能的代码,实际功能是保存在.text段中的ShellCode:

![e6d202d5-39d6-45a0-9862-549f91fbe687.png](https://shanghai.lx.qianxin.com/bsafe/e6d202d5-39d6-45a0-9862-549f91fbe687.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=8603f876febd6bae6c0e931b8b66042160f004f123261003f14705ff3d7f3c6a)

ShellCode中申请空间,并解密保存在PE中的数据,随后调用第二段ShellCode:

![1627e95b-1c0b-48cc-9762-4ece118fd4fa.png](https://shanghai.lx.qianxin.com/bsafe/1627e95b-1c0b-48cc-9762-4ece118fd4fa.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=15a2205c9a5bd92828f8b3d222c67c672f681c2546d325c32eaad4c67f2aff55)

第二段ShellCode中继续申请空间拷贝PE文件保存的加密数据,并对其解密,解密算法为每四字节异或0x954132AC,得到的数值与自己相减:

![ecab13f1-08f7-4e46-94c2-f881e7096f30.png](https://shanghai.lx.qianxin.com/bsafe/ecab13f1-08f7-4e46-94c2-f881e7096f30.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=8beb2096f111ab0354ab6d85fa8ac5ede6a614322478f6eae3a31e978aad6298)

解密完成为另一个PE文件,即Loader的真正代码功能,由Delphi编写:

![3d95f361-27f1-4785-b1d3-7a5d7d7a62b9.png](https://shanghai.lx.qianxin.com/bsafe/3d95f361-27f1-4785-b1d3-7a5d7d7a62b9.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=86a80ff9b16c4d1ee45cdfbe2815a35420df3df453bc48cba6a14e2d600e7018)

### **Delphi PayLoad分析**

启动之后会检测当前进程的参数个数,如果无参则会指定参数并重新创建进程:

![dac9a21d-4dde-4066-aef5-8ce63ca5dcf0.png](https://shanghai.lx.qianxin.com/bsafe/dac9a21d-4dde-4066-aef5-8ce63ca5dcf0.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=bcff1f45af28bc595ed32266cd69d276c2561242f8d239eae72e1098090833ca)

获取IE浏览器的缓存数据:

![30c01cc3-2037-411d-81cf-28112b5440b1.png](https://shanghai.lx.qianxin.com/bsafe/30c01cc3-2037-411d-81cf-28112b5440b1.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=a5f8259068a5727cdfd606e5c0ada5dd676fb25d829706338f9252ecb4ce6dcd)

获取缓存数据之后会先检查头四个字节是不是”http”,如果是则继续与PE中硬编码的字符串比较,来看是不是攻击者感兴趣的数据:

![4cdaeb6c-c81a-4851-8c8c-79f9abc4644c.png](https://shanghai.lx.qianxin.com/bsafe/4cdaeb6c-c81a-4851-8c8c-79f9abc4644c.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=717a9db592568577aa7ae26519a9ac2fb3a625b750b98bfb9e4d55d1c16aad52)

字符串列表,列表中字符串与银行有关:

bc.rshb  
---  
i.vtb.ru  
bsi.dll?  
online.payment.ru  
/ic/login.zhtml  
bankline.ru  
/servlets/ibc  
faktura.ru  
/iclient/  
ibank2  
elba.raiffeisen  
elbrus.raiffeisen  
handybank.  
wupos.westernunion  
bco.vtb24  
bo.vtb24  
dbo.vtb.  
online.sberbank.  
minbank.ru  
e-plat.mdmbank  
link.alfabank  
click.alfabank  
ib.avangard  
ibc.vuzbank  
ibc.ubrr  
my.modulbank  
online.centrinvest  
cb.mtsbank  
vbo.mkb  
i.bspb.ru  
/vpnkeylocal  
sci.interkassa  
ibank.mmbank.  
blockchain.info  
cb.asb.by  
bps-sberbank.by  
dbo2.bveb.by  
ibank.bsb.by  
corporate.bgpb.by  
ibank.alfa-bank.by  
ibank.belinvestbank.by  
ib2.ideabank.by  
client.paritetbank.by  
ibank.priorbank.by  
client.mybank.by  
online.stbank.by  
client.belapb.by  
  
随后获取缓存文件路径,拼接要访问的文件路径来拼接出Chrome浏览器的缓存文件:

路径一共2个,分别是” Google\Chrome\User Data\Profile2\History”和”Google\Chrome\User
Data\Default\History”。

![a8b73888-b734-4ac4-973a-016443ac1978.png](https://shanghai.lx.qianxin.com/bsafe/a8b73888-b734-4ac4-973a-016443ac1978.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=00fe810e5810e79a88b0f829c4bb052bf5461f3b954dd564c80f3a03ce4efffe)

获取文件属性:

![253c1725-bf5a-4439-8484-b5194ba6ca61.png](https://shanghai.lx.qianxin.com/bsafe/253c1725-bf5a-4439-8484-b5194ba6ca61.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=62226d4b0aeaaed467e1b3e9ef1fbba4daf91db8b7028479ff50bec66c3d2536)

将Chrome的历史文件拷贝到Temp目录下：

![e3b09910-3979-4e5b-a95b-76e3ca28eb87.png](https://shanghai.lx.qianxin.com/bsafe/e3b09910-3979-4e5b-a95b-76e3ca28eb87.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=d8d377672b0537e3687cd8f2be51923d65080358cc01092c26bad76b3168e86c)

通过FileMapping的方式将Chrome文件的历史记录映射到当前进程的内存中:

![38e8fa69-747b-443f-b193-ea1a2655987a.png](https://shanghai.lx.qianxin.com/bsafe/38e8fa69-747b-443f-b193-ea1a2655987a.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=c2e6f3b360d779828a1868b591167b8dd957e74d5aaeff39390a75467d31ffd0)

映射之后会循环递增，通过与0x70747468比较来定位文件中“http”字符串的位置，直到找到跟URL相关的数据，至此重复之前获取IE历史记录的步骤：

![04e27c82-2c6b-4146-8ed5-e4da769b07d1.png](https://shanghai.lx.qianxin.com/bsafe/04e27c82-2c6b-4146-8ed5-e4da769b07d1.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=c2f5915ee2e5ebf5832996f48db5f4fbb6dafb8403e127f5abefbfc638553545)

以及获取FireFox的历史记录：

![3527942c-6294-4b5d-a7c7-443c08eeda84.png](https://shanghai.lx.qianxin.com/bsafe/3527942c-6294-4b5d-a7c7-443c08eeda84.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=1019bdc592a4167b091c6656887a43e14ca0bd7efe8a173cbcae72816e7d1817)

浏览器历史记录获取完成之后会遍历文件，查找是否存在特定文件：

![ce5612b2-e6dd-486c-8cbb-8af7a543f1a4.png](https://shanghai.lx.qianxin.com/bsafe/ce5612b2-e6dd-486c-8cbb-8af7a543f1a4.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=f08ca48cf514efb2d174bf38352162a8abbaadcdf2b00aa0165f9eed714a6c04)

![b988f66c-85d3-4ff9-956d-5525d359ab35.png](https://shanghai.lx.qianxin.com/bsafe/b988f66c-85d3-4ff9-956d-5525d359ab35.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=50d8dd2a7a4de7298121591928ae02e1c77560bf6f61397b2b07c3f676bafa38)

文件名列表如下：

wclnt.exe  
---  
cbmain.exe  
bssax.ocx  
ibank.odb  
client.jks  
intpro.exe  
cbsmain.dll  
sbgclient.exe  
1cv8.exe  
1cv8c.exe  
1cv8s.exe  
1cv7.exe  
1cv71.exe  
1cv7s.exe  
winpost.exe  
clbank.exe  
qiwicasbier.exe  
iscc.exe  
webmoney.exe  
wallet.dat  
ifobsclient.exe  
transaq.exe  
maratl.exe  
_ftcgpk.exe  
ip_client.exe  
el_cli.exe  
bbclient.exe  
scdbo_.t.exe  
obcryptoapp.exe  
  
在获取了IE、Chrome、FireFox以及枚举完文件之后会链接服务器通过Http协议Get数据，从服务器获取插件的逻辑有2种。

一种方式是下载一个PE文件在内存中加载PE执行：

请求数据：

![23d58ea5-9eab-4ecb-9df3-bd1883b11642.png](https://shanghai.lx.qianxin.com/bsafe/23d58ea5-9eab-4ecb-9df3-bd1883b11642.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=f407500d1d58ace32268b972bd9649431b5b9e1b639f388e9bdfca09f2dea137)

数据请求完成之后解密,参数分别为Buff以及长度:

![e9bc8eac-f18e-4963-a1aa-a6bde2d157e6.png](https://shanghai.lx.qianxin.com/bsafe/e9bc8eac-f18e-4963-a1aa-a6bde2d157e6.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=9ccf03cc2b4905df9db6052feb3521da78a35cc99a5f4a15b88b52307e36eeb9)

解密完成之后是一个PE文件:

![ff47ee04-ac42-4569-88fa-25d2971bf153.png](https://shanghai.lx.qianxin.com/bsafe/ff47ee04-ac42-4569-88fa-25d2971bf153.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=9cd675b968c66c77d17ceca70bae0fc9bfc9e8d876427f03051ecd433f4f5a4b)

解密算法如下:

![da630***-3432-4fa2-88e0-a1e9aa08a7a2.png](https://shanghai.lx.qianxin.com/bsafe/da630***-3432-4fa2-88e0-a1e9aa08a7a2.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=7dfedd0bac5d7c13687c0c6466491337a3f567b40381a5ffef744eaba277b1e4)

随后申请空间,修改内存属性之后获取PE文件的导出函数”start”并调用:

![568ff9f4-145e-4fb8-9a13-56d3c186aa29.png](https://shanghai.lx.qianxin.com/bsafe/568ff9f4-145e-4fb8-9a13-56d3c186aa29.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=aa18ab37f9339b474319a6e90314d3ceceb05caa2e60275422c4424bc2d35474)

另一种是在获取完浏览器缓存之后请求一个DLL，并保存在Temp目录下，通过RunDll32执行。

![879eeff3-4dbf-42a9-a027-7230579ca3fb.png](https://shanghai.lx.qianxin.com/bsafe/879eeff3-4dbf-42a9-a027-7230579ca3fb.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=f5abab27e6c38e8f00a31b8a909f9466eed098e10fedbfe4c4be6df859d1ce89)

进程创完成之后给服务器发通知包：

![b5d4186b-10b3-480b-98d7-932cdcc57250.png](https://shanghai.lx.qianxin.com/bsafe/b5d4186b-10b3-480b-98d7-932cdcc57250.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=b3a403c6f941fefb7e5db44aa5e57a8efcea78dc1a3a5cb56cc89b3746fd879f)

## **PayLoad Rundll32执行的DLL分析**

该DLL OEP中插入了大量的Push Retn来修改程序EIP：

![864c91e0-36c6-47d1-bc4c-45a1b251b95a.png](https://shanghai.lx.qianxin.com/bsafe/864c91e0-36c6-47d1-bc4c-45a1b251b95a.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=54a9615875421f1dfff1656230b278ecd5ca12a5655f3e7aca2296bf42040f9d)

最终会跳到主要功能代码中，随后调用ViritualAlloc申请空间将PE文件中保存的加密数据拷贝到申请的空间：

![3a88d2d0-77a9-4f61-96cc-6bddf021859a.png](https://shanghai.lx.qianxin.com/bsafe/3a88d2d0-77a9-4f61-96cc-6bddf021859a.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=ec458f9b07eb23486879f77a8c82893cc75e59b5500b85e1b86233e366aa5f0e)

随后循环解密，解密算法如下：

![e16ae877-1ae3-4255-8d2e-17985f862d00.png](https://shanghai.lx.qianxin.com/bsafe/e16ae877-1ae3-4255-8d2e-17985f862d00.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=faa43b18768ab4844a03a65308d23c0ee106d1921cfb07b48a6ecf61e0f6f076)

最终在内存中释放出另一个PE文件，找到该DLL的导出函数GetClassObject并传参调用。

![ff8ecd96-33e5-4412-88db-6fa952e20cfe.png](https://shanghai.lx.qianxin.com/bsafe/ff8ecd96-33e5-4412-88db-6fa952e20cfe.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=3eaa3f825712523c71cd77684ff69ae53b7ccd8dd70253d89e3b9abbd6f09c10)

该DLL调用的多个API都是动态调用，在调用之前通过GetProcAddress获取函数地址保存在全局变量中：

![052cbba3-9895-49a7-afe4-25c7da73da67.png](https://shanghai.lx.qianxin.com/bsafe/052cbba3-9895-49a7-afe4-25c7da73da67.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=9aeb2910b4581098f4e845f69b99b1358538b5eee6a2b0dc37bbf204a2103e99)

获取当前进程的SID信息来判断当前进程的权限等级：

![693a4f5f-a4c3-4afa-a574-cd095dfef7aa.png](https://shanghai.lx.qianxin.com/bsafe/693a4f5f-a4c3-4afa-a574-cd095dfef7aa.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=dd56bfb13a68a0eca1c03eb4eb527f28495bbf9b6e4d6eb4a96b52db0f9fab64)

判断逻辑是如果返回值大于等于0x2000即大于等于SECURITY_MANDATORY_MEDIUM_RID：

![1c785b64-89c0-46ca-8230-9477855107a6.png](https://shanghai.lx.qianxin.com/bsafe/1c785b64-89c0-46ca-8230-9477855107a6.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=3db8f2eb2f25e694f4c064541a374d9452fec5813a18d6d3782811e2352e6625)

获取ProgramData的路径并拼接出一个新的文件夹路径，通过GetFileAttributesW返回值判断文件夹是否存在，如果不存在则调用CreateDirectoryW创建该文件夹，用以将Temp下的文件拷贝一份到指定目录下：

![e49be2d8-9b3d-46b8-9d62-5b97f30f4604.png](https://shanghai.lx.qianxin.com/bsafe/e49be2d8-9b3d-46b8-9d62-5b97f30f4604.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=ff860e6783d077b510697022adba728fdc86cb44f0b14089cf16f472f6bf2951)

创建文件夹之后读取当前自身文件：

![956741aa-387e-4360-a8f9-c859239c6e46.png](https://shanghai.lx.qianxin.com/bsafe/956741aa-387e-4360-a8f9-c859239c6e46.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=3aebdf3bff5a5572bbb56a38d6a879f7771baf13ff9f1badb8258c4f63ab54e4)

  

随后创建文件，将当前进程文件拷贝到ProgramData路径下：

![275f6d33-6b47-4a87-ad49-2949402490da.png](https://shanghai.lx.qianxin.com/bsafe/275f6d33-6b47-4a87-ad49-2949402490da.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=51e43a4ffb0e5b143355e68f6198975703e0631f053765c5b9cabbdae9a8a33f)

还会判断当前进程名称是不是Rundll32.exe:

![01906fad-cc92-417b-a4cc-73818bd75102.png](https://shanghai.lx.qianxin.com/bsafe/01906fad-cc92-417b-a4cc-73818bd75102.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=73c6e6d824b9a98fc7a624c71249d1de4240f7556b5486aba9407ea1ddf6b39a)

通过计划任务达到持久性攻击的目的:

![e3229c1c-c5d8-40da-bbfc-c26000ec4307.png](https://shanghai.lx.qianxin.com/bsafe/e3229c1c-c5d8-40da-bbfc-c26000ec4307.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=845926605e1aa6bb85fa6c5535ce224f582a9ea021e8339669dfd1e3b45d84b4)

该程序附带多个后门功能，通过InternetReadFile从服务器读取的数据来解析控制码从而执行不同的流程：

设置键盘钩子：

![c6cdf50f-5c2e-4e65-853b-9a244f6a8a8b.png](https://shanghai.lx.qianxin.com/bsafe/c6cdf50f-5c2e-4e65-853b-9a244f6a8a8b.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=266021be2e29e6869daacee8c7349fd64930564a403694980a3fc647ba9aefcb)

会通过DDE系列函数循环读取Figure类型窗口的信息：

![bcf08f0f-d77d-44ca-9e71-da0f28f3784d.png](https://shanghai.lx.qianxin.com/bsafe/bcf08f0f-d77d-44ca-9e71-da0f28f3784d.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=e1a574dd359c862abffc4c4829924d18e183b03f82c1ffa91fa3f736a773273f)

窗口列表如下：

SunAwtFrame  
---  
SunAwtDialog  
TLoginWindow  
fmISClient  
TfmISClient  
TInitialform  
TSYSCustomForm  
ДБО BS-Client  
Райффайзенбанк - система ELBRUS.erConfigurationWhere IPEnabled = True  
ЗАО "Инверсия"  
“E-Plat”  
ALBO  
Альфа-Клик.n  
АвангардИнтернет-банк  
АО "ВУЗ-банк"  
ПАО КБ "УБРиР".ет-банк  
Модульбанк - Личный кабинет  
SberbankBusiness Online  
МКБ Интернет-банк.Online  
МИнБанкБизнес Online  
  
获取当前系统信息，包括用户名、计算机名、时区、默认语言、Kernel32版本信息、系统版本信息以及当前进程的权限：

![0910678a-547b-497c-a9f2-20e67c2548a3.png](https://shanghai.lx.qianxin.com/bsafe/0910678a-547b-497c-a9f2-20e67c2548a3.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=e4b9e190326208d2c26a9a98dc87e31f5718603f2878e061f7e157b80c4bb3e1)

随后连接服务器：

![d9de8020-dc84-4b7a-b116-2cf82e98601c.png](https://shanghai.lx.qianxin.com/bsafe/d9de8020-dc84-4b7a-b116-2cf82e98601c.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=87301dc348b2333df17aa01618c10c984e7366ea2a80060***56006c40f34cde)

该程序功能齐全，是个典型的后门程序：

读取SCARD信息：

![63e067cf-68dc-48bc-8a9e-2107f6a47c52.png](https://shanghai.lx.qianxin.com/bsafe/63e067cf-68dc-48bc-8a9e-2107f6a47c52.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=b761fcc97bf7feefbddef116e20a082f6ed92346c56bd3bb20130070d20d19d8)

读取PCSC设备信息：

![ca109511-8bad-41fd-a73e-9a139da3029c.png](https://shanghai.lx.qianxin.com/bsafe/ca109511-8bad-41fd-a73e-9a139da3029c.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=24858f18fbc822ae19a049f74bcbb0468c6038741f6aa2b4954cc72a749fc662)

保存插件并调用ShellExecute执行：

![559ec7e8-8be5-4979-957c-b5604b80158d.png](https://shanghai.lx.qianxin.com/bsafe/559ec7e8-8be5-4979-957c-b5604b80158d.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=6e65adb7ae76cca9f4e805955ba3e39767e5b2ecd5d4d78df6f3aad9920c9616)

保存插件为DLL并加载：

![2c036b00-dd33-4eb0-8ea8-96c140f78025.png](https://shanghai.lx.qianxin.com/bsafe/2c036b00-dd33-4eb0-8ea8-96c140f78025.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=bb188d116f338b60303e390e74e871c4e125cfcda5d39b1a0af68011a2ac01cd)

执行从服务器下载的ShellCode：

![77692503-401d-4fe0-a9e8-ab6f25d4b10a.png](https://shanghai.lx.qianxin.com/bsafe/77692503-401d-4fe0-a9e8-ab6f25d4b10a.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=4d995a59601a9eaff17fdeab8857d0e972ca928eaee1325ef4aa512d571fdd52)

注册表读取：

![a46b25ef-4afe-4dff-80dc-5f8c1b31b968.png](https://shanghai.lx.qianxin.com/bsafe/a46b25ef-4afe-4dff-80dc-5f8c1b31b968.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=ba44ff7daf6a983c588cb0bddc69f0c72b741598558225ff634c9bef247e6e28)

创建不同Seeion的进程：

![3d8eb21c-da41-4279-81f8-49f379530011.png](https://shanghai.lx.qianxin.com/bsafe/3d8eb21c-da41-4279-81f8-49f379530011.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=711bd4462c91e02eda673d6366795fa31038e1489329b700467b2d80b193ec8c)

进程提权：

![a99ea145-f7f0-4390-93f0-d327367be58d.png](https://shanghai.lx.qianxin.com/bsafe/a99ea145-f7f0-4390-93f0-d327367be58d.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=2e31994943b758039f0eeb03df52a71fd62fbc85d178661af42d07c86a9a83c2)

文件读写操作：

![d88103ea-09a9-41f3-a6aa-557d1e22a37c.png](https://shanghai.lx.qianxin.com/bsafe/d88103ea-09a9-41f3-a6aa-557d1e22a37c.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=e0ec98fc2eb76ce0167713e798b9d5594d311d4c8b2fae91f54684c8d9bbb888)

Socket通信：

![f24b830a-d435-4c1e-9cc2-a6ad1ef9fe28.png](https://shanghai.lx.qianxin.com/bsafe/f24b830a-d435-4c1e-9cc2-a6ad1ef9fe28.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=54431e429be614306647945f10798a2dd538be0a5d2e4b3f7f6807ad9a285dcc)

屏幕截图：

![a0666707-b831-4433-b119-829e8401a415.png](https://shanghai.lx.qianxin.com/bsafe/a0666707-b831-4433-b119-829e8401a415.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=5e155698f2f19794891e5c0e46ee37a40c980618e3e9cd7c39cea89fa1b83dc7)

从功能上看该程序功能齐全，包含进程、文件、注册表以及网络通信等功能，还支持后续插件功能扩展，是一个典型的后门程序。

## **PayLoad 内存加载的PE分析**

主要获取Chrome在Temp中保存的数据，该文件是一个SQLite3格式的数据库文件，打开后如下，保存的包括用户登录信息，对应网站的账号密码等：

![cbd3f5bd-3ce6-44c5-89de-86a00524a065.png](https://shanghai.lx.qianxin.com/bsafe/cbd3f5bd-3ce6-44c5-89de-86a00524a065.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=404a80093ac9c0655c61882ce3cbcd2c04d63b492efda71fbc370714a0a65e67)  

  

随后调用SQL语句查询数据库：

![9ad0b5e2-7697-4016-bbda-8cb9bf8c3ed7.png](https://shanghai.lx.qianxin.com/bsafe/9ad0b5e2-7697-4016-bbda-8cb9bf8c3ed7.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=dac476c0856823a2bfa21503068a171f3a66fd1e2***b57084e3ac1799d99f6e)

获取kometa软件保存的数据库信息：

![74c56967-64e4-41f8-953a-d870905502fe.png](https://shanghai.lx.qianxin.com/bsafe/74c56967-64e4-41f8-953a-d870905502fe.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=52840faf75013eb410dfa8f52d7f412f882c6a58dbc53105700daded9a62222a)

获取orbitum浏览器保存的数据库信息：

![b406a205-447d-4b4a-9929-1c30eb365ed4.png](https://shanghai.lx.qianxin.com/bsafe/b406a205-447d-4b4a-9929-1c30eb365ed4.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=62304b86f5a1132713e26e23d846c092c4aee19947d13129be88a9a52ca29a19)

获取Opera浏览器数据库信息：

![62277cb2-85e4-4476-acee-d34e7bf6a7b2.png](https://shanghai.lx.qianxin.com/bsafe/62277cb2-85e4-4476-acee-d34e7bf6a7b2.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=0d66381bb9fc5255615bfaf931f7d881f22bdf8ed3353328d01d6676d2986d14)

获取yandex浏览器数据库信息：

![3387aa6e-427f-4e74-9ed8-8b394394e44a.png](https://shanghai.lx.qianxin.com/bsafe/3387aa6e-427f-4e74-9ed8-8b394394e44a.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=063be110a756ac992cf1e318852cc115b07ece3a5db4c7d44d8ebe0af6968ca4)

获取Amigo浏览器数据库信息：

![160029e5-753b-4072-a433-022f1ef4d51b.png](https://shanghai.lx.qianxin.com/bsafe/160029e5-753b-4072-a433-022f1ef4d51b.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062008Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=03c561507bb889f5139b4006305e0cba7ee0bb214277c5eb7c9fec87783b3ebb)

获取Firefox浏览器数据库信息：

![18780045-db52-4f1c-919a-4b622bf88791.png](https://shanghai.lx.qianxin.com/bsafe/18780045-db52-4f1c-919a-4b622bf88791.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062220Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=7380a850015427a18e8a42e497fdd1631b2443519646f98b8949379ada7eedf1)

获取thunderbird保存的用户信息：

![5a783d78-58a7-4c4f-b638-c4c72f17d643.png](https://shanghai.lx.qianxin.com/bsafe/5a783d78-58a7-4c4f-b638-c4c72f17d643.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062220Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=962411582126a480188642cfa6737712f8df26eb17355177212de59cf7ee9f45)

获取IE浏览器保存数据：

![ed2e2f53-e3b7-4370-b083-ca58410af633.png](https://shanghai.lx.qianxin.com/bsafe/ed2e2f53-e3b7-4370-b083-ca58410af633.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062220Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=b975889728b9fb9df7cef069c51295612da450235153d9738381bc98ff93911c)

通过注册表查询OutLook保存的数据：

![83eb1a84-683c-4a6d-a386-2db61c09b069.png](https://shanghai.lx.qianxin.com/bsafe/83eb1a84-683c-4a6d-a386-2db61c09b069.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062220Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=3bcd0ac4d84e373f2e135eca840d30aeeb1997af372514ca3b99372769837ba7)

获取incredimail邮箱软件数据：

![2df6f5fd-c6d0-4ff9-89a9-3d350e394bda.png](https://shanghai.lx.qianxin.com/bsafe/2df6f5fd-c6d0-4ff9-89a9-3d350e394bda.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062220Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=0c1f8766017e5a7ac4b4ef6b543fab17c2c3cacab9e75b16d6ccda8f0fd4d5ef)

获取WindowsMail数据信息：

![4f0af931-5609-43d9-8a5b-a368f5f462bc.png](https://shanghai.lx.qianxin.com/bsafe/4f0af931-5609-43d9-8a5b-a368f5f462bc.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062220Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=d47a7635e51d070e821280e6f183d0344d35ac53e80f85ea0233500996084cdc)

获取完成之后发送给服务器：

![39d0b645-8929-4bd3-8c88-3c8085da1958.png](https://shanghai.lx.qianxin.com/bsafe/39d0b645-8929-4bd3-8c88-3c8085da1958.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=RORI4SUJR6CTECQDOGNE%2F20191129%2Fshanghai%2Fs3%2Faws4_request&X-Amz-Date=20191129T062220Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=eb86488f6e8c1bdad6057b10ed34135d592b6e5f56ae01419d00d3c09e19f45a)

## **总结**

从攻击者手法上来看，攻击者依托诱饵邮件诱导用户执行从而获得攻击入口。样本通过多次内存释放PE，并且关键PayLoad托管在远程服务器上，并支持在内存中执行，增大了分析人员的分析难度。

攻击者利用普通用户不设防心里对攻击目标实施攻击。奇安信病毒响应中心提醒用户谨慎打开未知文档以及邮件，预防此类恶意样本攻击。

目前奇安信集团全线产品，包括天眼、SOC、态势感知、威胁情报平台，支持对涉及MYEC黑客团伙的攻击活动检测。奇安信天擎终端防护产品内置的EDR检测机制通过恶意代码的行为分析，支持对该组织此类样本的检测和查杀。  

  

## **IOCs**

C&C：

85.217.171.43/viewtopic.php?f576=501?f948=636d6d?f783=434d4d2d5043

85.217.171.43/viewtopic.php?f576=0?f948=636d6d?f783=434d4d2d5043

85.217.171.43/g_38472341.php

85.217.171.43/viewtopic.php?f576=501&e=0

185.203.119.111：80

MD5:

AA9E518A72D776E4ACE2EB5FA1329899

CDA842C3115A**D25B89360E547DD79B

6697F31EA7E27E8871B729A28FC96F4E

C0B24F70394A71E0B37A834352FA58BA

​

