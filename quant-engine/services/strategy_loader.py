"""策略加载服务 - 支持 custom 和 builtin 策略"""
import importlib.util
import sys
from pathlib import Path
from typing import Optional, Type

import backtrader as bt

from core.logger import get_logger

logger = get_logger(__name__)


def load_strategy(
    mode: str,
    strategy_code: Optional[str] = None,
    strategy_name: Optional[str] = None,
    parameters: Optional[dict] = None
) -> Type[bt.Strategy]:
    """
    加载策略类
    
    Args:
        mode: "custom" 或 "builtin"
        strategy_code: 自定义策略代码（mode=custom 时必填）
        strategy_name: 内置策略名称（mode=builtin 时必填）
        parameters: 策略参数
    
    Returns:
        Strategy 类（继承 bt.Strategy）
    """
    if mode == "custom":
        if not strategy_code:
            raise ValueError("custom 模式需要提供 strategy_code")
        return _load_custom_strategy(strategy_code, parameters)
    elif mode == "builtin":
        if not strategy_name:
            raise ValueError("builtin 模式需要提供 strategy_name")
        return _load_builtin_strategy(strategy_name, parameters)
    else:
        raise ValueError(f"不支持的策略模式: {mode}")


def _load_custom_strategy(
    strategy_code: str,
    parameters: Optional[dict] = None
) -> Type[bt.Strategy]:
    """
    加载自定义策略（AI 生成）
    
    使用 exec() 执行策略代码，不写文件、不访问网络
    """
    try:
        # 创建安全的执行环境
        exec_globals = {
            "__builtins__": __builtins__,
            "bt": bt,
            "Strategy": bt.Strategy,
            "Indicator": bt.Indicator,
        }
        
        # 如果提供了参数，注入到执行环境
        if parameters:
            exec_globals.update(parameters)
        
        # 执行策略代码
        exec(strategy_code, exec_globals)
        
        # 查找 Strategy 类
        strategy_class = None
        for name, obj in exec_globals.items():
            if (isinstance(obj, type) and 
                issubclass(obj, bt.Strategy) and 
                obj != bt.Strategy):
                strategy_class = obj
                break
        
        if not strategy_class:
            raise ValueError("策略代码中未找到继承 bt.Strategy 的类")
        
        logger.info(f"成功加载自定义策略: {strategy_class.__name__}")
        return strategy_class
        
    except SyntaxError as e:
        logger.error(f"策略代码语法错误: {e}")
        raise ValueError(f"策略代码语法错误: {e}")
    except Exception as e:
        logger.error(f"加载自定义策略失败: {e}")
        raise ValueError(f"加载策略失败: {e}")


def _load_builtin_strategy(
    strategy_name: str,
    parameters: Optional[dict] = None
) -> Type[bt.Strategy]:
    """
    加载内置策略
    
    从 strategies/ 目录加载策略模块
    """
    try:
        # 获取策略文件路径
        strategies_dir = Path(__file__).parent.parent / "strategies"
        strategy_file = strategies_dir / f"{strategy_name}.py"
        
        if not strategy_file.exists():
            available = [f.stem for f in strategies_dir.glob("*.py") if f.stem != "__init__"]
            raise ValueError(
                f"内置策略 '{strategy_name}' 不存在。"
                f"可用策略: {', '.join(available)}"
            )
        
        # 动态加载模块
        spec = importlib.util.spec_from_file_location(
            f"strategies.{strategy_name}",
            strategy_file
        )
        if spec is None or spec.loader is None:
            raise ValueError(f"无法加载策略模块: {strategy_name}")
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"strategies.{strategy_name}"] = module
        spec.loader.exec_module(module)
        
        # 查找 Strategy 类（通常命名为 Strategy 或与文件名相同）
        strategy_class = None
        for attr_name in [strategy_name.title().replace("_", ""), "Strategy"]:
            if hasattr(module, attr_name):
                obj = getattr(module, attr_name)
                if isinstance(obj, type) and issubclass(obj, bt.Strategy):
                    strategy_class = obj
                    break
        
        # 如果还没找到，遍历所有属性
        if not strategy_class:
            for name, obj in vars(module).items():
                if (isinstance(obj, type) and 
                    issubclass(obj, bt.Strategy) and 
                    obj != bt.Strategy):
                    strategy_class = obj
                    break
        
        if not strategy_class:
            raise ValueError(f"策略模块 '{strategy_name}' 中未找到 Strategy 类")
        
        # 如果提供了参数，创建参数化的策略类
        if parameters:
            class ParameterizedStrategy(strategy_class):
                params = tuple(parameters.items())
            
            ParameterizedStrategy.__name__ = strategy_class.__name__
            strategy_class = ParameterizedStrategy
        
        logger.info(f"成功加载内置策略: {strategy_name}")
        return strategy_class
        
    except Exception as e:
        logger.error(f"加载内置策略失败: {e}")
        raise ValueError(f"加载内置策略失败: {e}")
