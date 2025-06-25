<?php

namespace Database\Migrations\Commands;

use Illuminate\Console\Command;
use Illuminate\Database\Capsule\Manager as DB;
use Illuminate\Filesystem\Filesystem;

class MigrateCommand extends Command
{
    protected $signature = 'migrate {--force : Force the operation to run when in production}';
    protected $description = 'Run the database migrations';

    protected $filesystem;

    public function __construct()
    {
        parent::__construct();
        $this->filesystem = new Filesystem();
    }

    public function handle()
    {
        $this->createMigrationsTable();
        
        $migrations = $this->getPendingMigrations();
        
        if (empty($migrations)) {
            $this->info('Nothing to migrate.');
            return 0;
        }

        $this->info('Running migrations...');
        
        foreach ($migrations as $migration) {
            $this->runMigration($migration);
        }

        $this->info('Migrations completed successfully.');
        return 0;
    }

    protected function createMigrationsTable()
    {
        $table = $_ENV['MIGRATION_TABLE'] ?? 'migrations';
        
        if (!DB::schema()->hasTable($table)) {
            DB::schema()->create($table, function ($table) {
                $table->increments('id');
                $table->string('migration');
                $table->integer('batch');
            });
        }
    }

    protected function getPendingMigrations()
    {
        $migrationPath = __DIR__ . '/../../migrations';
        $files = $this->filesystem->glob($migrationPath . '/*.php');
        
        $migrations = [];
        foreach ($files as $file) {
            $migrationName = basename($file, '.php');
            if (!$this->hasRun($migrationName)) {
                $migrations[] = $file;
            }
        }

        sort($migrations);
        return $migrations;
    }

    protected function hasRun($migration)
    {
        $table = $_ENV['MIGRATION_TABLE'] ?? 'migrations';
        
        return DB::table($table)
            ->where('migration', $migration)
            ->exists();
    }

    protected function runMigration($file)
    {
        $migrationName = basename($file, '.php');
        
        $this->line("Migrating: {$migrationName}");
        
        $migration = require $file;
        $migration->up();
        
        $this->recordMigration($migrationName);
        
        $this->info("Migrated: {$migrationName}");
    }

    protected function recordMigration($migration)
    {
        $table = $_ENV['MIGRATION_TABLE'] ?? 'migrations';
        $batch = $this->getNextBatchNumber();
        
        DB::table($table)->insert([
            'migration' => $migration,
            'batch' => $batch,
        ]);
    }

    protected function getNextBatchNumber()
    {
        $table = $_ENV['MIGRATION_TABLE'] ?? 'migrations';
        
        return DB::table($table)->max('batch') + 1;
    }
} 