#!/bin/bash
# EXODUS Voice AI System - Production Deployment Script
# This script helps deploy the voice AI system with proper configuration

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}EXODUS Voice AI - Production Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}No .env file found. Creating from .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env file${NC}"
        echo -e "${YELLOW}⚠ IMPORTANT: Edit .env and add your API keys before deploying!${NC}"
        echo -e "${YELLOW}   - DEEPGRAM_API_KEY${NC}"
        echo -e "${YELLOW}   - GROQ_API_KEY${NC}"
        echo -e "${YELLOW}   - CEREBRAS_API_KEY (optional)${NC}"
        echo ""
        read -p "Press ENTER to open .env for editing (or Ctrl+C to exit)..."
        ${EDITOR:-nano} .env
    else
        echo -e "${RED}✗ .env.example not found!${NC}"
        exit 1
    fi
fi

# Validate required env vars
echo -e "${BLUE}Validating environment variables...${NC}"
source .env

MISSING_VARS=()
if [ -z "$DEEPGRAM_API_KEY" ] || [ "$DEEPGRAM_API_KEY" = "your_deepgram_api_key_here" ]; then
    MISSING_VARS+=("DEEPGRAM_API_KEY")
fi

if [ -z "$GROQ_API_KEY" ] || [ "$GROQ_API_KEY" = "your_groq_api_key_here" ]; then
    MISSING_VARS+=("GROQ_API_KEY")
fi

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo -e "${RED}✗ Missing or invalid API keys:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo -e "${RED}  - $var${NC}"
    done
    echo ""
    echo -e "${YELLOW}Please edit .env and add your API keys, then run this script again.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Required API keys configured${NC}"
echo ""

# Ask what to do
echo -e "${BLUE}What would you like to do?${NC}"
echo "1) Deploy all services (ASR + LLM + TTS + 20 Bots)"
echo "2) Deploy provider services only (ASR + LLM + TTS)"
echo "3) Deploy bot instances only (requires providers running)"
echo "4) Check service status"
echo "5) View logs"
echo "6) Stop all services"
echo "7) Restart all services"
echo "8) Validate configuration"
echo ""
read -p "Enter your choice [1-8]: " choice

case $choice in
    1)
        echo -e "${BLUE}Deploying all services...${NC}"
        docker-compose -f docker-compose-avr-production.yml up -d
        echo ""
        echo -e "${GREEN}✓ All services deployed${NC}"
        echo ""
        echo -e "${BLUE}Waiting for services to become healthy...${NC}"
        sleep 10
        docker-compose -f docker-compose-avr-production.yml ps
        ;;
        
    2)
        echo -e "${BLUE}Deploying provider services...${NC}"
        docker-compose -f docker-compose-avr-production.yml up -d avr-asr avr-llm avr-tts
        echo ""
        echo -e "${GREEN}✓ Provider services deployed${NC}"
        echo ""
        docker-compose -f docker-compose-avr-production.yml ps avr-asr avr-llm avr-tts
        ;;
        
    3)
        echo -e "${BLUE}Deploying bot instances...${NC}"
        BOT_SERVICES=$(docker-compose -f docker-compose-avr-production.yml config --services | grep "avr-bot-")
        docker-compose -f docker-compose-avr-production.yml up -d $BOT_SERVICES
        echo ""
        echo -e "${GREEN}✓ Bot instances deployed${NC}"
        echo ""
        docker-compose -f docker-compose-avr-production.yml ps | grep "avr-bot-"
        ;;
        
    4)
        echo -e "${BLUE}Service Status:${NC}"
        echo ""
        docker-compose -f docker-compose-avr-production.yml ps
        echo ""
        echo -e "${BLUE}Health Status:${NC}"
        docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "avr-(asr|llm|tts|bot)"
        ;;
        
    5)
        echo -e "${BLUE}Which logs would you like to view?${NC}"
        echo "1) All services"
        echo "2) ASR service"
        echo "3) LLM service"
        echo "4) TTS service"
        echo "5) Bot instances"
        read -p "Enter choice [1-5]: " log_choice
        
        case $log_choice in
            1) docker-compose -f docker-compose-avr-production.yml logs -f ;;
            2) docker-compose -f docker-compose-avr-production.yml logs -f avr-asr ;;
            3) docker-compose -f docker-compose-avr-production.yml logs -f avr-llm ;;
            4) docker-compose -f docker-compose-avr-production.yml logs -f avr-tts ;;
            5) 
                BOT_SERVICES=$(docker-compose -f docker-compose-avr-production.yml config --services | grep "avr-bot-")
                docker-compose -f docker-compose-avr-production.yml logs -f $BOT_SERVICES
                ;;
            *) echo -e "${RED}Invalid choice${NC}" ;;
        esac
        ;;
        
    6)
        echo -e "${YELLOW}Stopping all services...${NC}"
        docker-compose -f docker-compose-avr-production.yml down
        echo -e "${GREEN}✓ All services stopped${NC}"
        ;;
        
    7)
        echo -e "${YELLOW}Restarting all services...${NC}"
        docker-compose -f docker-compose-avr-production.yml restart
        echo -e "${GREEN}✓ All services restarted${NC}"
        echo ""
        docker-compose -f docker-compose-avr-production.yml ps
        ;;
        
    8)
        echo -e "${BLUE}Validating configuration...${NC}"
        docker-compose -f docker-compose-avr-production.yml config > /dev/null
        echo -e "${GREEN}✓ Configuration is valid${NC}"
        echo ""
        echo -e "${BLUE}Service ports:${NC}"
        docker-compose -f docker-compose-avr-production.yml config | grep -A 2 "ports:" | grep -E "909[2-9]|91[0-1][0-1]|601[01]|6002|6003" || true
        ;;
        
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Quick Commands:${NC}"
echo "  View status:    docker-compose -f docker-compose-avr-production.yml ps"
echo "  View logs:      docker-compose -f docker-compose-avr-production.yml logs -f"
echo "  Stop services:  docker-compose -f docker-compose-avr-production.yml down"
echo "  Check health:   docker ps --format 'table {{.Names}}\t{{.Status}}'"
echo ""
echo -e "${BLUE}Service Endpoints:${NC}"
echo "  ASR:  http://localhost:${ASR_PORT:-6010}"
echo "  LLM:  http://localhost:${GROQ_PORT:-6002}"
echo "  TTS:  http://localhost:${TTS_PORT:-6011}"
echo "  Bots: http://localhost:9092-9111"
echo ""
