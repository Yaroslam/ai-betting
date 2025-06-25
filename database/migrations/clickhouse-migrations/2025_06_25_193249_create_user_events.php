<?php

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
