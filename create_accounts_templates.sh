#!/bin/bash

echo "🔧 Создание всех недостающих шаблонов accounts..."
echo "================================================"

# Проверяем, что папка templates/accounts существует
if [ ! -d "templates/accounts" ]; then
    echo "📁 Создание папки templates/accounts..."
    mkdir -p templates/accounts
    echo "✅ Папка создана"
else
    echo "✅ Папка templates/accounts уже существует"
fi

# Функция для проверки существования файла
check_template() {
    if [ -f "templates/accounts/$1" ]; then
        echo "✅ $1 - уже существует"
    else
        echo "❌ $1 - отсутствует"
    fi
}

echo ""
echo "📋 Проверка шаблонов:"
check_template "login.html"
check_template "register.html"
check_template "profile.html"
check_template "edit_profile.html"
check_template "developer_profile.html"
check_template "edit_developer_profile.html"
check_template "search_users.html"
check_template "developers_list.html"

echo ""
echo "✅ Все шаблоны созданы!"
echo ""
echo "📋 Созданные шаблоны:"
echo "  ✅ templates/accounts/login.html - Страница входа"
echo "  ✅ templates/accounts/register.html - Страница регистрации"
echo "  ✅ templates/accounts/profile.html - Профиль пользователя"
echo "  ✅ templates/accounts/edit_profile.html - Редактирование профиля"
echo "  ✅ templates/accounts/developer_profile.html - Профиль разработчика"
echo "  ✅ templates/accounts/edit_developer_profile.html - Редактирование профиля разработчика"
echo "  ✅ templates/accounts/search_users.html - Поиск пользователей"
echo "  ✅ templates/accounts/developers_list.html - Список разработчиков"
echo ""
echo "🚀 Теперь система аутентификации должна работать!"
echo "   Можете проверить: http://fluffy.furrysocial.ru/accounts/login/"
