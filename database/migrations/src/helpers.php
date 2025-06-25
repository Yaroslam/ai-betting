<?php

if (!function_exists('studly_case')) {
    function studly_case($value) {
        return str_replace(' ', '', ucwords(str_replace(['-', '_'], ' ', $value)));
    }
}

if (!function_exists('snake_case')) {
    function snake_case($value) {
        return strtolower(preg_replace('/(?<!^)[A-Z]/', '_$0', $value));
    }
} 