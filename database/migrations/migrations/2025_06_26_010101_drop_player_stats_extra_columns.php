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
        DB::schema()->table('player_statistics', function (Blueprint $table) {
            if (DB::schema()->hasColumn('player_statistics', 'headshot_percentage')) {
                $table->dropColumn('headshot_percentage');
            }
            if (DB::schema()->hasColumn('player_statistics', 'saved_by_teammate_per_round')) {
                $table->dropColumn('saved_by_teammate_per_round');
            }
            if (DB::schema()->hasColumn('player_statistics', 'saved_teammates_per_round')) {
                $table->dropColumn('saved_teammates_per_round');
            }
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::schema()->table('player_statistics', function (Blueprint $table) {
            $table->decimal('headshot_percentage', 5, 2)->nullable()->comment('Процент хедшотов');
            $table->decimal('saved_by_teammate_per_round', 4, 3)->nullable()->comment('Спасений командой');
            $table->decimal('saved_teammates_per_round', 4, 3)->nullable()->comment('Спасений команды');
        });
    }
}; 