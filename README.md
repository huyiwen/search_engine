# $TF-IDF^2$: An Effective Search Engine

## 整体介绍

$TF-IDF^2$ 是一个基于两次 TF-IDF 查询的本地高效搜索引擎，包含从网页爬取、索引建立、自动评测到网页界面一系列功能。第一次 TF-IDF 查询采用细粒度、低精度索引，进行初步筛选；第二次 TF-IDF 查询在结果的基础上采用粗粒度、高精度查询，重新进行排序。为了实现 `Vue.js` 网页界面的实时查询，在实现上，本项目利用`pipe`、`pandas`、`numpy`等库的管道、半精度计算等功能，达到高效处理。同时单元测试与日志、`Flark` 等保证项目稳定运行。



![](assets/framework.jpg)

### 安装与初始化

```bash
git clone https://github.com/huyiwen/search_engine.git && cd search_engine
pip install -r requirements.txt
cd search_engine
python spider.py
python save_pure.py  # choose tokenize
python build_index.py
python save_pure.py  # choose pure
```

### 快速上手

```bash
# command line evaluation
python query.py

# Web UI
cd ../server
flask run > ../log/flask.out 2>&1 &  # to terminate the server process, just close the terminal
cd ../webui
npm run dev
```

### 公式



## 实现流程与代码细节

本项目利用 `pipe` ，将 `R` 和 `bash` 引以为傲的管道符融合在了项目中，兼顾代码简洁与效率。构建索引速度高达 $1000it/s$ 。

![](assets/index.png)

同时利用 `pandas` 及其半精度计算加速分数计算速率及内存占用。

![](assets/pandas.png)



## 界面展示

## 实验感想

## Reference

- https://github.com/xitu/gold-miner/blob/master/TODO1/developing-a-single-page-app-with-flask-and-vuejs.md
