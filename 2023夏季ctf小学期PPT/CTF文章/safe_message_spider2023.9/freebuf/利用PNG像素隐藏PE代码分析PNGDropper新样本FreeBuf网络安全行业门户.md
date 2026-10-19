## 前言

 **在这篇文章中，我们将跟大家介绍Turla组织研发和使用的PNG Dropper恶意软件。在2017年8月份，沉寂已久的PNG
Dropper重返人们的视野，而且当时它主要用来传播Snake，但近期研究人员又检测到了携带新型Payload的PNG Dropper样本，NCC
Group的研究人员也将这个样本命名为了RegRunnerSvc。**

## PNG Dropper

Carbon Black的研究团队此前已经对PNG
Dropper组件进行了非常详细的分析【[分析报告](https://www.carbonblack.com/2017/08/18/threat-analysis-carbon-black-threat-research-dissects-png-dropper/)】，但我们还是简单回顾一下它的工作机制吧！

![1.png](https://image.3001.net/images/20181212/1544619643_5c11067ba54bd.png!small)

Dropper的目的是为了加载和运行一个隐藏在多个PNG文件中的PE文件。上图显示的是Dropper的资源数据，我们可以看到有多个代码数据资源入口标记有“PNG”的字样。其中每一个资源都是一个有效的PNG文件，不过打开之后你看到的只是部分彩色像素：

![2.png](https://image.3001.net/images/20181212/1544619652_5c110684efa9c.png!small)

PNG使用了微软的GDI+库进行加载，下图中我们可以看到，代码会调用LockBits来从PNG文件中读取像素数据。像素数据的每一个字节都代表了每一个像素的RGB值。对每一个RGB值进行编码之后我们就能得到PE文件的字节数据了。

![3.png](https://image.3001.net/images/20181212/1544619659_5c11068b0ce91.png!small)

每一个PNG资源都会被枚举，像素数据也都会被提取出来，最终会进行拼接，而最后生成的完整PE文件会存储在内存中。接下来，Dropper需要手动加载PE文，然后执行PE文件的入口函数：

![4.png](https://image.3001.net/images/20181212/1544619667_5c11069366340.png!small)

## RegRunnerSvc

PNG
Dropper会利用其PNG资源解码并运行RegRunnerSvc，而RegRunnerSvc的目的就是从注册表中提取加密Payload，并将其加载进内存，然后运行。下图显示的是RegRunnerSvc的入口点，这里我们可以看到，代码调用了StartServiceCtrlDispatcher，目标服务名称为WerFaultSvc（还负责实现恶意软件的持久感染），很明显攻击者是想让恶意服务伪装成合法的Windows错误报告服务。

![5.png](https://image.3001.net/images/20181212/1544619681_5c1106a1bee39.png!small)

服务设置函数执行后，就需要找出注册表中的目标数据了。一般来说，注册表路径会保存在代码里的一个字符串中，但是PNG
Dropper却不是，因为它会使用RegEnumKeyExA和RegEnumValueA函数来枚举注册表键-值。

![6.png](https://image.3001.net/images/20181212/1544619689_5c1106a940070.png!small)

注册表中的数据包含加密Payload以及解密所需的数据。虽然其中不包含解密密钥，但是它包含了用于生成解密密钥所需的信息，而其中的部分数据使用了微软的CNG库函数（NCrypt*）来进行加密。第一阶段的Dropper将生成解密密钥并存储在系统默认密钥存储器中，这里使用的是“MicrosoftSoftware
Key Storage
Provider”。如果第一阶段的Dropper运行不成功，那么密钥将无法生成和存储，因此解密函数将会退出。下面给出的是解密数据的二进制数据结构：

![7.png](https://image.3001.net/images/20181212/1544619696_5c1106b0a0f6c.png!small)

Header解密成功后，我们就可以进行第二阶段的解密操作了。主Payload使用了AES算法进行加密。首先，代码会将一段注册表数据传递给BCryptGenerateSymmetricKey函数，此时AES解密密钥便创建成功了。密钥生成之后，解密属性便设置成功，Payload即可解密成功。接下来，代码会对解密后的Payload进行检测，以确保PE文件的有效性。如果检测通过，文件将会被加载，入口点将会被调用。

![8.png](https://image.3001.net/images/20181212/1544619708_5c1106bc8c34b.png!small)

## 总结

在这篇文章中，我们对Turla组织所使用的新型PNG
Dropper进行了分析。该组织目前也在配合RegRunnerSvc这个新组件来实施攻击，RegRunnerSvc可以从注册表中提取和加密PE文件，并对其进行解密和运行。目测，该组织是从无文件型恶意软件那里得到的灵感，比如说Poweliks和Kovter，而他们的目标就是为了在代码文件内尽可能地不留下攻击证据。

除此之外，我们还开发出了一款专门从PNG
Dropper中提取Payload的工具，并且将其开源，感兴趣的同学可以下载学习：【[下载地址】](https://github.com/nccgroup/Cyber-Defence/tree/master/Scripts/turla_image_decoder)。

### Yara规则

    
    
    rule turla_png_dropper {
    
        meta:
    
            author = "Ben Humphrey"
    
            description = "Detects the PNGDropper used by the Turla group"
    
           sha256 = 
    
    "6ed939f59476fd31dc4d99e96136e928fbd88aec0d9c59846092c0e93a3c0e27"
    
     
    
        strings:
    
            $api0 = "GdiplusStartup"
    
            $api1 = "GdipAlloc"
    
            $api2 ="GdipCreateBitmapFromStreamICM"
    
            $api3 = "GdipBitmapLockBits"
    
            $api4 = "GdipGetImageWidth"
    
            $api5 = "GdipGetImageHeight"
    
            $api6 = "GdiplusShutdown"
    
     
    
            $code32 = {
    
                8B 46 3C               // mov     eax, [esi+3Ch]
    
                B9 0B 01 00 00         // mov     ecx, 10Bh
    
                66 39 4C 30 18         // cmp     [eax+esi+18h], cx
    
                8B 44 30 28            // mov     eax, [eax+esi+28h]
    
                6A 00                  // push    0
    
                B9 AF BE AD DE         // mov     ecx, 0DEADBEAFh
    
                51                     // push    ecx
    
                51                     // push    ecx
    
                03 C6                  // add     eax, esi
    
                56                     // push    esi
    
                FF D0                  // call eax
    
            }
    
     
    
            $code64 = {
    
               48 63 43 3C            // movsxdrax, dword ptr [rbx+3Ch]
    
                B9 0B 01 00 00         // mov ecx, 10Bh
    
                BA AF BE AD DE         // mov edx, 0DEADBEAFh
    
                66 39 4C 18 18         // cmp [rax+rbx+18h], cx
    
                8B 44 18 28            // mov eax, [rax+rbx+28h]
    
                45 33 C9               // xor r9d, r9d
    
                44 8B C2               // mov r8d, edx
    
                48 8B CB               // mov rcx, rbx
    
                48 03 C3               // add rax, rbx
    
                FF D0                  // call rax
    
            }
    
     
    
        condition:
    
            (uint16(0) == 0x5A4D anduint16(uint32(0x3c)) == 0x4550) and
    
            all of ($api*) and 
    
            1 of ($code*)
    
    }
    
    
    rule turla_png_reg_enum_payload {
    
          meta:
    
                    author = "BenHumphrey"
    
                    description = "Payloadthat has most recently been dropped by the
    
    TurlaPNG Dropper"
    
                   shas256 =
    
    "fea27eb2e939e930c8617dcf64366d1649988f30555f6ee9cd09fe54e4bc22b3"
    
     
    
          strings:
    
              $crypt00 = "Microsoft SoftwareKey Storage Provider" wide
    
              $crypt01 ="ChainingModeCBC" wide
    
              $crypt02 = "AES" wide
    
     
    
          condition:
    
              (uint16(0) == 0x5A4D anduint16(uint32(0x3c)) == 0x4550) and
    
              pe.imports("advapi32.dll","StartServiceCtrlDispatcherA") and 
    
              pe.imports("advapi32.dll","RegEnumValueA") and 
    
              pe.imports("advapi32.dll","RegEnumKeyExA") and 
    
              pe.imports("ncrypt.dll","NCryptOpenStorageProvider") and 
    
              pe.imports("ncrypt.dll","NCryptEnumKeys") and 
    
              pe.imports("ncrypt.dll","NCryptOpenKey") and 
    
              pe.imports("ncrypt.dll","NCryptDecrypt") and
    
              pe.imports("ncrypt.dll","BCryptGenerateSymmetricKey") and 
    
              pe.imports("ncrypt.dll","BCryptGetProperty") and 
    
              pe.imports("ncrypt.dll","BCryptDecrypt") and 
    
              pe.imports("ncrypt.dll","BCryptEncrypt") and 
    
              all of them
    
    }

### 入侵威胁指标

样本分析：

    
    
    1、6ed939f59476fd31dc4d99e96136e928fbd88aec0d9c59846092c0e93a3c0e27(PNG Dropper)
    
    2、fea27eb2e939e930c8617dcf64366d1649988f30555f6ee9cd09fe54e4bc22b3(从PNG dropper中获取到的Payload)

服务：

    
    
    1、WerFaultSvc

## 参考资料

> <https://www.carbonblack.com/2017/08/18/threat-analysis-carbon-black-threat-> research-dissects-png-dropper/>

 ***参考来源：[nccgroup](https://www.nccgroup.trust/us/about-us/newsroom-and-events/blog/2018/november/turla-png-dropper-is-back/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

