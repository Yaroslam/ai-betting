<?php

namespace Database\Migrations\Commands;

use Illuminate\Console\Command;

class MigrateRefreshCommand extends Command
{
    protected $signature = 'migrate:refresh {--force : Force the operation to run when in production}';
    protected $description = 'Reset and re-run all migrations';

    public function handle()
    {
        $this->info('Refreshing migrations...');
        
        // Reset all migrations
        $this->call('migrate:reset', ['--force' => $this->option('force')]);
        
        // Run all migrations
        $this->call('migrate', ['--force' => $this->option('force')]);
        
        $this->info('Refresh completed successfully.');
        return 0;
    }
} 