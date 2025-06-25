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
        DB::schema()->create('team_rosters', function (Blueprint $table) {
            $table->id();
            $table->foreignId('team_id')->constrained('teams')->onDelete('cascade');
            $table->foreignId('player_id')->constrained('players')->onDelete('cascade');
            $table->string('role', 50)->nullable()->comment('Роль (IGL, AWPer, Support)');
            $table->boolean('is_active')->default(true)->comment('Активен ли в составе');
            $table->timestamp('joined_at')->comment('Дата присоединения');
            $table->timestamp('left_at')->nullable()->comment('Дата ухода (NULL если активен)');
            $table->timestamps();

            // Уникальность по команде, игроку и дате присоединения
            $table->unique(['team_id', 'player_id', 'joined_at']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::schema()->dropIfExists('team_rosters');
    }
};
