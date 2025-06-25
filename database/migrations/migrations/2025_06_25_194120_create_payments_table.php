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
        DB::schema()->create('payments', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained('users')->onDelete('cascade');

            // Платеж
            $table->decimal('amount', 10, 2)->comment('Сумма платежа');
            $table->string('currency', 3)->default('USD')->comment('Валюта');
            $table->string('payment_type', 50)->comment('Тип: premium_subscription, balance_topup');

            // Статус
            $table->string('status', 20)->default('pending')->comment('pending, completed, failed, refunded');

            // Внешние системы
            $table->string('external_payment_id', 255)->nullable()->comment('ID в платежной системе');
            $table->string('payment_method', 50)->nullable()->comment('Способ оплаты: card, crypto');

            // Метаданные
            $table->json('metadata')->nullable()->comment('Дополнительная информация');
            $table->timestamps();
        });

        // Проверочное ограничение на сумму
        DB::statement('ALTER TABLE payments ADD CONSTRAINT chk_payments_amount CHECK (amount > 0)');
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::schema()->dropIfExists('payments');
    }
};
