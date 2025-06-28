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
        // Удаляем неиспользуемые колонки из таблицы teams
        DB::schema()->table('teams', function (Blueprint $table) {
            if (DB::schema()->hasColumn('teams', 'country_code')) {
                $table->dropColumn('country_code');
            }
            if (DB::schema()->hasColumn('teams', 'country_name')) {
                $table->dropColumn('country_name');
            }
            if (DB::schema()->hasColumn('teams', 'logo_url')) {
                $table->dropColumn('logo_url');
            }
        });

        // Удаляем неиспользуемые колонки из таблицы players
        DB::schema()->table('players', function (Blueprint $table) {
            if (DB::schema()->hasColumn('players', 'country_code')) {
                $table->dropColumn('country_code');
            }
            if (DB::schema()->hasColumn('players', 'country_name')) {
                $table->dropColumn('country_name');
            }
            if (DB::schema()->hasColumn('players', 'age')) {
                $table->dropColumn('age');
            }
            if (DB::schema()->hasColumn('players', 'avatar_url')) {
                $table->dropColumn('avatar_url');
            }
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        // Возвращаем колонки в таблицу teams
        DB::schema()->table('teams', function (Blueprint $table) {
            $table->string('country_code', 3)->nullable()->comment('Код страны');
            $table->string('country_name', 100)->nullable()->comment('Название страны');
            $table->string('logo_url', 255)->nullable()->comment('URL логотипа');
        });

        // Возвращаем колонки в таблицу players
        DB::schema()->table('players', function (Blueprint $table) {
            $table->string('country_code', 3)->nullable()->comment('Код страны');
            $table->string('country_name', 100)->nullable()->comment('Название страны');
            $table->integer('age')->nullable()->comment('Возраст');
            $table->string('avatar_url', 255)->nullable()->comment('URL аватара');
        });
    }
}; 