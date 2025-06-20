import concurrent.futures
import logging
import os
import sys
from pathlib import Path
from socket import socket

from gunicorn.arbiter import Arbiter
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.logging import RichHandler
from uvicorn import Server
from uvicorn.workers import UvicornWorker


class ClipSettings(BaseModel):
    textual: str | None = None
    visual: str | None = None


class FacialRecognitionSettings(BaseModel):
    recognition: str | None = None
    detection: str | None = None


class PreloadModelData(BaseModel):
    clip_fallback: str | None = os.getenv("MACHINE_LEARNING_PRELOAD__CLIP", None)
    facial_recognition_fallback: str | None = os.getenv("MACHINE_LEARNING_PRELOAD__FACIAL_RECOGNITION", None)
    print(f"MACHINE_LEARNING_PRELOAD__CLIP: {clip_fallback}")

    if clip_fallback is not None:
        os.environ["MACHINE_LEARNING_PRELOAD__CLIP__TEXTUAL"] = clip_fallback
        os.environ["MACHINE_LEARNING_PRELOAD__CLIP__VISUAL"] = clip_fallback
        del os.environ["MACHINE_LEARNING_PRELOAD__CLIP"]
    if facial_recognition_fallback is not None:
        os.environ["MACHINE_LEARNING_PRELOAD__FACIAL_RECOGNITION__RECOGNITION"] = facial_recognition_fallback
        os.environ["MACHINE_LEARNING_PRELOAD__FACIAL_RECOGNITION__DETECTION"] = facial_recognition_fallback
        del os.environ["MACHINE_LEARNING_PRELOAD__FACIAL_RECOGNITION"]
    clip: ClipSettings = ClipSettings()
    facial_recognition: FacialRecognitionSettings = FacialRecognitionSettings()


class MaxBatchSize(BaseModel):
    facial_recognition: int | None = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MACHINE_LEARNING_",
        case_sensitive=False,
        env_nested_delimiter="__",
        protected_namespaces=("settings_",),
    )

    cache_folder: Path = (Path.home() / ".cache" / "immich_ml").resolve()
    model_ttl: int = 300
    model_ttl_poll_s: int = 10
    workers: int = 1
    worker_timeout: int = 300
    http_keepalive_timeout_s: int = 2
    test_full: bool = False
    request_threads: int = os.cpu_count() or 4
    model_inter_op_threads: int = 0
    model_intra_op_threads: int = 0
    ann: bool = True
    ann_fp16_turbo: bool = False
    ann_tuning_level: int = 2
    rknn: bool = True
    rknn_threads: int = 1
    preload: PreloadModelData | None = None
    max_batch_size: MaxBatchSize | None = None

    @property
    def device_id(self) -> str:
        return os.environ.get("MACHINE_LEARNING_DEVICE_ID", "0")


class NonPrefixedSettings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    immich_host: str = "[::]"
    immich_port: int = 3003
    immich_log_level: str = "info"
    no_color: bool = False


_clean_name = str.maketrans(":\\/", "___", ".")


def clean_name(model_name: str) -> str:
    return model_name.split("/")[-1].translate(_clean_name)


LOG_LEVELS: dict[str, int] = {
    "critical": logging.ERROR,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "warn": logging.WARNING,
    "info": logging.INFO,
    "log": logging.INFO,
    "debug": logging.DEBUG,
    "verbose": logging.DEBUG,
}

settings = Settings()
non_prefixed_settings = NonPrefixedSettings()

LOG_LEVEL = LOG_LEVELS.get(non_prefixed_settings.immich_log_level.lower(), logging.INFO)


class CustomRichHandler(RichHandler):
    def __init__(self) -> None:
        console = Console(color_system="standard", no_color=non_prefixed_settings.no_color)
        self.excluded = ["uvicorn", "starlette", "fastapi"]
        super().__init__(
            show_path=False,
            omit_repeated_times=False,
            console=console,
            rich_tracebacks=True,
            tracebacks_suppress=[*self.excluded, concurrent.futures],
            tracebacks_show_locals=LOG_LEVEL == logging.DEBUG,
        )

    # hack to exclude certain modules from rich tracebacks
    def emit(self, record: logging.LogRecord) -> None:
        if record.exc_info is not None:
            tb = record.exc_info[2]
            while tb is not None:
                if any(excluded in tb.tb_frame.f_code.co_filename for excluded in self.excluded):
                    tb.tb_frame.f_locals["_rich_traceback_omit"] = True
                tb = tb.tb_next

        return super().emit(record)


log = logging.getLogger("ml.log")
log.setLevel(LOG_LEVEL)


# patches this issue https://github.com/encode/uvicorn/discussions/1803
class CustomUvicornServer(Server):
    async def shutdown(self, sockets: list[socket] | None = None) -> None:
        for sock in sockets or []:
            sock.close()
        await super().shutdown()


class CustomUvicornWorker(UvicornWorker):
    async def _serve(self) -> None:
        self.config.app = self.wsgi
        server = CustomUvicornServer(config=self.config)
        self._install_sigquit_handler()
        await server.serve(sockets=self.sockets)
        if not server.started:
            sys.exit(Arbiter.WORKER_BOOT_ERROR)
