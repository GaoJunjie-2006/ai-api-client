# 快速上手指南

一分钟速成指南，学不会我吃

## 第一步：配置 API

在程序开头填入你的 API 配置，不管是买的还是白嫖的都行：

```python
# 配置 API
api_key = "在这里填入你的api"
client = OpenAI(
    base_url="在这里填入你的url",
    api_key=api_key,
)
```

## 第二步：安装依赖

用 conda 安装 `openai.yaml` 里的包就完事了：

```bash
conda env create -f openai.yaml
conda activate <环境名>
```

## 第三步：启动服务

运行程序，然后浏览器访问：

```
http://localhost:7860
```

没了
