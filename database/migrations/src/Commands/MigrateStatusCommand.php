<?php

namespace Database\Migrations\Commands;

use Illuminate\Console\Command;
use Illuminate\Database\Capsule\Manager as DB;
use Illuminate\Filesystem\Filesystem;

class MigrateStatusCommand extends Command
{
    protected $signature = 'migrate:status';
    protected $description = 'Show the status of each migration';

    protected $filesystem;

    public function __construct()
    {
        parent::__construct();
        $this->filesystem = new Filesystem();
    }

    public function handle()
    {
        if (!$this->migrationsTableExists()) {
            $this->error('No migrations found.');
            return 1;
        }

        $migrations = $this->getAllMigrations();
        
        if (empty($migrations)) {
            $this->info('No migrations found.');
            return 0;
        }

        $this->displayMigrations($migrations);
        return 0;
    }

    protected function migrationsTableExists()
    {
        $table = $_ENV['MIGRATION_TABLE'] ?? 'migrations';
        return DB::schema()->hasTable($table);
    }

    protected function getAllMigrations()
    {
        $migrationPath = __DIR__ . '/../../migrations';
        $files = $this->filesystem->glob($migrationPath . '/*.php');
        
        $migrations = [];
        foreach ($files as $file) {
            $migrationName = basename($file, '.php');
            $migrations[] = [
                'migration' => $migrationName,
                'ran' => $this->hasRun($migrationName),
                'batch' => $this->getBatch($migrationName),
            ];
        }

        return $migrations;
    }

    protected function hasRun($migration)
    {
        $table = $_ENV['MIGRATION_TABLE'] ?? 'migrations';
        
        return DB::table($table)
            ->where('migration', $migration)
            ->exists();
    }

    protected function getBatch($migration)
    {
        $table = $_ENV['MIGRATION_TABLE'] ?? 'migrations';
        
        $record = DB::table($table)
            ->where('migration', $migration)
            ->first();
            
        return $record ? $record->batch : null;
    }

    protected function displayMigrations($migrations)
    {
        $this->line('+------+' . str_repeat('-', 50) . '+--------+');
        $this->line('| Ran? | Migration' . str_repeat(' ', 41) . '| Batch  |');
        $this->line('+------+' . str_repeat('-', 50) . '+--------+');

        foreach ($migrations as $migration) {
            $ran = $migration['ran'] ? 'Yes' : 'No';
            $batch = $migration['batch'] ?? 'N/A';
            
            $migrationName = strlen($migration['migration']) > 48 
                ? substr($migration['migration'], 0, 45) . '...' 
                : $migration['migration'];
            
            $this->line(sprintf(
                '| %-4s | %-48s | %-6s |',
                $ran,
                $migrationName,
                $batch
            ));
        }

        $this->line('+------+' . str_repeat('-', 50) . '+--------+');
    }
} 