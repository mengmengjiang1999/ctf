github地址：https://github.com/spkiddai/rad_xray_burplog

xray配置详情见xray文档：<https://docs.xray.cool/#/tutorial/webscan_proxy>

## 一、查看目录文件

main.py tool_run.py
yaml_write.py是核心的三个文件。其中main是主函数，run是rad和xray运行，yaml_write是rad配置文件写入。

rad_config.yaml.example
xray_config.yaml.example是rad和xray的配置示例，运行配置文件均从example导入基本配置，可自定义改写。

config.yaml rad_config.yml是程序运行生成的配置文件，内含解析到的burp cookie参数等。

sys_config是Python程序的配置文件

rad_darwin_amd64 xray_darwin_amd64是rad和xray的程序。

log是存放rad和xray运行结果的目录。

ca.crt ca.key是证书文件。

说明：
为保证正常运行，xray和rad的运行程序需放在同级目录下。![](https://image.3001.net/images/20210323/1616492313_6059b7191abc16f697ddf.png!small)

## 二、修改sys_config配置：

sys是操作系统配置，由于操作系统不同，执行的命令不同，必须配置相应的操作系统。

xray.name是xray程序名称，proxy是xray执行后监听的端口地址

rad.name是rad的程序名称，chrome是chrome浏览器的路径(注:rad采用chrom浏览器进程数据爬取，默认会自动查找环境变量不需要填写，如运行rad报错，需要填写chrome路径地址。)

parse.hrader是解析Burp导出的log文件内容字段，默认只解析host cookie
ua，如需要增加其他字段的解析，如auth等，直接按照格式新增即可。![](https://image.3001.net/images/20210323/1616492326_6059b726c00ff5ed93500.png!small)

## 三、运行程序

程序接受的参数分为三种。

1）-t 单目标地址 如:https://www.spkiddai.xyz

2）-f 多目标文件 文件需要按照行分割目标地址

3）-l Brup log文件
直接从burp导出即可![](https://image.3001.net/images/20210323/1616492338_6059b732bd6f71d2672f8.png!small)

## 四、演示Burp导出log执行携带cookie登录扫描。

1)导出burp
log文件：![](https://image.3001.net/images/20210323/1616492380_6059b75c96a3a96ecade9.png!small)

2）查看文件内容。如需新增字段，如:Referer
则修改sys_config.yaml即可。![](https://image.3001.net/images/20210323/1616492399_6059b76f481bb1ed66b90.png!small)

3)
执行扫描![](https://image.3001.net/images/20210323/1616492409_6059b779700503e3dab5c.png!small)

4）日志显示

可同步查看rad和xray的log文件,xray log文件以传入参数命令，同时增加时间参数，避免重复覆盖，rad
log以检测host命令，同时增加时间参数，避免覆盖，显示运行状态，如报错可查看详情处理。![](https://image.3001.net/images/20210323/1616492421_6059b785440ed882b6d24.png!small)

5）扫描结果

扫描完成后，目录内会出现一个html的扫描结果，扫描结果以传入参数命令，同时增加时间参数，避免重复覆盖。![1616658654_605c40de1f2467b100b19.png!small?1616658654913](https://image.3001.net/images/20210325/1616658654_605c40de1f2467b100b19.png!small?1616658654913)

说明：个人制作，仅供学习使用，不可用于商业用途，切勿将代码内容用于任何违法行为, 违者后果自负。

