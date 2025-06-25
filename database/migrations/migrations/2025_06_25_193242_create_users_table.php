<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Capsule\Manager as DB;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        DB::schema()->create('users', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('telegram_id')->unique()->comment('ID пользователя в Telegram');

            // Профиль
            $table->string('username', 100)->nullable()->comment('Username в Telegram');
            $table->string('first_name', 100)->nullable()->comment('Имя');
            $table->string('last_name', 100)->nullable()->comment('Фамилия');
            $table->string('email', 255)->unique()->nullable()->comment('Email (опционально)');

            // Подписка
            $table->boolean('is_premium')->default(false)->comment('Премиум статус');
            $table->timestamp('premium_until')->nullable()->comment('До какого времени премиум');

            // Баланс
            $table->decimal('balance', 10, 2)->default(0.00)->comment('Баланс пользователя');

            // Настройки
            $table->json('notification_settings')->default('{}')->comment('Настройки уведомлений');

            // Статус
            $table->boolean('is_active')->default(true)->comment('Активен ли аккаунт');
            $table->boolean('is_banned')->default(false)->comment('Заблокирован ли');

            // Метаданные
            $table->timestamp('last_activity')->nullable()->comment('Последняя активность');
            $table->timestamps();

            // Индексы
            $table->index('telegram_id');
            $table->index('is_premium');
        });

        // Проверочное ограничение на баланс
        DB::statement('ALTER TABLE users ADD CONSTRAINT chk_users_balance CHECK (balance >= 0)');
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::schema()->dropIfExists('users');
    }
};
