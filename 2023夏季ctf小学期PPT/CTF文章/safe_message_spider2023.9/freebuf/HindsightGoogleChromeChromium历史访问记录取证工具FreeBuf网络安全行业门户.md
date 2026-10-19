****

**![Google
ChromeChromium历史访问记录取证工具](https://image.3001.net/images/20180804/1533334526_5b64d3fecff89.png!small)**

**hindsight是一款Google
Chrome/Chromium历史访问记录取证工具。它支持解析许多不同类型的web工件，包括URL，历史下载记录，缓存记录，书签，自动填充记录，保存的密码，首选项，浏览器扩展，HTTP
cookie和本地存储记录（HTML5
cookie）。从各个文件中提取数据后，它会自动的将这些提取数据与来自其他历史文件的数据相关联，并将他们添加到时间线中。**  

hindsight还为我们提供了一个简单易操作的web UI -启动它，运行“hindsight_gui.py”（或是Windows上打包的“hindsight_gui.exe”）并在浏览器中访问：[http://localhost:8080](http://localhost:8080/)

![Google
ChromeChromium历史访问记录取证工具](https://image.3001.net/images/20180804/1533334313_5b64d3296ca65.png!small)

其中唯一需要我们填写的就是要分析的Chrome配置文件的路径（在文末我列出了不同操作系统下的默认配置文件路径）
。点击“运行”，你将进入结果页面，您=你可以将结果保存为电子表格（或其他格式）。

##  **命令行**

除了UI，hindsight也提供了命令行版本 - hindsight.py/hindsight.exe。以下是在命令行中的使用示例：

    
    
    Example usage: > C:\hindsight.py -i "C:\Users\Ryan\AppData\Local\Google\Chrome\User Data\Default" -o test_case

命令行选项：

选项| 描述  
---|---  
-i 或 --input| Chrome（ium）“默认”目录的路径  
-o 或 --output| 输出文件的名称（不带扩展名）  
-f 或 --format| 输出格式（默认为XLSX，其他选项为SQLite）  
-c 或 --cache| 缓存目录的路径；仅当目录在给定的“input”目录之外时才需要。默认情况下，Mac系统以这种方式设置。  
-b 或 --browser_type| 输入文件所属的浏览器类型。支持的选项包括Chrome（默认）和Brave。  
-l 或 --log| 日志记录  
-h 或 --help| 显示这些选项和默认的Chrome数据位置  
-t 或 --timezone| 在XLSX输出中显示时间戳的时区  
  
 **默认配置文件路径**

> WinXP: [userdir]\Local Settings\Application Data\Google\Chrome\User
> Data\Default
>
> Vista/7/8: [userdir]\AppData\Local\Google\Chrome\User Data\Default
>
> Linux: [userdir]/.config/google-chrome/Default
>
> OS X: [userdir]/Library/Application Support/Google/Chrome/Default
>
> iOS: \Applications\com.google.chrome.ios\Library\Application
> Support\Google\Chrome\Default
>
> Android: /userdata/data/com.android.chrome/app_chrome/Default

 ** *参考来源：[github](https://github.com/obsidianforensics/hindsight)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

