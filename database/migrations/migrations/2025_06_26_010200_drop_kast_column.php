<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Capsule\Manager as DB;

return new class extends Migration
{
    public function up(): void
    {
        DB::schema()->table('player_statistics', function (Blueprint $table) {
            if (DB::schema()->hasColumn('player_statistics', 'kast')) {
                $table->dropColumn('kast');
            }
        });
    }

    public function down(): void
    {
        DB::schema()->table('player_statistics', function (Blueprint $table) {
            $table->decimal('kast', 5, 2)->nullable()->comment('KAST percentage');
        });
    }
}; 