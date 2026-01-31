#!/usr/bin/env python3
"""
Запуск сервера WebSocket чата
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=6088,
        reload=True,
        log_level="info"
    )