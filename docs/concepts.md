# 本番パススルー設計の仕組み

niltest が本番環境でのパフォーマンスに一切影響を与えない理由を解説します。

---

## 1. `@scenario` デコレータはパススルーになる

Python のデコレータは**モジュールのインポート時に一度だけ**実行されます。  
`PRODUCTION=true` の状態でインポートすると、`@scenario` は関数をラップせず
**元の関数オブジェクトをそのまま返します**。

```python
def scenario(title: str):
    def decorator(func):
        if _config._PRODUCTION:
            return func          # ← 何もせずそのまま返す
        return _ScenarioWrapper(func, title)
    return decorator
```

結果として、本番環境では `process_payment` は niltest の存在を
**まったく知らないプレーンな関数と完全に同一**になります。

---

## 2. `if expect:` ブロックは真偽判定だけでスキップされる

`expect` は `Expect` クラスのシングルトンインスタンスです。  
`__bool__` メソッドが `_config._PRODUCTION` を参照して真偽値を返します。

```python
class Expect:
    def __bool__(self) -> bool:
        return not _config._PRODUCTION   # PRODUCTION=True なら False
```

本番環境では `if expect:` が `if False:` と等価になり、  
Python インタープリタはブロック内を**評価すら行わず完全にスキップ**します。  
`expect.case(...)` の辞書リテラルは生成されません。`bool(expect)` の呼び出しコストは残ります。

---

## 3. ベンチマーク

`python benchmark_production.py` で、プレーン関数との実測差を確認できます。値はCPU・OS・Pythonバージョンで変わるため固定値は保証しません。本番モードでデコレータのラッパーは作られず、差分は主に `if expect:` の真偽判定です。

---

## 4. なぜ AST 操作を使わないのか

コンパイル時に `if expect:` ブロックをソースコードから物理的に消去する  
AST 操作（Import Hook + AST rewrite）というアプローチも存在します。

しかし niltest では採用しません。理由は以下の通りです。

| 問題 | 内容 |
|---|---|
| デバッガの行番号ズレ | AST 変換後のバイトコードと元のソースコードの行番号がズレ、ブレークポイントが機能しなくなる |
| ツールチェーンの誤作動 | mypy・pytest・coverage.py などがコード構造の変化を検知して誤動作するリスクがある |
| 起動時オーバーヘッド | インポート時に全ソースコードを AST 解析するコストが発生する |

`bool(expect)` の評価は多くのアプリケーションで十分小さく、危険なハックを使わずに予測可能な挙動を保てます。性能要件が厳しい場合は同梱ベンチマークを対象環境で実行してください。
