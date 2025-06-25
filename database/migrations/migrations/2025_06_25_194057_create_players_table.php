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
        DB::schema()->create('players', function (Blueprint $table) {
            $table->id();
            $table->integer('hltv_id')->unique()->comment('ID игрока на HLTV.org');
            $table->string('nickname', 50)->comment('Игровой ник');
            $table->string('real_name', 100)->nullable()->comment('Настоящее имя');
            $table->foreignId('country_id')->constrained('countries')->onDelete('cascade');
            $table->integer('age')->nullable()->comment('Возраст с проверкой');
            $table->string('avatar_url', 255)->nullable()->comment('URL аватара');
            $table->string('hltv_url', 255)->nullable()->comment('Ссылка на HLTV');
            $table->boolean('is_active')->default(true)->comment('Активен ли игрок');
            $table->timestamps();

            // Индексы для производительности
            $table->index('hltv_id');
            $table->index('is_active');
        });

        // Добавляем проверочное ограничение для возраста
        DB::statement('ALTER TABLE players ADD CONSTRAINT chk_players_age CHECK (age > 0 AND age < 100)');
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::schema()->dropIfExists('players');
    }
};
