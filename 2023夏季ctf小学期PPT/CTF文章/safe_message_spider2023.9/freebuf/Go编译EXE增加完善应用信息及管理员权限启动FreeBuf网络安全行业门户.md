![](https://image.3001.net/images/20200811/1597112970.png!small)本文是为了解决Go编译EXE文件后，如何将应用程序"完(wei)善(zhuang)"的更好，也是[书接上回](../articles/system/246174.html)的一个完善;

注：本文是一篇站在巨人肩膀上的实践记录

成功尝试有效的方法有[《GoVersionInfo》](https://github.com/josephspurrier/goversioninfo/)和[《windres.exe》](https://www.jianshu.com/p/7de0f8e9e43f)

## 一、完善应用详细信息图标及版本信息----GoVersionInfo

###
1.将[git文件](https://github.com/josephspurrier/goversioninfo/)下载到任意目录；将下载后的《resource》目录全部复制到本项目根目录；  
![](https://image.3001.net/images/20200811/1597116912.jpg!small)  
2.在被编译go文件头部增加

    
    
    //go:generate goversioninfo -icon=resource/icon.ico -manifest=resource/goversioninfo.exe.manifest

###
![](https://image.3001.net/images/20200811/1597117062.jpg!small)3.根据自己需要完善修改《versioninfo.json》版本信息文件

![](https://image.3001.net/images/20200811/1597117210.jpg!small)

### 4.“初始化”生成.syso文件，编译exe

    
    
    #go generate          // 会在项目文件目录生成resource.syso文件
    
    
    #CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build -ldflags "-s -w -H=windowsgui" client.go  //编译exe会自动把syso文件链接到程序中
    注：生成exe时文件夹下面不要用其他.go文件；否则编译失败；
    

### 5.查看程序文件信息

![](https://image.3001.net/images/20200811/1597121729.jpg!small)

## 二、完善应用详细信息图标及版本信息----windres

核心：通过windres生成一个中间文件
***.syso，然后通过go编译exe；(我们需要使用[MinGW](http://mingw.org/)安装windres编译所需的组件)

### 1.安装windres工具

网上搜索windres.exe进行下载，放入下面mingw安装后的bin目录“C:\MinGW\bin\”

### 2.[下载mingw](https://osdn.net/projects/mingw/releases/)并安装，然后安装gcc、g++等组件  
![](https://image.3001.net/images/20200811/1597122475.jpg!small)![](https://image.3001.net/images/20200811/1597122961.jpg!small)![](https://image.3001.net/images/20200811/1597122981.jpg!small)![](https://image.3001.net/images/20200811/1597123003.jpg!small)

### 3.增加环境变量到path  
![](https://image.3001.net/images/20200811/1597123156.jpg!small)4.检查gcc、g++、windres  
![](https://image.3001.net/images/20200811/1597123265.jpg!small)5.准备一个demo.dc文件

    
    
    1 VERSIONINFO
    FILEVERSION 2,4,1109,2
    PRODUCTVERSION 2,4,1109,2
    FILEOS 0x40004
    FILETYPE 0x1
    {
    BLOCK "StringFileInfo"
    {
        BLOCK "040904B0"
        {
            VALUE "CompanyName", "Amazon GNU Internal Tools"
            VALUE "FileDescription", "Amazon GNU Internal Tools"
            VALUE "FileVersion", "2,4,1109,2"
            VALUE "InternalName", "Amazon GNU Internal Tools"
            VALUE "LegalCopyright", "Copyright (C)2019 Amazon. All rights reserved."
            VALUE "OriginalFilename", "CofoxAmazonBestSellersHold.exe"
            VALUE "ProductName", "CofoxHoldAmazonTop100"
            VALUE "ProductVersion", "2,4,1109,2"
        }
    }
    
    
    
    
    BLOCK "VarFileInfo"
    {
        VALUE "Translation", 0X0409, 0X04B0
    }
    }
    
    
    
    IDI_ICON1 ICON "network.ico"
    1 VERSIONINFO
    FILEVERSION 2,4,1109,2
    PRODUCTVERSION 2,4,1109,2
    FILEOS 0x40004
    FILETYPE 0x1
    {
    BLOCK "StringFileInfo"
    {
        BLOCK "040904B0"
        {
            VALUE "CompanyName", "Amazon GNU Internal Tools"
            VALUE "FileDescription", "Amazon GNU Internal Tools"
            VALUE "FileVersion", "2,4,1109,2"
            VALUE "InternalName", "Amazon GNU Internal Tools"
            VALUE "LegalCopyright", "Copyright (C)2019 Amazon. All rights reserved."
            VALUE "OriginalFilename", "CofoxAmazonBestSellersHold.exe"
            VALUE "ProductName", "CofoxHoldAmazonTop100"
            VALUE "ProductVersion", "2,4,1109,2"
        }
    }
    
    
    
    
    BLOCK "VarFileInfo"
    {
        VALUE "Translation", 0X0409, 0X04B0
    }
    }
    
    
    
    IDI_ICON1 ICON "network.ico"

### 6.编译生成*.syso

    
    
    windres -i demo.rc -o demo.syso

###  
![](https://image.3001.net/images/20200811/1597123496.jpg!small)7.将syso文件复制到go项目目录，编译exe

    
    
    #CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build -ldflags "-s -w -H=windowsgui" -o GNUTools.exe

### 8.查看程序文件信息  
![](https://image.3001.net/images/20200811/1597123622.jpg!small)

## 三、请求管理员权限启动应用

如果程序启动时，默认请求管理员权限，是否就方便了很多？

### 1.思路非常简单，无论是上面那两种方法，只要修改*.manifest文件即可

    
    
    <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
      <assemblyIdentity
        type="win32"
        name="GNUtools.exe"
        version="1.0.0.0"
        processorArchitecture="*"/>
     <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
       <security>
         <requestedPrivileges>
          <requestedExecutionLevel level="requireAdministrator" uiAccess="false"/>
          </requestedPrivileges>
       </security>
     </trustInfo>
    </assembly>

如果使用上面第一种方法《GoVersionInfo》，则直接修改*.manifest文件；  
如果使用上线第二种方法《windres》,则需要修改一下demo.rc文件，在最下面加一行；并创建demo.manifest（文件内容参考上面*.manifest）

    
    
    IDI_MANIFEST1 RT_MANIFEST "demo.manifest"

###
![](https://image.3001.net/images/20200811/1597124858.jpg!small)2.编译程序，查看程序；

![](https://image.3001.net/images/20200811/1597125002.jpg!small)搞定！  
  
美中不足，文件信息需要解决文件签名问题！这样"完(wei)善(zhuang)"的会更好！  
下一篇，尝试程序签名！

