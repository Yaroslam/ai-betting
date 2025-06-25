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
        DB::schema()->create('maps', function (Blueprint $table) {
            $table->id();
            $table->string('name', 50)->unique()->comment('Название карты (de_dust2)');
            $table->string('display_name', 100)->comment('Отображаемое название (Dust II)');
            $table->string('image_url', 255)->nullable()->comment('URL изображения карты');
            $table->boolean('is_active')->default(true)->comment('Активна ли карта в пуле');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::schema()->dropIfExists('maps');
    }
};
