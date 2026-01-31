#!/usr/bin/env python3
"""
Запуск сервера WebSocket чата
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # Доступно со всех интерфейсов
        port=6088,       # Порт по умолчанию
        reload=True,     # Автоматическая перезагрузка при изменениях
        log_level="info" # Уровень логирования
    )