# ****事件概述****

Trigona是一个新兴的勒索软件家族，该家族于2022年中下旬首次出现以来一直处于活跃状态。近期，矢安知深攻防实验室经过持续追踪，发现该勒索软件家族分别新增了Linux平台与Win64平台恶意样本。表明该威胁行为者正在积极开展勒索软件业务，希望广大用户提高安全意识，注意防范。

Trigona勒索家族摘要  
  
---  
  
首次出现

|

2022年中下旬  
  
针对目标

|

全球用户  
  
针对行业

|

金融、建筑、制造、农业、市场营销等高科技行业  
  
传播方式

|

Microsoft SQL弱口令爆破  
  
加密算法

|

AES、RSA  
  
加密后缀

|

_locked  
  
支付方式

|

门罗币  
  
能否解密

|

无法解密  
  
赎金通知

|

how_to_decrypt.hta、how_to_decrypt.txt  
  
联系方式

|

farusbig@tutanota[.]com、phandaledr@onionmail[.]org、http://3x55o3u2b7cjs54eifja5m3ottxntlubhjzt6k6htp5nrocjmsxxh7ad[.]onion/  
  
#  ** **样本分析****

本次样本通过伪装系统组件进行传播，样本执行时可通过多个特定参数执行不同操作。首先判断是否存在命令行参数：

![1689068564_64ad24145c17a1b667a15.png!small](https://image.3001.net/images/20230711/1689068564_64ad24145c17a1b667a15.png!small)

下表分别对各参数进行说明：

命令

|

描述  
  
---|---  
  
/shdwn

|

加密后强制关机  
  
/r

|

允许以随机顺序加密文件  
  
/full

|

加密目标文件的全部内容（如果未指定，则仅加密前512kb数据）  
  
/erase

|

删除目标文件内容，默认只删除前512kb数据  
  
/!autorun

|

不创建Run注册表项  
  
/is_testing

|

测试/test_cid和/test_vid  
  
/test_cid

|

使用指定的计算机ID  
  
/test_vid

|

使用指定的用户ID  
  
/p

|

指定加密路径  
  
/path

|

指定加密路径  
  
/!local

|

不加密local文件  
  
/!lan

|

不加密网络共享  
  
/autorun_only

|

创建Run注册表项  
  
如果未指定命令行参数则通过计算机名称和系统目录时间计算CID，然后设置Run注册表键实现持久化：

![1689068571_64ad241bca6691e26424d.png!small](https://image.3001.net/images/20230711/1689068571_64ad241bca6691e26424d.png!small)

解析完命令行参数后，Trigona会从资源目录中读取名为“CFGS”的配置文件，该配置文件以字符串资源形式存储在程序中：

![1689068577_64ad2421b952d0fd777ac.png!small](https://image.3001.net/images/20230711/1689068577_64ad2421b952d0fd777ac.png!small)

获取配置文件以后在内存中生成勒索信，该勒索信以指定模板生成，然后用CID等信息进行填充，以下是一个通用的勒索信模板：

    
    
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
    
    <html>
    
    <title>ENCRYPTED</title>
    
    <hta:application showInTaskBar="no" APPLICATION="yes" ICON='msiexec.exe' SINGLEINSTANCE='yes' SysMenu="no" applicationname="ENCRYPTED" border="thick" contexmenu="no" scroll="no" selection="yes" singleinstance="yes" windowstate="normal" MAXIMIZEBUTTON="NO" BORDER="DIALOG" width="100" height="100" MINIMIZEBUTTON="NO"></hta:application>
    
    <script language="JavaScript">
    
      var authkey = '';
    
      var email = '[SUPPORT]';
    
      var url = 'http://3x55o3u2b7cjs54eifja5m3ottxntlubhjzt6k6htp5nrocjmsxxh7ad.onion/';
    
      var vid = '[VID]';
    
      var cid = '[CID]';
    
      var uniqueid;
    
     
    
      function Start() {
    
        window.resizeTo(658,500);
    
        
    
        if (vid == '') {
    
          uniqueid = cid;
    
        } else {
    
          uniqueid = vid;
    
        }
    
      }
    
      function copytext(s) {
    
        window.clipboardData.setData("Text", s);
    
        alert('Auth Key copied to clipboard');
    
      };
    
      function openpage(url) {
    
        window.clipboardData.setData("Text", url);
    
        alert('URL copied to buffer. Open it in TOR Browser');
    
      }
    
      function help() {
    
        window.clipboardData.setData("Text", uniqueid);
    
        alert('If you have trouble with the main contacts, write to '+email+'. Your ID copied to buffer');
    
      }
    
      function document.onkeydown() {
    
        var alt = window.event.altKey;
    
        if (event.keyCode == 116 || event.keyCode == 27 || alt && event.keyCode == 115) {
    
          event.keyCode = 0;
    
          event.cancelBubble = true;
    
          return false;
    
        }
    
      }
    
      Start();
    
    </script>
    
     
    
    <body style="background: #ffffff; font: 12px 'Arial', sans-serif; padding: 0; margin: 0; overflow-x: hidden;" onload="Start();">
    
    <textarea style="display: none" id="authkey">[REG_CRT]</textarea>
    
    <div style="">
    
      <div style="width: 100%; height: 100%; position: absolute; top: 0; left: 0; box-sizing: border-box; padding: 0px; overflow-x: hidden;overflow-y: hidden; background-color: #ffffff;">
    
        
    
    <div style="background-color: #A0031D; box-sizing: border-box; width: 100%; padding: 14px 0;">
    
          <div style="text-align: center; color: #ffffff; font-size: 25px; font-weight: 700; text-transform: uppercase;">the entire network is encrypted <br>your business is losing money</div>
    
        </div>
    
     
    
        <div style="background-color: #ffffff; width: 600px; padding: 20px; box-sizing: border-box;">
    
          <div style="margin-right: 18px; float: left; width: 31%;">
    
            <span style="float: left; font-weight: 700; color: #F80129; margin-right: 2px;">▲</span>
    
            <div style="float: left; font-size: 12px; color: #000000; width: 170px;">All documents, databases, backups and other critical data were encrypted and leaked</div>
    
            <div style="clear: both; float: none; height: 18px; width: 100%;"></div>
    
          </div>
    
     
    
          <div style="margin-right: 18px; float: left; width: 31%;">
    
            <span style="float: left; font-weight: 700; color: #F80129; margin-right: 2px;">▲</span>
    
            <div style="float: left; font-size: 12px; color: #000000; width: 170px;">The program uses a secure AES algorithm, which makes decryption impossible without contacting us</div>
    
            <div style="clear: both; float: none; height: 18px; width: 100%;"></div>
    
          </div>
    
     
    
          <div style="float: left; width: 31%;">
    
            <span style="float: left; font-weight: 700; color: #F80129; margin-right: 2px;">▲</span>
    
            <div style="float: left; font-size: 12px; color: #000000; width: 160px;">If you refuse to negotiate, the data will be auctioned off</div>
    
            <div style="clear: both; float: none; height: 18px; width: 100%;"></div>
    
          </div>
    
          <div style="clear: both; float: none; height: 0px; width: 100%;"></div>
    
     
    
          <div style="border: 1px solid #e5e5e5; padding: 20px; box-sizing: border-box;">
    
            <div style="font-size: 14px; font-weight: 700; color: #000000; text-align: center;">To recover your data, please follow the instructions</div>
    
     
    
            <div style="margin-top: 10px;">
    
              <div style="float: left; margin-right: 10px; margin-left: 10px; width: 31%;">
    
                <div style="font-size: 40px; font-weight: bold; color: #e5e5e5; float: left; margin-right: 13px;">1</div>
    
                <div style="float: left; margin-top: 5px;">
    
                  <div style="font-size: 12px; color: #5E5C5C; margin-bottom: 3px;">Download Tor Browser</div>
    
                  <a href="https://www.torproject.org/dist/torbrowser/12.0.4/torbrowser-install-win64-12.0.4_ALL.exe" style="font-size: 14px; font-weight: 700; color: #0C94E0; text-decoration: none;" target="_blank">Download</a>
    
                </div>
    
                <div style="clear: both; float: none;"></div>
    
              </div>
    
     
    
              <div style="float: left; margin-right: 10px; margin-left: 10px; width: 31%;">
    
                <div style="font-size: 40px; font-weight: bold; color: #e5e5e5; float: left; margin-right: 13px;">2</div>
    
                <div style="float: left; margin-top: 5px;">
    
                  <div style="font-size: 12px; color: #5E5C5C; margin-bottom: 3px;">Open decryption page</div>
    
                  <a href="#" style="font-size: 14px; font-weight: 700; color: #0C94E0; text-decoration: none;" target="_blank" onclick="openpage(url); return false;">Copy</a>
    
                </div>
    
                <div style="clear: both; float: none;"></div>
    
              </div>
    
     
    
              <div style="float: left; margin-right: 10px; margin-left: 10px; width: 31%;">
    
                <div style="font-size: 40px; font-weight: bold; color: #e5e5e5; float: left; margin-right: 13px;">3</div>
    
                <div style="float: left; margin-top: 5px;">
    
                  <div style="font-size: 12px; color: #5E5C5C; margin-bottom: 3px;">Auth using this key</div>
    
                  <a href="#" style="font-size: 14px; font-weight: 700; color: #0C94E0; text-decoration: none;" onclick="copytext(authkey); return false;">Copy</a>
    
                </div>
    
                <div style="clear: both; float: none;"></div>
    
              </div>
    
     
    
              <div style="clear: both; float: none;"></div>
    
            </div>
    
          </div>
    
     
    
          <div style="margin-top: 18px; width: 100%;">
    
            <div style="float: left; font-size: 12px; color: #5E5C5C;">The price depends on how soon you will contact us</div>
    
            <a href="" style="float: right; font-size: 12px; color: #0C94E0; text-decoration: none;" onclick="help(); return false;">Need help?</a>
    
            <div style="clear: both; float: none;"></div>
    
          </div>
    
        </div>
    
     
    
        <div style="padding: 20px 30px; width: 600px; background-color: #f7f2f3; box-sizing: border-box;">
    
          <div style="float: left; margin-right: 21px;">
    
            <div style="float: left; font-size: 11px; color: #F80129; font-weight: 700; margin-right: 6px;">●</div>
    
            <div style="float: left; width: 110px;">
    
              <div style="font-size: 11px; font-weight: 700; color: #000000; margin-bottom: 2px; margin-top: 1px;">Don't doubt</div>
    
              <div style="font-size: 11px; color: #5E5C5C;">You can decrypt 3 files for free as a guarantee</div>
    
            </div>
    
          </div>
    
     
    
          <div style="float: left; margin-right: 27px;">
    
            <div style="float: left; font-size: 11px; color: #F80129; font-weight: 700; margin-right: 6px;">●</div>
    
            <div style="float: left; width: 103px;">
    
              <div style="font-size: 11px; font-weight: 700; color: #000000; margin-bottom: 2px; margin-top: 1px;">Don't waste time</div>
    
              <div style="font-size: 11px; color: #5E5C5C;">Decryption price increases every hour</div>
    
            </div>
    
          </div>
    
     
    
          <div style="float: left; margin-right: 27px;">
    
            <div style="float: left; font-size: 11px; color: #F80129; font-weight: 700; margin-right: 6px;">●</div>
    
            <div style="float: left;  width: 114px;">
    
              <div style="font-size: 11px; font-weight: 700; color: #000000; margin-bottom: 2px; margin-top: 1px;">Don't contact resellers</div>
    
              <div style="font-size: 11px; color: #5E5C5C;">They resell our services at a premium</div>
    
            </div>
    
          </div>
    
     
    
          <div style="float: left;">
    
            <div style="float: left; font-size: 11px; color: #F80129; font-weight: 700; margin-right: 6px;">●</div>
    
            <div style="float: left; width: 108px;">
    
              <div style="font-size: 11px; font-weight: 700; color: #000000; margin-bottom: 2px; margin-top: 1px;">Don't recover files</div>
    
              <div style="font-size: 11px; color: #5E5C5C;">Additional recovery software will damage your data</div>
    
            </div>
    
          </div>
    
     
    
          <div style="clear: both; float: none; height: 0px; width: 100%;"></div>
    
        </div>
    
      </div>
    
    </div>
    
    <script language="JavaScript">
    
    authkey = document.getElementById('authkey').value;
    
    </script>
    
    </body>
    
     
    
    </html>

模板中包含“[SUPPORT]”、“[CID]” 、“[VID]”等字段，在生成阶段使用指定内容进行替换，其中CID为受害者电脑标识，
VID为用户标识（部分样本中的VID可能为空）：

![1689068639_64ad245f9cba22e590969.png!small](https://image.3001.net/images/20230711/1689068639_64ad245f9cba22e590969.png!small)

检查%Temp%路径下是否存在名为“how_to_decrypt.hta”的勒索信，如果不存在则创建：

![1689068645_64ad24656c552041b24f9.png!small](https://image.3001.net/images/20230711/1689068645_64ad24656c552041b24f9.png!small)

勒索信以HTML应用程序（HTA）展现，通过内嵌的JavaScript代码引导受害者下载Tor浏览器，通过步骤2中的URL进行访问，并且提供了一个授权秘钥用于受害者和攻击者进行沟通谈判：

![1689068649_64ad24691e48cd9e3c4c7.png!small](https://image.3001.net/images/20230711/1689068649_64ad24691e48cd9e3c4c7.png!small)

创建勒索信以后，新建线程，遍历26个系统盘符准备加密：

![1689068655_64ad246f5a21d6d23f7e3.png!small](https://image.3001.net/images/20230711/1689068655_64ad246f5a21d6d23f7e3.png!small)

加密时会分别过滤“windows”、“system32”、勒索信和已加密的文件：

![1689068660_64ad24741f5a4f438d089.png!small](https://image.3001.net/images/20230711/1689068660_64ad24741f5a4f438d089.png!small)

然后使用Delphi的Dcpcrypt加密组件库进行加密，加密过程通过AES+RSA完成：

![1689068665_64ad24791b6bef9871edb.png!small](https://image.3001.net/images/20230711/1689068665_64ad24791b6bef9871edb.png!small)

加密后的文件以“._locked”扩展名作为结尾：

![1689068670_64ad247e55cb33bbda65d.png!small](https://image.3001.net/images/20230711/1689068670_64ad247e55cb33bbda65d.png!small)

近期新增的Linux平台样本，主要功能与上文样本基本一致，可以理解为Win平台的64位版本：

![1689068676_64ad248498ac90749b4ba.png!small](https://image.3001.net/images/20230711/1689068676_64ad248498ac90749b4ba.png!small)

Win64平台样本在原有代码基础上新增了5个命令行参数：

命令

|

描述  
  
---|---  
  
/sleep

|

执行前休眠  
  
/debug

|

在调试模式下执行，配合 /p 执行  
  
/log_f

|

指定日志文件  
  
/fast

|

/  
  
/allow_system

|

允许加密系统目录文件  
  
#  ** **文件解密****

由于AES与RSA算法的安全性，在没有秘钥的前提下用户很难对文件内容进行解密。此外恶意软件作者也在其网站上提供了一个用于解密的专属工具，受害者在提交勒索赎金后可以通过该工具对加密内容进行解密。但是我们并不推荐受害者进行该操作，因为你无法确保威胁行为者会履行任何承诺！

![1689068699_64ad249bcfdf678d0e61b.png!small](https://image.3001.net/images/20230711/1689068699_64ad249bcfdf678d0e61b.png!small)

#  ** **关联分析****

通过多个维度的关联分析，我们发现Trigona运营团队与CryLock
勒索软件在TTP方面存在多处重叠。例如：在勒索信方面，两个家族都有使用HTA作为载体的做法。并且在外网一个求助Crylock勒索软件帮助的帖子中，CryLock使用了与Trigona相同的邮箱地址。我们暂时无法确定两个家族背后的威胁行为者是否共享了某些恶意代码或其它资源，亦或者它们本就是同一个运营商下的两个勒索软件？

![1689068713_64ad24a9513c7ef1183f0.png!small](https://image.3001.net/images/20230711/1689068713_64ad24a9513c7ef1183f0.png!small)

#  ** **I**** ** **OC**** ** **s****

530967fb3b7d9427552e4ac181a37b9a

7049824f0e920e44e18c013ab07facbc

b3371f094f50e40ea6bc3af3e0c6d61c

af4708d7d196d2ce9defafe2bb3dd665

68635ad9d12f683071611bfd34c1ec34

