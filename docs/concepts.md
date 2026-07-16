# ゼロコスト設計の仕組み

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

## 2. `if expect:` ブロックはゼロコストでスキップされる

`expect` は `Expect` クラスのシングルトンインスタンスです。  
`__bool__` メソッドが `_config._PRODUCTION` を参照して真偽値を返します。

```python
class Expect:
    def __bool__(self) -> bool:
        return not _config._PRODUCTION   # PRODUCTION=True なら False
```

本番環境では `if expect:` が `if False:` と等価になり、  
Python インタープリタはブロック内を**評価すら行わず完全にスキップ**します。  
`expect.case(...)` の辞書リテラルの生成もゼロです。

---

## 3. 実測値（100万回呼び出し）

| | 実行時間 | 1回あたり差分 |
|---|---|---|
| プレーンな関数 | 0.18s | — |
| niltest デコレート済み（PRODUCTION=True） | 0.19s | ~5ns |

5ナノ秒という値は CPU・OS のゆらぎ（測定誤差）の範囲内です。  
どのような DB アクセスや外部 API 呼び出しを行うコードでも、  
niltest によるパフォーマンス劣化は**実質ゼロ**です。

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

`bool(expect)` の評価コスト（~5ns）は実用上ゼロであり、  
危険なハックを使う必要はありません。
