{
  "code": 0,
  "message": "ok",
  "data": {
    "openapi": "3.0.0",
    "info": {
      "title": "QuantBull Unified API",
      "version": "1.0.0",
      "description": "Unified API documentation for all QuantBull microservices"
    },
    "paths": {
      "/api/quant/api/backtest/run": {
        "post": {
          "tags": [
            "quant-engine",
            "回测"
          ],
          "summary": "提交回测任务（异步，返回 task_id）",
          "description": "将回测任务提交到平台级 `task-service`，立即返回 `task_id` 给前端。\n\n注意：此接口不在请求中执行回测计算，回测由 task-service 后台异步执行。",
          "operationId": "run_backtest_api_backtest_run_post",
          "requestBody": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/quant-engine_BacktestRequest"
                }
              }
            },
            "required": true
          },
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {

                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_HTTPValidationError"
                  }
                }
              }
            }
          }
        }
      },
      "/api/quant/api/backtest/{backtest_id}": {
        "get": {
          "tags": [
            "quant-engine",
            "回测"
          ],
          "summary": "获取回测结果",
          "description": "获取指定回测的详细结果",
          "operationId": "get_backtest_api_backtest__backtest_id__get",
          "parameters": [
            {
              "name": "backtest_id",
              "in": "path",
              "required": true,
              "schema": {
                "type": "string",
                "title": "Backtest Id"
              }
            }
          ],
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_BaseResponse_BacktestResponse_"
                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_HTTPValidationError"
                  }
                }
              }
            }
          }
        }
      },
      "/api/quant/api/backtest": {
        "get": {
          "tags": [
            "quant-engine",
            "回测"
          ],
          "summary": "列出回测记录",
          "description": "列出所有回测记录",
          "operationId": "list_backtests_api_backtest_get",
          "parameters": [
            {
              "name": "limit",
              "in": "query",
              "required": false,
              "schema": {
                "type": "integer",
                "default": 10,
                "title": "Limit"
              }
            },
            {
              "name": "offset",
              "in": "query",
              "required": false,
              "schema": {
                "type": "integer",
                "default": 0,
                "title": "Offset"
              }
            }
          ],
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_PaginatedResponse_BacktestResponse_"
                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_HTTPValidationError"
                  }
                }
              }
            }
          }
        }
      },
      "/api/quant/api/backtest/run_async": {
        "post": {
          "tags": [
            "quant-engine",
            "回测"
          ],
          "summary": "异步提交回测任务（示例：调用 task-service）",
          "description": "示例业务：将回测任务提交到平台级 task-service，立即返回 task_id 给前端。",
          "operationId": "run_backtest_async_api_backtest_run_async_post",
          "requestBody": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/quant-engine_BacktestRequest"
                }
              }
            },
            "required": true
          },
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {

                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_HTTPValidationError"
                  }
                }
              }
            }
          }
        }
      },
      "/api/quant/api/strategy": {
        "post": {
          "tags": [
            "quant-engine",
            "策略"
          ],
          "summary": "创建策略",
          "description": "创建新的量化策略\n\n策略代码应为 Python 代码，通常继承 backtrader.Strategy",
          "operationId": "create_strategy_api_strategy_post",
          "requestBody": {
            "required": true,
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/quant-engine_StrategyCreateRequest"
                }
              }
            }
          },
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_StrategyResponse"
                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_HTTPValidationError"
                  }
                }
              }
            }
          }
        },
        "get": {
          "tags": [
            "quant-engine",
            "策略"
          ],
          "summary": "列出策略",
          "description": "列出所有策略\n\n支持按状态过滤和分页",
          "operationId": "list_strategies_api_strategy_get",
          "parameters": [
            {
              "name": "status",
              "in": "query",
              "required": false,
              "schema": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "null"
                  }
                ],
                "title": "Status"
              }
            },
            {
              "name": "limit",
              "in": "query",
              "required": false,
              "schema": {
                "type": "integer",
                "default": 20,
                "title": "Limit"
              }
            },
            {
              "name": "offset",
              "in": "query",
              "required": false,
              "schema": {
                "type": "integer",
                "default": 0,
                "title": "Offset"
              }
            }
          ],
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_StrategyListResponse"
                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_HTTPValidationError"
                  }
                }
              }
            }
          }
        }
      },
      "/api/quant/api/strategy/{strategy_id}": {
        "get": {
          "tags": [
            "quant-engine",
            "策略"
          ],
          "summary": "获取策略",
          "description": "获取指定策略的详细信息",
          "operationId": "get_strategy_api_strategy__strategy_id__get",
          "parameters": [
            {
              "name": "strategy_id",
              "in": "path",
              "required": true,
              "schema": {
                "type": "string",
                "title": "Strategy Id"
              }
            }
          ],
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_StrategyResponse"
                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_HTTPValidationError"
                  }
                }
              }
            }
          }
        },
        "put": {
          "tags": [
            "quant-engine",
            "策略"
          ],
          "summary": "更新策略",
          "description": "更新策略信息",
          "operationId": "update_strategy_api_strategy__strategy_id__put",
          "parameters": [
            {
              "name": "strategy_id",
              "in": "path",
              "required": true,
              "schema": {
                "type": "string",
                "title": "Strategy Id"
              }
            }
          ],
          "requestBody": {
            "required": true,
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/quant-engine_StrategyUpdateRequest"
                }
              }
            }
          },
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_StrategyResponse"
                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_HTTPValidationError"
                  }
                }
              }
            }
          }
        },
        "delete": {
          "tags": [
            "quant-engine",
            "策略"
          ],
          "summary": "删除策略",
          "description": "删除策略",
          "operationId": "delete_strategy_api_strategy__strategy_id__delete",
          "parameters": [
            {
              "name": "strategy_id",
              "in": "path",
              "required": true,
              "schema": {
                "type": "string",
                "title": "Strategy Id"
              }
            }
          ],
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "type": "object",
                    "additionalProperties": true,
                    "title": "Response Delete Strategy Api Strategy  Strategy Id  Delete"
                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_HTTPValidationError"
                  }
                }
              }
            }
          }
        }
      },
      "/api/quant/api/strategy/validate": {
        "post": {
          "tags": [
            "quant-engine",
            "策略"
          ],
          "summary": "验证策略代码",
          "description": "验证策略代码\n\n检查：\n- Python 语法\n- 必要的类和方法\n- 潜在的安全问题",
          "operationId": "validate_strategy_api_strategy_validate_post",
          "requestBody": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/quant-engine_StrategyValidateRequest"
                }
              }
            },
            "required": true
          },
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_StrategyValidateResponse"
                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_HTTPValidationError"
                  }
                }
              }
            }
          }
        }
      },
      "/api/quant/api/factor": {
        "post": {
          "tags": [
            "quant-engine",
            "因子"
          ],
          "summary": "创建因子",
          "description": "创建新的量化因子\n\n因子类别：\n- technical: 技术指标\n- fundamental: 基本面因子\n- macro: 宏观因子",
          "operationId": "create_factor_api_factor_post",
          "requestBody": {
            "required": true,
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/quant-engine_FactorCreateRequest"
                }
              }
            }
          },
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_FactorResponse"
                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_HTTPValidationError"
                  }
                }
              }
            }
          }
        },
        "get": {
          "tags": [
            "quant-engine",
            "因子"
          ],
          "summary": "列出因子",
          "description": "列出所有因子\n\n支持按类别过滤和分页",
          "operationId": "list_factors_api_factor_get",
          "parameters": [
            {
              "name": "category",
              "in": "query",
              "required": false,
              "schema": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "null"
                  }
                ],
                "title": "Category"
              }
            },
            {
              "name": "limit",
              "in": "query",
              "required": false,
              "schema": {
                "type": "integer",
                "default": 20,
                "title": "Limit"
              }
            },
            {
              "name": "offset",
              "in": "query",
              "required": false,
              "schema": {
                "type": "integer",
                "default": 0,
                "title": "Offset"
              }
            }
          ],
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_FactorListResponse"
                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_HTTPValidationError"
                  }
                }
              }
            }
          }
        }
      },
      "/api/quant/api/factor/{factor_id}": {
        "get": {
          "tags": [
            "quant-engine",
            "因子"
          ],
          "summary": "获取因子",
          "description": "获取指定因子的详细信息",
          "operationId": "get_factor_api_factor__factor_id__get",
          "parameters": [
            {
              "name": "factor_id",
              "in": "path",
              "required": true,
              "schema": {
                "type": "string",
                "title": "Factor Id"
              }
            }
          ],
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_FactorResponse"
                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_HTTPValidationError"
                  }
                }
              }
            }
          }
        },
        "put": {
          "tags": [
            "quant-engine",
            "因子"
          ],
          "summary": "更新因子",
          "description": "更新因子信息",
          "operationId": "update_factor_api_factor__factor_id__put",
          "parameters": [
            {
              "name": "factor_id",
              "in": "path",
              "required": true,
              "schema": {
                "type": "string",
                "title": "Factor Id"
              }
            }
          ],
          "requestBody": {
            "required": true,
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/quant-engine_FactorUpdateRequest"
                }
              }
            }
          },
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_FactorResponse"
                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_HTTPValidationError"
                  }
                }
              }
            }
          }
        },
        "delete": {
          "tags": [
            "quant-engine",
            "因子"
          ],
          "summary": "删除因子",
          "description": "删除因子",
          "operationId": "delete_factor_api_factor__factor_id__delete",
          "parameters": [
            {
              "name": "factor_id",
              "in": "path",
              "required": true,
              "schema": {
                "type": "string",
                "title": "Factor Id"
              }
            }
          ],
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "type": "object",
                    "additionalProperties": true,
                    "title": "Response Delete Factor Api Factor  Factor Id  Delete"
                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_HTTPValidationError"
                  }
                }
              }
            }
          }
        }
      },
      "/api/quant/api/factor/calculate": {
        "post": {
          "tags": [
            "quant-engine",
            "因子"
          ],
          "summary": "计算因子值",
          "description": "计算指定因子在给定时间范围内的值\n\n返回时间序列数据，可用于策略分析和可视化",
          "operationId": "calculate_factor_api_factor_calculate_post",
          "requestBody": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/quant-engine_FactorCalculateRequest"
                }
              }
            },
            "required": true
          },
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_FactorCalculateResponse"
                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/quant-engine_HTTPValidationError"
                  }
                }
              }
            }
          }
        }
      },
      "/api/quant/": {
        "get": {
          "summary": "Root",
          "description": "根路径",
          "operationId": "root__get",
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "additionalProperties": true,
                    "type": "object",
                    "title": "Response Root  Get"
                  }
                }
              }
            }
          },
          "tags": [
            "quant-engine"
          ]
        }
      },
      "/api/quant/health": {
        "get": {
          "summary": "Health Check",
          "description": "健康检查",
          "operationId": "health_check_health_get",
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "additionalProperties": true,
                    "type": "object",
                    "title": "Response Health Check Health Get"
                  }
                }
              }
            }
          },
          "tags": [
            "quant-engine"
          ]
        }
      },
      "/api/ai/api/ai/generate/news": {
        "post": {
          "tags": [
            "ai-hub",
            "AI"
          ],
          "summary": "生成新闻解读",
          "description": "根据财经快讯生成新闻解读\n\n- 默认模型：DeepSeek R1（文本生成、新闻能力强）\n- 支持显式指定模型\n- 基于 README.md 中的 Prompt 模板",
          "operationId": "generate_news_api_ai_generate_news_post",
          "requestBody": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ai-hub_NewsGenerationRequest"
                }
              }
            },
            "required": true
          },
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/ai-hub_NewsGenerationResponse"
                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/ai-hub_HTTPValidationError"
                  }
                }
              }
            }
          }
        }
      },
      "/api/ai/api/ai/generate/summary": {
        "post": {
          "tags": [
            "ai-hub",
            "AI"
          ],
          "summary": "生成投研摘要",
          "description": "生成投研摘要（偏结构化、要点式输出）\n\n- 默认模型：Qwen2.5（结构化输出能力强）\n- 支持显式指定模型\n- 支持多种摘要类型：structured/bullet/paragraph",
          "operationId": "generate_summary_api_ai_generate_summary_post",
          "requestBody": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ai-hub_SummaryGenerationRequest"
                }
              }
            },
            "required": true
          },
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/ai-hub_SummaryGenerationResponse"
                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/ai-hub_HTTPValidationError"
                  }
                }
              }
            }
          }
        }
      },
      "/api/ai/api/ai/generate/strategy": {
        "post": {
          "tags": [
            "ai-hub",
            "AI"
          ],
          "summary": "生成策略代码",
          "description": "生成 Backtrader 策略 Python 代码\n\n- 默认模型：Qwen2.5（代码生成能力强）\n- 支持显式指定模型\n- 基于 README.md 中的 Prompt 模板",
          "operationId": "generate_strategy_api_ai_generate_strategy_post",
          "requestBody": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ai-hub_StrategyGenerationRequest"
                }
              }
            },
            "required": true
          },
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/ai-hub_StrategyGenerationResponse"
                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/ai-hub_HTTPValidationError"
                  }
                }
              }
            }
          }
        }
      },
      "/api/ai/api/ai/chat": {
        "post": {
          "tags": [
            "ai-hub",
            "AI"
          ],
          "summary": "通用聊天接口",
          "description": "通用 AI 聊天接口\n\n支持指定模型或自动路由",
          "operationId": "chat_api_ai_chat_post",
          "requestBody": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ai-hub_ChatRequest"
                }
              }
            },
            "required": true
          },
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/ai-hub_ChatResponse"
                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/ai-hub_HTTPValidationError"
                  }
                }
              }
            }
          }
        }
      },
      "/api/ai/api/ai/report/generate": {
        "post": {
          "tags": [
            "ai-hub",
            "AI"
          ],
          "summary": "生成报告",
          "description": "生成公司研究报告\n\n基于 README.md 中的 Prompt 模板生成投研摘要",
          "operationId": "generate_report_api_ai_report_generate_post",
          "requestBody": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ai-hub_ReportGenerationRequest"
                }
              }
            },
            "required": true
          },
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/ai-hub_ReportGenerationResponse"
                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/ai-hub_HTTPValidationError"
                  }
                }
              }
            }
          }
        }
      },
      "/api/ai/api/ai/digital-human/generate": {
        "post": {
          "tags": [
            "ai-hub",
            "AI"
          ],
          "summary": "生成数字人视频",
          "description": "生成数字人视频\n\n将文本转换为数字人口播视频（需要配置第三方服务）",
          "operationId": "generate_digital_human_api_ai_digital_human_generate_post",
          "requestBody": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ai-hub_DigitalHumanRequest"
                }
              }
            },
            "required": true
          },
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/ai-hub_DigitalHumanResponse"
                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/ai-hub_HTTPValidationError"
                  }
                }
              }
            }
          }
        }
      },
      "/api/ai/api/ai/model/route": {
        "post": {
          "tags": [
            "ai-hub",
            "AI"
          ],
          "summary": "模型路由推荐",
          "description": "智能模型路由推荐\n\n根据任务类型推荐最适合的 AI 模型",
          "operationId": "route_model_api_ai_model_route_post",
          "requestBody": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ai-hub_ModelRouteRequest"
                }
              }
            },
            "required": true
          },
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/ai-hub_ModelRouteResponse"
                  }
                }
              }
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/ai-hub_HTTPValidationError"
                  }
                }
              }
            }
          }
        }
      },
      "/api/ai/": {
        "get": {
          "summary": "Root",
          "description": "根路径",
          "operationId": "root__get",
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "additionalProperties": true,
                    "type": "object",
                    "title": "Response Root  Get"
                  }
                }
              }
            }
          },
          "tags": [
            "ai-hub"
          ]
        }
      },
      "/api/ai/health": {
        "get": {
          "summary": "Health Check",
          "description": "健康检查",
          "operationId": "health_check_health_get",
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "additionalProperties": true,
                    "type": "object",
                    "title": "Response Health Check Health Get"
                  }
                }
              }
            }
          },
          "tags": [
            "ai-hub"
          ]
        }
      }
    },
    "components": {
      "schemas": {
        "quant-engine_AIReviewData": {
          "properties": {
            "strategy_type": {
              "type": "string",
              "title": "Strategy Type",
              "description": "策略类型（如：trend_following, mean_reversion）"
            },
            "holding_period_days_avg": {
              "type": "number",
              "title": "Holding Period Days Avg",
              "description": "平均持仓天数"
            },
            "trade_count": {
              "type": "integer",
              "title": "Trade Count",
              "description": "交易次数"
            },
            "win_rate": {
              "type": "number",
              "title": "Win Rate",
              "description": "胜率（0-1）"
            },
            "profit_loss_ratio": {
              "type": "number",
              "title": "Profit Loss Ratio",
              "description": "盈亏比"
            },
            "volatility": {
              "type": "number",
              "title": "Volatility",
              "description": "波动率"
            },
            "max_consecutive_loss": {
              "type": "integer",
              "title": "Max Consecutive Loss",
              "description": "最大连续亏损次数"
            },
            "drawdown_duration_days": {
              "type": "integer",
              "title": "Drawdown Duration Days",
              "description": "最大回撤持续时间（天）"
            },
            "return_over_drawdown": {
              "type": "number",
              "title": "Return Over Drawdown",
              "description": "收益回撤比"
            }
          },
          "type": "object",
          "required": [
            "strategy_type",
            "holding_period_days_avg",
            "trade_count",
            "win_rate",
            "profit_loss_ratio",
            "volatility",
            "max_consecutive_loss",
            "drawdown_duration_days",
            "return_over_drawdown"
          ],
          "title": "AIReviewData",
          "description": "AI 策略评价输入数据结构"
        },
        "quant-engine_BacktestRequest": {
          "properties": {
            "stock_code": {
              "type": "string",
              "minLength": 1,
              "title": "Stock Code",
              "description": "股票代码（如：000001）"
            },
            "start_date": {
              "type": "string",
              "title": "Start Date",
              "description": "开始日期（YYYY-MM-DD）"
            },
            "end_date": {
              "type": "string",
              "title": "End Date",
              "description": "结束日期（YYYY-MM-DD）"
            },
            "strategy_mode": {
              "type": "string",
              "enum": [
                "custom",
                "builtin"
              ],
              "title": "Strategy Mode",
              "description": "策略模式：custom（AI生成）或 builtin（系统内置）",
              "default": "custom"
            },
            "strategy_code": {
              "anyOf": [
                {
                  "type": "string",
                  "minLength": 1
                },
                {
                  "type": "null"
                }
              ],
              "title": "Strategy Code",
              "description": "策略代码（strategy_mode=custom 时必填）"
            },
            "strategy_name": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Strategy Name",
              "description": "策略名称（strategy_mode=builtin 时必填，如：ma_cross, rsi）"
            },
            "data_source": {
              "type": "string",
              "enum": [
                "tdengine",
                "tushare"
              ],
              "title": "Data Source",
              "description": "数据源：tdengine 或 tushare",
              "default": "tushare"
            },
            "enable_ai_review": {
              "type": "boolean",
              "title": "Enable Ai Review",
              "description": "是否启用 AI 评价（返回结构化评价输入数据）",
              "default": false
            },
            "initial_cash": {
              "type": "number",
              "minimum": 1000,
              "title": "Initial Cash",
              "description": "初始资金",
              "default": 1000000
            },
            "commission": {
              "type": "number",
              "maximum": 0.01,
              "minimum": 0,
              "title": "Commission",
              "description": "手续费率",
              "default": 0.001
            },
            "slippage": {
              "type": "number",
              "maximum": 0.01,
              "minimum": 0,
              "title": "Slippage",
              "description": "滑点",
              "default": 0
            },
            "parameters": {
              "additionalProperties": true,
              "type": "object",
              "title": "Parameters",
              "description": "策略参数"
            }
          },
          "type": "object",
          "required": [
            "stock_code",
            "start_date",
            "end_date"
          ],
          "title": "BacktestRequest",
          "description": "回测请求"
        },
        "quant-engine_BacktestResponse": {
          "properties": {
            "success": {
              "type": "boolean",
              "title": "Success",
              "description": "是否成功"
            },
            "backtest_id": {
              "type": "string",
              "title": "Backtest Id",
              "description": "回测ID"
            },
            "metrics": {
              "additionalProperties": true,
              "type": "object",
              "title": "Metrics",
              "description": "基础指标"
            },
            "daily_nav": {
              "items": {
                "additionalProperties": true,
                "type": "object"
              },
              "type": "array",
              "title": "Daily Nav",
              "description": "每日净值曲线，格式：[{date: 'YYYY-MM-DD', nav: float}]"
            },
            "ai_review": {
              "anyOf": [
                {
                  "$ref": "#/components/schemas/quant-engine_AIReviewData"
                },
                {
                  "type": "null"
                }
              ],
              "description": "AI 评价所需的结构化数据"
            },
            "message": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Message",
              "description": "消息或错误信息"
            }
          },
          "type": "object",
          "required": [
            "success",
            "backtest_id",
            "metrics",
            "daily_nav"
          ],
          "title": "BacktestResponse",
          "description": "回测响应",
          "example": {
            "ai_review": {
              "drawdown_duration_days": 78,
              "holding_period_days_avg": 12.4,
              "max_consecutive_loss": 5,
              "profit_loss_ratio": 1.37,
              "return_over_drawdown": 0.86,
              "strategy_type": "trend_following",
              "trade_count": 86,
              "volatility": 0.22,
              "win_rate": 0.54
            },
            "backtest_id": "backtest_001",
            "daily_nav": [
              {
                "date": "2022-01-01",
                "nav": 1
              },
              {
                "date": "2022-01-02",
                "nav": 1.02
              }
            ],
            "metrics": {
              "annual_return": 0.18,
              "max_drawdown": -0.21,
              "sharpe_ratio": 1.42
            },
            "success": true
          }
        },
        "quant-engine_BaseResponse_BacktestResponse_": {
          "properties": {
            "success": {
              "type": "boolean",
              "title": "Success"
            },
            "data": {
              "anyOf": [
                {
                  "$ref": "#/components/schemas/quant-engine_BacktestResponse"
                },
                {
                  "type": "null"
                }
              ]
            },
            "message": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Message"
            }
          },
          "type": "object",
          "required": [
            "success"
          ],
          "title": "BaseResponse[BacktestResponse]"
        },
        "quant-engine_FactorCalculateRequest": {
          "properties": {
            "factor_id": {
              "type": "string",
              "title": "Factor Id",
              "description": "因子ID"
            },
            "symbol": {
              "type": "string",
              "minLength": 1,
              "title": "Symbol",
              "description": "股票代码"
            },
            "start_date": {
              "type": "string",
              "title": "Start Date",
              "description": "开始日期（YYYY-MM-DD）"
            },
            "end_date": {
              "type": "string",
              "title": "End Date",
              "description": "结束日期（YYYY-MM-DD）"
            },
            "parameters": {
              "anyOf": [
                {
                  "additionalProperties": true,
                  "type": "object"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Parameters",
              "description": "因子参数（覆盖默认参数）"
            }
          },
          "type": "object",
          "required": [
            "factor_id",
            "symbol",
            "start_date",
            "end_date"
          ],
          "title": "FactorCalculateRequest",
          "description": "计算因子请求"
        },
        "quant-engine_FactorCalculateResponse": {
          "properties": {
            "factor_id": {
              "type": "string",
              "title": "Factor Id",
              "description": "因子ID"
            },
            "symbol": {
              "type": "string",
              "title": "Symbol",
              "description": "股票代码"
            },
            "start_date": {
              "type": "string",
              "title": "Start Date",
              "description": "开始日期"
            },
            "end_date": {
              "type": "string",
              "title": "End Date",
              "description": "结束日期"
            },
            "values": {
              "items": {
                "additionalProperties": true,
                "type": "object"
              },
              "type": "array",
              "title": "Values",
              "description": "因子值列表，格式：[{date: 'YYYY-MM-DD', value: float}]"
            },
            "total_points": {
              "type": "integer",
              "title": "Total Points",
              "description": "数据点总数"
            }
          },
          "type": "object",
          "required": [
            "factor_id",
            "symbol",
            "start_date",
            "end_date",
            "values",
            "total_points"
          ],
          "title": "FactorCalculateResponse",
          "description": "计算因子响应"
        },
        "quant-engine_FactorCreateRequest": {
          "properties": {
            "name": {
              "type": "string",
              "maxLength": 100,
              "minLength": 1,
              "title": "Name",
              "description": "因子名称"
            },
            "description": {
              "type": "string",
              "maxLength": 1000,
              "title": "Description",
              "description": "因子描述",
              "default": ""
            },
            "category": {
              "type": "string",
              "title": "Category",
              "description": "因子类别：technical/fundamental/macro",
              "default": "technical"
            },
            "formula": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Formula",
              "description": "因子公式"
            },
            "parameters": {
              "additionalProperties": true,
              "type": "object",
              "title": "Parameters",
              "description": "因子参数"
            }
          },
          "type": "object",
          "required": [
            "name"
          ],
          "title": "FactorCreateRequest",
          "description": "创建因子请求"
        },
        "quant-engine_FactorListResponse": {
          "properties": {
            "total": {
              "type": "integer",
              "title": "Total",
              "description": "总数"
            },
            "factors": {
              "items": {
                "$ref": "#/components/schemas/quant-engine_FactorResponse"
              },
              "type": "array",
              "title": "Factors",
              "description": "因子列表"
            }
          },
          "type": "object",
          "required": [
            "total",
            "factors"
          ],
          "title": "FactorListResponse",
          "description": "因子列表响应"
        },
        "quant-engine_FactorResponse": {
          "properties": {
            "id": {
              "type": "string",
              "title": "Id",
              "description": "因子ID"
            },
            "name": {
              "type": "string",
              "title": "Name",
              "description": "因子名称"
            },
            "description": {
              "type": "string",
              "title": "Description",
              "description": "因子描述"
            },
            "category": {
              "type": "string",
              "title": "Category",
              "description": "因子类别"
            },
            "formula": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Formula",
              "description": "因子公式"
            },
            "parameters": {
              "additionalProperties": true,
              "type": "object",
              "title": "Parameters",
              "description": "因子参数"
            },
            "created_at": {
              "type": "string",
              "title": "Created At",
              "description": "创建时间"
            }
          },
          "type": "object",
          "required": [
            "id",
            "name",
            "description",
            "category",
            "parameters",
            "created_at"
          ],
          "title": "FactorResponse",
          "description": "因子响应"
        },
        "quant-engine_FactorUpdateRequest": {
          "properties": {
            "name": {
              "anyOf": [
                {
                  "type": "string",
                  "maxLength": 100,
                  "minLength": 1
                },
                {
                  "type": "null"
                }
              ],
              "title": "Name",
              "description": "因子名称"
            },
            "description": {
              "anyOf": [
                {
                  "type": "string",
                  "maxLength": 1000
                },
                {
                  "type": "null"
                }
              ],
              "title": "Description",
              "description": "因子描述"
            },
            "category": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Category",
              "description": "因子类别"
            },
            "formula": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Formula",
              "description": "因子公式"
            },
            "parameters": {
              "anyOf": [
                {
                  "additionalProperties": true,
                  "type": "object"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Parameters",
              "description": "因子参数"
            }
          },
          "type": "object",
          "title": "FactorUpdateRequest",
          "description": "更新因子请求"
        },
        "quant-engine_HTTPValidationError": {
          "properties": {
            "detail": {
              "items": {
                "$ref": "#/components/schemas/quant-engine_ValidationError"
              },
              "type": "array",
              "title": "Detail"
            }
          },
          "type": "object",
          "title": "HTTPValidationError"
        },
        "quant-engine_PaginatedResponse_BacktestResponse_": {
          "properties": {
            "total": {
              "type": "integer",
              "title": "Total"
            },
            "items": {
              "items": {
                "$ref": "#/components/schemas/quant-engine_BacktestResponse"
              },
              "type": "array",
              "title": "Items"
            }
          },
          "type": "object",
          "required": [
            "total",
            "items"
          ],
          "title": "PaginatedResponse[BacktestResponse]"
        },
        "quant-engine_StrategyCreateRequest": {
          "properties": {
            "name": {
              "type": "string",
              "maxLength": 100,
              "minLength": 1,
              "title": "Name",
              "description": "策略名称"
            },
            "description": {
              "type": "string",
              "maxLength": 1000,
              "title": "Description",
              "description": "策略描述",
              "default": ""
            },
            "code": {
              "type": "string",
              "minLength": 10,
              "title": "Code",
              "description": "策略代码（Python）"
            },
            "parameters": {
              "additionalProperties": true,
              "type": "object",
              "title": "Parameters",
              "description": "策略参数"
            }
          },
          "type": "object",
          "required": [
            "name",
            "code"
          ],
          "title": "StrategyCreateRequest",
          "description": "创建策略请求"
        },
        "quant-engine_StrategyListResponse": {
          "properties": {
            "total": {
              "type": "integer",
              "title": "Total",
              "description": "总数"
            },
            "strategies": {
              "items": {
                "$ref": "#/components/schemas/quant-engine_StrategyResponse"
              },
              "type": "array",
              "title": "Strategies",
              "description": "策略列表"
            }
          },
          "type": "object",
          "required": [
            "total",
            "strategies"
          ],
          "title": "StrategyListResponse",
          "description": "策略列表响应"
        },
        "quant-engine_StrategyResponse": {
          "properties": {
            "id": {
              "type": "string",
              "title": "Id",
              "description": "策略ID"
            },
            "name": {
              "type": "string",
              "title": "Name",
              "description": "策略名称"
            },
            "description": {
              "type": "string",
              "title": "Description",
              "description": "策略描述"
            },
            "code": {
              "type": "string",
              "title": "Code",
              "description": "策略代码"
            },
            "parameters": {
              "additionalProperties": true,
              "type": "object",
              "title": "Parameters",
              "description": "策略参数"
            },
            "status": {
              "type": "string",
              "title": "Status",
              "description": "状态"
            },
            "created_at": {
              "type": "string",
              "title": "Created At",
              "description": "创建时间"
            },
            "updated_at": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Updated At",
              "description": "更新时间"
            }
          },
          "type": "object",
          "required": [
            "id",
            "name",
            "description",
            "code",
            "parameters",
            "status",
            "created_at"
          ],
          "title": "StrategyResponse",
          "description": "策略响应"
        },
        "quant-engine_StrategyUpdateRequest": {
          "properties": {
            "name": {
              "anyOf": [
                {
                  "type": "string",
                  "maxLength": 100,
                  "minLength": 1
                },
                {
                  "type": "null"
                }
              ],
              "title": "Name",
              "description": "策略名称"
            },
            "description": {
              "anyOf": [
                {
                  "type": "string",
                  "maxLength": 1000
                },
                {
                  "type": "null"
                }
              ],
              "title": "Description",
              "description": "策略描述"
            },
            "code": {
              "anyOf": [
                {
                  "type": "string",
                  "minLength": 10
                },
                {
                  "type": "null"
                }
              ],
              "title": "Code",
              "description": "策略代码（Python）"
            },
            "parameters": {
              "anyOf": [
                {
                  "additionalProperties": true,
                  "type": "object"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Parameters",
              "description": "策略参数"
            },
            "status": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Status",
              "description": "状态：active/inactive"
            }
          },
          "type": "object",
          "title": "StrategyUpdateRequest",
          "description": "更新策略请求"
        },
        "quant-engine_StrategyValidateRequest": {
          "properties": {
            "code": {
              "type": "string",
              "minLength": 10,
              "title": "Code",
              "description": "策略代码（Python）"
            }
          },
          "type": "object",
          "required": [
            "code"
          ],
          "title": "StrategyValidateRequest",
          "description": "策略验证请求"
        },
        "quant-engine_StrategyValidateResponse": {
          "properties": {
            "valid": {
              "type": "boolean",
              "title": "Valid",
              "description": "是否有效"
            },
            "errors": {
              "items": {
                "type": "string"
              },
              "type": "array",
              "title": "Errors",
              "description": "错误列表"
            },
            "warnings": {
              "items": {
                "type": "string"
              },
              "type": "array",
              "title": "Warnings",
              "description": "警告列表"
            },
            "message": {
              "type": "string",
              "title": "Message",
              "description": "验证消息"
            }
          },
          "type": "object",
          "required": [
            "valid",
            "message"
          ],
          "title": "StrategyValidateResponse",
          "description": "策略验证响应"
        },
        "quant-engine_ValidationError": {
          "properties": {
            "loc": {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "integer"
                  }
                ]
              },
              "type": "array",
              "title": "Location"
            },
            "msg": {
              "type": "string",
              "title": "Message"
            },
            "type": {
              "type": "string",
              "title": "Error Type"
            }
          },
          "type": "object",
          "required": [
            "loc",
            "msg",
            "type"
          ],
          "title": "ValidationError"
        },
        "ai-hub_ChatRequest": {
          "properties": {
            "message": {
              "type": "string",
              "minLength": 1,
              "title": "Message",
              "description": "用户消息"
            },
            "model": {
              "anyOf": [
                {
                  "$ref": "#/components/schemas/ai-hub_ModelType"
                },
                {
                  "type": "null"
                }
              ],
              "description": "指定模型，不指定则自动路由"
            },
            "temperature": {
              "anyOf": [
                {
                  "type": "number",
                  "maximum": 2,
                  "minimum": 0
                },
                {
                  "type": "null"
                }
              ],
              "title": "Temperature",
              "description": "温度参数"
            },
            "max_tokens": {
              "anyOf": [
                {
                  "type": "integer",
                  "maximum": 8192,
                  "minimum": 1
                },
                {
                  "type": "null"
                }
              ],
              "title": "Max Tokens",
              "description": "最大生成token数"
            },
            "system_prompt": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "System Prompt",
              "description": "系统提示词"
            }
          },
          "type": "object",
          "required": [
            "message"
          ],
          "title": "ChatRequest",
          "description": "聊天请求"
        },
        "ai-hub_ChatResponse": {
          "properties": {
            "content": {
              "type": "string",
              "title": "Content",
              "description": "AI 回复内容"
            },
            "model": {
              "type": "string",
              "title": "Model",
              "description": "使用的模型"
            },
            "tokens_used": {
              "anyOf": [
                {
                  "type": "integer"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Tokens Used",
              "description": "使用的token数"
            },
            "finish_reason": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Finish Reason",
              "description": "完成原因"
            }
          },
          "type": "object",
          "required": [
            "content",
            "model"
          ],
          "title": "ChatResponse",
          "description": "聊天响应"
        },
        "ai-hub_DigitalHumanRequest": {
          "properties": {
            "text": {
              "type": "string",
              "minLength": 1,
              "title": "Text",
              "description": "口播文本"
            },
            "duration_limit": {
              "type": "integer",
              "maximum": 120,
              "minimum": 10,
              "title": "Duration Limit",
              "description": "时长限制（秒）",
              "default": 40
            },
            "voice_style": {
              "type": "string",
              "title": "Voice Style",
              "description": "语音风格",
              "default": "professional"
            }
          },
          "type": "object",
          "required": [
            "text"
          ],
          "title": "DigitalHumanRequest",
          "description": "数字人视频生成请求"
        },
        "ai-hub_DigitalHumanResponse": {
          "properties": {
            "video_url": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Video Url",
              "description": "视频URL"
            },
            "task_id": {
              "type": "string",
              "title": "Task Id",
              "description": "任务ID"
            },
            "estimated_duration": {
              "type": "integer",
              "title": "Estimated Duration",
              "description": "预计时长（秒）"
            },
            "status": {
              "type": "string",
              "title": "Status",
              "description": "任务状态：pending/processing/completed/failed"
            }
          },
          "type": "object",
          "required": [
            "task_id",
            "estimated_duration",
            "status"
          ],
          "title": "DigitalHumanResponse",
          "description": "数字人视频生成响应"
        },
        "ai-hub_HTTPValidationError": {
          "properties": {
            "detail": {
              "items": {
                "$ref": "#/components/schemas/ai-hub_ValidationError"
              },
              "type": "array",
              "title": "Detail"
            }
          },
          "type": "object",
          "title": "HTTPValidationError"
        },
        "ai-hub_ModelRouteRequest": {
          "properties": {
            "task_type": {
              "$ref": "#/components/schemas/ai-hub_TaskType"
            },
            "message": {
              "type": "string",
              "minLength": 1,
              "title": "Message",
              "description": "消息内容"
            }
          },
          "type": "object",
          "required": [
            "task_type",
            "message"
          ],
          "title": "ModelRouteRequest",
          "description": "模型路由请求"
        },
        "ai-hub_ModelRouteResponse": {
          "properties": {
            "recommended_model": {
              "$ref": "#/components/schemas/ai-hub_ModelType",
              "description": "推荐的模型"
            },
            "reason": {
              "type": "string",
              "title": "Reason",
              "description": "推荐理由"
            }
          },
          "type": "object",
          "required": [
            "recommended_model",
            "reason"
          ],
          "title": "ModelRouteResponse",
          "description": "模型路由响应"
        },
        "ai-hub_ModelType": {
          "type": "string",
          "enum": [
            "deepseek",
            "qwen",
            "openai"
          ],
          "title": "ModelType",
          "description": "支持的 AI 模型类型"
        },
        "ai-hub_NewsGenerationRequest": {
          "properties": {
            "news_flash": {
              "type": "string",
              "minLength": 1,
              "title": "News Flash",
              "description": "快讯内容"
            },
            "stock_code": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Stock Code",
              "description": "股票代码"
            },
            "quote_data": {
              "anyOf": [
                {
                  "additionalProperties": true,
                  "type": "object"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Quote Data",
              "description": "行情数据"
            },
            "target_length": {
              "type": "integer",
              "maximum": 1000,
              "minimum": 100,
              "title": "Target Length",
              "description": "目标字数",
              "default": 300
            },
            "model": {
              "anyOf": [
                {
                  "$ref": "#/components/schemas/ai-hub_ModelType"
                },
                {
                  "type": "null"
                }
              ],
              "description": "显式指定模型，不指定则自动路由到 DeepSeek"
            }
          },
          "type": "object",
          "required": [
            "news_flash"
          ],
          "title": "NewsGenerationRequest",
          "description": "新闻生成请求"
        },
        "ai-hub_NewsGenerationResponse": {
          "properties": {
            "news_content": {
              "type": "string",
              "title": "News Content",
              "description": "生成的新闻内容"
            },
            "model": {
              "type": "string",
              "title": "Model",
              "description": "使用的模型"
            },
            "word_count": {
              "type": "integer",
              "title": "Word Count",
              "description": "字数统计"
            },
            "tokens_used": {
              "anyOf": [
                {
                  "type": "integer"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Tokens Used",
              "description": "使用的token数"
            }
          },
          "type": "object",
          "required": [
            "news_content",
            "model",
            "word_count"
          ],
          "title": "NewsGenerationResponse",
          "description": "新闻生成响应"
        },
        "ai-hub_ReportGenerationRequest": {
          "properties": {
            "company_info": {
              "type": "string",
              "minLength": 1,
              "title": "Company Info",
              "description": "公司信息"
            },
            "report_type": {
              "type": "string",
              "title": "Report Type",
              "description": "报告类型：summary/analysis",
              "default": "summary"
            },
            "include_risks": {
              "type": "boolean",
              "title": "Include Risks",
              "description": "是否包含风险因素",
              "default": true
            }
          },
          "type": "object",
          "required": [
            "company_info"
          ],
          "title": "ReportGenerationRequest",
          "description": "报告生成请求"
        },
        "ai-hub_ReportGenerationResponse": {
          "properties": {
            "report_content": {
              "type": "string",
              "title": "Report Content",
              "description": "生成的报告内容"
            },
            "model": {
              "type": "string",
              "title": "Model",
              "description": "使用的模型"
            },
            "sections": {
              "items": {
                "type": "string"
              },
              "type": "array",
              "title": "Sections",
              "description": "报告章节列表"
            }
          },
          "type": "object",
          "required": [
            "report_content",
            "model"
          ],
          "title": "ReportGenerationResponse",
          "description": "报告生成响应"
        },
        "ai-hub_StrategyGenerationRequest": {
          "properties": {
            "user_description": {
              "type": "string",
              "minLength": 1,
              "title": "User Description",
              "description": "用户策略描述"
            },
            "framework": {
              "type": "string",
              "title": "Framework",
              "description": "回测框架：backtrader/zipline",
              "default": "backtrader"
            },
            "include_risk_control": {
              "type": "boolean",
              "title": "Include Risk Control",
              "description": "是否包含风险控制",
              "default": true
            },
            "model": {
              "anyOf": [
                {
                  "$ref": "#/components/schemas/ai-hub_ModelType"
                },
                {
                  "type": "null"
                }
              ],
              "description": "显式指定模型，不指定则自动路由到 Qwen"
            }
          },
          "type": "object",
          "required": [
            "user_description"
          ],
          "title": "StrategyGenerationRequest",
          "description": "策略生成请求"
        },
        "ai-hub_StrategyGenerationResponse": {
          "properties": {
            "strategy_code": {
              "type": "string",
              "title": "Strategy Code",
              "description": "生成的策略代码"
            },
            "model": {
              "type": "string",
              "title": "Model",
              "description": "使用的模型"
            },
            "explanation": {
              "type": "string",
              "title": "Explanation",
              "description": "策略说明"
            },
            "parameters": {
              "additionalProperties": true,
              "type": "object",
              "title": "Parameters",
              "description": "策略参数"
            },
            "tokens_used": {
              "anyOf": [
                {
                  "type": "integer"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Tokens Used",
              "description": "使用的token数"
            }
          },
          "type": "object",
          "required": [
            "strategy_code",
            "model",
            "explanation"
          ],
          "title": "StrategyGenerationResponse",
          "description": "策略生成响应"
        },
        "ai-hub_SummaryGenerationRequest": {
          "properties": {
            "content": {
              "type": "string",
              "minLength": 1,
              "title": "Content",
              "description": "待摘要内容"
            },
            "summary_type": {
              "type": "string",
              "title": "Summary Type",
              "description": "摘要类型：structured/bullet/paragraph",
              "default": "structured"
            },
            "max_length": {
              "anyOf": [
                {
                  "type": "integer",
                  "maximum": 2000,
                  "minimum": 50
                },
                {
                  "type": "null"
                }
              ],
              "title": "Max Length",
              "description": "最大长度"
            },
            "model": {
              "anyOf": [
                {
                  "$ref": "#/components/schemas/ai-hub_ModelType"
                },
                {
                  "type": "null"
                }
              ],
              "description": "显式指定模型，不指定则自动路由到 Qwen"
            }
          },
          "type": "object",
          "required": [
            "content"
          ],
          "title": "SummaryGenerationRequest",
          "description": "摘要生成请求"
        },
        "ai-hub_SummaryGenerationResponse": {
          "properties": {
            "summary": {
              "type": "string",
              "title": "Summary",
              "description": "生成的摘要"
            },
            "model": {
              "type": "string",
              "title": "Model",
              "description": "使用的模型"
            },
            "tokens_used": {
              "anyOf": [
                {
                  "type": "integer"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Tokens Used",
              "description": "使用的token数"
            },
            "sections": {
              "anyOf": [
                {
                  "items": {
                    "type": "string"
                  },
                  "type": "array"
                },
                {
                  "type": "null"
                }
              ],
              "title": "Sections",
              "description": "结构化摘要的章节列表"
            }
          },
          "type": "object",
          "required": [
            "summary",
            "model"
          ],
          "title": "SummaryGenerationResponse",
          "description": "摘要生成响应"
        },
        "ai-hub_TaskType": {
          "type": "string",
          "enum": [
            "code",
            "news",
            "summary",
            "strategy",
            "general"
          ],
          "title": "TaskType",
          "description": "任务类型"
        },
        "ai-hub_ValidationError": {
          "properties": {
            "loc": {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "integer"
                  }
                ]
              },
              "type": "array",
              "title": "Location"
            },
            "msg": {
              "type": "string",
              "title": "Message"
            },
            "type": {
              "type": "string",
              "title": "Error Type"
            }
          },
          "type": "object",
          "required": [
            "loc",
            "msg",
            "type"
          ],
          "title": "ValidationError"
        }
      },
      "securitySchemes": {
        "OAuth2PasswordBearer": {
          "type": "oauth2",
          "flows": {
            "password": {
              "tokenUrl": "/auth/token",
              "scopes": {

              }
            }
          }
        }
      }
    },
    "tags": [
      {
        "name": "quant-engine",
        "description": "APIs from quant-engine"
      },
      {
        "name": "ai-hub",
        "description": "APIs from ai-hub"
      }
    ],
    "security": [
      {
        "OAuth2PasswordBearer": []
      }
    ]
  }
}