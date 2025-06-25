<?php

namespace Database\Migrations\Commands;

use Illuminate\Console\Command;
use Illuminate\Database\Capsule\Manager as DB;

class MigrateResetCommand extends Command
{
    protected $signature = 'migrate:reset {--force : Force the operation to run when in production}';
    protected $description = 'Rollback all database migrations';

    public function handle()
    {
        $migrations = $this->getAllMigrations();
        
        if (empty($migrations)) {
            $this->info('Nothing to reset.');
            return 0;
        }

        $this->info('Resetting all migrations...');
        
        foreach ($migrations as $migration) {
            $this->rollbackMigration($migration);
        }

        $this->info('Reset completed successfully.');
        return 0;
    }

    protected function getAllMigrations()
    {
        $table = $_ENV['MIGRATION_TABLE'] ?? 'migrations';
        
        return DB::table($table)
            ->orderBy('batch', 'desc')
            ->orderBy('migration', 'desc')
            ->get();
    }

    protected function rollbackMigration($migration)
    {
        $this->line("Rolling back: {$migration->migration}");
        
        $migrationPath = __DIR__ . '/../../migrations/' . $migration->migration . '.php';
        
        if (file_exists($migrationPath)) {
            $migrationInstance = require $migrationPath;
            $migrationInstance->down();
        }
        
        $this->removeMigrationRecord($migration->migration);
        
        $this->info("Rolled back: {$migration->migration}");
    }

    protected function removeMigrationRecord($migration)
    {
        $table = $_ENV['MIGRATION_TABLE'] ?? 'migrations';
        
        DB::table($table)
            ->where('migration', $migration)
            ->delete();
    }
} 