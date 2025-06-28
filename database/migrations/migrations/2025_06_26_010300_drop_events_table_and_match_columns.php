<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Capsule\Manager as DB;

return new class extends Migration
{
    public function up(): void
    {
        // Удаляем внешние ключи и колонки из matches
        DB::schema()->table('matches', function (Blueprint $table) {
            if (DB::schema()->hasColumn('matches', 'event_id')) {
                $table->dropForeign(['event_id']);
                $table->dropColumn('event_id');
            }
            if (DB::schema()->hasColumn('matches', 'event_name')) {
                $table->dropColumn('event_name');
            }
            if (DB::schema()->hasColumn('matches', 'match_type')) {
                $table->dropColumn('match_type');
            }
        });

        // Удаляем таблицу events, если существует
        if (DB::schema()->hasTable('events')) {
            DB::schema()->dropIfExists('events');
        }
    }

    public function down(): void
    {
        // Восстанавливаем таблицу events
        DB::schema()->create('events', function (Blueprint $table) {
            $table->id();
            $table->integer('hltv_id')->unique();
            $table->string('name', 200);
            $table->timestamps();
        });

        // Восстанавливаем колонки в matches
        DB::schema()->table('matches', function (Blueprint $table) {
            $table->unsignedBigInteger('event_id')->nullable();
            $table->string('event_name', 200)->nullable();
            $table->string('match_type', 50)->nullable();
            $table->foreign('event_id')->references('id')->on('events')->onDelete('cascade');
        });
    }
}; 