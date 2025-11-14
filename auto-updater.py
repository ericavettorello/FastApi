#!/usr/bin/env python3
"""
Автоматическое обновление Docker контейнеров
Альтернатива Watchtower, совместимая с новым Docker API
"""

import docker
import docker.errors
import time
import logging
import os
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация
POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '30'))  # секунды
REGISTRY_URL = os.getenv('REGISTRY_URL', 'localhost:5000')
CLEANUP = os.getenv('CLEANUP', 'true').lower() == 'true'
# Отслеживание системных контейнеров (registry, nginx и т.д.)
TRACK_SYSTEM_CONTAINERS = os.getenv('TRACK_SYSTEM_CONTAINERS', 'true').lower() == 'true'
# Список системных контейнеров для отслеживания (через запятую)
SYSTEM_CONTAINERS = os.getenv('SYSTEM_CONTAINERS', 'docker-registry').split(',')

def get_docker_client():
    """Создает клиент Docker"""
    try:
        client = docker.from_env()
        # Проверяем версию API
        version = client.version()
        logger.info(f"Docker API версия: {version.get('ApiVersion', 'unknown')}")
        return client
    except Exception as e:
        logger.error(f"Ошибка подключения к Docker: {e}")
        raise

def check_image_update(client, container):
    """Проверяет наличие обновлений для образа контейнера"""
    try:
        image_name = container.image.tags[0] if container.image.tags else None
        if not image_name:
            return False
        
        # Проверяем, является ли это системным контейнером для отслеживания
        is_system_container = TRACK_SYSTEM_CONTAINERS and container.name in SYSTEM_CONTAINERS
        
        # Пропускаем образы, которые не из нашего registry (если это не системный контейнер)
        if not is_system_container and REGISTRY_URL not in image_name:
            return False
        
        # Проверяем, есть ли метка для исключения из обновления
        labels = container.labels or {}
        if labels.get('com.autodeploy.update', 'true').lower() == 'false':
            logger.debug(f"Контейнер {container.name} исключен из обновления")
            return False
        
        # Получаем текущий digest образа
        current_image = client.images.get(image_name)
        current_digest = current_image.id
        
        # Пытаемся обновить образ
        try:
            container_type = "системный контейнер" if is_system_container else "контейнер из registry"
            logger.info(f"Проверка обновлений для {image_name} ({container_type})...")
            client.images.pull(image_name)
            updated_image = client.images.get(image_name)
            updated_digest = updated_image.id
            
            if current_digest != updated_digest:
                logger.info(f"Обнаружено обновление для {image_name} ({container_type})")
                return True
            else:
                logger.debug(f"Обновлений для {image_name} не найдено")
                return False
        except Exception as e:
            logger.warning(f"Не удалось проверить обновления для {image_name}: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Ошибка при проверке обновлений для контейнера {container.name}: {e}")
        return False

def update_container(client, container):
    """Обновляет контейнер с новым образом"""
    try:
        image_name = container.image.tags[0] if container.image.tags else None
        if not image_name:
            return False
        
        container_name = container.name
        logger.info(f"Обновление контейнера {container_name}...")
        
        # Сохраняем ID старого образа до удаления контейнера
        old_image_id = container.image.id
        
        # Получаем конфигурацию контейнера
        container_config = container.attrs
        was_running = container.status == 'running'
        
        # Останавливаем контейнер
        if was_running:
            container.stop()
            logger.info(f"Контейнер {container_name} остановлен")
        
        # Получаем конфигурацию для пересоздания
        config = container_config.get('Config', {})
        host_config = container_config.get('HostConfig', {})
        
        # Подготавливаем параметры для создания нового контейнера
        create_kwargs = {
            'image': image_name,
            'name': container_name,
            'detach': True,
        }
        
        # Добавляем команду
        if config.get('Cmd'):
            create_kwargs['command'] = config.get('Cmd')
        
        # Добавляем переменные окружения
        if config.get('Env'):
            create_kwargs['environment'] = {e.split('=', 1)[0]: e.split('=', 1)[1] if '=' in e else '' 
                                          for e in config.get('Env', [])}
        
        # Добавляем labels
        if config.get('Labels'):
            create_kwargs['labels'] = config.get('Labels')
        
        # Добавляем volumes
        if host_config.get('Binds'):
            create_kwargs['volumes'] = {bind.split(':')[1] if ':' in bind else bind: {} 
                                       for bind in host_config.get('Binds', [])}
        
        # Добавляем порты
        port_bindings = host_config.get('PortBindings', {})
        if port_bindings:
            ports = {}
            for container_port, host_bindings in port_bindings.items():
                if host_bindings:
                    host_port = host_bindings[0].get('HostPort', '')
                    ports[container_port] = host_port if host_port else None
            if ports:
                create_kwargs['ports'] = ports
        
        # Добавляем restart policy
        restart_policy = host_config.get('RestartPolicy', {})
        if restart_policy.get('Name') != 'no':
            create_kwargs['restart_policy'] = {
                'Name': restart_policy.get('Name', 'unless-stopped')
            }
        
        # Удаляем старый контейнер
        container.remove()
        logger.info(f"Старый контейнер {container_name} удален")
        
        # Создаем новый контейнер
        new_container = client.containers.create(**create_kwargs)
        logger.info(f"Новый контейнер {container_name} создан")
        
        # Запускаем новый контейнер, если он был запущен
        if was_running:
            new_container.start()
            logger.info(f"Контейнер {container_name} успешно обновлен и запущен")
        else:
            logger.info(f"Контейнер {container_name} успешно обновлен (остановлен)")
        
        # Очистка старых образов
        if CLEANUP:
            try:
                # Удаляем только если образ не используется другими контейнерами
                client.images.remove(old_image_id, force=False)
                logger.info(f"Старый образ {old_image_id[:12]} удален")
            except docker.errors.ImageNotFound:
                pass
            except Exception as e:
                logger.debug(f"Не удалось удалить старый образ (возможно, используется): {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении контейнера {container.name}: {e}")
        return False

def main():
    """Основной цикл обновления"""
    logger.info("Запуск автоматического обновления контейнеров")
    logger.info(f"Интервал проверки: {POLL_INTERVAL} секунд")
    logger.info(f"Registry URL: {REGISTRY_URL}")
    logger.info(f"Отслеживание системных контейнеров: {TRACK_SYSTEM_CONTAINERS}")
    if TRACK_SYSTEM_CONTAINERS:
        logger.info(f"Отслеживаемые системные контейнеры: {', '.join(SYSTEM_CONTAINERS)}")
    
    client = get_docker_client()
    
    while True:
        try:
            # Получаем все контейнеры
            containers = client.containers.list(all=True)
            logger.info(f"Проверка {len(containers)} контейнеров...")
            
            for container in containers:
                try:
                    # Пропускаем сам контейнер обновления
                    if container.name == 'auto-updater':
                        continue
                    
                    # Проверяем обновления
                    if check_image_update(client, container):
                        # Обновляем контейнер
                        update_container(client, container)
                        
                except Exception as e:
                    logger.error(f"Ошибка при обработке контейнера {container.name}: {e}")
                    continue
            
            logger.info(f"Следующая проверка через {POLL_INTERVAL} секунд...")
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("Остановка обновления...")
            break
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            time.sleep(POLL_INTERVAL)

if __name__ == '__main__':
    main()

