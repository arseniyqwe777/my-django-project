// Пользовательские JavaScript функции для библиотечной системы

// Подтверждение удаления
function confirmDelete(message) {
    return confirm(message || 'Вы уверены, что хотите удалить эту запись?');
}

// Валидация инвентарного номера
function validateInventoryNumber(input) {
    const value = input.value;
    const pattern = /^\d{5}$/;

    if (!pattern.test(value)) {
        input.setCustomValidity('Инвентарный номер должен состоять из 5 цифр');
        return false;
    } else {
        input.setCustomValidity('');
        return true;
    }
}

// Автоматическое форматирование инвентарного номера
function formatInventoryNumber(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length > 5) {
        value = value.slice(0, 5);
    }
    input.value = value;
}

// Поиск с задержкой (debounce)
let searchTimeout;
function debounceSearch(func, delay) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(func, delay);
}

// Показ уведомлений
function showNotification(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);

    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

// Подсветка поискового запроса
function highlightSearchTerm(text, term) {
    if (!term) return text;
    const regex = new RegExp(`(${term})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
}

// Отключение кнопки после отправки (защита от двойного нажатия)
function disableButton(button) {
    if (button.disabled) return false;

    button.disabled = true;
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Сохранение...';

    // Сохраняем оригинальный текст для восстановления
    button.dataset.originalText = originalText;

    return true;
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Автофокус на поле поиска
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput && !searchInput.value) {
        searchInput.focus();
    }

    // Валидация инвентарного номера
    const inventoryInput = document.querySelector('input[name="inventory_number"]');
    if (inventoryInput) {
        inventoryInput.addEventListener('input', function() {
            formatInventoryNumber(this);
            validateInventoryNumber(this);
        });
    }

    // Подтверждение удаления для всех кнопок delete
    document.querySelectorAll('.btn-delete, .delete-btn, .btn-outline-danger').forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (this.classList.contains('clicked')) {
                e.preventDefault();
                return false;
            }

            if (!confirmDelete(this.dataset.message)) {
                e.preventDefault();
                return false;
            }

            this.classList.add('clicked');
        });
    });

    // ========== ЗАЩИТА ОТ ДВОЙНОГО НАЖАТИЯ ==========
    // Находим все формы
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        // Добавляем обработчик отправки формы
        form.addEventListener('submit', function(e) {
            // Находим все кнопки отправки в этой форме
            const submitButtons = form.querySelectorAll('button[type="submit"], input[type="submit"]');

            let preventSubmit = false;

            submitButtons.forEach(button => {
                // Если кнопка уже отключена - предотвращаем отправку
                if (button.disabled) {
                    preventSubmit = true;
                } else {
                    // Отключаем кнопку
                    button.disabled = true;
                    const originalText = button.innerHTML;
                    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Обработка...';

                    // Возвращаем текст через 10 секунд (на случай ошибки сети)
                    setTimeout(() => {
                        if (button.disabled) {
                            button.disabled = false;
                            button.innerHTML = originalText;
                        }
                    }, 10000);
                }
            });

            // Если хотя бы одна кнопка уже была отключена - блокируем отправку
            if (preventSubmit) {
                e.preventDefault();
                showNotification('Запрос уже обрабатывается. Пожалуйста, подождите...', 'warning');
                return false;
            }
        });
    });

    // Защита для ссылок удаления от двойного клика
    const deleteLinks = document.querySelectorAll('.btn-danger, .delete-link, .text-danger');
    deleteLinks.forEach(link => {
        if (link.getAttribute('href') && link.getAttribute('href').includes('delete')) {
            link.addEventListener('click', function(e) {
                if (link.classList.contains('clicked')) {
                    e.preventDefault();
                    showNotification('Запрос уже обрабатывается', 'warning');
                    return false;
                }
                link.classList.add('clicked');
            });
        }
    });

    // Предотвращение повторной отправки формы при обновлении страницы
    if (window.performance && window.performance.navigation.type === 1) {
        // Страница была перезагружена
        sessionStorage.removeItem('form_submitted');
    }

    // Блокировка повторной отправки формы при возврате назад
    window.addEventListener('pageshow', function(event) {
        if (event.persisted || (window.performance && window.performance.navigation.type === 2)) {
            // Страница загружена из кэша (нажата кнопка "назад")
            const forms = document.querySelectorAll('form');
            forms.forEach(form => {
                const buttons = form.querySelectorAll('button[type="submit"]');
                buttons.forEach(button => {
                    button.disabled = false;
                    button.classList.remove('disabled');
                    if (button.innerHTML.includes('spinner')) {
                        button.innerHTML = button.getAttribute('data-original-text') || 'Сохранить';
                    }
                });
            });
        }
    });
});