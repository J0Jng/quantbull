{
  "openapi": "3.1.0",
  "info": {
    "title": "API Gateway",
    "description": "量化牛牛统一 API 网关",
    "version": "1.0.0"
  },
  "paths": {
    "/": {
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
        }
      }
    },
    "/health": {
      "get": {
        "summary": "Health Check",
        "description": "健康检查（不需要鉴权）",
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
        }
      }
    },
    "/api/gateway/health": {
      "get": {
        "tags": [
          "网关管理"
        ],
        "summary": "Gateway Health",
        "description": "网关健康检查",
        "operationId": "gateway_health_api_gateway_health_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "additionalProperties": true,
                  "type": "object",
                  "title": "Response Gateway Health Api Gateway Health Get"
                }
              }
            }
          }
        }
      }
    },
    "/api/gateway/services/health": {
      "get": {
        "tags": [
          "网关管理"
        ],
        "summary": "Check All Services",
        "description": "检查所有微服务的健康状态",
        "operationId": "check_all_services_api_gateway_services_health_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "items": {
                    "$ref": "#/components/schemas/ServiceHealth"
                  },
                  "type": "array",
                  "title": "Response Check All Services Api Gateway Services Health Get"
                }
              }
            }
          }
        }
      }
    },
    "/api/auth/login": {
      "post": {
        "tags": [
          "认证"
        ],
        "summary": "Login",
        "description": "用户登录（OAuth2 标准格式）- 委托 user-service\n\n返回格式符合 OAuth2 标准，供 Swagger UI 使用",
        "operationId": "login_api_auth_login_post",
        "requestBody": {
          "content": {
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/Body_login_api_auth_login_post"
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
                  "additionalProperties": true,
                  "type": "object",
                  "title": "Response Login Api Auth Login Post"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        },
        "security": []
      }
    },
    "/api/auth/login/json": {
      "post": {
        "tags": [
          "认证"
        ],
        "summary": "Login Json",
        "description": "用户登录（JSON 格式）- 委托 user-service",
        "operationId": "login_json_api_auth_login_json_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/LoginRequest"
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
                  "additionalProperties": true,
                  "type": "object",
                  "title": "Response Login Json Api Auth Login Json Post"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        },
        "security": []
      }
    },
    "/api/auth/register": {
      "post": {
        "tags": [
          "认证"
        ],
        "summary": "Register",
        "description": "用户注册 - 透传 user-service",
        "operationId": "register_api_auth_register_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/LoginRequest"
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
                  "additionalProperties": true,
                  "type": "object",
                  "title": "Response Register Api Auth Register Post"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        },
        "security": []
      }
    },
    "/api/auth/me": {
      "get": {
        "tags": [
          "认证"
        ],
        "summary": "Get Current User",
        "description": "获取当前用户信息，依赖 user-service 校验",
        "operationId": "get_current_user_api_auth_me_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "additionalProperties": true,
                  "type": "object",
                  "title": "Response Get Current User Api Auth Me Get"
                }
              }
            }
          }
        },
        "security": [
          {
            "OAuth2PasswordBearer": []
          }
        ]
      }
    },
    "/api/auth/verify": {
      "get": {
        "tags": [
          "认证"
        ],
        "summary": "Verify Token",
        "description": "校验令牌有效性 - 透传 user-service",
        "operationId": "verify_token_api_auth_verify_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "additionalProperties": true,
                  "type": "object",
                  "title": "Response Verify Token Api Auth Verify Get"
                }
              }
            }
          }
        },
        "security": [
          {
            "OAuth2PasswordBearer": []
          }
        ]
      }
    },
    "/api/admin/users": {
      "get": {
        "tags": [
          "admin"
        ],
        "summary": "获取用户列表",
        "description": "管理员获取所有用户列表（支持分页）",
        "operationId": "list_users_api_admin_users_get",
        "security": [
          {
            "OAuth2PasswordBearer": []
          }
        ],
        "parameters": [
          {
            "name": "limit",
            "in": "query",
            "required": false,
            "schema": {
              "type": "integer",
              "description": "每页数量",
              "default": 100,
              "title": "Limit"
            },
            "description": "每页数量"
          },
          {
            "name": "offset",
            "in": "query",
            "required": false,
            "schema": {
              "type": "integer",
              "description": "偏移量",
              "default": 0,
              "title": "Offset"
            },
            "description": "偏移量"
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
                  "title": "Response List Users Api Admin Users Get"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "post": {
        "tags": [
          "admin"
        ],
        "summary": "创建用户",
        "description": "管理员创建新用户",
        "operationId": "create_user_api_admin_users_post",
        "security": [
          {
            "OAuth2PasswordBearer": []
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/UserCreateRequest"
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
                  "type": "object",
                  "additionalProperties": true,
                  "title": "Response Create User Api Admin Users Post"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/admin/users/{user_id}": {
      "get": {
        "tags": [
          "admin"
        ],
        "summary": "获取用户详情",
        "description": "管理员获取指定用户的详细信息",
        "operationId": "get_user_api_admin_users__user_id__get",
        "security": [
          {
            "OAuth2PasswordBearer": []
          }
        ],
        "parameters": [
          {
            "name": "user_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "integer",
              "title": "User Id"
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
                  "title": "Response Get User Api Admin Users  User Id  Get"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "patch": {
        "tags": [
          "admin"
        ],
        "summary": "更新用户",
        "description": "管理员更新用户信息（重置密码、修改角色）",
        "operationId": "update_user_api_admin_users__user_id__patch",
        "security": [
          {
            "OAuth2PasswordBearer": []
          }
        ],
        "parameters": [
          {
            "name": "user_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "integer",
              "title": "User Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/UserUpdateRequest"
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
                  "type": "object",
                  "additionalProperties": true,
                  "title": "Response Update User Api Admin Users  User Id  Patch"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "delete": {
        "tags": [
          "admin"
        ],
        "summary": "删除用户",
        "description": "管理员删除指定用户",
        "operationId": "delete_user_api_admin_users__user_id__delete",
        "security": [
          {
            "OAuth2PasswordBearer": []
          }
        ],
        "parameters": [
          {
            "name": "user_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "integer",
              "title": "User Id"
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
                  "title": "Response Delete User Api Admin Users  User Id  Delete"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/ai/generate/news": {
      "post": {
        "tags": [
          "AI Hub"
        ],
        "summary": "生成新闻解读",
        "description": "根据财经快讯生成新闻解读\n\n- 默认模型：DeepSeek R1（文本生成、新闻能力强）\n- 支持显式指定模型\n- 基于 README.md 中的 Prompt 模板",
        "operationId": "generate_news_api_ai_generate_news_post",
        "parameters": [
          {
            "name": "authorization",
            "in": "header",
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
              "title": "Authorization"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ai_NewsGenerationRequest"
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
                  "$ref": "#/components/schemas/ai_NewsGenerationResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ai_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/ai/generate/summary": {
      "post": {
        "tags": [
          "AI Hub"
        ],
        "summary": "生成投研摘要",
        "description": "生成投研摘要（偏结构化、要点式输出）\n\n- 默认模型：Qwen2.5（结构化输出能力强）\n- 支持显式指定模型\n- 支持多种摘要类型：structured/bullet/paragraph",
        "operationId": "generate_summary_api_ai_generate_summary_post",
        "parameters": [
          {
            "name": "authorization",
            "in": "header",
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
              "title": "Authorization"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ai_SummaryGenerationRequest"
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
                  "$ref": "#/components/schemas/ai_ApiResponse_SummaryGenerationResponse_"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ai_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/ai/generate/strategy": {
      "post": {
        "tags": [
          "AI Hub"
        ],
        "summary": "生成策略代码",
        "description": "生成 Backtrader 策略 Python 代码\n\n- 默认模型：Qwen2.5（代码生成能力强）\n- 支持显式指定模型\n- 基于 README.md 中的 Prompt 模板",
        "operationId": "generate_strategy_api_ai_generate_strategy_post",
        "parameters": [
          {
            "name": "authorization",
            "in": "header",
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
              "title": "Authorization"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ai_StrategyGenerationRequest"
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
                  "$ref": "#/components/schemas/ai_StrategyGenerationResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ai_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/ai/chat": {
      "post": {
        "tags": [
          "AI Hub"
        ],
        "summary": "通用聊天接口",
        "description": "通用 AI 聊天接口\n\n支持指定模型或自动路由",
        "operationId": "chat_api_ai_chat_post",
        "parameters": [
          {
            "name": "authorization",
            "in": "header",
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
              "title": "Authorization"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ai_ChatRequest"
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
                  "$ref": "#/components/schemas/ai_ChatResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ai_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/ai/report/generate": {
      "post": {
        "tags": [
          "AI Hub"
        ],
        "summary": "生成报告",
        "description": "生成公司研究报告\n\n基于 README.md 中的 Prompt 模板生成投研摘要",
        "operationId": "generate_report_api_ai_report_generate_post",
        "parameters": [
          {
            "name": "authorization",
            "in": "header",
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
              "title": "Authorization"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ai_ReportGenerationRequest"
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
                  "$ref": "#/components/schemas/ai_ReportGenerationResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ai_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/ai/digital-human/generate": {
      "post": {
        "tags": [
          "AI Hub"
        ],
        "summary": "生成数字人视频（占位）",
        "description": "数字人服务占位，暂未实现",
        "operationId": "generate_digital_human_api_ai_digital_human_generate_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ai_DigitalHumanRequest"
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
                  "additionalProperties": true,
                  "type": "object",
                  "title": "Response Generate Digital Human Api Ai Digital Human Generate Post"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ai_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/ai/model/route": {
      "post": {
        "tags": [
          "AI Hub"
        ],
        "summary": "模型路由推荐",
        "description": "智能模型路由推荐\n\n根据任务类型推荐最适合的 AI 模型",
        "operationId": "route_model_api_ai_model_route_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ai_ModelRouteRequest"
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
                  "$ref": "#/components/schemas/ai_ModelRouteResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ai_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/data/clean": {
      "post": {
        "tags": [
          "Data Service"
        ],
        "summary": "Clean Data",
        "operationId": "clean_data_api_data_clean_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/data_CleanRequest"
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
                  "$ref": "#/components/schemas/data_CleanResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/data_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/quotes/realtime": {
      "post": {
        "tags": [
          "Data Service"
        ],
        "summary": "Get Realtime Quotes",
        "description": "获取实时行情数据（使用 Tushare API）\n\n支持沪深 A 股（000/002/300/600/601/603 等）\n自动根据股票代码判断交易所（深圳/上海）并转换为 Tushare 格式\n\n注意：需要配置环境变量 TUSHARE_TOKEN",
        "operationId": "get_realtime_quotes_api_quotes_realtime_options",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/data_RealtimeQuoteRequest"
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
                  "$ref": "#/components/schemas/data_RealtimeQuoteResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/data_HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "options": {
        "tags": [
          "Data Service"
        ],
        "summary": "Get Realtime Quotes",
        "description": "获取实时行情数据（使用 Tushare API）\n\n支持沪深 A 股（000/002/300/600/601/603 等）\n自动根据股票代码判断交易所（深圳/上海）并转换为 Tushare 格式\n\n注意：需要配置环境变量 TUSHARE_TOKEN",
        "operationId": "get_realtime_quotes_api_quotes_realtime_options",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/data_RealtimeQuoteResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/data_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/tushare/daily": {
      "post": {
        "tags": [
          "Data Service"
        ],
        "summary": "Get Daily Quotes",
        "description": "获取日线行情数据\n\n支持批量查询多只股票的日线行情数据\n数据会自动保存到数据库（upsert）",
        "operationId": "get_daily_quotes_api_tushare_daily_options",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/data_DailyQuoteRequest"
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
                  "$ref": "#/components/schemas/data_DailyQuoteResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/data_HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "options": {
        "tags": [
          "Data Service"
        ],
        "summary": "Get Daily Quotes",
        "description": "获取日线行情数据\n\n支持批量查询多只股票的日线行情数据\n数据会自动保存到数据库（upsert）",
        "operationId": "get_daily_quotes_api_tushare_daily_options",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/data_DailyQuoteResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/data_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/tushare/stock_basic": {
      "get": {
        "tags": [
          "Data Service"
        ],
        "summary": "Get Stock Basic",
        "description": "获取股票基础信息",
        "operationId": "get_stock_basic_api_tushare_stock_basic_get",
        "parameters": [
          {
            "name": "exchange",
            "in": "query",
            "required": false,
            "schema": {
              "type": "string",
              "default": "",
              "title": "Exchange"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/data_StockBasicResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/data_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/tushare/fund_daily": {
      "post": {
        "tags": [
          "Data Service"
        ],
        "summary": "Get Fund Daily",
        "description": "获取 ETF 日线行情",
        "operationId": "get_fund_daily_api_tushare_fund_daily_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/data_DailyQuoteRequest"
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
                  "$ref": "#/components/schemas/data_DailyQuoteResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/data_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/market/overview": {
      "get": {
        "tags": [
          "Data Service"
        ],
        "summary": "Get Market Overview",
        "description": "获取市场概览",
        "operationId": "get_market_overview_api_market_overview_get",
        "parameters": [
          {
            "name": "date",
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
              "description": "交易日期 YYYY-MM-DD，不传则使用最近交易日",
              "title": "Date"
            },
            "description": "交易日期 YYYY-MM-DD，不传则使用最近交易日"
          }
        ],
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
                  "$ref": "#/components/schemas/data_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/etf/list": {
      "get": {
        "tags": [
          "Data Service"
        ],
        "summary": "Get Etf List",
        "description": "获取 ETF 候选池",
        "operationId": "get_etf_list_api_etf_list_get",
        "parameters": [
          {
            "name": "date",
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
              "description": "交易日期 YYYY-MM-DD，不传则使用最近交易日",
              "title": "Date"
            },
            "description": "交易日期 YYYY-MM-DD，不传则使用最近交易日"
          },
          {
            "name": "limit",
            "in": "query",
            "required": false,
            "schema": {
              "type": "integer",
              "maximum": 500,
              "minimum": 1,
              "description": "返回数量限制",
              "default": 50,
              "title": "Limit"
            },
            "description": "返回数量限制"
          }
        ],
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
                  "$ref": "#/components/schemas/data_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/stock/list": {
      "get": {
        "tags": [
          "Data Service"
        ],
        "summary": "Get Stock List",
        "description": "获取股票候选池",
        "operationId": "get_stock_list_api_stock_list_get",
        "parameters": [
          {
            "name": "date",
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
              "description": "交易日期 YYYY-MM-DD，不传则使用最近交易日",
              "title": "Date"
            },
            "description": "交易日期 YYYY-MM-DD，不传则使用最近交易日"
          },
          {
            "name": "limit",
            "in": "query",
            "required": false,
            "schema": {
              "type": "integer",
              "maximum": 1000,
              "minimum": 1,
              "description": "返回数量限制",
              "default": 100,
              "title": "Limit"
            },
            "description": "返回数量限制"
          },
          {
            "name": "min_turnover",
            "in": "query",
            "required": false,
            "schema": {
              "type": "number",
              "minimum": 0,
              "description": "最小成交额过滤（元）",
              "default": 0,
              "title": "Min Turnover"
            },
            "description": "最小成交额过滤（元）"
          }
        ],
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
                  "$ref": "#/components/schemas/data_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/fundamentals/batch": {
      "post": {
        "tags": [
          "Data Service"
        ],
        "summary": "Get Fundamentals Batch",
        "description": "批量获取股票基本面数据\n\n返回：行业、上市日期、是否ST、市值、估值（PE/PB）、财务指标等",
        "operationId": "get_fundamentals_batch_api_fundamentals_batch_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/data_FundamentalsRequest"
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
                  "$ref": "#/components/schemas/data_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/fundamentals/industry/rank": {
      "get": {
        "tags": [
          "Data Service"
        ],
        "summary": "Get Industry Rank",
        "description": "获取行业景气度排名\n\n基于行业内股票的平均财务增长率（净利润yoy、营收yoy、ROE yoy）计算\n\n注意：如果数据库没有数据且 auto_calculate=False，会返回空列表。\n建议通过定时任务预热数据，而非通过接口触发实时计算（需 10-15 分钟）",
        "operationId": "get_industry_rank_api_fundamentals_industry_rank_get",
        "parameters": [
          {
            "name": "month",
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
              "description": "月份 YYYY-MM，不传则使用最近月",
              "title": "Month"
            },
            "description": "月份 YYYY-MM，不传则使用最近月"
          },
          {
            "name": "auto_calculate",
            "in": "query",
            "required": false,
            "schema": {
              "type": "boolean",
              "description": "如果数据库没有数据，是否自动计算（默认否，避免超时）",
              "default": false,
              "title": "Auto Calculate"
            },
            "description": "如果数据库没有数据，是否自动计算（默认否，避免超时）"
          }
        ],
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
                  "$ref": "#/components/schemas/data_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/fundamentals/sentiment/score": {
      "post": {
        "tags": [
          "Data Service"
        ],
        "summary": "Get Sentiment Scores",
        "description": "获取舆情评分\n\n基于同花顺热度、龙虎榜、资金流向综合计算",
        "operationId": "get_sentiment_scores_api_fundamentals_sentiment_score_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/data_SentimentRequest"
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
                  "$ref": "#/components/schemas/data_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/fundamentals/hot/score": {
      "post": {
        "tags": [
          "Data Service"
        ],
        "summary": "Get Hot Scores",
        "description": "获取热点/主线分数\n\n基于涨跌停统计、概念板块、龙虎榜综合计算",
        "operationId": "get_hot_scores_api_fundamentals_hot_score_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/data_HotScoreRequest"
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
                  "$ref": "#/components/schemas/data_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/backtest/run": {
      "post": {
        "tags": [
          "Quant Engine"
        ],
        "summary": "异步执行回测（后台任务)",
        "description": "提交回测任务到后台执行，立即返回 backtest_id，客户端轮询状态。",
        "operationId": "run_backtest_api_backtest_run_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/quant_BacktestRequest"
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
                  "$ref": "#/components/schemas/quant_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/backtest/{backtest_id}": {
      "get": {
        "tags": [
          "Quant Engine"
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

                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/quant_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/backtest": {
      "get": {
        "tags": [
          "Quant Engine"
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

                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/quant_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/backtest/run_async": {
      "post": {
        "tags": [
          "Quant Engine"
        ],
        "summary": "兼容：异步提交回测（后台执行）",
        "operationId": "run_backtest_async_api_backtest_run_async_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/quant_BacktestRequest"
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
                  "$ref": "#/components/schemas/quant_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/backtest/run_sync": {
      "post": {
        "tags": [
          "Quant Engine"
        ],
        "summary": "同步执行回测（task-service worker 调用）",
        "operationId": "run_backtest_sync_api_backtest_run_sync_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/quant_BacktestExecuteRequest"
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
                  "$ref": "#/components/schemas/quant_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/strategy": {
      "post": {
        "tags": [
          "Quant Engine"
        ],
        "summary": "创建策略",
        "description": "创建新的量化策略\n\n策略代码应为 Python 代码，通常继承 backtrader.Strategy",
        "operationId": "create_strategy_api_strategy_post",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/quant_StrategyCreateRequest"
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
                  "$ref": "#/components/schemas/quant_StrategyResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/quant_HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "get": {
        "tags": [
          "Quant Engine"
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
                  "$ref": "#/components/schemas/quant_StrategyListResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/quant_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/strategy/{strategy_id}": {
      "get": {
        "tags": [
          "Quant Engine"
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
                  "$ref": "#/components/schemas/quant_StrategyResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/quant_HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "put": {
        "tags": [
          "Quant Engine"
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
                "$ref": "#/components/schemas/quant_StrategyUpdateRequest"
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
                  "$ref": "#/components/schemas/quant_StrategyResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/quant_HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "delete": {
        "tags": [
          "Quant Engine"
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
                  "$ref": "#/components/schemas/quant_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/strategy/validate": {
      "post": {
        "tags": [
          "Quant Engine"
        ],
        "summary": "验证策略代码",
        "description": "验证策略代码\n\n检查：\n- Python 语法\n- 必要的类和方法\n- 潜在的安全问题",
        "operationId": "validate_strategy_api_strategy_validate_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/quant_StrategyValidateRequest"
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
                  "$ref": "#/components/schemas/quant_StrategyValidateResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/quant_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/factor": {
      "post": {
        "tags": [
          "Quant Engine"
        ],
        "summary": "创建因子",
        "description": "创建新的量化因子\n\n因子类别：\n- technical: 技术指标\n- fundamental: 基本面因子\n- macro: 宏观因子",
        "operationId": "create_factor_api_factor_post",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/quant_FactorCreateRequest"
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
                  "$ref": "#/components/schemas/quant_FactorResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/quant_HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "get": {
        "tags": [
          "Quant Engine"
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
                  "$ref": "#/components/schemas/quant_FactorListResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/quant_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/factor/{factor_id}": {
      "get": {
        "tags": [
          "Quant Engine"
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
                  "$ref": "#/components/schemas/quant_FactorResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/quant_HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "put": {
        "tags": [
          "Quant Engine"
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
                "$ref": "#/components/schemas/quant_FactorUpdateRequest"
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
                  "$ref": "#/components/schemas/quant_FactorResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/quant_HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "delete": {
        "tags": [
          "Quant Engine"
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
                  "$ref": "#/components/schemas/quant_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/factor/calculate": {
      "post": {
        "tags": [
          "Quant Engine"
        ],
        "summary": "计算因子值",
        "description": "计算指定因子在给定时间范围内的值\n\n返回时间序列数据，可用于策略分析和可视化",
        "operationId": "calculate_factor_api_factor_calculate_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/quant_FactorCalculateRequest"
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
                  "$ref": "#/components/schemas/quant_FactorCalculateResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/quant_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/report": {
      "post": {
        "tags": [
          "Daily Report"
        ],
        "summary": "创建日报",
        "description": "创建新的日报\n\n支持创建日报、周报、月报",
        "operationId": "create_report_api_report_post",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/report_ReportCreateRequest"
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
                  "$ref": "#/components/schemas/report_ReportResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/report_HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "get": {
        "tags": [
          "Daily Report"
        ],
        "summary": "列出日报",
        "description": "列出所有日报\n\n支持按类型、状态、日期过滤和分页",
        "operationId": "list_reports_api_report_get",
        "parameters": [
          {
            "name": "report_type",
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
              "title": "Report Type"
            }
          },
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
            "name": "report_date",
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
              "title": "Report Date"
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
                  "$ref": "#/components/schemas/report_ReportListResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/report_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/report/{report_id}": {
      "get": {
        "tags": [
          "Daily Report"
        ],
        "summary": "获取日报",
        "description": "获取指定日报的详细信息",
        "operationId": "get_report_api_report__report_id__get",
        "parameters": [
          {
            "name": "report_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "title": "Report Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/report_ReportResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/report_HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "put": {
        "tags": [
          "Daily Report"
        ],
        "summary": "更新日报",
        "description": "更新日报信息",
        "operationId": "update_report_api_report__report_id__put",
        "parameters": [
          {
            "name": "report_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "title": "Report Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/report_ReportUpdateRequest"
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
                  "$ref": "#/components/schemas/report_ReportResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/report_HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "delete": {
        "tags": [
          "Daily Report"
        ],
        "summary": "删除日报",
        "description": "删除日报",
        "operationId": "delete_report_api_report__report_id__delete",
        "parameters": [
          {
            "name": "report_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "title": "Report Id"
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
                  "title": "Response Delete Report Api Report  Report Id  Delete"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/report_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/report/summaries/list": {
      "get": {
        "tags": [
          "Daily Report"
        ],
        "summary": "获取日报摘要列表",
        "description": "获取日报摘要列表（不包含完整内容）\n\n适用于列表展示场景，性能更优",
        "operationId": "get_report_summaries_api_report_summaries_list_get",
        "parameters": [
          {
            "name": "report_type",
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
              "title": "Report Type"
            }
          },
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
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/report_ReportSummaryResponse"
                  },
                  "title": "Response Get Report Summaries Api Report Summaries List Get"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/report_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/report/{report_id}/publish": {
      "post": {
        "tags": [
          "Daily Report"
        ],
        "summary": "发布日报",
        "description": "发布日报\n\n将状态从 draft 改为 published",
        "operationId": "publish_report_api_report__report_id__publish_post",
        "parameters": [
          {
            "name": "report_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "title": "Report Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/report_ReportResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/report_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/report/{report_id}/archive": {
      "post": {
        "tags": [
          "Daily Report"
        ],
        "summary": "归档日报",
        "description": "归档日报\n\n将状态改为 archived",
        "operationId": "archive_report_api_report__report_id__archive_post",
        "parameters": [
          {
            "name": "report_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "title": "Report Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/report_ReportResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/report_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/daily-report/generate": {
      "post": {
        "tags": [
          "Daily Report"
        ],
        "summary": "手动触发生成每日投资方案",
        "description": "手动触发生成每日投资方案\n\n- 如果不提供 report_date，则使用今日日期\n- 如果 force=True，即使已存在也会重新生成",
        "operationId": "generate_report_api_daily_report_generate_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/report_GenerateReportRequest"
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
                  "$ref": "#/components/schemas/report_DailyReportResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/report_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/daily-report/latest": {
      "get": {
        "tags": [
          "Daily Report"
        ],
        "summary": "获取最新的投资方案",
        "description": "获取最新的投资方案",
        "operationId": "get_latest_report_api_daily_report_latest_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/report_DailyReportResponse"
                }
              }
            }
          }
        }
      }
    },
    "/api/daily-report/date/{report_date}": {
      "get": {
        "tags": [
          "Daily Report"
        ],
        "summary": "根据日期获取投资方案",
        "description": "根据日期获取投资方案\n\n- report_date: 日期格式 YYYY-MM-DD",
        "operationId": "get_report_by_date_api_daily_report_date__report_date__get",
        "parameters": [
          {
            "name": "report_date",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "title": "Report Date"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/report_DailyReportResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/report_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/daily-report/{report_id}": {
      "get": {
        "tags": [
          "Daily Report"
        ],
        "summary": "根据ID获取投资方案",
        "description": "根据ID获取投资方案详情",
        "operationId": "get_report_api_daily_report__report_id__get",
        "parameters": [
          {
            "name": "report_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "title": "Report Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/report_DailyReportResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/report_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/daily-report": {
      "get": {
        "tags": [
          "Daily Report"
        ],
        "summary": "列出所有投资方案",
        "description": "列出所有投资方案\n\n- 支持分页（limit, offset）\n- 支持按状态过滤（status: draft/published/archived）",
        "operationId": "list_reports_api_daily_report_get",
        "parameters": [
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
          },
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
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/report_DailyReportListResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/report_HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/api/tasks": {
      "post": {
        "summary": "Create Task",
        "operationId": "create_task_api_tasks_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/task_CreateTaskRequest"
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
                  "$ref": "#/components/schemas/task_HTTPValidationError"
                }
              }
            }
          }
        },
        "tags": [
          "Task Service"
        ]
      }
    },
    "/api/tasks/{task_id}": {
      "get": {
        "summary": "Get Task",
        "operationId": "get_task_api_tasks__task_id__get",
        "parameters": [
          {
            "name": "task_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "title": "Task Id"
            }
          }
        ],
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
                  "$ref": "#/components/schemas/task_HTTPValidationError"
                }
              }
            }
          }
        },
        "tags": [
          "Task Service"
        ]
      }
    },
    "/healthz": {
      "get": {
        "summary": "Healthz",
        "operationId": "healthz_healthz_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {

                }
              }
            }
          }
        },
        "tags": [
          "Task Service"
        ]
      }
    },
    "/api/tokens/balance": {
      "get": {
        "tags": [
          "User Service"
        ],
        "summary": "Get Balance",
        "description": "获取当前用户的 AI Token 余额\n\n- admin 用户虽然返回 ai_tokens 值，但实际上没有限制",
        "operationId": "get_balance_api_tokens_balance_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/user_routers__ai_tokens__Envelope"
                }
              }
            }
          }
        },
        "security": [
          {
            "OAuth2PasswordBearer": []
          }
        ]
      }
    },
    "/api/tokens/consume": {
      "post": {
        "tags": [
          "User Service"
        ],
        "summary": "Consume Tokens",
        "description": "扣减用户 AI Token\n\n- admin 用户不检查、不扣减，直接返回成功\n- 普通用户检查余额，余额不足返回 402 错误\n- 使用数据库原子更新保证并发安全",
        "operationId": "consume_tokens_api_tokens_consume_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/user_ConsumeRequest"
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
                  "$ref": "#/components/schemas/user_routers__ai_tokens__Envelope"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/user_HTTPValidationError"
                }
              }
            }
          }
        },
        "security": [
          {
            "OAuth2PasswordBearer": []
          }
        ]
      }
    }
  },
  "components": {
    "schemas": {
      "Body_login_api_auth_login_post": {
        "properties": {
          "grant_type": {
            "anyOf": [
              {
                "type": "string",
                "pattern": "password"
              },
              {
                "type": "null"
              }
            ],
            "title": "Grant Type"
          },
          "username": {
            "type": "string",
            "title": "Username"
          },
          "password": {
            "type": "string",
            "title": "Password"
          },
          "scope": {
            "type": "string",
            "title": "Scope",
            "default": ""
          },
          "client_id": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Client Id"
          },
          "client_secret": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Client Secret"
          }
        },
        "type": "object",
        "required": [
          "username",
          "password"
        ],
        "title": "Body_login_api_auth_login_post"
      },
      "HTTPValidationError": {
        "properties": {
          "detail": {
            "items": {
              "$ref": "#/components/schemas/ValidationError"
            },
            "type": "array",
            "title": "Detail"
          }
        },
        "type": "object",
        "title": "HTTPValidationError"
      },
      "LoginRequest": {
        "properties": {
          "username": {
            "type": "string",
            "title": "Username"
          },
          "password": {
            "type": "string",
            "title": "Password"
          }
        },
        "type": "object",
        "required": [
          "username",
          "password"
        ],
        "title": "LoginRequest",
        "description": "登录请求"
      },
      "ServiceHealth": {
        "properties": {
          "service_name": {
            "type": "string",
            "title": "Service Name"
          },
          "status": {
            "type": "string",
            "title": "Status"
          },
          "url": {
            "type": "string",
            "title": "Url"
          },
          "response_time_ms": {
            "anyOf": [
              {
                "type": "number"
              },
              {
                "type": "null"
              }
            ],
            "title": "Response Time Ms"
          },
          "error": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Error"
          }
        },
        "type": "object",
        "required": [
          "service_name",
          "status",
          "url"
        ],
        "title": "ServiceHealth",
        "description": "服务健康状态"
      },
      "UserCreateRequest": {
        "properties": {
          "username": {
            "type": "string",
            "title": "Username"
          },
          "password": {
            "type": "string",
            "title": "Password"
          },
          "role": {
            "type": "string",
            "title": "Role",
            "default": "user"
          }
        },
        "type": "object",
        "required": [
          "username",
          "password"
        ],
        "title": "UserCreateRequest",
        "description": "创建用户请求"
      },
      "UserUpdateRequest": {
        "properties": {
          "password": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Password"
          },
          "role": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Role"
          }
        },
        "type": "object",
        "title": "UserUpdateRequest",
        "description": "更新用户请求"
      },
      "ValidationError": {
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
      "ai_ApiResponse_SummaryGenerationResponse_": {
        "properties": {
          "code": {
            "type": "integer",
            "title": "Code",
            "default": 0
          },
          "message": {
            "type": "string",
            "title": "Message",
            "default": "ok"
          },
          "data": {
            "anyOf": [
              {
                "$ref": "#/components/schemas/ai_SummaryGenerationResponse"
              },
              {
                "type": "null"
              }
            ]
          }
        },
        "type": "object",
        "title": "ApiResponse[SummaryGenerationResponse]"
      },
      "ai_ChatRequest": {
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
                "$ref": "#/components/schemas/ai_ModelType"
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
      "ai_ChatResponse": {
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
      "ai_DigitalHumanRequest": {
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
      "ai_HTTPValidationError": {
        "properties": {
          "detail": {
            "items": {
              "$ref": "#/components/schemas/ai_ValidationError"
            },
            "type": "array",
            "title": "Detail"
          }
        },
        "type": "object",
        "title": "HTTPValidationError"
      },
      "ai_ModelRouteRequest": {
        "properties": {
          "task_type": {
            "$ref": "#/components/schemas/ai_TaskType"
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
      "ai_ModelRouteResponse": {
        "properties": {
          "recommended_model": {
            "$ref": "#/components/schemas/ai_ModelType",
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
      "ai_ModelType": {
        "type": "string",
        "enum": [
          "deepseek",
          "qwen",
          "openai"
        ],
        "title": "ModelType",
        "description": "支持的 AI 模型类型"
      },
      "ai_NewsGenerationRequest": {
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
                "$ref": "#/components/schemas/ai_ModelType"
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
      "ai_NewsGenerationResponse": {
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
      "ai_ReportGenerationRequest": {
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
      "ai_ReportGenerationResponse": {
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
          "report_content",
          "model"
        ],
        "title": "ReportGenerationResponse",
        "description": "报告生成响应"
      },
      "ai_StrategyGenerationRequest": {
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
                "$ref": "#/components/schemas/ai_ModelType"
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
      "ai_StrategyGenerationResponse": {
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
      "ai_SummaryGenerationRequest": {
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
                "$ref": "#/components/schemas/ai_ModelType"
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
      "ai_SummaryGenerationResponse": {
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
      "ai_TaskType": {
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
      "ai_ValidationError": {
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
      "data_CleanRequest": {
        "properties": {
          "source": {
            "type": "string",
            "title": "Source",
            "description": "Data source identifier"
          },
          "content": {
            "type": "string",
            "title": "Content",
            "description": "Raw text content"
          },
          "tags": {
            "items": {
              "type": "string"
            },
            "type": "array",
            "title": "Tags",
            "description": "Optional tags"
          }
        },
        "type": "object",
        "required": [
          "source",
          "content"
        ],
        "title": "CleanRequest"
      },
      "data_CleanResponse": {
        "properties": {
          "source": {
            "type": "string",
            "title": "Source",
            "description": "Data source identifier"
          },
          "content": {
            "type": "string",
            "title": "Content",
            "description": "Raw text content"
          },
          "tags": {
            "items": {
              "type": "string"
            },
            "type": "array",
            "title": "Tags",
            "description": "Optional tags"
          },
          "summary": {
            "type": "string",
            "title": "Summary",
            "description": "Human readable summary"
          }
        },
        "type": "object",
        "required": [
          "source",
          "content",
          "summary"
        ],
        "title": "CleanResponse"
      },
      "data_DailyQuoteItem": {
        "properties": {
          "code": {
            "type": "string",
            "title": "Code",
            "description": "股票代码（6位）"
          },
          "trade_date": {
            "type": "string",
            "title": "Trade Date",
            "description": "交易日期 YYYYMMDD"
          },
          "open": {
            "type": "number",
            "title": "Open",
            "description": "开盘价"
          },
          "high": {
            "type": "number",
            "title": "High",
            "description": "最高价"
          },
          "low": {
            "type": "number",
            "title": "Low",
            "description": "最低价"
          },
          "close": {
            "type": "number",
            "title": "Close",
            "description": "收盘价"
          },
          "vol": {
            "type": "integer",
            "title": "Vol",
            "description": "成交量（手）"
          },
          "amount": {
            "type": "number",
            "title": "Amount",
            "description": "成交额（元）"
          }
        },
        "type": "object",
        "required": [
          "code",
          "trade_date",
          "open",
          "high",
          "low",
          "close",
          "vol",
          "amount"
        ],
        "title": "DailyQuoteItem",
        "description": "日线行情数据项"
      },
      "data_DailyQuoteRequest": {
        "properties": {
          "codes": {
            "items": {
              "type": "string"
            },
            "type": "array",
            "maxItems": 100,
            "minItems": 1,
            "title": "Codes",
            "description": "股票代码列表"
          },
          "start_date": {
            "type": "string",
            "title": "Start Date",
            "description": "开始日期 YYYYMMDD"
          },
          "end_date": {
            "type": "string",
            "title": "End Date",
            "description": "结束日期 YYYYMMDD"
          }
        },
        "type": "object",
        "required": [
          "codes",
          "start_date",
          "end_date"
        ],
        "title": "DailyQuoteRequest",
        "description": "日线行情请求"
      },
      "data_DailyQuoteResponse": {
        "properties": {
          "data": {
            "items": {
              "$ref": "#/components/schemas/data_DailyQuoteItem"
            },
            "type": "array",
            "title": "Data",
            "description": "行情数据列表"
          },
          "success_codes": {
            "items": {
              "type": "string"
            },
            "type": "array",
            "title": "Success Codes",
            "description": "成功获取的股票代码"
          },
          "failed_codes": {
            "items": {
              "type": "string"
            },
            "type": "array",
            "title": "Failed Codes",
            "description": "获取失败的股票代码"
          }
        },
        "type": "object",
        "title": "DailyQuoteResponse",
        "description": "日线行情响应"
      },
      "data_FundamentalsRequest": {
        "properties": {
          "codes": {
            "items": {
              "type": "string"
            },
            "type": "array",
            "maxItems": 100,
            "minItems": 1,
            "title": "Codes",
            "description": "股票代码列表（6位）"
          },
          "trade_date": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Trade Date",
            "description": "交易日期 YYYYMMDD，不传则使用最近日期"
          }
        },
        "type": "object",
        "required": [
          "codes"
        ],
        "title": "FundamentalsRequest",
        "description": "基本面批量请求"
      },
      "data_HTTPValidationError": {
        "properties": {
          "detail": {
            "items": {
              "$ref": "#/components/schemas/data_ValidationError"
            },
            "type": "array",
            "title": "Detail"
          }
        },
        "type": "object",
        "title": "HTTPValidationError"
      },
      "data_HotScoreRequest": {
        "properties": {
          "codes": {
            "items": {
              "type": "string"
            },
            "type": "array",
            "maxItems": 100,
            "minItems": 1,
            "title": "Codes",
            "description": "股票代码列表"
          }
        },
        "type": "object",
        "required": [
          "codes"
        ],
        "title": "HotScoreRequest",
        "description": "热点分数请求"
      },
      "data_QuoteItem": {
        "properties": {
          "code": {
            "type": "string",
            "title": "Code",
            "description": "股票代码"
          },
          "name": {
            "type": "string",
            "title": "Name",
            "description": "股票名称"
          },
          "price": {
            "type": "number",
            "title": "Price",
            "description": "最新价"
          },
          "pct_change": {
            "type": "number",
            "title": "Pct Change",
            "description": "涨跌幅（百分比）"
          },
          "turnover": {
            "type": "number",
            "title": "Turnover",
            "description": "成交额（元）"
          },
          "update_time": {
            "type": "string",
            "format": "date-time",
            "title": "Update Time",
            "description": "更新时间"
          }
        },
        "type": "object",
        "required": [
          "code",
          "name",
          "price",
          "pct_change",
          "turnover",
          "update_time"
        ],
        "title": "QuoteItem",
        "description": "行情数据项"
      },
      "data_RealtimeQuoteRequest": {
        "properties": {
          "codes": {
            "items": {
              "type": "string"
            },
            "type": "array",
            "maxItems": 100,
            "minItems": 1,
            "title": "Codes",
            "description": "股票代码列表"
          }
        },
        "type": "object",
        "required": [
          "codes"
        ],
        "title": "RealtimeQuoteRequest",
        "description": "实时行情请求"
      },
      "data_RealtimeQuoteResponse": {
        "properties": {
          "data": {
            "items": {
              "$ref": "#/components/schemas/data_QuoteItem"
            },
            "type": "array",
            "title": "Data",
            "description": "行情数据列表"
          },
          "success_codes": {
            "items": {
              "type": "string"
            },
            "type": "array",
            "title": "Success Codes",
            "description": "成功获取的股票代码"
          },
          "failed_codes": {
            "items": {
              "type": "string"
            },
            "type": "array",
            "title": "Failed Codes",
            "description": "获取失败的股票代码"
          }
        },
        "type": "object",
        "required": [
          "data"
        ],
        "title": "RealtimeQuoteResponse",
        "description": "实时行情响应"
      },
      "data_SentimentRequest": {
        "properties": {
          "codes": {
            "items": {
              "type": "string"
            },
            "type": "array",
            "maxItems": 100,
            "minItems": 1,
            "title": "Codes",
            "description": "股票代码列表"
          },
          "start_date": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Start Date",
            "description": "开始日期 YYYYMMDD"
          },
          "end_date": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "End Date",
            "description": "结束日期 YYYYMMDD"
          }
        },
        "type": "object",
        "required": [
          "codes"
        ],
        "title": "SentimentRequest",
        "description": "舆情评分请求"
      },
      "data_StockBasicResponse": {
        "properties": {
          "data": {
            "items": {
              "additionalProperties": true,
              "type": "object"
            },
            "type": "array",
            "title": "Data",
            "description": "股票基础信息列表"
          }
        },
        "type": "object",
        "title": "StockBasicResponse",
        "description": "股票基础信息响应"
      },
      "data_ValidationError": {
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
      "quant_BacktestExecuteRequest": {
        "properties": {
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
            "description": "股票代码（如：000001），单标的时必填"
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
          "symbols": {
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
            "title": "Symbols",
            "description": "多标的列表（如：['000001','600000']）"
          },
          "rebalance_frequency": {
            "type": "string",
            "enum": [
              "D",
              "W",
              "M"
            ],
            "title": "Rebalance Frequency",
            "description": "再平衡频率：D/W/M",
            "default": "M"
          },
          "allocation": {
            "type": "string",
            "enum": [
              "equal_weight",
              "inverse_vol"
            ],
            "title": "Allocation",
            "description": "权重分配方式",
            "default": "equal_weight"
          },
          "allow_short": {
            "type": "boolean",
            "title": "Allow Short",
            "description": "是否允许做空",
            "default": false
          },
          "universe_mode": {
            "type": "string",
            "enum": [
              "manual",
              "stock_pool",
              "stock_etf_pool"
            ],
            "title": "Universe Mode",
            "description": "股票池模式: manual/stock_pool/stock_etf_pool",
            "default": "manual"
          },
          "universe_params": {
            "additionalProperties": true,
            "type": "object",
            "title": "Universe Params",
            "description": "股票池参数（如 limit, min_turnover, stock_limit, etf_limit）"
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
          },
          "backtest_id": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Backtest Id",
            "description": "回测ID，可由上游指定"
          },
          "task_id": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Task Id",
            "description": "task-service 的任务ID，便于链路追踪"
          }
        },
        "type": "object",
        "required": [
          "start_date",
          "end_date"
        ],
        "title": "BacktestExecuteRequest",
        "description": "供 task-service worker 调用的同步执行请求"
      },
      "quant_BacktestRequest": {
        "properties": {
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
            "description": "股票代码（如：000001），单标的时必填"
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
          "symbols": {
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
            "title": "Symbols",
            "description": "多标的列表（如：['000001','600000']）"
          },
          "rebalance_frequency": {
            "type": "string",
            "enum": [
              "D",
              "W",
              "M"
            ],
            "title": "Rebalance Frequency",
            "description": "再平衡频率：D/W/M",
            "default": "M"
          },
          "allocation": {
            "type": "string",
            "enum": [
              "equal_weight",
              "inverse_vol"
            ],
            "title": "Allocation",
            "description": "权重分配方式",
            "default": "equal_weight"
          },
          "allow_short": {
            "type": "boolean",
            "title": "Allow Short",
            "description": "是否允许做空",
            "default": false
          },
          "universe_mode": {
            "type": "string",
            "enum": [
              "manual",
              "stock_pool",
              "stock_etf_pool"
            ],
            "title": "Universe Mode",
            "description": "股票池模式: manual/stock_pool/stock_etf_pool",
            "default": "manual"
          },
          "universe_params": {
            "additionalProperties": true,
            "type": "object",
            "title": "Universe Params",
            "description": "股票池参数（如 limit, min_turnover, stock_limit, etf_limit）"
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
          "start_date",
          "end_date"
        ],
        "title": "BacktestRequest",
        "description": "回测请求"
      },
      "quant_FactorCalculateRequest": {
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
      "quant_FactorCalculateResponse": {
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
      "quant_FactorCreateRequest": {
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
          "expression": {
            "type": "string",
            "minLength": 1,
            "title": "Expression",
            "description": "因子表达式/公式"
          },
          "data_source": {
            "type": "string",
            "title": "Data Source",
            "description": "数据来源：price/fundamental/tdengine",
            "default": "price"
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
            "description": "因子类别（兼容旧字段）"
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
            "description": "兼容旧字段：因子公式"
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
          "name",
          "expression"
        ],
        "title": "FactorCreateRequest",
        "description": "创建因子请求"
      },
      "quant_FactorListResponse": {
        "properties": {
          "total": {
            "type": "integer",
            "title": "Total",
            "description": "总数"
          },
          "factors": {
            "items": {
              "$ref": "#/components/schemas/quant_FactorResponse"
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
      "quant_FactorResponse": {
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
          "expression": {
            "type": "string",
            "title": "Expression",
            "description": "因子表达式/公式"
          },
          "data_source": {
            "type": "string",
            "title": "Data Source",
            "description": "数据来源"
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
            "description": "因子公式（兼容旧字段）"
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
          "expression",
          "data_source",
          "parameters",
          "created_at"
        ],
        "title": "FactorResponse",
        "description": "因子响应"
      },
      "quant_FactorUpdateRequest": {
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
          "expression": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Expression",
            "description": "因子表达式/公式"
          },
          "data_source": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Data Source",
            "description": "数据来源"
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
            "description": "因子公式（兼容旧字段）"
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
      "quant_HTTPValidationError": {
        "properties": {
          "detail": {
            "items": {
              "$ref": "#/components/schemas/quant_ValidationError"
            },
            "type": "array",
            "title": "Detail"
          }
        },
        "type": "object",
        "title": "HTTPValidationError"
      },
      "quant_StrategyCreateRequest": {
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
          "factor_ids": {
            "items": {
              "type": "string"
            },
            "type": "array",
            "minItems": 1,
            "title": "Factor Ids",
            "description": "关联的因子ID列表"
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
            "description": "策略状态：draft/active/archived",
            "default": "draft"
          }
        },
        "type": "object",
        "required": [
          "name",
          "code",
          "factor_ids"
        ],
        "title": "StrategyCreateRequest",
        "description": "创建策略请求"
      },
      "quant_StrategyListResponse": {
        "properties": {
          "total": {
            "type": "integer",
            "title": "Total",
            "description": "总数"
          },
          "strategies": {
            "items": {
              "$ref": "#/components/schemas/quant_StrategyResponse"
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
      "quant_StrategyResponse": {
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
          "factor_ids": {
            "items": {
              "type": "string"
            },
            "type": "array",
            "title": "Factor Ids",
            "description": "关联因子"
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
          "factor_ids",
          "parameters",
          "status",
          "created_at"
        ],
        "title": "StrategyResponse",
        "description": "策略响应"
      },
      "quant_StrategyUpdateRequest": {
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
          "factor_ids": {
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
            "title": "Factor Ids",
            "description": "关联的因子ID列表"
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
            "description": "状态：draft/active/archived"
          }
        },
        "type": "object",
        "title": "StrategyUpdateRequest",
        "description": "更新策略请求"
      },
      "quant_StrategyValidateRequest": {
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
      "quant_StrategyValidateResponse": {
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
      "quant_ValidationError": {
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
      "report_DailyReportListResponse": {
        "properties": {
          "total": {
            "type": "integer",
            "title": "Total",
            "description": "总数"
          },
          "reports": {
            "items": {
              "$ref": "#/components/schemas/report_DailyReportResponse"
            },
            "type": "array",
            "title": "Reports",
            "description": "报告列表"
          }
        },
        "type": "object",
        "required": [
          "total",
          "reports"
        ],
        "title": "DailyReportListResponse",
        "description": "每日投资方案列表响应"
      },
      "report_DailyReportResponse": {
        "properties": {
          "id": {
            "type": "string",
            "title": "Id",
            "description": "报告ID"
          },
          "report_date": {
            "type": "string",
            "title": "Report Date",
            "description": "报告日期"
          },
          "title": {
            "type": "string",
            "title": "Title",
            "description": "报告标题"
          },
          "status": {
            "type": "string",
            "title": "Status",
            "description": "状态"
          },
          "market_sentiment": {
            "type": "string",
            "title": "Market Sentiment",
            "description": "市场情绪总结"
          },
          "etf_recommendations": {
            "items": {
              "$ref": "#/components/schemas/report_ETFRecommendation"
            },
            "type": "array",
            "title": "Etf Recommendations",
            "description": "ETF 推荐"
          },
          "stock_recommendations": {
            "items": {
              "$ref": "#/components/schemas/report_StockRecommendation"
            },
            "type": "array",
            "title": "Stock Recommendations",
            "description": "股票推荐"
          },
          "risk_warning": {
            "type": "string",
            "title": "Risk Warning",
            "description": "风险提示"
          },
          "article_title": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Article Title",
            "description": "公众号文章标题"
          },
          "article_outline": {
            "anyOf": [
              {
                "additionalProperties": true,
                "type": "object"
              },
              {
                "type": "null"
              }
            ],
            "title": "Article Outline",
            "description": "公众号文章大纲"
          },
          "created_at": {
            "type": "string",
            "format": "date-time",
            "title": "Created At",
            "description": "创建时间"
          },
          "updated_at": {
            "anyOf": [
              {
                "type": "string",
                "format": "date-time"
              },
              {
                "type": "null"
              }
            ],
            "title": "Updated At",
            "description": "更新时间"
          },
          "generation_status": {
            "type": "string",
            "title": "Generation Status",
            "description": "生成状态"
          }
        },
        "type": "object",
        "required": [
          "id",
          "report_date",
          "title",
          "status",
          "market_sentiment",
          "etf_recommendations",
          "stock_recommendations",
          "risk_warning",
          "created_at",
          "generation_status"
        ],
        "title": "DailyReportResponse",
        "description": "每日投资方案响应"
      },
      "report_ETFRecommendation": {
        "properties": {
          "code": {
            "type": "string",
            "title": "Code",
            "description": "ETF 代码"
          },
          "name": {
            "type": "string",
            "title": "Name",
            "description": "ETF 名称"
          },
          "category": {
            "type": "string",
            "title": "Category",
            "description": "所属主题/行业"
          },
          "reasoning": {
            "type": "string",
            "maxLength": 500,
            "title": "Reasoning",
            "description": "推荐逻辑（结合市场风格、行业轮动、情绪）"
          }
        },
        "type": "object",
        "required": [
          "code",
          "name",
          "category",
          "reasoning"
        ],
        "title": "ETFRecommendation",
        "description": "ETF 推荐"
      },
      "report_GenerateReportRequest": {
        "properties": {
          "report_date": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Report Date",
            "description": "报告日期，不提供则使用今日"
          },
          "force": {
            "type": "boolean",
            "title": "Force",
            "description": "是否强制重新生成（如果已存在）",
            "default": false
          }
        },
        "type": "object",
        "title": "GenerateReportRequest",
        "description": "手动触发生成报告请求"
      },
      "report_HTTPValidationError": {
        "properties": {
          "detail": {
            "items": {
              "$ref": "#/components/schemas/report_ValidationError"
            },
            "type": "array",
            "title": "Detail"
          }
        },
        "type": "object",
        "title": "HTTPValidationError"
      },
      "report_ReportCreateRequest": {
        "properties": {
          "title": {
            "type": "string",
            "maxLength": 200,
            "minLength": 1,
            "title": "Title",
            "description": "日报标题"
          },
          "content": {
            "type": "string",
            "minLength": 1,
            "title": "Content",
            "description": "日报内容"
          },
          "report_date": {
            "type": "string",
            "title": "Report Date",
            "description": "报告日期 (YYYY-MM-DD)"
          },
          "report_type": {
            "type": "string",
            "title": "Report Type",
            "description": "报告类型：daily/weekly/monthly",
            "default": "daily"
          },
          "author": {
            "anyOf": [
              {
                "type": "string",
                "maxLength": 100
              },
              {
                "type": "null"
              }
            ],
            "title": "Author",
            "description": "作者"
          },
          "tags": {
            "items": {
              "type": "string"
            },
            "type": "array",
            "title": "Tags",
            "description": "标签列表"
          }
        },
        "type": "object",
        "required": [
          "title",
          "content",
          "report_date"
        ],
        "title": "ReportCreateRequest",
        "description": "创建日报请求"
      },
      "report_ReportListResponse": {
        "properties": {
          "total": {
            "type": "integer",
            "title": "Total",
            "description": "总数"
          },
          "reports": {
            "items": {
              "$ref": "#/components/schemas/report_ReportResponse"
            },
            "type": "array",
            "title": "Reports",
            "description": "日报列表"
          }
        },
        "type": "object",
        "required": [
          "total",
          "reports"
        ],
        "title": "ReportListResponse",
        "description": "日报列表响应"
      },
      "report_ReportResponse": {
        "properties": {
          "id": {
            "type": "string",
            "title": "Id",
            "description": "日报ID"
          },
          "title": {
            "type": "string",
            "title": "Title",
            "description": "日报标题"
          },
          "content": {
            "type": "string",
            "title": "Content",
            "description": "日报内容"
          },
          "report_date": {
            "type": "string",
            "title": "Report Date",
            "description": "报告日期"
          },
          "report_type": {
            "type": "string",
            "title": "Report Type",
            "description": "报告类型"
          },
          "status": {
            "type": "string",
            "title": "Status",
            "description": "状态"
          },
          "author": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Author",
            "description": "作者"
          },
          "tags": {
            "items": {
              "type": "string"
            },
            "type": "array",
            "title": "Tags",
            "description": "标签列表"
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
          "title",
          "content",
          "report_date",
          "report_type",
          "status",
          "tags",
          "created_at"
        ],
        "title": "ReportResponse",
        "description": "日报响应"
      },
      "report_ReportSummaryResponse": {
        "properties": {
          "id": {
            "type": "string",
            "title": "Id",
            "description": "日报ID"
          },
          "title": {
            "type": "string",
            "title": "Title",
            "description": "日报标题"
          },
          "report_date": {
            "type": "string",
            "title": "Report Date",
            "description": "报告日期"
          },
          "report_type": {
            "type": "string",
            "title": "Report Type",
            "description": "报告类型"
          },
          "status": {
            "type": "string",
            "title": "Status",
            "description": "状态"
          },
          "author": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Author",
            "description": "作者"
          },
          "tags": {
            "items": {
              "type": "string"
            },
            "type": "array",
            "title": "Tags",
            "description": "标签列表"
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
          "title",
          "report_date",
          "report_type",
          "status",
          "tags",
          "created_at"
        ],
        "title": "ReportSummaryResponse",
        "description": "日报摘要响应"
      },
      "report_ReportUpdateRequest": {
        "properties": {
          "title": {
            "anyOf": [
              {
                "type": "string",
                "maxLength": 200,
                "minLength": 1
              },
              {
                "type": "null"
              }
            ],
            "title": "Title",
            "description": "日报标题"
          },
          "content": {
            "anyOf": [
              {
                "type": "string",
                "minLength": 1
              },
              {
                "type": "null"
              }
            ],
            "title": "Content",
            "description": "日报内容"
          },
          "report_date": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Report Date",
            "description": "报告日期 (YYYY-MM-DD)"
          },
          "report_type": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Report Type",
            "description": "报告类型：daily/weekly/monthly"
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
            "description": "状态：draft/published/archived"
          },
          "author": {
            "anyOf": [
              {
                "type": "string",
                "maxLength": 100
              },
              {
                "type": "null"
              }
            ],
            "title": "Author",
            "description": "作者"
          },
          "tags": {
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
            "title": "Tags",
            "description": "标签列表"
          }
        },
        "type": "object",
        "title": "ReportUpdateRequest",
        "description": "更新日报请求"
      },
      "report_StockRecommendation": {
        "properties": {
          "code": {
            "type": "string",
            "title": "Code",
            "description": "股票代码"
          },
          "name": {
            "type": "string",
            "title": "Name",
            "description": "股票名称"
          },
          "factor_scores": {
            "additionalProperties": true,
            "type": "object",
            "title": "Factor Scores",
            "description": "多因子评分，如: {momentum: 8.5, liquidity: 7.2, sentiment: 6.8}"
          },
          "ai_analysis": {
            "type": "string",
            "maxLength": 80,
            "title": "Ai Analysis",
            "description": "AI 解读（不超过80字）"
          }
        },
        "type": "object",
        "required": [
          "code",
          "name",
          "factor_scores",
          "ai_analysis"
        ],
        "title": "StockRecommendation",
        "description": "股票推荐"
      },
      "report_ValidationError": {
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
      "task_CreateTaskRequest": {
        "properties": {
          "task_type": {
            "type": "string",
            "title": "Task Type"
          },
          "payload": {
            "anyOf": [
              {
                "additionalProperties": true,
                "type": "object"
              },
              {
                "type": "null"
              }
            ],
            "title": "Payload",
            "default": {

            }
          }
        },
        "type": "object",
        "required": [
          "task_type"
        ],
        "title": "CreateTaskRequest"
      },
      "task_HTTPValidationError": {
        "properties": {
          "detail": {
            "items": {
              "$ref": "#/components/schemas/task_ValidationError"
            },
            "type": "array",
            "title": "Detail"
          }
        },
        "type": "object",
        "title": "HTTPValidationError"
      },
      "task_ValidationError": {
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
      "user_Body_login_api_auth_login_post": {
        "properties": {
          "grant_type": {
            "anyOf": [
              {
                "type": "string",
                "pattern": "password"
              },
              {
                "type": "null"
              }
            ],
            "title": "Grant Type"
          },
          "username": {
            "type": "string",
            "title": "Username"
          },
          "password": {
            "type": "string",
            "title": "Password"
          },
          "scope": {
            "type": "string",
            "title": "Scope",
            "default": ""
          },
          "client_id": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Client Id"
          },
          "client_secret": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Client Secret"
          }
        },
        "type": "object",
        "required": [
          "username",
          "password"
        ],
        "title": "Body_login_api_auth_login_post"
      },
      "user_ConsumeRequest": {
        "properties": {
          "tokens": {
            "type": "integer",
            "exclusiveMinimum": 0,
            "title": "Tokens",
            "description": "要扣减的 token 数量"
          },
          "reason": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Reason",
            "description": "扣减原因"
          },
          "request_id": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Request Id",
            "description": "请求 ID（用于幂等）"
          }
        },
        "type": "object",
        "required": [
          "tokens"
        ],
        "title": "ConsumeRequest"
      },
      "user_HTTPValidationError": {
        "properties": {
          "detail": {
            "items": {
              "$ref": "#/components/schemas/user_ValidationError"
            },
            "type": "array",
            "title": "Detail"
          }
        },
        "type": "object",
        "title": "HTTPValidationError"
      },
      "user_LoginPayload": {
        "properties": {
          "username": {
            "type": "string",
            "title": "Username"
          },
          "password": {
            "type": "string",
            "title": "Password"
          }
        },
        "type": "object",
        "required": [
          "username",
          "password"
        ],
        "title": "LoginPayload"
      },
      "user_UserCreateRequest": {
        "properties": {
          "username": {
            "type": "string",
            "title": "Username"
          },
          "password": {
            "type": "string",
            "title": "Password"
          },
          "role": {
            "type": "string",
            "title": "Role",
            "default": "user"
          }
        },
        "type": "object",
        "required": [
          "username",
          "password"
        ],
        "title": "UserCreateRequest"
      },
      "user_UserUpdateRequest": {
        "properties": {
          "password": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Password"
          },
          "role": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Role"
          },
          "ai_tokens": {
            "anyOf": [
              {
                "type": "integer"
              },
              {
                "type": "null"
              }
            ],
            "title": "Ai Tokens"
          }
        },
        "type": "object",
        "title": "UserUpdateRequest"
      },
      "user_ValidationError": {
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
      "user_routers__admin__Envelope": {
        "properties": {
          "code": {
            "type": "integer",
            "title": "Code"
          },
          "message": {
            "type": "string",
            "title": "Message"
          },
          "data": {
            "anyOf": [
              {
                "additionalProperties": true,
                "type": "object"
              },
              {
                "items": {

                },
                "type": "array"
              }
            ],
            "title": "Data"
          }
        },
        "type": "object",
        "required": [
          "code",
          "message",
          "data"
        ],
        "title": "Envelope"
      },
      "user_routers__ai_tokens__Envelope": {
        "properties": {
          "code": {
            "type": "integer",
            "title": "Code"
          },
          "message": {
            "type": "string",
            "title": "Message"
          },
          "data": {
            "anyOf": [
              {
                "additionalProperties": true,
                "type": "object"
              },
              {
                "items": {

                },
                "type": "array"
              },
              {
                "type": "null"
              }
            ],
            "title": "Data"
          }
        },
        "type": "object",
        "required": [
          "code",
          "message",
          "data"
        ],
        "title": "Envelope"
      },
      "user_routers__auth__Envelope": {
        "properties": {
          "code": {
            "type": "integer",
            "title": "Code"
          },
          "message": {
            "type": "string",
            "title": "Message"
          },
          "data": {
            "additionalProperties": true,
            "type": "object",
            "title": "Data"
          }
        },
        "type": "object",
        "required": [
          "code",
          "message",
          "data"
        ],
        "title": "Envelope"
      }
    },
    "securitySchemes": {
      "OAuth2PasswordBearer": {
        "type": "oauth2",
        "flows": {
          "password": {
            "scopes": {

            },
            "tokenUrl": "/api/auth/login"
          }
        }
      }
    }
  },
  "security": [
    {
      "OAuth2PasswordBearer": []
    }
  ],
  "tags": [
    {
      "name": "AI Hub",
      "description": "AI Hub APIs"
    },
    {
      "name": "Data Service",
      "description": "Data Service APIs"
    },
    {
      "name": "Quant Engine",
      "description": "Quant Engine APIs"
    },
    {
      "name": "Daily Report",
      "description": "Daily Report APIs"
    },
    {
      "name": "Task Service",
      "description": "Task Service APIs"
    },
    {
      "name": "User Service",
      "description": "User Service APIs"
    }
  ]
}