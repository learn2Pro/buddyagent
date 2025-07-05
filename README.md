## multi-agent for deep search


## code structure

## architecture

## descriptions

- langgraph visualize

```
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . langgraph dev --allow-blocking
```

## run fast api
```
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## run web server
```
uv run python -m http.server -d fe/ 8001
```

## docker 
```
sudo docker network inspect mjapi >/dev/null 2>&1 || sudo docker network create mjapi

sudo docker build -t buddyagent:0.0.1 -f Dockerfile .
sudo docker run -d --net mjapi -p  8000:8000 buddyagent:0.0.1

sudo docker build -t buddyweb:0.0.1 -f Dockerfile_fe .
sudo docker run -d --net mjapi -p  8001:8001 buddyweb:0.0.1
```

## test

| 功能          | usage                             |
| ----------- | ------------------------------ |
| 跑某个测试函数     | `pytest test/test_example.py::test_add` |
| 显示 print 输出 | `pytest -s`                    |
| 自动重跑失败      | `pytest --reruns 3`（需插件）       |
| 生成 HTML 报告  | 使用 `pytest-html` 插件            |
