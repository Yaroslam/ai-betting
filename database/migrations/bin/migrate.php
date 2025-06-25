#!/usr/bin/env php
<?php

require_once __DIR__ . '/../vendor/autoload.php';

use ByJG\DbMigration\Migration;
use ByJG\Util\Uri;

// Load environment variables
if (file_exists(__DIR__ . '/../.env')) {
    $lines = file(__DIR__ . '/../.env', FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        if (strpos($line, '=') !== false && !str_starts_with($line, '#')) {
            putenv($line);
        }
    }
}

class CS2MigrationManager
{
    private string $database;
    private array $config;

    public function __construct(string $database)
    {
        $this->database = $database;
        $this->loadConfig();
    }

    private function loadConfig(): void
    {
        if ($this->database !== 'postgres') {
            throw new InvalidArgumentException("Only PostgreSQL is currently supported");
        }

        $this->config = [
            'host' => getenv('POSTGRES_HOST') ?: 'localhost',
            'port' => getenv('POSTGRES_PORT') ?: '5432',
            'database' => getenv('POSTGRES_DB') ?: 'cs2_prediction',
            'username' => getenv('POSTGRES_USER') ?: 'cs2_user',
            'password' => getenv('POSTGRES_PASSWORD') ?: 'cs2_password',
            'migrations_path' => __DIR__ . '/../migrations/postgres'
        ];
    }

    public function getMigration(): Migration
    {
        $connectionUri = $this->getConnectionUri();
        
        // Create migration instance without registering database (let library handle it)
        $migration = new Migration($connectionUri, $this->config['migrations_path']);
        
        // Add progress callback
        $migration->addCallbackProgress(function ($action, $currentVersion, $fileInfo) {
            $status = $fileInfo['exists'] ? '✓' : '✗';
            echo sprintf(
                "[%s] %s v%s: %s (%s)\n",
                strtoupper($this->database),
                $action,
                $currentVersion,
                $fileInfo['description'] ?? 'Migration',
                $status
            );
        });

        return $migration;
    }

    private function getConnectionUri(): Uri
    {
        $dsn = sprintf(
            'pdo://pgsql:host=%s;port=%s;dbname=%s?user=%s&password=%s',
            $this->config['host'],
            $this->config['port'],
            $this->config['database'],
            $this->config['username'],
            $this->config['password']
        );

        return new Uri($dsn);
    }

    public function createMigration(string $name): void
    {
        $timestamp = date('YmdHis');
        $filename = sprintf('%s_%s.sql', $timestamp, $this->sanitizeName($name));
        
        $migrationsDir = $this->config['migrations_path'];
        $upDir = $migrationsDir . '/up';
        $downDir = $migrationsDir . '/down';

        // Create directories if they don't exist
        if (!is_dir($upDir)) {
            mkdir($upDir, 0755, true);
        }
        if (!is_dir($downDir)) {
            mkdir($downDir, 0755, true);
        }

        // Create UP migration file
        $upFile = $upDir . '/' . $filename;
        $upContent = $this->getMigrationTemplate($name, 'up');
        file_put_contents($upFile, $upContent);

        // Create DOWN migration file
        $downFile = $downDir . '/' . $timestamp . '.sql';
        $downContent = $this->getMigrationTemplate($name, 'down');
        file_put_contents($downFile, $downContent);

        echo "✓ Created migration files:\n";
        echo "  UP:   {$upFile}\n";
        echo "  DOWN: {$downFile}\n";
    }

    private function sanitizeName(string $name): string
    {
        return strtolower(preg_replace('/[^a-zA-Z0-9_]/', '_', $name));
    }

    private function getMigrationTemplate(string $name, string $direction): string
    {
        $comment = ucfirst($direction) . ' migration: ' . $name;
        return "-- {$comment}\n-- PostgreSQL Migration\n\n-- Add your {$direction} migration SQL here\n\n";
    }

    public function showStatus(): void
    {
        try {
            $migration = $this->getMigration();
            $currentVersion = $migration->getCurrentVersion();
            
            echo "=== {$this->database} Migration Status ===\n";
            echo "Current Version: {$currentVersion}\n";
            echo "Database: {$this->config['database']}\n";
            echo "Host: {$this->config['host']}:{$this->config['port']}\n";
            echo "Migrations Path: {$this->config['migrations_path']}\n";
            
        } catch (Exception $e) {
            echo "Error getting status: " . $e->getMessage() . "\n";
            echo "Make sure your database is running and credentials are correct in .env file\n";
        }
    }
}

// Main execution
function main(array $argv): void
{
    if (count($argv) < 2) {
        showUsage();
        exit(1);
    }

    $database = $argv[1];
    $command = $argv[2] ?? 'migrate';

    if ($database !== 'postgres') {
        echo "Error: Only 'postgres' database is currently supported\n";
        showUsage();
        exit(1);
    }

    try {
        $manager = new CS2MigrationManager($database);

        switch ($command) {
            case 'migrate':
            case '--migrate':
                echo "Running migrations for {$database}...\n";
                $migration = $manager->getMigration();
                $migration->update();
                echo "✓ Migrations completed successfully!\n";
                break;

            case 'status':
            case '--status':
                $manager->showStatus();
                break;

            case 'reset':
            case '--reset':
                echo "Resetting {$database} database...\n";
                $migration = $manager->getMigration();
                $migration->reset();
                echo "✓ Database reset completed!\n";
                break;

            case 'create':
            case '--create':
                $name = $argv[3] ?? 'new_migration';
                echo "Creating new migration for {$database}: {$name}\n";
                $manager->createMigration($name);
                break;

            default:
                echo "Error: Unknown command '{$command}'\n";
                showUsage();
                exit(1);
        }

    } catch (Exception $e) {
        echo "Error: " . $e->getMessage() . "\n";
        exit(1);
    }
}

function showUsage(): void
{
    echo "CS2 Prediction System - Database Migration Tool\n\n";
    echo "Usage:\n";
    echo "  php migrate.php <database> [command] [options]\n\n";
    echo "Databases:\n";
    echo "  postgres    - PostgreSQL database (main application data)\n\n";
    echo "Commands:\n";
    echo "  migrate     - Run pending migrations (default)\n";
    echo "  status      - Show current migration status\n";
    echo "  reset       - Reset database and run all migrations\n";
    echo "  create      - Create new migration files\n\n";
    echo "Examples:\n";
    echo "  php migrate.php postgres migrate\n";
    echo "  php migrate.php postgres status\n";
    echo "  php migrate.php postgres create \"add_users_table\"\n";
}

// Run the script
main($argv); 