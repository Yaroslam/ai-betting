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
        // 1. Обновляем таблицу teams - добавляем поля стран и удаляем внешний ключ
        DB::schema()->table('teams', function (Blueprint $table) {
            // Добавляем новые поля для хранения информации о стране
            $table->string('country_code', 3)->nullable()->comment('Код страны');
            $table->string('country_name', 100)->nullable()->comment('Название страны');
        });

        // Копируем данные из таблицы countries в teams
        DB::statement('
            UPDATE teams 
            SET country_code = countries.code, 
                country_name = countries.name
            FROM countries 
            WHERE teams.country_id = countries.id
        ');

        // Удаляем внешний ключ и поле country_id из teams
        DB::schema()->table('teams', function (Blueprint $table) {
            $table->dropForeign(['country_id']);
            $table->dropColumn('country_id');
        });

        // 2. Обновляем таблицу players - добавляем поля стран и удаляем внешний ключ
        DB::schema()->table('players', function (Blueprint $table) {
            // Добавляем новые поля для хранения информации о стране
            $table->string('country_code', 3)->nullable()->comment('Код страны');
            $table->string('country_name', 100)->nullable()->comment('Название страны');
        });

        // Копируем данные из таблицы countries в players
        DB::statement('
            UPDATE players 
            SET country_code = countries.code, 
                country_name = countries.name
            FROM countries 
            WHERE players.country_id = countries.id
        ');

        // Удаляем внешний ключ и поле country_id из players
        DB::schema()->table('players', function (Blueprint $table) {
            $table->dropForeign(['country_id']);
            $table->dropColumn('country_id');
        });

        // 3. Обновляем таблицу events - добавляем поля типа события и удаляем внешний ключ
        DB::schema()->table('events', function (Blueprint $table) {
            // Добавляем новые поля для хранения информации о типе события
            $table->string('event_type', 50)->nullable()->comment('Тип турнира');
            $table->string('tier', 20)->nullable()->comment('Уровень турнира (S, A, B, C)');
        });

        // Копируем данные из таблицы event_types в events
        DB::statement('
            UPDATE events 
            SET event_type = event_types.name, 
                tier = event_types.tier
            FROM event_types 
            WHERE events.event_type_id = event_types.id
        ');

        // Удаляем внешний ключ и поле event_type_id из events
        DB::schema()->table('events', function (Blueprint $table) {
            $table->dropForeign(['event_type_id']);
            $table->dropColumn('event_type_id');
        });

        // 4. Добавляем поле event_name в таблицу matches для быстрого доступа
        DB::schema()->table('matches', function (Blueprint $table) {
            $table->string('event_name', 200)->nullable()->comment('Название события');
        });

        // Копируем названия событий в matches
        DB::statement('
            UPDATE matches 
            SET event_name = events.name
            FROM events 
            WHERE matches.event_id = events.id
        ');

        // 5. Удаляем таблицы countries и event_types
        DB::schema()->dropIfExists('countries');
        DB::schema()->dropIfExists('event_types');
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        // 1. Восстанавливаем таблицу countries
        DB::schema()->create('countries', function (Blueprint $table) {
            $table->id();
            $table->string('code', 3)->unique()->comment('ISO 3166-1 alpha-3 код');
            $table->string('name', 100)->comment('Название страны');
            $table->string('flag_url', 255)->nullable()->comment('URL флага');
            $table->timestamps();
        });

        // 2. Восстанавливаем таблицу event_types
        DB::schema()->create('event_types', function (Blueprint $table) {
            $table->id();
            $table->string('name', 100)->unique()->comment('Название типа турнира');
            $table->string('tier', 20)->comment('Уровень турнира (S, A, B, C)');
            $table->timestamps();
        });

        // 3. Восстанавливаем связи в таблице teams
        DB::schema()->table('teams', function (Blueprint $table) {
            $table->foreignId('country_id')->nullable()->constrained('countries')->onDelete('cascade');
        });

        // 4. Восстанавливаем связи в таблице players
        DB::schema()->table('players', function (Blueprint $table) {
            $table->foreignId('country_id')->nullable()->constrained('countries')->onDelete('cascade');
        });

        // 5. Восстанавливаем связи в таблице events
        DB::schema()->table('events', function (Blueprint $table) {
            $table->foreignId('event_type_id')->nullable()->constrained('event_types')->onDelete('cascade');
        });

        // 6. Удаляем новые поля
        DB::schema()->table('teams', function (Blueprint $table) {
            $table->dropColumn(['country_code', 'country_name']);
        });

        DB::schema()->table('players', function (Blueprint $table) {
            $table->dropColumn(['country_code', 'country_name']);
        });

        DB::schema()->table('events', function (Blueprint $table) {
            $table->dropColumn(['event_type', 'tier']);
        });

        DB::schema()->table('matches', function (Blueprint $table) {
            $table->dropColumn('event_name');
        });
    }
}; 