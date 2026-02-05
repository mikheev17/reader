"""
Централизованная настройка логирования приложения.
Уровень логирования задаётся через LOG_LEVEL в настройках (env).
"""

import logging


def setup_logging(level_name: str = "INFO") -> None:
    """
    Настраивает корневой логгер: уровень и формат сообщений.
    Вызывается при старте приложения (api.py).
    """
    level = getattr(logging, (level_name or "INFO").upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )
