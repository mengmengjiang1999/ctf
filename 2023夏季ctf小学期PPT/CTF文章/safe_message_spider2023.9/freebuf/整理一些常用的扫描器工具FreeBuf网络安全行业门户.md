渗透测试和真实的攻击场景中，需要使用到一系列的黑客工具，今晚抽空专门整理一些扫描器工具系列。在kali和parrot这样的专门为网络安全专家开发的操作系统内置了较多的信息搜集工具，其中就包含常见的扫描器等等。而也有一些没有被kali内置并且使用起来又比较好用的，单独列出来可供选择使用。

 **1、网络扫描器**

    
    
    nmap

![图片](https://image.3001.net/images/20221010/1665406473_634416095e5a4615ad8ef.png!small)

    
    
    OpenVAS Scanner

![图片](https://image.3001.net/images/20221010/1665406538_6344164a5a04589b5d043.png!small)

 **2、WEB扫描器**

    
    
    Nikto

![图片](https://image.3001.net/images/20221010/1665406564_634416644f837b7f2b715.png!small)

    
    
    sslyze

![图片](https://image.3001.net/images/20221010/1665406578_63441672c30c5614292e7.png!small)

    
    
    whatweb

![图片](https://image.3001.net/images/20221010/1665406589_6344167ddce142689da60.png!small)

 **3、CMS扫描器**

    
    
    wpscan

![图片](https://image.3001.net/images/20221010/1665406601_63441689688d4db5ea528.png!small)

    
    
    joomlavs

![图片](https://image.3001.net/images/20221010/1665406612_63441694373dcbff1817b.png!small)

    
    
    droopescan

![图片](https://image.3001.net/images/20221010/1665406649_634416b98cbdc1c17c64f.png!small)

  * 

    
    
    domain info scanner :recon-ng

![图片](https://image.3001.net/images/20221010/1665406664_634416c827220f5d898e2.png!small)

扫描器在展开渗透测试的第一阶段其中非常重要的作用，搜集足够的目标信息数据，掌握目标的资产清单，对资产中存在的漏洞进行识别，然后在后面展开针对性的威胁建模以及脆弱性分析，为成功拿下目标奠定基础。

上面展示的这些扫描器工具，不会对目标系统造成直接伤害，因此呢在平时的练习过程中可以多多测试使用的方法，nmap的功能比较强大，但是结合OpenVAS扫描的结果会更加全面，所以这里提出要锻炼灵活组合扫描器的能力以获取更全面的信息的目的。

