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
        DB::schema()->create('matches', function (Blueprint $table) {
            $table->id();
            $table->integer('hltv_id')->unique()->comment('ID матча на HLTV.org');
            $table->foreignId('event_id')->constrained('events')->onDelete('cascade');

            // Участники
            $table->foreignId('team1_id')->constrained('teams')->onDelete('cascade');
            $table->foreignId('team2_id')->constrained('teams')->onDelete('cascade');

            // Результат
            $table->integer('team1_score')->nullable()->comment('Счет первой команды');
            $table->integer('team2_score')->nullable()->comment('Счет второй команды');
            $table->foreignId('winner_id')->nullable()->constrained('teams')->onDelete('set null');

            // Детали
            $table->string('match_format', 20)->comment('Bo1, Bo3, Bo5');
            $table->string('match_type', 50)->nullable()->comment('Group Stage, Final и т.д.');
            $table->timestamp('scheduled_at')->nullable()->comment('Запланированное время');
            $table->timestamp('started_at')->nullable()->comment('Время начала');
            $table->timestamp('ended_at')->nullable()->comment('Время окончания');

            // Статус
            $table->string('status', 20)->default('scheduled')->comment('scheduled, live, completed, cancelled');
            $table->string('hltv_url', 255)->nullable()->comment('Ссылка на HLTV');
            $table->timestamps();

            // Индексы для производительности
            $table->index('scheduled_at');
            $table->index('status');
            $table->index(['team1_id', 'team2_id'], 'idx_matches_teams');
        });

        // Проверочные ограничения
        DB::statement('ALTER TABLE matches ADD CONSTRAINT chk_matches_different_teams CHECK (team1_id != team2_id)');
        DB::statement('ALTER TABLE matches ADD CONSTRAINT chk_matches_winner CHECK (winner_id IS NULL OR winner_id = team1_id OR winner_id = team2_id)');
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::schema()->dropIfExists('matches');
    }
};
