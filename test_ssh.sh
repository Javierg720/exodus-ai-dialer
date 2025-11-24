#!/bin/bash
timeout 5 ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@46.62.216.79 "echo 'SSH connection successful'" 2>&1
