## 概述

awvs扫描真的很累人，手动添加资产，来不来就是几百条，真是气死人，不气死都累死了。所以要想活得久，就要减轻工作量，这是真事。你看，这牛，它一天天的劳作，总会累死。而你看那狗，就跟大爷似的，一天天只需要躺在那儿，就有饭吃。

![](https://image.3001.net/images/20220508/1651939236_627697a40dbda0ed6463a.gif!small)

##  **插件功能**

chrome浏览器量身打造的脚本，你只需要用chrome浏览器登录awvs。

然后你只需要打开"TARGET"栏目的"Add Target"，这个时候，只需要指定脚本里你的url.txt文件的位置。

它就会解放你的双手，自动的复制粘贴你要扫描的网站了，嗯，真是摸鱼必备的脚本啊。

当有人来视察的时候，悄悄运行脚本，把双手放在键盘上，远远望去，你的电脑不停的闪着灯光，仿佛在辛勤的工作干活一般。

但你真的是在干活，毕竟眼睛还在动，即便如此，你的工作也因为这个脚本越来越轻松，而你也越来越快乐。

##  **脚本代码**

>  
>  //Chrome_WidgetWin_1  
> Hwnd = Plugin.Window.Find("Chrome_WidgetWin_0", 0)  
> If Not Hwnd Then  
> Hwnd = Plugin.Window.Find("Chrome_WidgetWin_1", 0)  
> End If
>
> //按键精灵2014  
> Call Plugin.Window.Active(Hwnd)  
> //MsgBox "当前激活窗口"
>
> Hwnd = Plugin.Window.Foreground()  
> //下面这句是得到窗口句柄的标题  
> sText = Plugin.Window.GetTextEx(Hwnd,0)  
> //MsgBox "得到窗口句柄的信息内容为："& sText  
> If StrComp("Acunetix - Add Targets - Google Chrome",sText,1) Then //匹配返回0  
> //Msgbox "条件判断不通过!!"  
> // EndScript  
> Else  
> //Msgbox "条件判断符合被通过!!"  
> End If//Chrome_RenderWidgetHostHWND  
> Hwnd = Plugin.Window.Find("Chrome_RenderWidgetHostHWND", 0)  
> Call Plugin.Window.Active(Hwnd)
>
> //CFRL+F  
> KeyDown 17, 1  
> KeyPress 70, 1  
> KeyUp 17, 1  
> SayString "http://example.com"  
> Delay 1000  
> KeyUp "Enter", 1  
> //KeyUp "Enter", 1KeyDown "Esc", 1  
> Delay 1000  
> KeyUp "Esc", 1  
> Delay 1000  
> KeyPress "Tab", 32
>
> //read: url.txt  
> Text = Plugin.File.ReadFileEx("C:\Users\1\Desktop\url.txt")  
> //Msgbox "向目标文件读出文本内容为："& Text  
> dim MyArray  
> MyArray = Split(Text, "|")  
> If UBound(MyArray)>=0 Then  
> i=0  
> For UBound(MyArray)  
>  
> //下面这句是得到文本内容  
> //Msgbox "第 " & i+1 &" 行文本内容为："& MyArray(i) //Msgbox "第 " & i+1 &" 行文本内容为："&
> Cstr(MyArray(i))  
> SayString One_Url = NULL  
> One_Url = MyArray(i)  
> Call Plugin.Sys.SetCLB(NULL)  
> Call Plugin.Sys.SetCLB(One_Url)//设置剪贴板的内容  
> //Msgbox "剪贴板："& One_Url  
> //剪贴板  
> KeyDown 17, 1  
> KeyPress 86, 1  
> KeyUp 17, 1  
> //系统时间  
> KeyPress "Tab", 1  
> s=Plugin.Sys.GetDateTime()  
> //MessageBox "您的操作系统日期和时间：" & s  
> Call Plugin.Sys.SetCLB(s)  
> KeyDown 17, 1  
> KeyPress 86, 1  
> KeyUp 17, 1  
> //下一行  
> If i=0 Then  
> KeyPress "Tab", 1  
> Else  
> KeyPress "Tab", 0  
> End If  
> //CFRL+F  
> KeyDown 17, 1  
> KeyPress 70, 1  
> KeyUp 17, 1  
> SayString "http://example.com"  
> Delay 100  
> KeyUp "Enter", 1  
> //定位。。。  
> KeyDown "Esc", 1  
> Delay 100  
> KeyUp "Esc", 1  
> //KeyUp "Enter", 1  
> KeyPress "Tab", 1  
> KeyDown "Enter", 1  
> KeyUp "Enter", 1  
> Delay 100  
> KeyPress "Tab", 34 + (i*3)  
> Delay 3000
>
> i=i+1  
> Next  
> End If

### 建议：

因为awvs扫描的任务，Description是根据系统时间来命名的，所以，建议各位在使用的时候,url.txt里面不要超过100条。

如图，点击“save”以后，可以在“Targets”里面，直接点Description来进行排序了。

![1651940033_62769ac17a94e19ce8a6b.png!small](https://image.3001.net/images/20220508/1651940033_62769ac17a94e19ce8a6b.png!small)

这个脚本发来让大家happy一下就行。

