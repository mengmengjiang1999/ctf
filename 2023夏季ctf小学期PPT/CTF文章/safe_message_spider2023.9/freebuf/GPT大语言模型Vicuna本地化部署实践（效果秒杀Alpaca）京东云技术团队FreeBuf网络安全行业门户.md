## 背景

上一篇文章《[GPT 大语言模型 Alpaca-lora 本地化部署实践](articles/database/366733.html)》介绍了斯坦福大学的
Alpaca-lora 模型的本地化部署，并验证了实际的推理效果。

总体感觉其实并不是特别理想，原始 Alpaca-lora 模型对中文支持并不好，用 52k 的中文指令集对模型进行 fine-tuning
之后，效果依然达不到网上说的媲美 GPT-3.5 的推理效果，验证了那句话：“事不目见耳闻，而臆断其有无，可乎？”

在具有 3 块 Tesla P40 显卡的服务器上，利用 3 块 GPU 显卡加载模型参数和计算，进行一次简单的推理（非数学运算和逻辑运算）也需要大概
30s-1min 的时间，效率简直慢的惊人。在京东云 GPU 云主机部署上，虽然推理效率提高了很多，用中文数据集对模型进行了 fine-tuning，然而对中文的支持也并不是很好，经常会出现乱码、重复问题、词不达意等情况。

最近大模型也同雨后春笋般的层出不穷，各个大厂和科研机构都推出了自己的大模型，其中基于
LLaMA（开源且好用）的最多，所以决定再看看其他模型，有没有推理效果好，中文支持好，同时推理效率高的模型。

经过筛选， **Vicuna-13B 的推理效果据说达到了 ChatGPT 的 90% 以上的能力，优于 LLaMA-13B 和 Alpaca-13B
的效果（具体如下图所示）** 。评估方法是对各个模型 Alpaca、LLaMA、ChatGPT 和 Bard 输入同样的问题，然后通过 GPT-4
当裁判对推理结果进行打分，以 ChatGPT 的回答作为 100
分，回答越接近得分越高（虽然评估方法并不科学，但是目前看也没有更好的办法对模型推理结果进行更科学的评估）。

同时 Vicuna 的训练成本也很低，据说只需要 $300 左右，所以尝试本地化部署一下 Vicuna-7B，看看效果如何，说干就干。

![1684382038_6465a15614a07e2400385.png!small?1684382038534](https://image.3001.net/images/20230518/1684382038_6465a15614a07e2400385.png!small?1684382038534)

## 环境准备

由于之前本地化部署过 Alpaca-lora 模型了，本以为可以直接下载开源包，简单部署一下就可以看到效果了，结果发现我还是 “too young，too
simple” 了，环境部署和解决包冲突的过程竟然比第一次部署 Alpaca-lora 模型还要费劲。

简单的复述一下部署流程，详细的可以参考上一篇内容《[GPT 大语言模型 Alpaca-lora
本地化部署实践](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fwww.toutiao.com%2Farticle%2F7233963907356967483%2F)》。

  1. 本地化部署或 GPU 云主机部署：GPU 服务器具有 4 块独立的 GPU，型号是 P40，单个 P40 算力相当于 60 个同等主频 CPU 的算力；GPU 云主机要选购 P40https://www.jdcloud.com/cn/calculator/calHost
  2. 安装显卡驱动和 CUDA 驱动

### 模型准备

由于 Vicuna 是基于 LLaMA 模型的，为了符合 LLaMA 模型 license 授权，仅发布了 delta 权重，所以我们需要将原始
llama-7b 模型与 delta 模型权重合并之后，才能得到 vicuna 权重。

首先是下载 llama-7b 模型，由于文件比较大，所以用 lfs 直接从文件服务器上下载，大小有 26G，执行：

git lfsclonehttps://huggingface.co/decapoda-research/llama-7b-hf

然后是下载 delta 模型，执行：

git lfsclonehttps://huggingface.co/lmsys/vicuna-7b-delta-v1.1

下载完成后进行权重合并，执行：

python -m fastchat.model.apply_delta \ --base ./model/llama-7b-hf \ --delta
./model/vicuna-7b-delta-v1.1 \ --target ./model/vicuna-7b-all-v1.1

这个合并过程会很快，最终结果如下，合并之后参数大小变成了 13G。

![1684382051_6465a16389c785ecac57a.png!small?1684382052188](https://image.3001.net/images/20230518/1684382051_6465a16389c785ecac57a.png!small?1684382052188)

合并之后的目录下会有配置文件和数据文件。

![1684382061_6465a16d1a303a654217e.png!small?1684382062229](https://image.3001.net/images/20230518/1684382061_6465a16d1a303a654217e.png!small?1684382062229)

### 安装依赖包

Vicuna 主要用到 3 个依赖包，fschat、tensorboardX 和 flash-attn，前 2 个安装比较顺利，直接 pip install
fschat、tensorboardX 即可安装完成。flash-attn 安装遇到了问题，一直报以下错误：

![1684382071_6465a17760be79b9f1513.png!small?1684382071885](https://image.3001.net/images/20230518/1684382071_6465a17760be79b9f1513.png!small?1684382071885)

经过一番检索，发现是 gcc 版本太低导致的，需要升级 gcc，首先查看了一下本地的 gcc 版本，gcc -v 和 g++ -v 发现是 4.8.5
的，确实是太低了，那么既然要升级，就升级到最新版，直接下载 13.1 版本，可以在  
[http://ftp.gnu.org/gnu/gcc/ 选择想要安装的版本，这里选择的是
gcc-13.1.0.tar.gz。](https://www.oschina.net/action/GoToLink?url=http%3A%2F%2Fftp.gnu.org%2Fgnu%2Fgcc%2F%25E9%2580%2589%25E6%258B%25A9%25E6%2583%25B3%25E8%25A6%2581%25E5%25AE%2589%25E8%25A3%2585%25E7%259A%2584%25E7%2589%2588%25E6%259C%25AC%25EF%25BC%258C%25E8%25BF%2599%25E9%2587%258C%25E9%2580%2589%25E6%258B%25A9%25E7%259A%2584%25E6%2598%25AFgcc-13.1.0.tar.gz%25E3%2580%2582)

执行：

tar -xzf gcc-13.1.0.tar.gz

cd gcc-13.1.0

./contrib/download_prerequisites

mkdir build

cd build/

../configure -enable-checking=release -enable-languages=c,c++ -disable-multilib

然后执行 make 编译，注意这里 make 时间会非常长，可能会持续几个小时，可以使用 make -j 8 让 make 最多运行 8
个编译命令同时运行，加快编译速度。

顺利完成后，我们再执行 make install 进行安装。

然后用 gcc -v 和 g++ -v 验证版本是否已经更新，如果提示如下，说明安装完成。

![1684382083_6465a18369fee309cbf4b.png!small?1684382084003](https://image.3001.net/images/20230518/1684382083_6465a18369fee309cbf4b.png!small?1684382084003)

然后我们需要卸载原有的 gcc 和 g++，切换到 root 权限，执行 yum -y remove gcc g++。

配置新版本全局可用，执行 ln -s /usr/local/bin/gcc/usr/bin/gcc。

更新链接库，执行：

查看原链接库：strings /usr/lib64/libstdc++.so.6 | grep CXXABI

删除原链接库：rm -f /usr/lib64/libstdc++.so.6

建立软连接：ln -s /usr/local/lib64/libstdc++.so.6.0.29 /usr/lib64/libstdc++.so.6

查看新链接库：strings /usr/lib64/libstdc++.so.6 | grep CXXABI

如果最新版本有变化，那么恭喜你，说明已经升级成功啦。

![1684382094_6465a18e347d4ef6b190a.png!small?1684382094753](https://image.3001.net/images/20230518/1684382094_6465a18e347d4ef6b190a.png!small?1684382094753)

### 安装 cuda

由于之前是用 rpm 包安装的 cuda，有些文件是缺失的，运行时会报各种奇奇怪怪的错误，这里就不赘述了（只有经历过才会懂），直接介绍用二进制文件安装
cuda 过程。

下载地址：  
[https://developer.nvidia.com/cuda-11-7-0-download-archive?target_os=Linux⌖_arch=x86_64&Distribution=CentOS⌖_version=7⌖_type=runfile_local](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fdeveloper.nvidia.com%2Fcuda-11-7-0-download-archive%3Ftarget_os%3DLinux%26target_arch%3Dx86_64%26Distribution%3DCentOS%26target_version%3D7%26target_type%3Drunfile_local)

注意这里要选择 runfile (local)。

![1684382105_6465a199323fcc9cf53bc.png!small?1684382105687](https://image.3001.net/images/20230518/1684382105_6465a199323fcc9cf53bc.png!small?1684382105687)

然后执行 sh  
cuda_11.7.0_515.43.04_linux.run。

安装完成后，需要配置环境变量，在本地.bash_profile 中配置如下两项：

![1684382116_6465a1a4000a63132f044.png!small?1684382117010](https://image.3001.net/images/20230518/1684382116_6465a1a4000a63132f044.png!small?1684382117010)

下面验证一下安装是否成功，执行 nvcc -V，如下图所示，那么恭喜你，安装成功啦。

![1684382125_6465a1adb78f936c0e01a.png!small?1684382126726](https://image.3001.net/images/20230518/1684382125_6465a1adb78f936c0e01a.png!small?1684382126726)

### 安装 cudnn 和 nccl

安装 cudnn 和 nccl 需要先在 nvidia 注册账号，注册之后可以在以下两个地址下载相应的 rpm 包，然后 rpm -ivh
XXXXX.rpm 包即可。

cudnn 下载地址：
[https://developer.nvidia.com/cudnn](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fdeveloper.nvidia.com%2Fcudnn)

nccl 下载地址： [https://developer.nvidia.com/nccl/nccl-legacy-downloads](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fdeveloper.nvidia.com%2Fnccl%2Fnccl-legacy-downloads)

安装完成后，如下图所示说明已经安装成功 rpm 包。

![1684382135_6465a1b74dfa19d312ff9.png!small?1684382136083](https://image.3001.net/images/20230518/1684382135_6465a1b74dfa19d312ff9.png!small?1684382136083)

## 模型推理

又到激动人心的时刻啦，让我们来测试一下看看模型的推理效果如何？首先我们先擦拭一下还没有干透辛勤的汗水，一切努力，都是为了最终能跟机器人程序对上话，理想情况是让我们感觉它并不是一个机器人。

在终端执行如下命令，然后输入问题即可。

python -m fastchat.serve.cli --model-path ./model/vicuna-7b-all-v1.1 --style
rich

当然，还可以根据不同的需求场景，设置不用的运行参数，如下：

#压缩模型 预测效果会稍差一点，适合 GPU 显存不够的场景

python -m fastchat.serve.cli --model-path ./model/vicuna-7b-all-v1.1
--load-8bit --style rich

#使用 cpu 进行推理，速度会很慢，慎用

python -m fastchat.serve.cli --model-path ./model/vicuna-7b-all-v1.1 --device
cpu --style rich

#使用多个 GPU 进行预测

python -m fastchat.serve.cli --model-path ./model/vicuna-7b-all-v1.1 --num-gpus 3 --style rich

1）推荐菜谱测试：

![1684382147_6465a1c3644c466667bb9.png!small?1684382148076](https://image.3001.net/images/20230518/1684382147_6465a1c3644c466667bb9.png!small?1684382148076)

2）多语言测试：

![1684382157_6465a1cdd11822c1f1611.png!small?1684382158500](https://image.3001.net/images/20230518/1684382157_6465a1cdd11822c1f1611.png!small?1684382158500)

3）代码能力测试：

![1684382173_6465a1ddc6e16b2b7089c.png!small?1684382174311](https://image.3001.net/images/20230518/1684382173_6465a1ddc6e16b2b7089c.png!small?1684382174311)

![1684382186_6465a1eab5364a81c9ace.png!small?1684382187483](https://image.3001.net/images/20230518/1684382186_6465a1eab5364a81c9ace.png!small?1684382187483)

![1684382194_6465a1f2e87bd93fd177b.png!small?1684382195388](https://image.3001.net/images/20230518/1684382194_6465a1f2e87bd93fd177b.png!small?1684382195388)

4）数学计算测试

![1684382205_6465a1fdb6d47b0dbb984.png!small?1684382206468](https://image.3001.net/images/20230518/1684382205_6465a1fdb6d47b0dbb984.png!small?1684382206468)

5）普通对话推荐

![1684382215_6465a207b08f42f606525.png!small?1684382216766](https://image.3001.net/images/20230518/1684382215_6465a207b08f42f606525.png!small?1684382216766)

推理过程中 GPU 服务器资源使用情况，目前使用单 GPU 进行推理，都可以做到秒级响应，GPU 内存空加载 13G，推理时不到 15G，推理时单 GPU
算力基本可以达到 90% 以上，甚至 100%，如下图所示。

![1684382226_6465a2124d01984524941.png!small?1684382227064](https://image.3001.net/images/20230518/1684382226_6465a2124d01984524941.png!small?1684382227064)

总结一下：

1）对精确的推理效果并不是很理想，比如推荐菜谱，感觉是在一本正经的胡说八道，按照推理的结果很难做出可口的饭菜️；

2）对多种自然语言的支持，这个真的是出乎预料，竟然日语和西班牙语完全都能够自如应对，可以说是相当的惊艳了；

3）编码能力还是可以的，能够大概给出基本需求，当然如果想直接编译执行可能还需要人工微调，但是作为辅助工具应该是没问题的；

4）数据计算能力目前看还是比较弱的，简单的乘法目前还不能够给出正确的答案；

5）普通的对话是完全没有问题的，对中文的理解也完全能否符合预期，解解闷排解一下孤独是能够 cover 住的。

由于模型目前还没有做 fine-tuning，从目前的推理效果来看，已经是非常不错了，而且推理的效率也是非常不错的，即使使用单 GPU
进行推理也可以做到秒级响应，而且推理过程中显存占用也才只有 60% 多，跟空载时候的 50% 多没差多少，总之在没有经过 fine-tuning
的情况下，模型的推理表现和推理效率还是可以打 7-8 分（满分 10 分）的，如果假以时日，有足够的语料库和进行 fine-tuning
的话，效果还是可期的。

## 模型 fine-tuning

要想使模型适合某一特定领域内的场景，获取特定领域的知识是必不可少的，基于原始模型就要做 fine-tuning 操作，那么我们尝试做一下 fine-tuning，看看效果如何吧。

fine-tuning 需要在终端执行一下命令：

    
    
    torchrun --nproc_per_node=3 --master_port=40001 ./FastChat/fastchat/train/train_mem.py \
        --model_name_or_path ./model/llama-7b-hf  \
        --data_path dummy.json \
        --bf16 False \
        --output_dir ./model/vicuna-dummy \
        --num_train_epochs 2 \
        --per_device_train_batch_size 1 \
        --per_device_eval_batch_size 1 \
        --gradient_accumulation_steps 8 \
        --evaluation_strategy "no" \
        --save_strategy "steps" \
        --save_steps 300 \
        --save_total_limit 10 \
        --learning_rate 2e-5 \
        --weight_decay 0. \
        --warmup_ratio 0.03 \
        --lr_scheduler_type "cosine" \
        --logging_steps 1 \
        --report_to "tensorboard" \
        --fsdp "full_shard auto_wrap" \
        --fsdp_transformer_layer_cls_to_wrap 'LlamaDecoderLayer' \
        --tf32 False \
        --model_max_length 2048 \
        --gradient_checkpointing True \
        --lazy_preprocess True
    

最终./model/vicuna-dummy 目录输出就是我们 fine-tuning 之后的模型权重文件目录。

很遗憾，本文 fine-tuning 没有成功，报错如下：

![1684382242_6465a22258518e80dd42e.png!small?1684382243020](https://image.3001.net/images/20230518/1684382242_6465a22258518e80dd42e.png!small?1684382243020)

原因也很简单，由于我们使用的 GPU 型号是 Tesla P40，此款显卡使用的 SM_62 架构，目前模型 fine-tuning 至少需要 SM_75
及以上架构，看社区有在 4090、A100 或者 A80 显卡上 fine-tuning 成功的，所以 fine-tuning
只能后续再更高架构的显卡上进行了。

![1684382253_6465a22d6612c7e8e931c.png!small?1684382254378](https://image.3001.net/images/20230518/1684382253_6465a22d6612c7e8e931c.png!small?1684382254378)

## 后续工作

终上，Vicuna 模型在整体表现和推理效率上可以说是秒杀 Alpaca 模型的，我们本文测试用的是 Vicuna-7b，如果是 Vicuna-13b
效果会更好，而且对多种自然语言（包含中文）的支持也要远远好于 Alpaca 模型，确实像社区所说的，目前 Vicuna
模型可以说是开源大模型的天花板了，如果想基于开源大模型进行二次开发，是个不二的选择。

基于大模型的本地化部署工作目前就告一段落了，后续做的工作可能有以下几点：

1）如果有更好的显卡，可以对 vicuna 进行 fine-tuinig，验证一下 fine-tuning
之后模型能不能学到特定领域的知识；后续准备使用公司内部提供的试用资源【京东云 GPU 云主机 **p.n3a100 系列** 】，这个产品提供
Nvidia® A100 GPU（80G 显存），搭配使用 Intel® Xeon® Platinum 8338C 处理器及 DDR4 内存，支持
NVLink，单精度浮点运算峰值能达到 156TFlops，可以说是最强算力了。

![1684382263_6465a2378a8f0008ecd51.png!small?1684382264174](https://image.3001.net/images/20230518/1684382263_6465a2378a8f0008ecd51.png!small?1684382264174)

2）找到合适的与目前应用结合的场景，将大语言模型应用落地；

3）基于 vicuna 开源项目进行二次开发，封装成可用的服务；

4）基于大语言模型进行更多的探索和学习。

> 来源：京东云开发者社区
>
> 作者：Beyond_luo（未经授权请勿转载）

