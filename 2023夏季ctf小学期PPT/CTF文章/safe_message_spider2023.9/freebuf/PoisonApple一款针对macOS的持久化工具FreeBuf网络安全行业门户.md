**HW期间，为防范钓鱼，即日起FreeBuf将取消投稿文章的一切外部链接。给您带来的不便，敬请谅解~**

![](https://image.3001.net/images/20210410/1618063142_6071af261124dea1de2da.png!small)

## PoisonApple

PoisonApple是一款针对macOS的持久化工具，该工具是一个命令行工具，可以帮助广大研究人员在macOS系统上测试和执行各种持久化机制技术。该工具主要目的是为了帮助广大研究人员对网络威胁进行模拟和分析，请不要将其用于恶意目的。

## 注意事项

> PoisonApple将会对你的macOS系统进行一些配置修改，因此我们建议大家在虚拟机上安装和使用PoisonApple。研究人员可以使用-> r参数轻松移除该工具所实现的任何持久化机制技术。
>
> 建议：该工具将会触发常见反病毒软件/EDR和其他macOS安全产品发出警报提醒。

## 工具安装

由于该工具基于Python开发，因此广大研究人员首先需要在本地设备上配置好Python环境，然后运行下列命令安装和配置PoisonApple：

    
    
    $ pip3 install poisonapple --user

注意：PoisonApple基于Python 3.9开发和测试，因此我们建议广大研究人员使用Python 3.6+版本。

## 工具使用

广大研究人员可以使用下列命令查看该工具的帮助选项（--help）：

    
    
    $ poisonapple --help
    
    usage: poisonapple [-h] [-l] [-t TECHNIQUE] [-n NAME] [-c COMMAND] [-r]
    
     
    
    Command-line tool to perform various persistence mechanism techniques on macOS.
    
     
    
    optional arguments:
    
      -h, --help            显示帮助信息并退出。
    
      -l, --list             列举所有可用的持久化机制技术。
    
      -t TECHNIQUE, --technique TECHNIQUE
    
                            需要使用的持久化机制技术。
    
      -n NAME, --name NAME  用于持久化技术的文件或标签。
    
      -c COMMAND, --command COMMAND
    
                            执行持久化技术的命令。
    
      -r, --remove            移除持久化机制。

 **列举所有可用的持久化机制技术：**

    
    
    $ poisonapple --list
    
          ,       _______       __
    
      .-.:|.-.   |   _   .-----|__|-----.-----.-----.
    
    .'        '. |.  |   |  |  |  |__ --|  |  |  |  |
    
    '-."~".  .-' |.  ____|_____|__|_____|_____|__|__|
    
      } ` }  {   |:  |  _______             __
    
      } } }  {   |::.| |   _   .-----.-----|  |-----.
    
      } ` }  {   `---' |.  |   |  |  |  |  |  |  -__|
    
    .-'"~"   '-.       |.  _   |   __|   __|__|_____|
    
    '.        .'       |:  |   |__|  |__|
    
      '-_.._-'         |::.|:. |
    
                       `--- ---' v0.2.1
    
     
    
    +--------------------+
    
    | AtJob              |
    
    +--------------------+
    
    | Bashrc             |
    
    +--------------------+
    
    | Cron               |
    
    +--------------------+
    
    | CronRoot           |
    
    +--------------------+
    
    | Emond              |
    
    +--------------------+
    
    | LaunchAgent        |
    
    +--------------------+
    
    | LaunchAgentUser    |
    
    +--------------------+
    
    | LaunchDaemon       |
    
    +--------------------+
    
    | LoginHook          |
    
    +--------------------+
    
    | LoginHookUser      |
    
    +--------------------+
    
    | LoginItem          |
    
    +--------------------+
    
    | LogoutHook         |
    
    +--------------------+
    
    | LogoutHookUser     |
    
    +--------------------+
    
    | Periodic           |
    
    +--------------------+
    
    | Reopen             |
    
    +--------------------+
    
    | Zshrc              |
    
    +--------------------+

 **应用持久化机制：**

    
    
    $ poisonapple -t LaunchAgentUser -n testing
    
          ,       _______       __
    
      .-.:|.-.   |   _   .-----|__|-----.-----.-----.
    
    .'        '. |.  |   |  |  |  |__ --|  |  |  |  |
    
    '-."~".  .-' |.  ____|_____|__|_____|_____|__|__|
    
      } ` }  {   |:  |  _______             __
    
      } } }  {   |::.| |   _   .-----.-----|  |-----.
    
      } ` }  {   `---' |.  |   |  |  |  |  |  |  -__|
    
    .-'"~"   '-.       |.  _   |   __|   __|__|_____|
    
    '.        .'       |:  |   |__|  |__|
    
      '-_.._-'         |::.|:. |
    
                       `--- ---' v0.2.1
    
     
    
    [+] Success! The persistence mechanism action was successful: LaunchAgentUser

如果命令在执行的过程中没有指定-c选项的话，工具则会使用一个默认的触发命令，并在每次持久化机制被触发的时候，向桌面写入一个文件：

    
    
    $ cat ~/Desktop/PoisonApple-LaunchAgentUser
    
    Triggered @ Tue Mar 23 17:46:02 CDT 2021
    
    Triggered @ Tue Mar 23 17:46:13 CDT 2021
    
    Triggered @ Tue Mar 23 17:46:23 CDT 2021
    
    Triggered @ Tue Mar 23 17:46:33 CDT 2021
    
    Triggered @ Tue Mar 23 17:46:43 CDT 2021
    
    Triggered @ Tue Mar 23 17:46:53 CDT 2021
    
    Triggered @ Tue Mar 23 17:47:03 CDT 2021
    
    Triggered @ Tue Mar 23 17:47:13 CDT 2021
    
    Triggered @ Tue Mar 23 17:48:05 CDT 2021
    
    Triggered @ Tue Mar 23 17:48:15 CDT 2021

 **移除一个持久化机制：**

    
    
    $ poisonapple -t LaunchAgentUser -n testing -r
    
    ...

 **使用一个自定义命令：**

    
    
    $ poisonapple -t LaunchAgentUser -n foo -c "echo foo >> /Users/user/Desktop/foo"
    
    ...

## 项目地址

PoisonApple：https://github.com/CyborgSecurity/PoisonApple

## 参考资料

https://taomm.org/PDFs/vol1/CH%200x02%20Persistence.pdf

