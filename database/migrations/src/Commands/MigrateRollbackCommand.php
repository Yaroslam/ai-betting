<?php

namespace Database\Migrations\Commands;

use Illuminate\Console\Command;
use Illuminate\Database\Capsule\Manager as DB;

class MigrateRollbackCommand extends Command
{
    protected $signature = 'migrate:rollback {--steps=1 : Number of migrations to rollback}';
    protected $description = 'Rollback the last database migration';

    public function handle()
    {
        $steps = (int) $this->option('steps');
        
        $migrations = $this->getMigrationsToRollback($steps);
        
        if (empty($migrations)) {
            $this->info('Nothing to rollback.');
            return 0;
        }

        $this->info('Rolling back migrations...');
        
        foreach ($migrations as $migration) {
            $this->rollbackMigration($migration);
        }

        $this->info('Rollback completed successfully.');
        return 0;
    }

    protected function getMigrationsToRollback($steps)
    {
        $table = $_ENV['MIGRATION_TABLE'] ?? 'migrations';
        
        $lastBatch = DB::table($table)->max('batch');
        
        if ($steps === 1) {
            return DB::table($table)
                ->where('batch', $lastBatch)
                ->orderBy('migration', 'desc')
                ->get();
        }

        return DB::table($table)
            ->orderBy('batch', 'desc')
            ->orderBy('migration', 'desc')
            ->limit($steps)
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