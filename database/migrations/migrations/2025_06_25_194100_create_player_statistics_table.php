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
        DB::schema()->create('player_statistics', function (Blueprint $table) {
            $table->id();
            $table->foreignId('player_id')->constrained('players')->onDelete('cascade');

            // Основные показатели из HLTV
            $table->decimal('rating_2_0', 4, 3)->nullable()->comment('Рейтинг 2.0 (1.234)');
            $table->decimal('kd_ratio', 4, 3)->nullable()->comment('Kill/Death ratio');
            $table->decimal('adr', 5, 2)->nullable()->comment('Average Damage per Round');
            $table->decimal('kast', 5, 2)->nullable()->comment('KAST percentage');
            $table->decimal('headshot_percentage', 5, 2)->nullable()->comment('Процент хедшотов');

            // Детальная статистика
            $table->integer('maps_played')->default(0)->comment('Количество сыгранных карт');
            $table->decimal('kills_per_round', 4, 3)->nullable()->comment('Убийств за раунд');
            $table->decimal('assists_per_round', 4, 3)->nullable()->comment('Ассистов за раунд');
            $table->decimal('deaths_per_round', 4, 3)->nullable()->comment('Смертей за раунд');
            $table->decimal('saved_by_teammate_per_round', 4, 3)->nullable()->comment('Спасений командой');
            $table->decimal('saved_teammates_per_round', 4, 3)->nullable()->comment('Спасений команды');

            // Временные рамки
            $table->date('period_start')->comment('Начало периода');
            $table->date('period_end')->comment('Конец периода');
            $table->timestamp('last_updated')->nullable()->comment('Последнее обновление');
            $table->timestamps();

            // Уникальность по игроку и периоду
            $table->unique(['player_id', 'period_start', 'period_end']);
            
            // Индексы для быстрого поиска
            $table->index(['rating_2_0'], 'idx_player_statistics_rating');
            $table->index(['period_start', 'period_end'], 'idx_player_statistics_period');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::schema()->dropIfExists('player_statistics');
    }
};
