![](https://image.3001.net/images/20210818/1629283757_611ce5ad026b4fcbb376f.png!small)

## 关于GDir-Thief

GDir-Thief是一款专为红队研究人员设计的数据提取工具，在该工具的帮助下，广大安全研究人员可以通过Google的People
API来提取已访问过的目标组织的Google People目录。

## 工具依赖

该工具的正常运行需要安装好Google API库，运行下列命令安装即可：

    
    
    pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/antman1p/GDir-Thief.git

## 创建一个新的Google云平台（GCP）项目

首先，我们需要通过下列命令来获取Google API的访问令牌：

> 创建一个Gmail或Google账号。
>
> 登录账号。
>
> 访问Google云控制台。
>
> 点击“向下箭头”，此时会弹出一个当前项目列表对话框。
>
> 点击“新建项目”。
>
> 在“项目名称”栏中，输入项目描述名称。
>
> 点击“创建”，控制台将会导航至仪表盘页面，并在几分钟内完成项目创建。

## 启用一个Google工作区API

点击“向下箭头”，从弹出的当前项目列表对话框中选择我们的项目。

在页面左上角，点击“菜单”->“API & 服务”。

点击“启用API和服务”，此时将会显示“API库欢迎页面”。

在搜索栏中，输入“People”。

点击并启用API。

## 配置OAuth同意界面

在概览页面的左侧点击“凭证”，然后选择“配置同意界面”，此时将显示“OAuth同意界面”。

点击应用程序的外部用户类型，点击创建。

填写“应用名称”、“用户支持邮件”和“开发者联系信息”，然后点击保存。

在弹出的页面中选择“保存并继续”，然后点击“添加或移除Scope”。

在弹出的页面中检查应用程序中所有的Google People范围。

点击“更新”，然后点击“保存并继续”。

## 将目标Google账号添加至应用程序的测试用户

为了使用该脚本对目标执行测试，我们需要将目标Google账号添加至应用程序的测试用户列表中：

> 在页面左侧点击“OAutch同意界面”。
>
> 在“测试用户”栏中点击“添加用户”按钮。
>
> 在邮件栏中输入目标用户的Gmail邮箱地址。
>
> 点击“保存”按钮即可。

## 工具使用

    
    
    usage:
    
    python3 gdir_thief.py [-h]
    
     
    
    help:
    
     
    
    This Module will connect to Google's People API using an access token and exfiltrate the organization's
    
    People directory.  It will output a CSV file to ./loot/directory.csv

## 项目地址

 **GDir-Thief：** 【[ _GitHub传送门_](https://github.com/antman1p/GDir-Thief)】

