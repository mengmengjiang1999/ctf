![Bandit：一款Python代码安全漏洞检测工具](https://image.3001.net/images/20190530/1559228563_5ceff09353f25.png!small)

## 工具介绍

**Bandit这款工具可以用来搜索Python代码中常见的安全问题，在检测过程中，Bandit会对每一份Python代码文件进行处理，并构建AST，然后针对每一个AST节点运行相应的检测插件。完成安全扫描之后，Bandit会直接给用户生成检测报告。**

## 工具安装

Bandit使用PyPI来进行分发，建议广大用户直接使用pip来安装Bandit。

创建虚拟环境（可选）：

    
    
    virtualenv bandit-env

安装Bandit：

    
    
    pip install bandit
    
    # Or if you're working with a Python 3 project
    
    pip3 install bandit

运行Bandit：

    
    
    bandit -r path/to/your/code

用户还可以使用源码文件直接安装Bandit，先从PyPI下载原tarball，然后运行下列命令：

    
    
    python setup.py install

## 工具使用

节点树使用样例：

    
    
    bandit -r ~/your_repos/project

examples/目录遍历使用样例，显示三行内容，并只报告高危问题：

    
    
    bandit examples/*.py -n 3 –lll

Bandit还能够结合配置参数一起运行，运行下列命令即可使用ShellInjection来对examples目录运行安全扫描：

    
    
    bandit examples/*.py -p ShellInjection

Bandit还支持使用标准输入模式来扫描指定行数的代码：

    
    
    cat examples/imports.py | bandit –

### 使用样例：

    
    
    $bandit -h
    
    usage:bandit [-h] [-r] [-a {file,vuln}] [-n CONTEXT_LINES] [-c CONFIG_FILE]
    
                  [-p PROFILE] [-t TESTS] [-sSKIPS] [-l] [-i]
    
                  [-f{csv,custom,html,json,screen,txt,xml,yaml}]
    
                  [--msg-template MSG_TEMPLATE] [-o[OUTPUT_FILE]] [-v] [-d] [-q]
    
                  [--ignore-nosec] [-x EXCLUDED_PATHS] [-bBASELINE]
    
                  [--ini INI_PATH] [--version]
    
                  [targets [targets ...]]
    
     
    
    Bandit- a Python source code security analyzer
    
     
    
    positionalarguments:
    
      targets               source file(s) or directory(s)to be tested
    
     
    
    optionalarguments:
    
      -h, --help            show this help message and exit
    
      -r, --recursive       find and process files in subdirectories
    
      -a {file,vuln}, --aggregate {file,vuln}
    
                            aggregate output byvulnerability (default) or by
    
                            filename
    
      -n CONTEXT_LINES, --number CONTEXT_LINES
    
                            maximum number of codelines to output for each issue
    
      -c CONFIG_FILE, --configfile CONFIG_FILE
    
                            optional config file touse for selecting plugins and
    
                            overriding defaults
    
      -p PROFILE, --profile PROFILE
    
                            profile to use(defaults to executing all tests)
    
      -t TESTS, --tests TESTS
    
                            comma-separated list oftest IDs to run
    
      -s SKIPS, --skip SKIPS
    
                            comma-separated list oftest IDs to skip
    
      -l, --level           report only issues of a givenseverity level or higher
    
                            (-l for LOW, -ll for MEDIUM, -lll forHIGH)
    
      -i, --confidence      report only issues of a given confidencelevel or
    
                            higher (-i for LOW, -iifor MEDIUM, -iii for HIGH)
    
      -f{csv,custom,html,json,screen,txt,xml,yaml}, --format{csv,custom,html,json,screen,txt,xml,yaml}
    
                            specify output format
    
      --msg-template MSG_TEMPLATE
    
                            specify output messagetemplate (only usable with
    
                            --format custom), seeCUSTOM FORMAT section for list
    
                            of available values
    
      -o [OUTPUT_FILE], --output [OUTPUT_FILE]
    
                            write report tofilename
    
      -v, --verbose         output extra information like excludedand included
    
                            files
    
      -d, --debug           turn on debug mode
    
      -q, --quiet, --silent
    
                            only show output in thecase of an error
    
      --ignore-nosec        do not skip lines with # nosec comments
    
      -x EXCLUDED_PATHS, --exclude EXCLUDED_PATHS
    
                            comma-separated list ofpaths (glob patterns supported)
    
                            to exclude from scan(note that these are in addition
    
                            to the excluded pathsprovided in the config file)
    
      -b BASELINE, --baseline BASELINE
    
                            path of a baselinereport to compare against (only
    
                            JSON-formatted filesare accepted)
    
      --ini INI_PATH        path to a .bandit file that suppliescommand line
    
                            arguments
    
      --version             show program's version number andexit
    
     
    
    CUSTOMFORMATTING
    
    -----------------    
     
    
    Availabletags:
    
     
    
        {abspath}, {relpath}, {line},  {test_id},
    
        {severity}, {msg}, {confidence}, {range}
    
     
    
    Exampleusage:
    
     
    
        Default template:
    
        bandit -r examples/ --format custom--msg-template \
    
        "{abspath}:{line}: {test_id}[bandit]:{severity}: {msg}"
    
     
    
        Provides same output as:
    
        bandit -r examples/ --format custom
    
     
    
        Tags can also be formatted in python string.format()style:
    
        bandit -r examples/ --format custom--msg-template \
    
        "{relpath:20.20s}: {line:03}:{test_id:^8}: DEFECT: {msg:>20}"
    
     
    
        See python documentation for moreinformation about formatting style:
    
        <https://docs.python.org/3.4/library/string.html>
    
     
    
    Thefollowing tests were discovered and loaded:
    
    -----------------------------------------------    
     
    
      B101 assert_used
    
      B102 exec_used
    
      B103 set_bad_file_permissions
    
      B104 hardcoded_bind_all_interfaces
    
      B105 hardcoded_password_string
    
      B106 hardcoded_password_funcarg
    
      B107 hardcoded_password_default
    
      B108 hardcoded_tmp_directory
    
      B110 try_except_pass
    
      B112 try_except_continue
    
      B201 flask_debug_true
    
      B301 pickle
    
      B302 marshal
    
      B303 md5
    
      B304 ciphers
    
      B305 cipher_modes
    
      B306 mktemp_q
    
      B307 eval
    
      B308 mark_safe
    
      B309 httpsconnection
    
      B310 urllib_urlopen
    
      B311 random
    
      B312 telnetlib
    
      B313 xml_bad_cElementTree
    
      B314 xml_bad_ElementTree
    
      B315 xml_bad_expatreader
    
      B316 xml_bad_expatbuilder
    
      B317 xml_bad_sax
    
      B318 xml_bad_minidom
    
      B319 xml_bad_pulldom
    
      B320 xml_bad_etree
    
      B321 ftplib
    
      B322 input
    
      B323 unverified_context
    
      B324 hashlib_new_insecure_functions
    
      B325 tempnam
    
      B401 import_telnetlib
    
      B402 import_ftplib
    
      B403 import_pickle
    
      B404 import_subprocess
    
      B405 import_xml_etree
    
      B406 import_xml_sax
    
      B407 import_xml_expat
    
      B408 import_xml_minidom
    
      B409 import_xml_pulldom
    
      B410 import_lxml
    
      B411 import_xmlrpclib
    
      B412 import_httpoxy
    
      B413 import_pycrypto
    
      B501 request_with_no_cert_validation
    
      B502 ssl_with_bad_version
    
      B503 ssl_with_bad_defaults
    
      B504 ssl_with_no_version
    
      B505 weak_cryptographic_key
    
      B506 yaml_load
    
      B507 ssh_no_host_key_verification
    
      B601 paramiko_calls
    
      B602 subprocess_popen_with_shell_equals_true
    
      B603 subprocess_without_shell_equals_true
    
      B604 any_other_function_with_shell_equals_true
    
      B605 start_process_with_a_shell
    
      B606 start_process_with_no_shell
    
      B607 start_process_with_partial_path
    
      B608 hardcoded_sql_expressions
    
      B609 linux_commands_wildcard_injection
    
      B610 django_extra_used
    
      B611 django_rawsql_used
    
      B701 jinja2_autoescape_false
    
      B702 use_of_mako_templates
    
      B703 django_mark_safe

## 基准线

Bandit允许用户指定需要进行比对的基线报告路径：

    
    
    bandit -b BASELINE

这样可以帮助大家忽略某些已知问题，或者是那些你不认为是问题的“问题”。大家可以使用下列命令生成基线报告：

    
    
    bandit -f json -o PATH_TO_OUTPUT_FILE

### 版本控制整合

安装并使用pre-commit，将下列内容添加至代码库的.pre-commit-config.yaml文件中：

    
    
    repos:
    
    -   repo: <https://github.com/PyCQA/bandit>
    
        rev: '' # Update me!
    
        hooks:
    
    - id: bandit

然后运行pre-commit即可。

## 扩展Bandit

Bandit允许用户编写和注册扩展以实现自定义检测或格式化（Formatter）功能。Bandit可以从下列两个节点加载插件：

    
    
    bandit.formatters
    
    bandit.plugins

Formatter需要接收下列四种输入参数：

    
    
    result_store:一个bandit.core.BanditResultStore实例
    
    file_list:需要扫描检测的文件列表
    
    scores:每个文件的扫描评分
    
    excluded_files:列表中不需要扫描的文件

利用bandit.checks来对特定类型的AST节点进行检测扫描：

    
    
    @bandit.checks('Call')
    
    defprohibit_unsafe_deserialization(context):
    
        if 'unsafe_load' incontext.call_function_name_qual:
    
            return bandit.Issue(
    
                severity=bandit.HIGH,
    
                confidence=bandit.HIGH,
    
                text="Unsafe deserializationdetected."
    
            )

### 注册插件时Bandit给用户提供了两个选项：

1、 如果你直接使用了安装工具（setuptools），我们需要在setup调用中添加下列信息：

    
    
    # Ifyou have an imaginary bson formatter in the bandit_bson module
    
    # anda function called `formatter`.
    
    entry_points={'bandit.formatters':['bson = bandit_bson:formatter']}
    
    # Ora check for using mako templates in bandit_mako that
    
    entry_points={'bandit.plugins':['mako = bandit_mako']}

2、 如果你使用的是pbr，你需要在setup.cfg文件中添加下列信息：

    
    
    [entry_points]
    
    bandit.formatters=
    
        bson= bandit_bson:formatter
    
    bandit.plugins=
    
        mako = bandit_mako

## 项目地址

参考文档：【[最新版本](https://bandit.readthedocs.io/en/latest/)】

Bandit：【[GitHub传送门](https://github.com/PyCQA/bandit)】

漏洞提交：【[传送门](https://github.com/PyCQA/bandit/issues)】

### 许可证协议

本项目遵循Apache开源许可证协议。

 ***
参考来源：[bandit](https://github.com/PyCQA/bandit)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

