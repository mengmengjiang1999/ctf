## 关于Qlog

Qlog是一款功能强大的Windows安全日志工具，该工具可以为Windows操作系统上的安全相关事件提供丰富的事件日志记录功能。该工具目前仍处于积极开发状态，当前版本为Alpha版本。Qlog没有使用API钩子技术，也不需要在目标系统上安装驱动程序，Qlog指挥使用ETW检索遥测数据。当前版本的Qlog仅支持“进程创建”事件，之后还会添加更多丰富的事件支持。Qlog可以看作为Windows服务运行，但也可以在控制台模式下运行，因此我们可以将丰富的事件信息直接传输到控制台进行处理。

## 工作机制

Qlog可以从ETW读取数据，并将丰富的事件信息写入Qlog的事件通道，工具将会创建并使用名为“QMonitor”的新事件源，并写入Windows事件日志中。

 **以下是Qlog的事件处理顺序：**

> 创建ETW会话，并订阅相关内核和用户区ETW Provider；
>
> 从ETW提供程序读取事件；
>
> 丰富的事件支持；
>
> 将丰富的事件写入事件日志通道QLOG；

## 工具依赖&安装&使用

Qlog的运行需要在本地系统中安装并配置好.NET Framework >= 4.7.2环境。

接下来，我们需要使用下列命令将该项目克隆至本地：

    
    
    git clone https://github.com/threathunters-io/QLOG.git

接下来，我们可以使用下列命令以交互式终端模式运行Qlog：

    
    
    qlog.exe

或者，以Windows服务的方式运行：

    
    
    #安装服务
    
    qlog.exe -i
    
    #卸载服务
    
    qlog.exe -u

## 进程处理事件数据输出

    
    
    {
    
      "EventGuid": "68795fe8-67e7-410b-a5c0-8364746d7ffe",
    
      "StartTime": "2021-07-11T11:06:56.9621746+02:00",
    
      "QEventID": 100,
    
      "QType": "Process Create",
    
      "Username": "TESTOS\\TESTUSER",
    
      "Imagefilename": "TEAMS.EXE",
    
      "KernelImagefilename": "TEAMS.EXE",
    
      "OriginalFilename": "TEAMS.EXE",
    
      "Fullpath": "C:\\Users\\TESTUSER\\AppData\\Local\\Microsoft\\Teams\\current\\Teams.exe",
    
      "PID": 21740,
    
      "Commandline": "\"C:\\Users\\TESTUSER\\AppData\\Local\\Microsoft\\Teams\\current\\Teams.exe\" --type=renderer --autoplay-policy=no-user-gesture-required --disable-background-timer-throttling --field-trial-handle=1668,499009601563875864,12511830007210419647,131072 --enable-features=WebComponentsV0Enabled --disable-features=CookiesWithoutSameSiteMustBeSecure,SameSiteByDefaultCookies,SpareRendererForSitePerProcess --lang=de --enable-wer --ms-teams-less-cors=522133263 --app-user-model-id=com.squirrel.Teams.Teams --app-path=\"C:\\Users\\jocke",
    
      "Modulecount": 41,
    
      "TTPHash": "42AC63285408F5FD91668B16F8E9157FD97046AB63E84117A14E31A188DDC62F",
    
      "Imphash": "F14F00FA1D4C82B933279C1A28957252",
    
      "sha256": "155625190ECAA90E596CB258A07382184DB738F6EDB626FEE4B9652FA4EC1CC2",
    
      "md5": "9453BC2A9CC489505320312F4E6EC21E",
    
      "sha1": "7219CB54AC535BA55BC1B202335A6291FDC2D76E",
    
      "ProcessIntegrityLevel": "None",
    
      "isOndisk": true,
    
      "isRunning": true,
    
      "Signed": "Signature valid",
    
      "AuthenticodeHash": "B8AD58EE5C35B3F80C026A318EEA34BABF6609C077CB3D45AEE69BF5C9CF8E11",
    
      "Signatures": [
    
        {
    
          "Subject": "CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
    
          "Issuer": "CN=Microsoft Code Signing PCA 2010, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
    
          "NotBefore": "15.12.2020 22:24:20",
    
          "NotAfter": "02.12.2021 22:24:20",
    
          "DigestAlgorithmName": "SHA256",
    
          "Thumbprint": "E8C15B4C98AD91E051EE5AF5F524A8729050B2A2",
    
          "TimestampSignatures": [
    
            {
    
              "Subject": "CN=Microsoft Time-Stamp Service, OU=Thales TSS ESN:3BBD-E338-E9A1, OU=Microsoft America Operations, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
    
              "Issuer": "CN=Microsoft Time-Stamp PCA 2010, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
    
              "NotBefore": "12.11.2020 19:26:02",
    
              "NotAfter": "11.02.2022 19:26:02",
    
              "DigestAlgorithmName": "SHA256",
    
              "Thumbprint": "E8220CE2AAD2073A9C8CD78752775E29782AABE8",
    
              "Timestamp": "15.06.2021 00:39:50 +02:00"
    
            }
    
          ]
    
        },
    
        {
    
          "Subject": "CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
    
          "Issuer": "CN=Microsoft Code Signing PCA 2011, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
    
          "NotBefore": "15.12.2020 22:31:47",
    
          "NotAfter": "02.12.2021 22:31:47",
    
          "DigestAlgorithmName": "SHA256",
    
          "Thumbprint": "C774204049D25D30AF9AC2F116B3C1FB88EE00A4",
    
          "TimestampSignatures": [
    
            {
    
              "Subject": "CN=Microsoft Time-Stamp Service, OU=Thales TSS ESN:F87A-E374-D7B9, OU=Microsoft Operations Puerto Rico, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
    
              "Issuer": "CN=Microsoft Time-Stamp PCA 2010, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
    
              "NotBefore": "14.01.2021 20:02:23",
    
              "NotAfter": "11.04.2022 21:02:23",
    
              "DigestAlgorithmName": "SHA256",
    
              "Thumbprint": "ED2C601EDD49DD2A934D2AB32DCACC19940161EF",
    
              "Timestamp": "15.06.2021 00:39:53 +02:00"
    
            }
    
          ]
    
        }
    
      ],
    
      "ParentProcess": {
    
        "EventGuid": null,
    
        "StartTime": "2021-07-11T09:54:28.9558001+02:00",
    
        "QEventID": 100,
    
        "QType": "Process Create",
    
        "Username": "TEST-OS\\TESTUSER",
    
        "Imagefilename": "",
    
        "KernelImagefilename": "",
    
        "OriginalFilename": "TEAMS.EXE",
    
        "Fullpath": "C:\\Users\\TESTUSER\\AppData\\Local\\Microsoft\\Teams\\current\\Teams.exe",
    
        "PID": 16232,
    
        "Commandline": "C:\\Users\\TESTUSER\\AppData\\Local\\Microsoft\\Teams\\current\\Teams.exe ",
    
        "Modulecount": 162,
    
        "TTPHash": "",
    
        "Imphash": "F14F00FA1D4C82B933279C1A28957252",
    
        "sha256": "155625190ECAA90E596CB258A07382184DB738F6EDB626FEE4B9652FA4EC1CC2",
    
        "md5": "9453BC2A9CC489505320312F4E6EC21E",
    
        "sha1": "7219CB54AC535BA55BC1B202335A6291FDC2D76E",
    
        "ProcessIntegrityLevel": "Medium",
    
        "isOndisk": true,
    
        "isRunning": true,
    
        "Signed": "Signature valid",
    
        "AuthenticodeHash": "B8AD58EE5C35B3F80C026A318EEA34BABF6609C077CB3D45AEE69BF5C9CF8E11",
    
        "Signatures": [
    
          {
    
            "Subject": "CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
    
            "Issuer": "CN=Microsoft Code Signing PCA 2010, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
    
            "NotBefore": "15.12.2020 22:24:20",
    
            "NotAfter": "02.12.2021 22:24:20",
    
            "DigestAlgorithmName": "SHA256",
    
            "Thumbprint": "E8C15B4C98AD91E051EE5AF5F524A8729050B2A2",
    
            "TimestampSignatures": [
    
              {
    
                "Subject": "CN=Microsoft Time-Stamp Service, OU=Thales TSS ESN:3BBD-E338-E9A1, OU=Microsoft America Operations, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
    
                "Issuer": "CN=Microsoft Time-Stamp PCA 2010, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
    
                "NotBefore": "12.11.2020 19:26:02",
    
                "NotAfter": "11.02.2022 19:26:02",
    
                "DigestAlgorithmName": "SHA256",
    
                "Thumbprint": "E8220CE2AAD2073A9C8CD78752775E29782AABE8",
    
                "Timestamp": "15.06.2021 00:39:50 +02:00"
    
              }
    
            ]
    
          },
    
          {
    
            "Subject": "CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
    
            "Issuer": "CN=Microsoft Code Signing PCA 2011, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
    
            "NotBefore": "15.12.2020 22:31:47",
    
            "NotAfter": "02.12.2021 22:31:47",
    
            "DigestAlgorithmName": "SHA256",
    
            "Thumbprint": "C774204049D25D30AF9AC2F116B3C1FB88EE00A4",
    
            "TimestampSignatures": [
    
              {
    
                "Subject": "CN=Microsoft Time-Stamp Service, OU=Thales TSS ESN:F87A-E374-D7B9, OU=Microsoft Operations Puerto Rico, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
    
                "Issuer": "CN=Microsoft Time-Stamp PCA 2010, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
    
                "NotBefore": "14.01.2021 20:02:23",
    
                "NotAfter": "11.04.2022 21:02:23",
    
                "DigestAlgorithmName": "SHA256",
    
                "Thumbprint": "ED2C601EDD49DD2A934D2AB32DCACC19940161EF",
    
                "Timestamp": "15.06.2021 00:39:53 +02:00"
    
              }
    
            ]
    
          }
    
        ],
    
        "ParentProcess": null
    
      }
    
    }

## 项目地址

 **Qlog：** 【[ _GitHub传送门_](https://github.com/threathunters-io/QLOG)】

## 参考资料

> [ _https://threathunters.io/_](https://threathunters.io/)

