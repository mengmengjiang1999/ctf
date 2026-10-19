## 概要介绍

 **mmpi**
，是一款使用python实现的开源邮件快速检测工具库，基于[community](https://github.com/cuckoosandbox/community)框架设计开发。
**mmpi** 支持对邮件头、邮件正文、邮件附件的解析检测，并输出json检测报告。

代码项目地址：[ **mmpi**](https://github.com/a232319779/mmpi)

pypi项目地址：[
**pypi**](%5Bhttps%3A/pypi.org/project/mmpi/%5D\(https:/pypi.org/project/mmpi/\))

 **mmpi** ，邮件快速检测工具库检测逻辑：

  1. 支持解析提取邮件头数据，包括收件人、发件人的姓名和邮箱，邮件主题，邮件发送时间，以及邮件原始发送IP。通过检测发件人邮箱和邮件原始发送IP，实现对邮件头的检测。

  2. 支持对邮件正文的解析检测，提取 **text** 和 **html** 格式的邮件正文，对 **text** 邮件正文进行关键字匹配，对 **html** 邮件正文进行解析分析检测，实现 **探针邮件检测** 、 **钓鱼邮件检测** 、 **垃圾邮件检测** 等其他检测。

  3. 支持对邮件附件等解析检测

    1. ole文件格式：如doc、xls等，提取其中的vba宏代码、模板注入链接

    2. zip文件格式：提取压缩文件列表，统计文件名、文件格式等

    3. rtf文件格式：解析内嵌ole对象等

    4. 其他文件格式：如PE可执行文件

  4. 检测方式包括

    1. 基础信息规则检测方式

    2. yara规则检测方式

## 适用前提

 **mmpi** 的分析判定检测前提：邮件系统环境。脱离邮件环境上下文，检测规则的依据就不可靠了。

## 使用方式

### 1\. 安装

    
    
    $ pip install mmpi

备注： **windows** 安装 **yara-python** ，点击[
**这里**](https://github.com/VirusTotal/yara-python/releases)下载

### 2\. 命令执行

    
    
    $ mmpi-run $email_path

### 3\. 快速开始

    
    
    from mmpi import mmpi
    
    def main():
        emp = mmpi()
        emp.parse('test.eml')
        report = emp.get_report()
        print(report)
    
    if __name__ == "__main__":
    main()

### 4\. 输出格式

    
    
    {
        // 固定字段
        "headers": [],
        "body": [],
        "attachments": [],
        "signatures": []
        // 动态字段
        "vba": [],
        "rtf": [],
        ......
    }

## 工具说明

 **mmpi** 完全基于python开发，使用python原生 **email、html、zip** 库进行解析，基于[
**oletools**](https://github.com/decalage2/oletools)做定制化修改，支持对 **office** 文档和
**rtf** 文档的解析，再结合 **yara** 实现对其他文件的检测。

### 项目代码结构

    
    
    .
    ├── mmpi
    │   ├── common
    │   ├── core
    │   ├── data
    │   │   ├── signatures
    │   │   │   ├── eml
    │   │   │   ├── html
    │   │   │   ├── ole
    │   │   │   ├── other
    │   │   │   ├── rtf
    │   │   │   └── zip
    │   │   ├── white
    │   │   └── yara
    │   │       ├── exe
    │   │       ├── pdf
    │   │       └── vba
    │   └── processing
    └── tests
        └── samples

  *  **mmpi/common** ：基础模块，实现基本流程功能

  *  **mmpi/core** ：核心调度模块，实现插件的加载及相关模块的初始化

  *  **mmpi/data** ：核心检测模块，实现基本检测规则及yara检测规则

  *  **mmpi/processing** ：核心解析模块，实现 **eml、html、zip** 等文件格式的解析

  *  **tests** ：测试模块

### 检测规则示例说明

 **1\. PE文件伪装文档类检测**

 **检测规则：压缩包中文件名以.exe结尾，并且中间插入20个以上空格的**

    
    
    class PEFakeDocument(Signature):
        authors = ["ddvv"]
        sig_type = 'zip'
        name = "pe_fake_document"
        severity = 9
        description = "PE File Fake Document"
    
        def on_complete(self):
            results = self.get_results()
            for result in results:
                if result.get('type', '') == self.sig_type:
                    infos = result.get('value', {}).get('infos', [])
                    for info in infos:
                        file_type = info.get('type')
                        file_name = info.get('name')
                        space_count = file_name.count('  ')
                        if 'exe' == file_type and space_count > 20:
                            self.mark(type="zip", tag=self.name, data=info.get('name'))
                            return self.has_marks()
            return None

 **2\. DLL劫持检测**

 **检测规则：压缩包中同时存在exe和dll文件**

    
    
    class DLLHijacking(Signature):
        authors = ["ddvv"]
        sig_type = 'zip'
        name = "dll_hijacking"
        severity = 9
        description = "DLL Hijacking"
    
        def on_complete(self):
            results = self.get_results()
            for result in results:
                if result.get('type', '') == self.sig_type:
                    infos = result.get('value', {}).get('infos', [])
                    file_types = [info.get('type') for info in infos]
                    if set(['exe', 'dll']).issubset(file_types):
                        self.mark(type="zip", tag=self.name)
                        return self.has_marks()
            return None

 **3\. RTF漏洞利用检测**

 **检测规则：RTF文档中存在OLE对象，并且class_name是OLE2Link或者以equation开头**

    
    
    class RTFExploitDetected(Signature):
        authors = ["ddvv"]
        sig_type = 'rtf'
        name = "rtf_exploit_detected"
        severity = 9
        description = "RTF Exploit Detected"
    
        def on_complete(self):
            results = self.get_results()
            for result in results:
                if result.get('type', '') == self.sig_type:
                    infos = result.get('value', {}).get('infos', [])
                    for info in infos:
                        if info.get('is_ole', False):
                            class_name = info.get('class_name', '')
                            if class_name == 'OLE2Link' or class_name.lower().startswith('equation'):
                                self.mark(type="rtf", tag=self.name)
                                return self.has_marks()
            return None

### 结果示例

 **结果说明：邮件包含漏洞利用的RTF文档，属于恶意邮件。**

包括收发件人信息、主题信息、发送时间，邮件正文，以及附件信息。

 **vba** 和 **rtf** 字段为附件检测基本信息。

 **signatures** 字段说明命中规则。

    
    
    {
        "headers": [
            {
                "From": [
                    {
                        "name": "Mohd Mukhriz Ramli (MLNG/GNE)",
                        "addr": "info@vm1599159.3ssd.had.wf"
                    }
                ],
                "To": [
                    {
                        "name": "",
                        "addr": ""
                    }
                ],
                "Subject": "Re: Proforma Invoice",
                "Date": "2020-11-24 12:37:38 UTC+01:00",
                "X-Originating-IP": []
            }
        ],
        "body": [
            {
                "type": "text",
                "content": " \nDEAR SIR, \n\nPLEASE SIGN THE PROFORMA INVOICE SO THAT I CAN PAY AS SOON AS POSSIBLE.\n\nATTACHED IS THE PROFORMA INVOICE,\n\nPLEASE REPLY QUICKLY, \n\nTHANKS & REGARDS' \n\nRAJASHEKAR \n\n Dubai I Kuwait I Saudi Arabia I India I Egypt \nKuwait: +965 22261501 \nSaudi Arabia: +966 920033029 \nUAE: +971 42431343 \nEmail ID: help@rehlat.co [1]m\n \n\nLinks:\n------\n[1]\nhttps://deref-mail.com/mail/client/OV1N7sILlK8/dereferrer/?redirectUrl=https%3A%2F%2Fe.mail.ru%2Fcompose%2F%3Fmailto%3Dmailto%253ahelp%40rehlat.com"
            }
        ],
        "attachments": [
            {
                "type": "doc",
                "filename": "Proforma Invoice.doc",
                "filesize": 1826535,
                "md5": "558c4aa596b0c4259182253a86b35e8c",
                "sha1": "63982d410879c09ca090a64873bc582fcc7d802b"
            }
        ],
        "vba": [],
        "rtf": [
            {
                "is_ole": true,
                "format_id": 2,
                "format_type": "Embedded",
                "class_name": "EQUATion.3",
                "data_size": 912305,
                "md5": "a5cee525de80eb537cfea247271ad714"
            }
        ],
        "signatures": [
            {
                "name": "rtf_suspicious_detected",
                "description": "RTF Suspicious Detected",
                "severity": 3,
                "marks": [
                    {
                        "type": "rtf",
                        "tag": "rtf_suspicious_detected"
                    }
                ],
                "markcount": 1
            },
            {
                "name": "rtf_exploit_detected",
                "description": "RTF Exploit Detected",
                "severity": 9,
                "marks": [
                    {
                        "type": "rtf",
                        "tag": "rtf_exploit_detected"
                    }
                ],
                "markcount": 1
            }
        ]
    }

