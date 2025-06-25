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
        DB::schema()->create('match_maps', function (Blueprint $table) {
            $table->id();
            $table->foreignId('match_id')->constrained('matches')->onDelete('cascade');
            $table->foreignId('map_id')->constrained('maps')->onDelete('cascade');
            $table->integer('map_number')->comment('Порядковый номер в матче');

            // Результат по карте
            $table->integer('team1_rounds')->nullable()->comment('Раунды первой команды');
            $table->integer('team2_rounds')->nullable()->comment('Раунды второй команды');
            $table->foreignId('winner_id')->nullable()->constrained('teams')->onDelete('set null');

            // Статус
            $table->string('status', 20)->default('upcoming')->comment('upcoming, live, completed');
            $table->timestamps();

            // Уникальность по матчу и номеру карты
            $table->unique(['match_id', 'map_number']);
        });

        // Проверочное ограничение на номер карты
        DB::statement('ALTER TABLE match_maps ADD CONSTRAINT chk_match_maps_map_number CHECK (map_number > 0)');
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::schema()->dropIfExists('match_maps');
    }
};
