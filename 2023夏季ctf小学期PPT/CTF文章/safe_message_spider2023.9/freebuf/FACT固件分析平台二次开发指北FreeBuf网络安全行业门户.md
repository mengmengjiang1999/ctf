FACT ( The Firmware Analysis and Comparison Tool ) 是由 Fraunhofer
开发的开源平台，旨在自动化分析设备固件。平台自身在解包、分析和比较模块中提供一些默认功能，最重要的是，提供插件开发接口，可按需自行构建定制化系统。

本文侧重介绍平台二次开发，阐述主要插件接口使用，并给出简单的自编栗子，搭建过程Freebuf上已有[相关文章](../sectool/179056.html)，这里只粗略涉及。

## 0x01 平台掠影

![](https://image.3001.net/images/20220301/1646132715_621dfdebe6ffd2b531365.png!small)

### 功能介绍

FACT由三个组件组成：前端、数据库和后端。其数据流原理图如下所示，这里不做赘述：

![](https://image.3001.net/images/20220301/1646132815_621dfe4f0fc887ea9536b.png!small)所有组件都可以安装在一台或多台机器上，需要较高配置，因为会对固件检测到的所有文件不停作Hash和分析，简直就是在挖~矿~，笔者将环境迁移到服务器卡顿感才消失。

###
![](https://image.3001.net/images/20220301/1646133001_621dff0951f97fb7ccefb.png!small)搭建过程

由于搭建过程需要Git远程数据，刚开始逐个解决问题非常繁琐，建议使用 shell proxy，整个过程会丝滑很多，笔者使用的是Ubuntu
20.04.2，虽然不再Github列表里，但测试是成功的。

搭建简要命令如下：

    
    
    # 使用shell proxy, proxy端略
    export http_proxy=http://127.0.0.1:port
    export https_proxy=http://127.0.0.1:port
    
    # 安装工具 (以用户身份执行以下命令，不是root)
    $ sudo apt update && sudo apt upgrade && sudo apt install git
    $ git clone https://github.com/fkie-cad/FACT_core.git ~/FACT_core
    
    # 预安装
    $ ~/FACT_core/src/install/pre_install.sh && sudo mkdir /media/data && sudo chown -R $USER /media/data
    $ sudo reboot
    
    # 重启后安装主要模块
    $ ~/FACT_core/src/install.py
    
    # 启动FACT服务
    $ ~/FACT_core/start_all_installed_fact_components
    # 访问 localhost:5000 使用 ctrl+c关闭
    # 当然也可以修改地址使端口对外
    

### 可能的问题

大部分问题都因为requests没安装完全导致的报错，在使用shell proxy后得以解决，这里不一一列举，过程中如果报

 **FileNotFoundError: [Errno 2] No such file or directory:
'/tmp/extractor/input’** 的错误，

解决方法是修改 **src/unpacker/unpack.py** 文件添加自己指定的dir目录，具体如下：

    
    
    diff --git a/src/unpacker/unpack.py b/src/unpacker/unpack.py
    index 862e56da..ab352607 100644
    --- a/src/unpacker/unpack.py
    +++ b/src/unpacker/unpack.py
    @@ -32,7 +32,7 @@ class Unpacker(UnpackBase):
                 self._store_unpacking_depth_skip_info(current_fo)
                 return []
    
    -        tmp_dir = TemporaryDirectory(prefix='fact_unpack_')
    +        tmp_dir = TemporaryDirectory(prefix='fact_unpack_', dir="/home/fact/tmp")
    
             file_path = self._generate_local_file_path(current_fo)
    

完成后即可访问，效果图如：

![](https://image.3001.net/images/20220301/1646134169_621e03991934e8613e3a3.png!small)

基本服务起来后就可以开始二次开发，下面介绍插件的开发与UI的修改(如有需求)。

## 0x02 插件开发

### 用户管理

FACT为用户管理提供了专门的手册，如只需创建用户可以调用/src/manage_users.py并按提示操作：

    
    
    create users admin and worker:
    
    create_role
    # superuser
    # analyst
    
    create_user
    # admin
    # password
    
    # worker
    # password again
    
    add_role_to_user
    # admin
    # superuser
    
    # worker
    # analyst
    
    get_apikey_for_user
    # admin
    # worker
    

### 解包 ( unpacker )

解包插件开发是笔者较感兴趣的，在新版(V3.0以上版本，截至到此文章创建最新版本为V3.2)，FACT将解包插件拎出称为[单独项目](https://github.com/fkie-cad/fact_extractor)，并以Docker的形式调用。V2.6以下版本还是集成环境，新旧版本的插件开发机制相同，但V3.0后使用的Docker在使用自研插件时会出现一些问题，希望官方能早日更新，当然也有不优雅的解决方案，笔者的做法是
**修改原始函数文件劫持数据流** ，需要对代码有进一步认识，篇幅限制这里不作赘述。

单独 **Unpacker** 项目使用流程如下：

    
    
    docker pull fkiecad/fact_extractor
    wget https://raw.githubusercontent.com/fkie-cad/fact_extractor/master/extract.py
    chmod +x extract.py
    ./extract.py ./relative/or/absolute/path/to/your/file
    

解包插件需要在 **fact_extractor docker中的src/unpacking** 文件夹下创建单个插件(文件夹)，文件目录和格式如下：

    
    
    .
    ├── __init__.py
    ├── install.sh [OPTIONAL]
    ├── code
    │   ├── __init__.py
    │   └── PLUGIN_NAME.py
    ├── internal [OPTIONAL]
    │   └── ADDITIONAL_SOURCES_OR_CODE
    └── test
        ├── __init__.py
        ├── test_PLUGIN_NAME.py
        └── data [OPTIONAL]
            └── SOME DATA FILES TO TEST
    

**install.sh** 用于插件的安装，不是必要的，实际就是安装自己需要解析的结构的一些依赖和拷贝文件：

    
    
    #!/usr/bin/env bash
    
    # change cwd to current file's directory
    cd "$( dirname "${BASH_SOURCE[0]}" )" 
    
    echo "------------------------------------"
    echo "       SOME MEANINGFUL TITLE        "
    echo "------------------------------------"
    
    [YOUR CODE HERE]
    	
    exit 0 # 这句一定要加
    

**test** 文件夹下的py用于插件可用性的测试，当然也非必要，但鉴于完整性规范最好还是编写。

主功能是 **code** 文件下的 **plugin.py** ，示例如下：

    
    
    '''
    This plugin unpacks CONTAINER_NAME files.
    '''
     
    NAME = 'PLUGIN_NAME'
    MIME_PATTERNS = ['MIME_PATTERN_1', 'MIME_PATTERN_2', ...]
    VERSION = 'x.x'
    
    
    def unpack_function(file_path, tmp_dir):
        '''
        file_path specifies the input file.
        tmp_dir must be used to store the extracted files.
        Optional: Return a dict with meta information
        '''
        INSERT YOUR UNPACKING CODE HERE
    		# file_path 是需要解包的文件
    		# tmp_dir 是解包后的文件夹
    		# 解包过程自行实现
    
        return META_DICT
    
    
    # ----> Do not edit below this line <----    def setup(unpack_tool):
        for item in MIME_PATTERNS:
            unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
    

当然修改文以上文件还未结束， **plugin **需要通过** custommime.mgc**注册进平台系统，先来看
**custommime.mgc** 解析命令：

    
    
    # 通过custommime生成custommime.mgc:
    file -C -m custommime
    
    # 反向解析：
    file -m custommime.mgc --mime-type FILE_PATH
    

**custommime** 文件格式如下，目的是通过文件头字节识别固件：

    
    
    # Some comment describing your definition
    0    string   \\x00\\x01\\x02\\x03   some text chown when file is used without --mime-type
    !:mime MIME/TYPE
    

安装好fact_helper_file后，custommime.mgc安装位置在 **/usr/local/lib/python3.8/dist-packages/fact_helper_file/bin** 下， **custommime.mgc** 通过安装
**https://github.com/fkie-cad/fact_helper_file.git** 获取，在
**/usr/local/lib/python3.8/dist-packages/fact_helper_file/bin** 文件夹下，通过
**get_file_type_from_path** 和 **get_file_type_from_binary** 函数判断固件类型。  
修改插件后，可一次更新所有 **custommime.mgc** ：

    
    
    # 将自己的custommime拷贝至fact_hleper_file/mime文件夹下
    
    cat fact_helper_file/mime/custom_* > custommime
    file -C -m custommime
    mv -f custommime.mgc /usr/local/lib/python3.8/dist-packages/fact_helper_file/bin/
    rm custommime
    

解包涉及固件具体结构分析，很多固件还需解密，涉及厂商关键技术，这里就省略demo。

### 分析 ( analysis )

接下来的插件目录结构类似，开发方法也基本相同，笔者主要给出自己的开发实栗，也可以参考官方[栗子](https://github.com/fkie-cad/FACT_analysis_plugin_template)。其目录结构如下：

    
    
    .
    ├── __init__.py
    ├── install.sh [OPTIONAL]
    ├── code
    │   ├── __init__.py
    │   └── PLUGIN_NAME.py
    ├── internal [OPTIONAL]
    │   └── ADDITIONAL_SOURCES_OR_CODE
    ├── signatures [OPTIONAL: JUST FOR YARA PLUGINS]
    ├── test [OPTIONAL]
    │   ├── __init__.py
    │   ├── test_PLUGIN_NAME.py
    │   └── data
    │       └── SOME DATA FILES TO TEST
    └── view 
        └── PLUGIN_NAME.html [OPTIONAL]
    

值得注意的是，与解包插件一样，官方将 **cwe_checker** 插件打包成Docker，可单独使用，用于危险函数检测，

![](https://image.3001.net/images/20220301/1646134221_621e03cd21057afe5ceb0.png!small)

使用方法如下：

    
    
    # use docker 
    docker run --rm -v /PATH/TO/BINARY:/input fkiecad/cwe_checker /input
    
    # use locally
    cwe_checker BINARY
    

以下是笔者写的demo，  
描述： 统计非文本文件的01比特数，比率通过饼状图展示：

![](https://image.3001.net/images/20220301/1646134257_621e03f148bf53d9aab95.png!small)

首先新建 **src/plugin/analysis/bits_count** 文件夹，其结构如下：

    
    
    .
    ├── __init__.py
    ├── code
    │   ├── __init__.py
    │   └── bits_count.py
    |
    ├── test [OPTIONAL]
    │   ├── __init__.py
    │   ├── bits_count.py
    │   └── data
    │
    └── view
        └── bits_count.html
    

修改 **src/config/main.cfg**

    
    
    # add
    [bits_count]
    threads = 2
    

**bits_count.py** 代码如下:

    
    
    from fact_helper_file import get_file_type_from_path
    
    from analysis.PluginBase import AnalysisBasePlugin
    
    
    class AnalysisPlugin(AnalysisBasePlugin):
        '''
        This Plugin detects the mime type of the file
        '''
        NAME = "bits_count"
        DESCRIPTION = "count bits"
        VERSION = "0.1"
    
        def __init__(self, plugin_administrator, config=None, recursive=True):
            '''
            recursive flag: If True recursively analyze included files
            propagate flag: If True add analysis result of child to parent object
            default flags should be edited above. Otherwise the scheduler cannot overwrite them.
            '''
            self.config = config
    
            # additional init stuff can go here
    
            super().__init__(plugin_administrator, config=config, recursive=recursive, plugin_path=__file__)
    
        def process_object(self, file_object):
            '''
            This function must be implemented by the plugin.
            Analysis result must be a list stored in file_object.processed_analysis[self.NAME]
            '''
            file_object.processed_analysis[self.NAME] = get_file_type_from_path(file_object.file_path)
            if file_object.processed_analysis[self.NAME]['mime'] == 'text/plain':
                file_object.processed_analysis[self.NAME]['NA'] = ['It is a text file !!!']
                return file_object
            file_object.processed_analysis[self.NAME]['summary'] = self._get_bits_count(file_object.file_path)
            return file_object
    
        @staticmethod
        def _get_bits_count(results):
            with open(results, 'rb') as fpr:
                content = fpr.read()
            total_bits = len(content) * 8
            one_bits = 0
            for byte in content:
                one_bits = one_bits + bin(int(byte)).count('1')
    
            zero_bits = total_bits - one_bits
            zero_rate = round((zero_bits/total_bits)*100, 2)
            one_rate = round((one_bits/total_bits)*100, 2)
            summary = ['{}% {} ({} / {})'.format(zero_rate, ' '*10, zero_bits, total_bits), \\
            '{}% {} ({} / {})'.format(one_rate, ' '*10, one_bits, total_bits), zero_rate, one_rate]
            return summary
    

**bits_count.html** 代码如下：

    
    
    {% extends "analysis_plugins/general_information.html" %}
    
    {% block head %}
        <script type="text/javascript" src="{{ url_for('static', filename='js/jquery.min.js') }}"></script>
        <script type="text/javascript" src="{{ url_for('static', filename='js/highcharts.js') }}"></script>
    {% endblock %}
    
    {% block analysis_result_details %}
    
        {% if 'NA' in firmware.processed_analysis[selected_analysis] %}
            <tr>
                <td>Warning</td>
                <td><pre>{{ firmware.processed_analysis[selected_analysis]['NA'][0] }}</pre></td>
            </tr>
        {% else %}
        <tr>
            <td>0 Bits</td>
            <td>{{ firmware.processed_analysis[selected_analysis]['summary'][0] }}</td>
        </tr>
        <tr>
            <td>1 Bits</td>
            <td>{{ firmware.processed_analysis[selected_analysis]['summary'][1] }}</td>
        </tr>
        <tr>
            <td>Chart</td>
            <td>
                <div id="container" style="width: 550px; height: 400px; margin: 0 auto"></div>
                <script language="JavaScript">
                $(document).ready(function() {
                    var chart = {
                        plotBackgroundColor: null,
                        plotBorderWidth: null,
                        plotShadow: false
                    };
                    var zero_rate = {{ firmware.processed_analysis[selected_analysis]['summary'][2] }};
                    var one_rate =  {{ firmware.processed_analysis[selected_analysis]['summary'][3] }};
                    var title = {
                        text: '0 1 比特饼状图'
                    };
                    var tooltip = {
                        pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
                    };
                    var plotOptions = {
                        pie: {
                            allowPointSelect: true,
                            cursor: 'pointer',
                            dataLabels: {
                            enabled: true,
                            format: '<b>{point.name}</b>: {point.percentage:.2f} %',
                            style: {
                                color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                            }
                            }
                        }
                    };
                    var series= [{
                        type: 'pie',
                        name: 'Browser share',
                        data: [
                            ['0 bits', zero_rate],
                            ['1 bits', one_rate]
                        ]
                    }];
    
                    var json = {};
                    json.chart = chart;
                    json.title = title;
                    json.tooltip = tooltip;
                    json.series = series;
                    json.plotOptions = plotOptions;
                    $('#container').highcharts(json);
                });
                </script>
            </td>
        </tr>
        {% endif %}
    
    {% endblock %}
    

### 比较 ( compare )

比较也是一样的，区别是涉及两个文件，也可参阅[官方实例](https://github.com/fkie-cad/FACT_core/wiki/compare-plugin-development)，其目录结构如下：

    
    
    .
    ├── __init__.py
    ├── install.sh [OPTIONAL]
    ├── code
    │   ├── __init__.py
    │   └── PLUGIN_NAME.py
    ├── internal [OPTIONAL]
    │   └── ADDITIONAL_SOURCES_OR_CODE
    ├── test
    │    ├── __init__.py
    │    ├── test_PLUGIN_NAME.py
    │    └── data [OPTIONAL]
    │        └── SOME DATA FILES TO TEST
    └── view [OPTIONAL]
        └── PLUGIN_NAME.html
    

直接给出demo，  
描述：对比两个ELF文件的依赖库

![](https://image.3001.net/images/20220301/1646134315_621e042ba40a82fb86de0.png!small)

插件文件夹结构如下：

    
    
    .
    ├── __init__.py
    ├── code
    │   ├── __init__.py
    │   └── lib_dependence.py
    |
    ├── test [OPTIONAL]
    │   ├── __init__.py
    │   ├── lib_dependence.py
    │   └── data
    │
    └── view 
        └── lib_dependence.html
    

**lib_dependence.py** 代码如下：

    
    
    from itertools import combinations
    from typing import Dict, List, Set, Tuple
    import os
    
    import networkx
    import ssdeep
    
    from compare.PluginBase import CompareBasePlugin
    from helperFunctions.compare_sets import iter_element_and_rest, remove_duplicates_from_list
    from helperFunctions.data_conversion import convert_uid_list_to_compare_id
    from objects.file import FileObject
    
    from tempfile import NamedTemporaryFile
    
    from flask import Markup
    
    
    class ComparePlugin(CompareBasePlugin):
        '''
        Compares ELF lib dependence
        '''
    
        NAME = 'lib_dependence'
        DEPENDENCIES = []
        VERSION = '0.1'
    
        def __init__(self, plugin_administrator, config=None, db_interface=None, plugin_path=__file__):
            super().__init__(plugin_administrator, config=config, db_interface=db_interface, plugin_path=plugin_path)
            self.ssdeep_ignore_threshold = self.config.getint('ExpertSettings', 'ssdeep_ignore')
    
        def compare_function(self, fo_list):
            filename = [name.file_name for name in fo_list]
            binary_list = [name.binary for name in fo_list]
    
            binary_lib_list = _get_lib_from_binary(binary_list)
    
            compare_result = dict()
            compare_result['file_name'] = {'file_name' : filename}
            compare_result['file_ulib'] = {'independce_lib' : binary_lib_list}
    
            return compare_result
    
    
    def _get_lib_from_binary(binary_list):
        result_list = []
        for binary in binary_list:
            tmp_file = NamedTemporaryFile(prefix='faf_compare_')
            tmp_file.write(binary)
    
            result = os.popen('readelf -d {} |grep "Shared library"'.format(tmp_file.name))
            result_list.append(result.read().split('\\n'))
            tmp_file.close()
    
        return result_list
    

**lib_dependence.html** 代码如下：

    
    
    {% for feature in result['plugins'][plugin] | sort %}
        {% for features in result['plugins'][plugin][feature] | sort %}
        <tr>
            <td>{{ features | replace_underscore }}</td>
            {% for item in result['plugins'][plugin][feature][features] %}
                {% if features == 'independce_lib' %}
                <td>{% for libs in item %}
                        {{ libs }} <br />
                    {% endfor %}</td>
                {% else %}
                <td>{{ item }}</td>
                 {% endif %}
            {% endfor %}
        </tr>
        {% endfor %}
    {% endfor %}
    

## 0x3 界面开发

有些童鞋可能有汉化和美化需求，当然对于功能使用来说不是必须的，作为Flask开发的web应该是比较好修改的，最暴力的方法可以用grep
-r在FACT_core文件夹里搜索需要修改的关键字，实际都在web_interface文件夹中，这里直接给出一些基本目录信息：

  *  **FACT_core/src/web_interface/templates** 中的html是框架模版，如果要汉化可以修改这里，比如修改base.html改导航栏

  *  **FACT_core/src/web_interface/static** 中存放静态文件，如修改图片可以在这里替换

笔者修改的最后效果如下：

![](https://image.3001.net/images/20220301/1646134332_621e043cd5e31703ec8f3.png!small)

## 0x4 总结

随着固件安全堡垒越筑越高，很多厂商都选择加密、加扰等诸多防护措施，大大提升了分析和漏洞挖掘门槛。很多童靴可能费劲装上FACT后发现其效果平平，甚至可能毫无建树，但笔者认为该开源项目在于构建框架，而具体功能以插件的形式由个人自由填充，是内部自建固件分析平台的很好选择。

参考链接：

[FACT官方指南](https://fkie-cad.github.io/FACT_core/)

[FACT Github](https://github.com/fkie-cad/FACT_core)

