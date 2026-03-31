"""
main.py - 全体フローの制御

Flow:
    1. trend_fetcher   : トレンド・ネタを外部から取得
    2. content_generator: Claude API でツイート文を生成
    3. human review    : ターミナルで確認・承認
    4. x_poster        : X API で投稿

Future hooks (not implemented yet):
    - scheduler        : 指定時間に自動投稿
    - risk_checker     : 炎上・誤情報の事前チェック
    - engagement_bot   : リプライ・いいねへの自動対応
    - account_manager  : マルチアカウント切り替え
    - analytics        : インプレッション・フォロワー可視化
"""

from dotenv import load_dotenv

from trend_fetcher import fetch_trends
from content_generator import generate_tweet
from x_poster import post_tweet


def review_and_confirm(tweet: str) -> bool:
    """生成されたツイートを人間がレビューして承認/却下する。"""
    print("\n" + "=" * 50)
    print("【生成されたツイート】")
    print(tweet)
    print("=" * 50)
    answer = input("\nこの内容で投稿しますか？ [y/N]: ").strip().lower()
    return answer == "y"


def main():
    load_dotenv()

    # Step 1: トレンド取得
    print("[1/4] トレンドを取得中...")
    trends = fetch_trends()

    # Step 2: ツイート生成
    print("[2/4] ツイートを生成中...")
    tweet = generate_tweet(trends)

    # Step 3: 人間によるレビュー
    print("[3/4] レビューしてください")
    approved = review_and_confirm(tweet)

    if not approved:
        print("投稿をキャンセルしました。")
        return

    # Step 4: 投稿
    print("[4/4] X に投稿中...")
    post_tweet(tweet)
    print("投稿が完了しました。")


if __name__ == "__main__":
    main()
