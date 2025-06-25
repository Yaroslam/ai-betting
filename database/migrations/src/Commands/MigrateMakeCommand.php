<?php

namespace Database\Migrations\Commands;

use Illuminate\Console\Command;
use Illuminate\Filesystem\Filesystem;

class MigrateMakeCommand extends Command
{
    protected $signature = 'make:migration {name : The name of the migration}
                            {--create= : The table to be created}
                            {--table= : The table to migrate}';

    protected $description = 'Create a new migration file';

    protected $filesystem;

    public function __construct(Filesystem $filesystem)
    {
        parent::__construct();
        $this->filesystem = $filesystem;
    }

    public function handle()
    {
        $name = $this->argument('name');
        $table = $this->option('table');
        $create = $this->option('create');

        $migrationPath = $this->getMigrationPath();
        $className = $this->getClassName($name);
        $filename = $this->getFilename($name);

        if ($this->filesystem->exists($migrationPath . '/' . $filename)) {
            $this->error('Migration already exists!');
            return 1;
        }

        $stub = $this->getStub($table, $create);
        $stub = $this->replacePlaceholders($stub, $className, $table, $create);

        $this->filesystem->put($migrationPath . '/' . $filename, $stub);

        $this->info("Created Migration: {$filename}");
        return 0;
    }

    protected function getMigrationPath()
    {
        return __DIR__ . '/../../migrations';
    }

    protected function getClassName($name)
    {
        return studly_case($name);
    }

    protected function getFilename($name)
    {
        $timestamp = date('Y_m_d_His');
        $name = snake_case($name);
        return "{$timestamp}_{$name}.php";
    }

    protected function getStub($table, $create)
    {
        if ($create) {
            return $this->getCreateStub();
        } elseif ($table) {
            return $this->getUpdateStub();
        }

        return $this->getBlankStub();
    }

    protected function getCreateStub()
    {
        return '<?php

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
        DB::schema()->create(\'{{table}}\', function (Blueprint $table) {
            $table->id();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::schema()->dropIfExists(\'{{table}}\');
    }
};
';
    }

    protected function getUpdateStub()
    {
        return '<?php

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
        DB::schema()->table(\'{{table}}\', function (Blueprint $table) {
            // Add your migration logic here
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::schema()->table(\'{{table}}\', function (Blueprint $table) {
            // Add your rollback logic here
        });
    }
};
';
    }

    protected function getBlankStub()
    {
        return '<?php

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
        // Add your migration logic here
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        // Add your rollback logic here
    }
};
';
    }

    protected function replacePlaceholders($stub, $className, $table, $create)
    {
        $stub = str_replace('{{class}}', $className, $stub);
        $stub = str_replace('{{table}}', $table ?: $create, $stub);

        return $stub;
    }
}

 