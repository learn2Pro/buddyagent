## multi-agent for deep search


## code structure

## architecture

## descriptions

- langgraph visualize

```
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . langgraph dev --allow-blocking
```

## test

| 功能          | usage                             |
| ----------- | ------------------------------ |
| 跑某个测试函数     | `pytest test/test_example.py::test_add` |
| 显示 print 输出 | `pytest -s`                    |
| 自动重跑失败      | `pytest --reruns 3`（需插件）       |
| 生成 HTML 报告  | 使用 `pytest-html` 插件            |
