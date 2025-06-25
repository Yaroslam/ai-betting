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
        DB::schema()->create('match_predictions', function (Blueprint $table) {
            $table->id();
            $table->foreignId('match_id')->unique()->constrained('matches')->onDelete('cascade');

            // Прогноз
            $table->foreignId('predicted_winner_id')->constrained('teams')->onDelete('cascade');
            $table->decimal('confidence_percentage', 5, 2)->comment('Уверенность (0-100%)');
            $table->string('predicted_score', 10)->nullable()->comment('Предсказанный счет (2-1)');

            // Текст прогноза
            $table->text('prediction_text')->comment('Основной текст прогноза');
            $table->text('reasoning')->nullable()->comment('Обоснование прогноза');
            $table->json('analyzed_factors')->nullable()->comment('JSON с факторами анализа');

            // Результат прогноза
            $table->boolean('is_correct')->nullable()->comment('Верен ли прогноз (NULL до завершения)');
            $table->foreignId('actual_winner_id')->nullable()->constrained('teams')->onDelete('set null');
            $table->string('actual_score', 10)->nullable()->comment('Фактический счет');

            $table->timestamps();
        });

        // Проверочное ограничение на процент уверенности
        DB::statement('ALTER TABLE match_predictions ADD CONSTRAINT chk_match_predictions_confidence CHECK (confidence_percentage >= 0 AND confidence_percentage <= 100)');
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::schema()->dropIfExists('match_predictions');
    }
};
