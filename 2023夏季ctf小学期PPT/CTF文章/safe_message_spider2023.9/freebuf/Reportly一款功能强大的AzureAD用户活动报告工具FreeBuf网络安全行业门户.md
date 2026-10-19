![](https://image.3001.net/images/20230602/1685670902_64794bf65dbdba5469e51.png!small)

## 关于Reportly

Reportly是一款功能强大的AzureAD用户活动报告工具，在该工具的帮助下，广大蓝队安全研究人员可以在云端事件发生时第一时间收到通知。

在运行该工具的过程中，研究人员需要输入一个可疑用户账号和时间参数，随后便会收到一份详细的报告，其中包括下列内容：

> 1、与目标用户相关的信息；
>
> 2、目标用户采取的活动信息；
>
> 3、针对目标用户采取的活动信息；
>
> 4、用户登录和失败日志；

## 工具安装

由于该工具基于Python开发，因此我们首先需要在本地设备上安装并配置好Python环境。接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/sap8899/reportly.git

在使用该工具之前，我们需要一个包含下列APi权限的AzureAD应用程序：

> AuditLog.Read.All
>
> GroupMember.Read.All
>
> RoleManagement.Read.Directory
>
> User.Read
>
> User.Read.All

然后授权管理员权限：

![](https://image.3001.net/images/20230602/1685670933_64794c159507a579a6ccb.png!small)

切换到“App registration”标签页，创建一个应用程序，并选择“New registration”选项：

![](https://image.3001.net/images/20230602/1685670941_64794c1d6663fd30313a7.png!small)

在创建应用程序的时候，确保勾选了下列选项：

![](https://image.3001.net/images/20230602/1685670948_64794c242f238a881fda7.png!small)

向应用程序添加一个密钥令牌：

![](https://image.3001.net/images/20230602/1685670959_64794c2f729630b28e451.png!small)

创建好之后，我们还需要打开config.cfg文件，并按照参数修改下列内容：

> clientId = 应用程序id
>
> clientSecret = 应用程序密钥令牌
>
> tenantId = 租户id

## 工具使用

在运行该工具的时候，将显示一个指向身份验证的链接和一个设备码，此时我们需要点击链接并输入身份验证码：

![](https://image.3001.net/images/20230602/1685670984_64794c48d8c94a1bedcd6.png!small)

接下来，输入一个可以可疑用户的用户主体名称，并按下列格式输入开始和结束时间：2022-11-16。我们建议这个时间范围不要超过一个星期。

身份认证完成之后，为了创建一份完整报告，请选择选项“5”：

![](https://image.3001.net/images/20230602/1685670992_64794c50caf8160f9f280.png!small)

此时报告便生成完毕，并输出“Your report is ready！”的提示文字，生成好的报告位于项目目录中。

## 工具演示视频

 **视频地址** ：【[ _点我观看_](https://user-images.githubusercontent.com/88736901/202284687-9862e097-a5d6-4557-a474-d99e37269c2e.mp4)】

## 项目地址

 **Reportly** ：【[ _GitHub传送门_](https://github.com/sap8899/reportly)】

