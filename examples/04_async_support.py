"""
04. Async (非同期) 関数のサポート

niltest は async/await を使った非同期関数もネイティブにサポートします。
モックモードでは `await func()` と呼び出した際に即座に値が返ります。
テストモードでも自動的にイベントループを回して照合を行います。
"""

import asyncio

import niltest
from niltest import expect, scenario

niltest.configure(mode="mock")


@scenario("非同期データ取得 API")
async def fetch_remote_data(endpoint: str) -> dict[str, str | int]:
    if expect:
        expect.case(
            "正常系: ユーザーデータ",
            given=dict(endpoint="/users/1"),
            returns={"id": 1, "name": "Alice"},
        )
        expect.case(
            "異常系: 存在しないパス",
            given=dict(endpoint="/notfound"),
            returns={"error": "Not Found"},
        )

    # 実際の非同期処理のシミュレーション
    print(f"Fetching from {endpoint}...")
    await asyncio.sleep(1)

    if endpoint == "/users/1":
        return {"id": 1, "name": "Alice"}
    return {"error": "Not Found"}


async def main() -> None:
    print("=== モックモード実行 ===")
    # モックなので asyncio.sleep は呼ばれず一瞬で返る
    result1 = await fetch_remote_data("/users/1")
    print("Result 1:", result1)

    result2 = await fetch_remote_data("/notfound")
    print("Result 2:", result2)


if __name__ == "__main__":
    # モックの実行
    asyncio.run(main())

    print("\n=== テスト実行 ===")
    # テストランナーは同期関数なので、await せずに呼べる
    # (内部でイベントループを回して実行してくれます)
    niltest.configure(mode="test")
    niltest.run_tests(fetch_remote_data)
