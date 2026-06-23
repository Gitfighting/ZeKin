import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


class EmojiFormatter(logging.Formatter):
    EMOJI = {
        logging.ERROR: "🔴",
        logging.WARNING: "🟠",
        logging.INFO: "🟢",
        logging.DEBUG: "🟡",
    }

    def format(self, record: logging.LogRecord) -> str:
        record.level_emoji = self.EMOJI.get(record.levelno, "⚫")
        return super().format(record)


def configure_logging() -> None:
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    formatter = EmojiFormatter(
        "%(asctime)s.%(msecs)03d %(level_emoji)s %(levelname)-5s "
        "%(name)s (%(filename)s:%(lineno)d) %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    file_handler = TimedRotatingFileHandler(
        logs_dir / "zekin.log",
        when="midnight",
        backupCount=30,
        encoding="utf-8",
    )
    handlers.append(file_handler)
    for handler in handlers:
        handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, handlers=handlers, force=True)

