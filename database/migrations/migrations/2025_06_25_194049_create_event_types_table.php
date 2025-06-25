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
        DB::schema()->create('event_types', function (Blueprint $table) {
            $table->id();
            $table->string('name', 100)->unique()->comment('Название типа турнира');
            $table->string('tier', 20)->comment('Уровень турнира (S, A, B, C)');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::schema()->dropIfExists('event_types');
    }
};
