"""
Application configuration module
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache
import os
import json
import time


class Settings(BaseSettings):
    """Application settings"""
    
    # Basic application settings
    app_name: str = "AI-PreInterview"
    app_env: str = "development"
    debug: bool = True
    port: int = 8000
    
    # CORS configuration
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    
    # LLM configuration
    llm_provider: str = "dashscope"
    llm_api_key: Optional[str] = None
    llm_api_base: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    llm_model: str = "deepseek-v3"
    
    # ASR configuration (Speech to Text)
    asr_provider: str = "dashscope"
    asr_api_key: Optional[str] = None
    asr_api_base: str = "wss://dashscope.aliyuncs.com/api-ws/v1/realtime"
    asr_model: str = "qwen3-asr-flash-realtime"
    
    # TTS configuration (Text to Speech)
    tts_provider: str = "dashscope"
    tts_api_key: Optional[str] = None
    tts_api_base: str = "wss://dashscope.aliyuncs.com/api-ws/v1/realtime"
    tts_model: str = "qwen3-tts-flash-realtime"
    tts_voice: str = "Maia"
    
    # Resume/JD parser service (reserved)
    resume_parser_api_url: Optional[str] = None
    resume_parser_api_key: Optional[str] = None
    jd_parser_api_url: Optional[str] = None
    jd_parser_api_key: Optional[str] = None
    
    # Database configuration
    database_url: str = "sqlite:///./data/interview.db"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


DEBUG_LOG_PATH = r"d:\DOCUMENTS\Company\AI_PreInterview\.cursor\debug.log"


def _debug_log(message: str, data: dict, hypothesis_id: str, run_id: str = "run1") -> None:
    """Write NDJSON debug logs to file without secrets."""
    payload = {
        "sessionId": "debug-session",
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": "app/core/config.py",
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    try:
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass


@lru_cache()
def get_settings() -> Settings:
    """Get settings singleton"""
    # #region agent log
    _debug_log(
        message="env_var_presence",
        data={
            "cwd": os.getcwd(),
            "has_api_key": "api_key" in os.environ,
            "has_API_KEY": "API_KEY" in os.environ,
            "has_DASHSCOPE_API_KEY": "DASHSCOPE_API_KEY" in os.environ,
            "has_LLM_API_KEY": "LLM_API_KEY" in os.environ,
            "has_ASR_API_KEY": "ASR_API_KEY" in os.environ,
            "has_TTS_API_KEY": "TTS_API_KEY" in os.environ,
        },
        hypothesis_id="H1",
    )
    # #endregion
    # #region agent log
    env_path = os.path.join(os.getcwd(), ".env")
    env_keys = set()
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as env_file:
                for line in env_file:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key = line.split("=", 1)[0].strip()
                    env_keys.add(key)
        except Exception:
            pass
    _debug_log(
        message="dotenv_key_presence",
        data={
            "env_path": env_path,
            "env_exists": os.path.exists(env_path),
            "has_api_key": "api_key" in env_keys,
            "has_API_KEY": "API_KEY" in env_keys,
            "has_DASHSCOPE_API_KEY": "DASHSCOPE_API_KEY" in env_keys,
            "has_LLM_API_KEY": "LLM_API_KEY" in env_keys,
            "has_ASR_API_KEY": "ASR_API_KEY" in env_keys,
            "has_TTS_API_KEY": "TTS_API_KEY" in env_keys,
        },
        hypothesis_id="H2",
    )
    # #endregion
    try:
        settings = Settings()
        # #region agent log
        _debug_log(
            message="settings_init_success",
            data={
                "llm_provider": settings.llm_provider,
                "llm_api_base": settings.llm_api_base,
                "asr_api_base": settings.asr_api_base,
                "tts_api_base": settings.tts_api_base,
                "llm_api_key_set": bool(settings.llm_api_key),
                "asr_api_key_set": bool(settings.asr_api_key),
                "tts_api_key_set": bool(settings.tts_api_key),
            },
            hypothesis_id="H3",
        )
        # #endregion
        return settings
    except Exception as exc:
        # #region agent log
        error_list = []
        try:
            if hasattr(exc, "errors"):
                for err in exc.errors():
                    error_list.append(
                        {"loc": err.get("loc"), "type": err.get("type"), "msg": err.get("msg")}
                    )
        except Exception:
            error_list = []
        _debug_log(
            message="settings_init_error",
            data={
                "error_type": type(exc).__name__,
                "error_count": len(error_list),
                "errors": error_list,
            },
            hypothesis_id="H4",
        )
        # #endregion
        raise
