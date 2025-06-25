<?php

namespace Database\Migrations\Commands;

use Illuminate\Console\Command;
use Illuminate\Filesystem\Filesystem;

class ClickHouseMakeMigrationCommand extends Command
{
    protected $signature = 'make:clickhouse-migration {name : The name of the migration}';
    protected $description = 'Create a new ClickHouse migration file';

    protected $filesystem;

    public function __construct(Filesystem $filesystem)
    {
        parent::__construct();
        $this->filesystem = $filesystem;
    }

    public function handle()
    {
        $name = $this->argument('name');

        $migrationPath = $this->getMigrationPath();
        $className = $this->getClassName($name);
        $filename = $this->getFilename($name);

        if ($this->filesystem->exists($migrationPath . '/' . $filename)) {
            $this->error('Migration already exists!');
            return 1;
        }

        $stub = $this->getStub();
        $stub = $this->replacePlaceholders($stub, $className);

        $this->filesystem->put($migrationPath . '/' . $filename, $stub);

        $this->info("Created ClickHouse Migration: {$filename}");
        return 0;
    }

    protected function getMigrationPath()
    {
        return __DIR__ . '/../../clickhouse-migrations';
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

    protected function getStub()
    {
        return '<?php

use Database\Migrations\ClickHouseMigration;

return new class extends ClickHouseMigration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        // Add your ClickHouse migration logic here
        // Example:
        // $this->execute("CREATE TABLE example_table (
        //     id UInt64,
        //     name String,
        //     created_at DateTime DEFAULT now()
        // ) ENGINE = MergeTree()
        // ORDER BY id");
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        // Add your ClickHouse rollback logic here
        // Example:
        // $this->execute("DROP TABLE IF EXISTS example_table");
    }
};
';
    }

    protected function replacePlaceholders($stub, $className)
    {
        $stub = str_replace('{{class}}', $className, $stub);
        return $stub;
    }
}

 