#!/bin/bash
# Скрипт для настройки автоматической отправки на GitHub

echo "🔧 Настройка автоматической отправки на GitHub..."

# Проверяем наличие git репозитория
if [ ! -d ".git" ]; then
    echo "❌ Git репозиторий не найден!"
    exit 1
fi

# Создаем post-commit hook
cat > .git/hooks/post-commit << 'EOF'
#!/bin/bash
# Автоматическая отправка изменений на GitHub после коммита

BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "🚀 Автоматическая отправка на GitHub (ветка: $BRANCH)..."

# Используем credential helper для сохранения токена
if git push origin "$BRANCH" 2>&1; then
    echo "✅ Изменения отправлены на GitHub"
else
    echo "⚠️  Автоматическая отправка не удалась"
    echo "💡 Выполните: git push origin $BRANCH"
fi
EOF

chmod +x .git/hooks/post-commit
echo "✅ Post-commit hook установлен"

# Настраиваем credential helper для сохранения токена
echo ""
echo "📝 Настройка credential helper..."
echo "Выберите метод аутентификации:"
echo "1) Personal Access Token (рекомендуется)"
echo "2) SSH ключ"
read -p "Ваш выбор (1 или 2): " choice

if [ "$choice" = "1" ]; then
    echo ""
    echo "Для использования Personal Access Token:"
    echo "1. Создайте токен: https://github.com/settings/tokens"
    echo "2. При первом push введите токен как пароль"
    echo "3. Git сохранит его для будущих операций"
    git config --global credential.helper store
    echo "✅ Credential helper настроен для сохранения токена"
elif [ "$choice" = "2" ]; then
    echo ""
    echo "Для использования SSH:"
    echo "1. Создайте SSH ключ: ssh-keygen -t ed25519 -C 'your_email@example.com'"
    echo "2. Добавьте ключ в GitHub: https://github.com/settings/keys"
    echo "3. Измените remote: git remote set-url origin git@github.com:ericavettorello/FastApi.git"
    git remote set-url origin git@github.com:ericavettorello/FastApi.git
    echo "✅ Remote изменен на SSH"
else
    echo "⚠️  Неверный выбор, credential helper не настроен"
fi

echo ""
echo "✅ Настройка завершена!"
echo "Теперь каждый коммит будет автоматически отправляться на GitHub"

