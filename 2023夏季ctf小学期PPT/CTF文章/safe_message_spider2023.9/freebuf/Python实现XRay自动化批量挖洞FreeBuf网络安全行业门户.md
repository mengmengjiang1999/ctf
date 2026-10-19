![image](https://image.3001.net/images/20210120/1611139508_600809b4e341814b90fa2.jpeg!small)

## 0x01 前言

小白我看到一个脚本不错，可以使得原本没有批量扫描功能的X-Ray实现此功能，特别改了一些，使体验更好

## 0x02 过程

详细过程如下：

## 采集子域名

用朋友采集的子域名，来源是oneforall+jsfinder+fuzzer，保存为url.txt文件  
![5\[133VX9S\({1O@$`I7Q\(MEY.png
](https://image.3001.net/images/20210120/1611137975_600803b7cceab4486dc35.png!small)

## 运行Python脚本

在同一目录创建一个文件exp.txt，然后运行xray.py脚本如下：

    
    
    import os
    
    def xray(ip):
    
        print(("./xray webscan --basic-crawler {0}/ --html-output {1}.html").format(ip, ip))
    
    if __name__ == "__main__":
    
        with open('url.txt', 'r') as file:
            list = [www.strip() for www in file.readlines()]
        with open('exp.txt', 'w') as f:
            for ip in list:
                xray(ip)
                f.write(("./xray webscan --basic-crawler {0}/ --html-output {1}.html\n").format(ip, ip))
    

## 复制粘贴

打开exp.txt文件，右键全选，直接复制，比起原来的代码，更适合大量子域名扫描  
![\)TO{1J\]B}XNJ}U6\(ASMB1NK.png](https://image.3001.net/images/20210120/1611138611_60080633a43d6a0653085.png!small)  
打开PowerShell，cd到对应的目录中，右键直接粘贴，开启X-Ray自动化挖洞进程（这里的xray.exe命名请注意）

# 总结

不断学习总结，梅南德说过：“辛劳者无须失望，任何事情都靠辛劳完成”。

