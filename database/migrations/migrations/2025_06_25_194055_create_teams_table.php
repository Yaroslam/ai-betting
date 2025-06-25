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
        DB::schema()->create('teams', function (Blueprint $table) {
            $table->id();
            $table->integer('hltv_id')->unique()->comment('ID команды на HLTV.org');
            $table->string('name', 100)->comment('Название команды');
            $table->string('tag', 10)->comment('Короткий тег (NAVI, G2)');
            $table->foreignId('country_id')->constrained('countries')->onDelete('cascade');
            $table->string('logo_url', 255)->nullable()->comment('URL логотипа');
            $table->string('hltv_url', 255)->nullable()->comment('Ссылка на HLTV');
            $table->integer('world_ranking')->nullable()->comment('Мировой рейтинг');
            $table->integer('points')->default(0)->comment('Рейтинговые очки');
            $table->boolean('is_active')->default(true)->comment('Активна ли команда');
            $table->timestamps();

            // Индексы для производительности
            $table->index('hltv_id');
            $table->index('world_ranking');
            $table->index('is_active');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::schema()->dropIfExists('teams');
    }
};
