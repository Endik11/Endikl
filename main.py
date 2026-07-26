from game.engine import GameEngine
from game.crash_reporter import handle_unhandled_exception


def main() -> None:
    try:
        GameEngine().run()
    except Exception as exc:
        handle_unhandled_exception(exc)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()

