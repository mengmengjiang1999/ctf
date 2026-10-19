**![68747470733a2f2f63646e2e706272642e636f2f696d616765732f475475357645592e706e67.png](https://image.3001.net/images/20180512/15260802631472.png!small)**

**SpookFlare是一款可帮助你有机会绕过各种安全措施的工具，例如客户端检测和网络端检测的端点策略。SpookFlare还是Meterpreter，Empire，Koadic等的loader/dropper生成器。此外，SpookFlare还具有混淆，编码，运行时代码编译和字符替换的功能。因此，你大可在目标系统的技术人员了解，学习和掌握SpookFlare
payloads之前，用它来绕过目标系统的防护策略。**

> 混淆
>
> 编码
>
> 运行时代码编译
>
> 字符替换
>
> Patched Meterpreter Stage支持
>
> Blocked powershell.exe绕过
    
    
         ___ ___  ___   ___  _  _____ _      _   ___ ___ 
        / __| _ \/ _ \ / _ \| |/ / __| |    /_\ | _ \ __|
        \__ \  _/ (_) | (_) | ' <| _|| |__ / _ \|   / _| 
        |___/_|  \___/ \___/|_|\_\_| |____/_/ \_\_|_\___|
                Version    : 2.0
                Author     : Halil Dalabasmaz
                WWW        : artofpwn.com, spookflare.com
                Twitter    : @hlldz
                Github     : @hlldz
                Licence    : Apache License 2.0
                Note       : Stay in shadows!
     [*] You can use "help" command for access help section.
    SpookFlare > list
     ID | Payload                | Description                                                
    ----+------------------------+------------------------------------------------------------     1  | meterpreter/binary     | .EXE Meterpreter Reverse HTTP and HTTPS loader             
     2  | meterpreter/powershell | PowerShell based Meterpreter Reverse HTTP and HTTPS loader 
     3  | javascript/hta         | .HTA loader with .HTML extension for specific command      
     4  | vba/macro              | Office Macro loader for specific command                   
    

## 安装

    
    
    # git clone https://github.com/hlldz/SpookFlare.git
    # cd SpookFlare
    # pip install -r requirements.txt

## 技术细节

<https://artofpwn.com/spookflare.html>

## 使用视频教程

Koadic的SpookFlare HTA Loader：<https://youtu.be/6OyZuyIbRLU>

Meterpreter的SpookFlare PowerShell/VBA Loaders：<https://youtu.be/xFBRZz78U_M>

v1.0使用视频：<https://www.youtube.com/watch?v=p_eKKVoEl0o>

 **免责声明**

SpookFlare仅适用于技术研究，渗透测试，红队合作以及教育目的！

## 致谢和参考

特别感谢以下项目以及贡献者。

<https://github.com/rapid7/metasploit-framework>

<https://github.com/zerosum0x0/koadic>

<https://github.com/EmpireProject/Empire>

<https://github.com/Veil-Framework/Veil>

<https://github.com/nccgroup/demiguise>

 ***参考来源：[GitHub](https://github.com/hlldz/SpookFlare)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**  

