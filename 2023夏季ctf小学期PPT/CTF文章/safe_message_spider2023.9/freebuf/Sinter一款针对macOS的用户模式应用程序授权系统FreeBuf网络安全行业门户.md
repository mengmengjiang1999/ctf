![](https://image.3001.net/images/20200929/1601309197_5f720a0d204e8ab6ce5ad.jpg!small)

## Sinter

Sinter是一款针对macOS
v10.15及其以上版本的100%用户模式终端安全代理，该工具基于Swift语言开发，使用了用户模式EndpointSecurity
API来订阅和接收来自macOS内核的授权回调，这里主要针对的是安全相关的事件类型。Sinter的当前版本支持允许/拒绝进程执行，在将来的版本中，我们打算支持其他类型的事件，比如说文件操作、套接字和内核事件等等。

## 功能介绍

  * 通过代码目录哈希来允许或拒绝进程执行；
  * “监控器模式”支持跟踪和记录所有的进程执行事件（拒绝所有未知程序、拒绝所有未签名程序、拒绝所有无效签名程序）；
  * 接受来自Santa同步服务器的允许/拒绝规则；
  * 支持来自本地或同步服务器的JSON格式配置拒绝规则；
  * 在本地文件系统以结构化JSON格式记录日志；

## 其他特性

  * 未使用内核扩展；
  * 不支持遗留macOS系统（14及之前版本）；
  * 未使用任何内存不安全的代码；
  * 有限的第三方库依赖；
  * 并非反恶意软件或反病毒产品，不包含特征数据库；
  * 仅使用规则来拒绝你不想要执行的进程或程序；

## 工具下载&安装

广大研究人员可以使用该项目[
_Releases页面_](https://github.com/trailofbits/sinter/releaseshttps:/github.com/trailofbits/sinter/releases)中提供的pkg安装工具来下载和安装最新版本的Sinter。

安装好Sinter之后，你还需要为Sinter.app提供完整的磁盘访问权限。这里可以打开系统设置->安全->隐私->完整磁盘访问，勾选Sinter.app即可。如果使用了DMD，你还可以在终端自动启用该权限，整个过程也不需要涉及用户交互。

### 工具配置

Sinter需要在/etc/sinter/config.json中生成一个配置文件，下面给出的的配置文件源码样例:

    
    
    {
    
      "Sinter": {
    
        "decision_manager": "local",
    
        "logger": "filesystem",
    
     
    
        "allow_unsigned_programs": "true",
    
        "allow_invalid_programs": "true",
    
        "allow_unknown_programs": "true",
    
        "allow_expired_auth_requests": "true",
    
        "allow_misplaced_applications": "true",
    
     
    
        "config_update_interval": 600,
    
     
    
        "allowed_application_directories": [
    
          "/bin",
    
          "/usr/bin",
    
          "/usr/local/bin",
    
          "/Applications",
    
          "/System",
    
          "/usr/sbin",
    
          "/usr/libexec",
    
        ],
    
      },
    
      
    
      "FilesystemLogger": {
    
        "log_file_path": "/var/log/sinter.log",
    
      },
    
     
    
      "RemoteDecisionManager": {
    
        "server_url": "https://server_address:port",
    
        "machine_identifier": "identifier",
    
      },
    
     
    
      "LocalDecisionManager": {
    
        "rule_database_path": "/etc/sinter/rules.json",
    
      }
    
    }

## 启用UI通知

1、安装通知服务器，PKG安装器将会自动完成这部分组件的安装：

    
    
    sudo /Applications/Sinter.app/Contents/MacOS/Sinter --install-notification-server

2、使用下列命令开启代理：

    
    
    /Applications/Sinter.app/Contents/MacOS/Sinter --start-notification-server

## 规则格式

规则数据库以JSON格式编写，下面给出的样例数据库允许来自cmake.okg的CMake应用程序Bundle运行：

    
    
    {
    
      "rules": [
    
        {
    
          "rule_type": "BINARY",
    
          "policy": "ALLOWLIST",
    
          "sha256": "BDD0AF132D89EA4810566B3E1E0D1E48BAC6CF18D0C787054BB62A4938683039",
    
          "custom_msg": "CMake"
    
        }
    
      ]
    
    }

Sinter目前仅支持BINARY规则，这里可以使用ALLOWLIST或DENYLIST策略。代码目录哈希值可以从codesign工具的输出获取，比如说codesign
-dvvv
/Applications/CMake.app。需要注意的是，即使命令行工具能够获取完整的SHA256哈希，Kernel/EndpointSecurity
API仍然只能获取前20字节的哈希。

## 许可证协议

Sinter项目的开发与发布遵循AGPLv3开源许可证协议。

## 项目地址

Sinter：【[ _GitHub传送门_](https://github.com/trailofbits/sinter)】

