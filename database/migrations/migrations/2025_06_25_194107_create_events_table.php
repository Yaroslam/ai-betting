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
        DB::schema()->create('events', function (Blueprint $table) {
            $table->id();
            $table->integer('hltv_id')->unique()->comment('ID события на HLTV.org');
            $table->string('name', 200)->comment('Название турнира');
            $table->foreignId('event_type_id')->constrained('event_types')->onDelete('cascade');
            $table->date('start_date')->comment('Дата начала');
            $table->date('end_date')->comment('Дата окончания');
            $table->integer('prize_pool')->nullable()->comment('Призовой фонд в USD');
            $table->string('location', 100)->nullable()->comment('Место проведения');
            $table->string('hltv_url', 255)->nullable()->comment('Ссылка на HLTV');
            $table->boolean('is_completed')->default(false)->comment('Завершен ли турнир');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::schema()->dropIfExists('events');
    }
};
