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
        DB::schema()->create('countries', function (Blueprint $table) {
            $table->id();
            $table->string('code', 3)->unique()->comment('ISO 3166-1 alpha-3 код');
            $table->string('name', 100)->comment('Название страны');
            $table->string('flag_url', 255)->nullable()->comment('URL флага');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::schema()->dropIfExists('countries');
    }
};
