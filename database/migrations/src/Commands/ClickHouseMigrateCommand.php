<?php

namespace Database\Migrations\Commands;

use Illuminate\Console\Command;
use Illuminate\Filesystem\Filesystem;

class ClickHouseMigrateCommand extends Command
{
    protected $signature = 'migrate:clickhouse {--force : Force the operation to run when in production}';
    protected $description = 'Run the ClickHouse migrations';

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

        $this->info('Running ClickHouse migrations...');
        
        foreach ($migrations as $migration) {
            $this->runMigration($migration);
        }

        $this->info('ClickHouse migrations completed successfully.');
        return 0;
    }

    protected function createMigrationsTable()
    {
        $table = $_ENV['CLICKHOUSE_MIGRATION_TABLE'] ?? 'clickhouse_migrations';
        
        $ch = $this->getClickHouseConnection();
        
        $sql = "CREATE TABLE IF NOT EXISTS {$table} (
            id UInt64,
            migration String,
            batch UInt32,
            created_at DateTime DEFAULT now()
        ) ENGINE = MergeTree()
        ORDER BY id";
        
        $this->executeClickHouseQuery($sql);
    }

    protected function getPendingMigrations()
    {
        $migrationPath = __DIR__ . '/../../clickhouse-migrations';
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
        $table = $_ENV['CLICKHOUSE_MIGRATION_TABLE'] ?? 'clickhouse_migrations';
        
        $sql = "SELECT COUNT(*) as count FROM {$table} WHERE migration = '{$migration}'";
        $result = $this->executeClickHouseQuery($sql);
        
        return ($result[0]['count'] ?? 0) > 0;
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
        $table = $_ENV['CLICKHOUSE_MIGRATION_TABLE'] ?? 'clickhouse_migrations';
        $batch = $this->getNextBatchNumber();
        
        $sql = "INSERT INTO {$table} (id, migration, batch) VALUES ({$this->getNextId()}, '{$migration}', {$batch})";
        $this->executeClickHouseQuery($sql);
    }

    protected function getNextBatchNumber()
    {
        $table = $_ENV['CLICKHOUSE_MIGRATION_TABLE'] ?? 'clickhouse_migrations';
        
        $sql = "SELECT MAX(batch) as max_batch FROM {$table}";
        $result = $this->executeClickHouseQuery($sql);
        
        return ($result[0]['max_batch'] ?? 0) + 1;
    }

    protected function getNextId()
    {
        $table = $_ENV['CLICKHOUSE_MIGRATION_TABLE'] ?? 'clickhouse_migrations';
        
        $sql = "SELECT MAX(id) as max_id FROM {$table}";
        $result = $this->executeClickHouseQuery($sql);
        
        return ($result[0]['max_id'] ?? 0) + 1;
    }

    protected function getClickHouseConnection()
    {
        $host = $_ENV['CLICKHOUSE_HOST'] ?? 'localhost';
        $port = $_ENV['CLICKHOUSE_PORT'] ?? '8123';
        $username = $_ENV['CLICKHOUSE_USERNAME'] ?? 'default';
        $password = $_ENV['CLICKHOUSE_PASSWORD'] ?? '';
        $database = $_ENV['CLICKHOUSE_DATABASE'] ?? 'default';
        
        return [
            'host' => $host,
            'port' => $port,
            'username' => $username,
            'password' => $password,
            'database' => $database,
        ];
    }

    protected function executeClickHouseQuery($sql)
    {
        $config = $this->getClickHouseConnection();
        
        $url = "http://{$config['host']}:{$config['port']}/";
        
        $postData = [
            'query' => $sql,
            'database' => $config['database'],
        ];
        
        if (!empty($config['username'])) {
            $postData['user'] = $config['username'];
        }
        
        if (!empty($config['password'])) {
            $postData['password'] = $config['password'];
        }
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($postData));
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/x-www-form-urlencoded']);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode !== 200) {
            throw new \Exception("ClickHouse query failed: {$response}");
        }
        
        // Parse response if it's JSON
        $decoded = json_decode($response, true);
        return $decoded ?: [];
    }
} 