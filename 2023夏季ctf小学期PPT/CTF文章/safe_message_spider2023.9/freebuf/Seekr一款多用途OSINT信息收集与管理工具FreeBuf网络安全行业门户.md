![](https://image.3001.net/images/20230526/1685083630_647055ee9675efc6140e2.jpeg!small)

## 关于Seekr

Seekr是一款功能强大的多用途OSINT信息收集与管理工具，该工具提供了一个简洁的Web接口，可以帮助广大研究人员轻松收集和管理OSINT公开资源情报信息。

Seekr可以允许研究人员将所有喜爱的OSINT工具集成在一个工具中，该工具的后端采用Go语言编写，使用BadgerDB作为数据库，并为数据收集、组织和分析提供了广泛的功能。

无论你是研究人员、调查员，还是只是想收集信息的人，Seekr都可以轻松地找到和管理你需要的数据。

## 功能介绍

> 1、所有功能均不需要API密钥；
>
> 2、提供了桌面接口；
>
> 3、数据库存储OSINT目标；
>
> 4、整合了多种热门OSINT工具，例如phoneinfoga；
>
> 5、详细的数据库存储记录；
>
> 6、预定义常见数据库字段；
>
> 7、支持主题和插件；

## 工具安装

### Windows

广大研究人员可以直接访问该项目的【[ _Releases页面_](https://github.com/seekr-osint/seekr/releases/latest)】下载最新版本的Seekr可执行文件。

安装完成后，即可在浏览器中打开并使用Seekr的Web接口了：

    
    
    http://localhost:8569/web/

### Docker

    
    
    docker pull ghcr.io/seekr-osint/seekr:latest
    
    docker run -p 8569:8569 ghcr.io/seekr-osint/seekr:latest

### Linux（稳定）

广大研究人员可以直接访问该项目的【[ _Releases页面_](https://github.com/seekr-osint/seekr/releases/latest)】下载稳定版的Seekr可执行文件。

### Linux（不稳定）

广大研究人员可以使用下列命令在Linux系统上安装和使用Seekr：

    
    
    git clone https://github.com/seekr-osint/seekr
    
    cd seekr
    
    go run main.go

安装完成后，即可在浏览器中打开并使用Seekr的Web接口了：

    
    
    http://localhost:8569/web/

## 自定义主题

    
    
    [data-theme="arctic"] {
    
      /* Background */
    
     
    
      --bg: #E4EBF5;
    
      --bg-bright: #e9edf1;
    
     
    
      /* Text */
    
      
    
      --textColor-1: #9baacf;
    
      --textColor-hover: #6d5dfc;
    
     
    
      /* Icons */
    
     
    
      --iconColor-1: #9CCF9B;
    
      --iconColor-2: #E4EBF5;
    
      --iconColor-3: #CF9B9B;
    
     
    
      /* Loading spinner */
    
     
    
      --loadingColor: #6d5dfc;
    
      --loadingColor-dark: #5b0eeb;
    
     
    
      /* No search results text */
    
     
    
      --noResultsText: rgba(155, 170, 207, 0.5);
    
     
    
      /* Shadows */
    
     
    
      --shadow-1: #c8d0e7;
    
      --shadow-2: #FFFFFF;
    
     
    
      --shadowPreset-1: 0.8rem 0.8rem 1.4rem var(--shadow-1), -0.2rem -0.2rem 1.8rem var(--shadow-2);
    
      --shadowPreset-2: inset 0.2rem 0.2rem 0.5rem var(--shadow-1), inset -0.2rem -0.2rem 0.5rem var(--shadow-2);
    
      --shadowPreset-3: 0.3rem 0.3rem 0.6rem var(--shadow-1), -0.2rem -0.2rem 0.5rem var(--shadow-2);
    
      --shadowPreset-4: 8px 8px 16px var(--shadow-1), -8px -8px 16px var(--shadow-2);
    
      --shadowPreset-5: 0.3rem 0.3rem 0.6rem var(--shadow-1), -0.2rem -0.2rem 0.5rem var(--shadow-2);
    
      --shadowPreset-6: inset 6.91px 6.91px 15px var(--shadow-1), inset -6.91px -6.91px 15px var(--shadow-2);
    
      --shadowPreset-7: 0 0 15px var(--loadingColor);
    
    }

## 工具使用演示

### 工具主界面

![](https://image.3001.net/images/20230526/1685083723_6470564b2776522390983.png!small)

### 账号查看

![](https://image.3001.net/images/20230526/1685083731_6470565355ce3f5fceaab.png!small)

### 详情查看

![](https://image.3001.net/images/20230526/1685083739_6470565b4158efd98d75f.png!small)

## 许可证协议

本项目的开发与发布遵循[ _GPL_ _-3.0_](https://github.com/seekr-osint/seekr/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Seekr** ：【[ _GitHub传送门_](https://github.com/seekr-osint/seekr)】

