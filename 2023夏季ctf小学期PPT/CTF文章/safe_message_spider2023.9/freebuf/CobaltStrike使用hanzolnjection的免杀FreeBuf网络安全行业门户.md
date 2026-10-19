## 使用hanzolnjection的免杀

###  ** **一、介绍：****

 ** **Hanzoinjection介绍****

 ** **对于免杀，我们也可以使用cs生成一个二进制格式的payload，也就是raw格式，运行时我们需要借助hanzolnjection ,
hanzolnjection类似于加载器，它会以字节的方式把payload注入到内存中来执行。****

 ** ******

 ** **地址:****[
_https://github.com/P0cL4bs/hanzoInjection_](https://github.com/P0cL4bs/hanzoInjection)  

 ** **命令解析：****

 ** **-e 跟上生成的bin文件即可 -p -o 输出的位置/名字 -h 帮助****

###  ** **二、复现****

 ** **1.生成payload****

![1616331792_60574410ee9ee74bd28c3.png!small?1616331791193](https://image.3001.net/images/20210321/1616331792_60574410ee9ee74bd28c3.png!small?1616331791193)

 ** **x64不要勾选，你攻击的系统不论是32还是64这个都不要勾选****

![1616331802_6057441ac291274c1f787.png!small?1616331800973](https://image.3001.net/images/20210321/1616331802_6057441ac291274c1f787.png!small?1616331800973)

 ** **生成到桌面****

![1616331811_605744236b6dffb100a49.png!small?1616331809595](https://image.3001.net/images/20210321/1616331811_605744236b6dffb100a49.png!small?1616331809595)

 ** **2.将生成的bin文件和放到hanzo文件夹里面，一起上传到靶机上面进行执行****

 ** **执行命令****

 ** **hanzolnjection.exe -e payload.bin****

 ** **这里我们使用windows server 2016来测试****

![1616331820_6057442ca233102c0af3f.png!small?1616331819153](https://image.3001.net/images/20210321/1616331820_6057442ca233102c0af3f.png!small?1616331819153)

 ** **发现成功上线****

![1616331829_60574435ba01980e49abc.png!small?1616331828081](https://image.3001.net/images/20210321/1616331829_60574435ba01980e49abc.png!small?1616331828081)

  

