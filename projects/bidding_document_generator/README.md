# bidding_document_generator
### 项目结构
```
bidding_document_generator/
│
├── data/
│   ├── laws.csv
│   ├── standards.csv
│   ├── project_cases.csv
│   ├── suppliers.csv
│   ├── experts.csv
│   └── bidding_data.csv
│
├── templates/
│   ├── bidding_template.json
│   ├── evaluation_report_template.json
│   ├── answer_letter_template.json
│   ├── winning_notice_template.json
│   └──...
│
├── src/
│   ├── __init__.py
│   ├── nlp_model_integration.py
│   ├── knowledge_graph_construction.py
│   ├── template_management.py
│   └── main.py
│
├── requirements.txt
└── README.md
```

### 说明
- **data 目录**：
    - 存储所有与招投标相关的数据文件，包括但不限于法律法规、行业标准、项目案例、供应商信息、专家库以及用于微调的数据文件。

- **templates 目录**：
    - 包含各种招投标文件的模板，如招标文件、评标报告、答疑函件、中标通知书等的模板文件。模板使用JSON格式存储，其中包含占位符，方便后续填充。

- **src 目录**：
    - `__init__.py`：使 `src` 目录成为一个 Python 包。
    - `multi_threaded_file_preprocessor.py`：负责实现多线程处理大批量文件，包括格式识别、解析以及预处理。
    - `nlp_model_integration.py`：负责自然语言处理模型的集成、微调及多模型融合。
    - `knowledge_graph_construction.py`：实现知识图谱的构建和查询。
    - `template_management.py`：处理模板的管理和自动化填充。
    - `main.py`：作为项目的主入口，协调不同模块的调用，完成最终文件的生成。

- **requirements.txt**：
    - 列出项目所需的所有 Python 依赖。

- **README.md**：
    - 提供项目的说明，包括如何安装、运行项目，以及每个模块的功能概述。

### 运行项目
1. 确保 `neo4j` 数据库已启动并配置好用户名和密码。
2. 安装所需的依赖：
    ```bash
    pip install -r requirements.txt
    ```
3. 运行项目：
    ```bash
    python src/main.py
    ```