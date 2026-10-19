![](https://image.3001.net/images/20210329/1616949022_6060af1eea6d26a1ee896.png!small)

## 写在前面的话

OSCP-Exam-Report-Template-Markdown这款工具是一个针对Offensive Security
OSCP、OSWE、OSCE、OSEE、OSWP测试报告的Markdown模板。在它的帮助下，当你在进行Offensive Security
OSCP、OSWE、OSCE、OSEE、OSWP测试的时候，就不再需要LaTeX、Microsoft Office Word和LibreOffice了！

 **现在，当你在编校你的测试报告时，效率和速度都将获得极大提升。**

> 编写校对速度提升：大大减少你在编写校对测试报告时所需的时间。
>
> 所见即所得的编辑器无格式问题：Microsoft Office Word和LibreOffice用户，可以跟那些不需要的空格和换行符说再见了。
>
> Markdown配置复用：我们可以直接将自己习惯的格式（无论加粗还是字体）直接应用到报告中。
>
> 支持版本控制：将您的标记模板保存到一个私有的Git存储库中。
>
> 支持使用熟悉的编辑器或笔记应用：比如说VSCode、Atom、Vnote、QQwnNotes或Boostnote等等。
>
> 干净的专家级报告风格：专业的人使用专业的报告。
>
> 无错误：使用生成脚本来生成报告和存档，这样就不会出现任何提交格式和名称错误。

![](https://image.3001.net/images/20210329/1616949040_6060af30e4f54db1cc726.png!small)

## 工具要求

[ _Pandoc_](https://pandoc.org/installing.html)；

LaTeX（比如说[ _TeX Live_](http://www.tug.org/texlive/)）：为了获取pdflatex或xelatex；

E _isvogel Pandoc LaTeX PDF_ _模板_；

[ _p7zip_](http://p7zip.sourceforge.net/)（如果你想要使用脚本生成文档的话）；

## 工具使用

使用Markdown编写你的测试报告。

### 自动化使用

工具脚本将帮助我们完成下列操作：

> 选择模板；
>
> 选择语句高亮风格；
>
> 生成PDF；
>
> 生成7z文档；
    
    
    ruby generate.rb

### 手动使用

从Markdown模板生成PDF报告：

    
    
    pandoc src/OSCP-exam-report-template_whoisflynn_v3.2.md \
    
    -o output/OSCP-OS-XXXXX-Exam-Report.pdf \
    
    --from markdown+yaml_metadata_block+raw_html \
    
    --template eisvogel \
    
    --table-of-contents \
    
    --toc-depth 6 \
    
    --number-sections \
    
    --top-level-division=chapter \
    
    --highlight-style breezedark

你可以使用 _\--highlight-style_选项修改代码语句高亮主题。

## 工具颜色集

我们可以使用模板YAML前端颜色集来呈现我们的报告：

![](https://image.3001.net/images/20210329/1616949070_6060af4e07713726eceb3.png!small)

## 可用模板

 **渗透测试：**

> OSCP：[ _Official Offensive Security Template
> v1_](https://github.com/noraj/OSCP-Exam-Report-Template-> Markdown/blob/master/output/OSCP-exam-report-template_OS_v1.pdf)、[ _Official
> Offensive Security Template v_](https://github.com/noraj/OSCP-Exam-Report-> Template-Markdown/blob/master/output/OSCP-exam-report-template_OS_v2.pdf)2
>
> OSWP：[ _Official Offensive Security Template
> v1_](https://github.com/noraj/OSCP-Exam-Report-Template-> Markdown/blob/master/output/OSWP-exam-report-template_OS_v1.pdf)
>
> OSEP：[ _Official Offensive Security Template
> v1_](https://github.com/noraj/OSCP-Exam-Report-Template-> Markdown/blob/master/output/OSEP-exam-report-template_OS_v1.pdf)

 **Web应用程序：**

> OSWE：[ _Official Offensive Security Template
> v1_](https://github.com/noraj/OSCP-Exam-Report-Template-> Markdown/blob/master/output/OSWE-exam-report-template_OS_v1.pdf)

 **漏洞利用开发：**

> OSED：[ _Official Offensive Security Template
> v1_](https://github.com/noraj/OSCP-Exam-Report-Template-> Markdown/blob/master/output/OSED-exam-report-template_OS_v1.pdf)
>
> OSEE：[ _Official Offensive Security Template
> v1_](https://github.com/noraj/OSCP-Exam-Report-Template-> Markdown/blob/master/output/OSEE-exam-report-template_OS_v1.pdf)
>
> OSCE ：[ _Official Offensive Security Template
> v1﻿_](https://github.com/noraj/OSCP-Exam-Report-Template-> Markdown/blob/master/output/OSCE-exam-report-template_OS_v1.pdf)

## 工具演示

 **OSCP whoisflynn improved template v3.2：**

![](https://image.3001.net/images/20210329/1616949170_6060afb222b1c0e970f6c.png!small)

![](https://image.3001.net/images/20210329/1616949176_6060afb88e6c4c4201152.png!small)

 **OSCP Official Offensive Security Template v1：**

![](https://image.3001.net/images/20210329/1616949186_6060afc29a4e94d99d2d1.png!small)

![](https://image.3001.net/images/20210329/1616949197_6060afcd806644451df62.png!small)

## 项目地址

OSCP-Exam-Report-Template-Markdown：【[
_GitHub传送门_](https://github.com/noraj/OSCP-Exam-Report-Template-Markdown)】

## 参考资料

[ _https://support.offensive-security.com/oscp-exam-guide/#submission-format-and-name_](https://support.offensive-security.com/oscp-exam-guide/#submission-format-and-name)

[ _https://pandoc.org/installing.html_](https://pandoc.org/installing.html)

[ _http://www.tug.org/texlive/_](http://www.tug.org/texlive/)

[ _https://github.com/Wandmalfarbe/pandoc-latex-template#installation﻿_](https://github.com/Wandmalfarbe/pandoc-latex-template#installation)

[ _http://p7zip.sourceforge.net/_](http://p7zip.sourceforge.net/)

[ _https://pandoc.org/MANUAL.html#option--highlight-style﻿_](https://pandoc.org/MANUAL.html#option--highlight-style)

