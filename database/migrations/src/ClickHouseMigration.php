<?php

namespace Database\Migrations;

abstract class ClickHouseMigration
{
    /**
     * Run the migrations.
     */
    abstract public function up(): void;

    /**
     * Reverse the migrations.
     */
    abstract public function down(): void;

    /**
     * Execute a ClickHouse query.
     */
    protected function execute(string $sql): array
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

    /**
     * Get ClickHouse connection configuration.
     */
    protected function getClickHouseConnection(): array
    {
        return [
            'host' => $_ENV['CLICKHOUSE_HOST'] ?? 'localhost',
            'port' => $_ENV['CLICKHOUSE_PORT'] ?? '8123',
            'username' => $_ENV['CLICKHOUSE_USERNAME'] ?? 'default',
            'password' => $_ENV['CLICKHOUSE_PASSWORD'] ?? '',
            'database' => $_ENV['CLICKHOUSE_DATABASE'] ?? 'default',
        ];
    }

    /**
     * Create a table in ClickHouse.
     */
    protected function createTable(string $tableName, string $schema, string $engine = 'MergeTree()', string $orderBy = 'id'): void
    {
        $sql = "CREATE TABLE IF NOT EXISTS {$tableName} ({$schema}) ENGINE = {$engine} ORDER BY {$orderBy}";
        $this->execute($sql);
    }

    /**
     * Drop a table in ClickHouse.
     */
    protected function dropTable(string $tableName): void
    {
        $sql = "DROP TABLE IF EXISTS {$tableName}";
        $this->execute($sql);
    }

    /**
     * Add an index to a table.
     */
    protected function addIndex(string $tableName, string $indexName, string $column, string $type = 'bloom_filter'): void
    {
        $sql = "ALTER TABLE {$tableName} ADD INDEX {$indexName} {$column} TYPE {$type} GRANULARITY 1";
        $this->execute($sql);
    }

    /**
     * Drop an index from a table.
     */
    protected function dropIndex(string $tableName, string $indexName): void
    {
        $sql = "ALTER TABLE {$tableName} DROP INDEX {$indexName}";
        $this->execute($sql);
    }
} 