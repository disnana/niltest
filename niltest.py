import os
import threading
import inspect
from typing import Any, Callable, Dict, Optional, TypeVar

# グローバル設定
_PRODUCTION = os.getenv("PRODUCTION", "false").lower() == "true"
_MODE = os.getenv("MODE", "MOCK").upper()  # MOCK, TEST, None

class MockReturnException(BaseException):
    """モック値を呼び出し元に返却するための特殊例外"""
    def __init__(self, value: Any):
        self.value = value

# スレッドセーフな実行状態管理
_local_state = threading.local()

class Expect:
    def __init__(self):
        self.current_cases = None

    def __bool__(self) -> bool:
        # 動的に本番フラグを参照して真偽値を判定
        return not _PRODUCTION

    def cases(self, mapping: Dict[str, Dict[str, Any]]):
        if _PRODUCTION:
            return

        # 先に定義情報を保持
        self.current_cases = mapping

        # 呼び出し元のフレーム情報を取得して、現在の引数とマッチングする
        state = getattr(_local_state, "current_call", None)
        if state is not None:
            func_name, actual_args, actual_kwargs = state
            
            # 各ケースと実際の引数をマッチング
            for case_name, case_data in mapping.items():
                matched = False
                
                # when 条件がある場合、実際の引数を渡して評価する
                if "when" in case_data:
                    when_func = case_data["when"]
                    if callable(when_func):
                        try:
                            # when 関数の引数定義に実引数をバインドして評価
                            sig = inspect.signature(when_func)
                            bound = sig.bind(*actual_args, **actual_kwargs)
                            bound.apply_defaults()
                            matched = bool(when_func(*bound.args, **bound.kwargs))
                        except Exception:
                            matched = False
                
                # when 条件がない場合は、args/kwargs の完全一致でフォールバック
                else:
                    target_args = case_data.get("args", ())
                    target_kwargs = case_data.get("kwargs", {})
                    matched = (actual_args == target_args and actual_kwargs == target_kwargs)
                
                if matched:
                    # MOCKモードなら、例外を発生させて関数の実行を中断し、戻り値を返却
                    if _MODE == "MOCK":
                        raise MockReturnException(case_data.get("returns"))

# シングルトン expect (インスタンスは常に同一に保つことで import 時の参照ズレを防ぐ)
expect = Expect()

def configure(production: Optional[bool] = None, mode: Optional[str] = None):
    """niltestの動作モードを設定します。"""
    global _PRODUCTION, _MODE
    if production is not None:
        _PRODUCTION = production
    if mode is not None:
        _MODE = mode.upper() if mode else None

F = TypeVar("F", bound=Callable[..., Any])

def scenario(title: str):
    """仕様検証可能な対象としてマークするデコレータ。本番環境ではパススルーされます。"""
    def decorator(func: F) -> F:
        if _PRODUCTION:
            return func

        # ラッパーの実装
        def wrapper(*args, **kwargs):
            # 呼び出しコンテキストをセット
            _local_state.current_call = (func.__name__, args, kwargs)
            try:
                # 実際に関数を実行
                result = func(*args, **kwargs)
                return result
            except MockReturnException as e:
                # モックモードでマッチした場合はモック値を返す
                return e.value
            finally:
                # コンテキストをクリア
                _local_state.current_call = None
                
                # 初回実行時に `expect.current_cases` からドックストリングを書き換える
                if expect.current_cases and not getattr(wrapper, "_doc_generated", False):
                    _generate_doc(wrapper, title, expect.current_cases)
                    wrapper._doc_generated = True
                    expect.current_cases = None

        # メタデータのコピー
        wrapper.__name__ = func.__name__
        wrapper.__module__ = func.__module__
        wrapper.__doc__ = func.__doc__ or ""
        wrapper.__annotations__ = func.__annotations__
        wrapper.__wrapped__ = func
        
        return wrapper
        
    return decorator

def _generate_doc(func_obj: Any, title: str, cases: Dict[str, Dict[str, Any]]):
    """仕様ケース一覧からドックストリングを美しく生成します。"""
    doc_lines = []
    if func_obj.__doc__:
        doc_lines.append(func_obj.__doc__.strip())
        doc_lines.append("")
    
    doc_lines.append(f"■ Scenario: {title}")
    doc_lines.append("-" * 40)
    for case_name, case_data in cases.items():
        doc_lines.append(f"● {case_name}")
        if "description" in case_data:
            doc_lines.append(f"  説明: {case_data['description']}")
        
        if "when" in case_data:
            when_func = case_data["when"]
            try:
                source = inspect.getsource(when_func).strip()
                source = " ".join(source.split())
                doc_lines.append(f"  条件: {source}")
            except Exception:
                doc_lines.append(f"  条件: <callable>")
        else:
            if "args" in case_data:
                doc_lines.append(f"  入力 (args): {case_data['args']}")
            if "kwargs" in case_data:
                doc_lines.append(f"  入力 (kwargs): {case_data['kwargs']}")
                
        doc_lines.append(f"  期待する出力: {case_data.get('returns')}")
        doc_lines.append("")
        
    func_obj.__doc__ = "\n".join(doc_lines)
