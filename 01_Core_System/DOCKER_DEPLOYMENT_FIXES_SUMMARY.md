# Docker Deployment Fixes Summary

## Overview
Comprehensive fixes applied to Docker deployment configuration for production-ready deployment.

## Changes Implemented

### 1. Port Conflict Resolution ✅
**Issue**: Groq and Cerebras both using port 6002
**Fix**: 
- Groq LLM: Port 6002
- Cerebras LLM: Port 6003 (NEW)
- Added separate Cerebras service definition

### 2. Environment Variables Migration ✅
**Created**: `.env.example` with all configuration variables

**API Keys Externalized**:
- `DEEPGRAM_API_KEY` - ASR/TTS service
- `GROQ_API_KEY` - Primary LLM
- `CEREBRAS_API_KEY` - Alternative LLM

**Service Configuration**:
```bash
# ASR Service
ASR_PORT=6010
ASR_LANGUAGE=en-US
ASR_MODEL=nova-2-phonecall
ASR_SAMPLE_RATE=8000

# LLM Services
GROQ_PORT=6002
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.6

CEREBRAS_PORT=6003
CEREBRAS_MODEL=llama3.1-8b
CEREBRAS_TEMPERATURE=0.6

# TTS Service
TTS_PORT=6011
TTS_VOICE=en-US-AvaMultilingualNeural
TTS_RATE=+30%

# Bot Configuration
BOT_INTERRUPT_LISTENING=false
BOT_MIN_SPEECH_MS=150
BOT_VAD_SENSITIVITY=0
BOT_ASR_TIMEOUT_MS=2500
```

### 3. Health Checks Added ✅
**All services now include health checks**:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:${PORT}/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

**Services with health checks**:
- ✅ ASR Service (avr-asr)
- ✅ LLM Service Groq (avr-llm)
- ✅ LLM Service Cerebras (avr-llm-cerebras)
- ✅ TTS Service (avr-tts)
- ✅ All 20 Bot instances (avr-bot-9092 through 9111)

### 4. Resource Limits Configured ✅

**ASR Service**:
- Memory: 2GB limit, 1GB reservation
- CPU: 2 cores

**LLM Services** (Groq & Cerebras):
- Memory: 4GB limit, 2GB reservation
- CPU: 2 cores

**TTS Service**:
- Memory: 1GB limit, 512MB reservation
- CPU: 1 core

**Bot Services** (each):
- Memory: 512MB limit, 256MB reservation
- CPU: 0.5 cores

**Environment Variables for Customization**:
```bash
# Resource Limits
ASR_MEMORY_LIMIT=2G
ASR_MEMORY_RESERVATION=1G
ASR_CPU_LIMIT=2

LLM_MEMORY_LIMIT=4G
LLM_MEMORY_RESERVATION=2G
LLM_CPU_LIMIT=2

TTS_MEMORY_LIMIT=1G
TTS_MEMORY_RESERVATION=512M
TTS_CPU_LIMIT=1

BOT_MEMORY_LIMIT=512M
BOT_MEMORY_RESERVATION=256M
BOT_CPU_LIMIT=0.5
```

### 5. Improved Network Configuration ✅

**Standardized network aliases**:
```yaml
avr-asr:
  networks:
    avr-net:
      aliases:
        - avr-asr
        - avr-asr-deepgram

avr-llm:
  networks:
    avr-net:
      aliases:
        - avr-llm
        - avr-llm-groq

avr-llm-cerebras:
  networks:
    avr-net:
      aliases:
        - avr-llm-cerebras

avr-tts:
  networks:
    avr-net:
      aliases:
        - avr-tts
        - avr-tts-edge
```

### 6. Improved Service Dependencies ✅

**Health-check based dependencies**:
```yaml
avr-bot-9092:
  depends_on:
    avr-asr:
      condition: service_healthy
    avr-llm:
      condition: service_healthy
    avr-tts:
      condition: service_healthy
```

This ensures bots only start after provider services are healthy.

## Files Created

### 1. `.env.example`
Located at: `01_Core_System/.env.example`
- Template for environment variables
- Includes all configurable parameters
- Contains documentation for each variable
- Safe defaults provided

### 2. Backup Files
- `docker-compose-avr-production.yml.backup-[timestamp]`
- Original file preserved before changes

## Security Improvements ✅

1. **API Keys Removed from Git**:
   - Keys moved to `.env` file
   - `.env` already in `.gitignore`
   - `.env.example` committed with placeholders

2. **Secret Management**:
   ```bash
   # Copy example file
   cp .env.example .env
   
   # Edit with your actual keys
   nano .env
   
   # Verify .env is not tracked
   git status  # Should not show .env
   ```

## Deployment Instructions

### Initial Setup
```bash
cd 01_Core_System

# 1. Create environment file
cp .env.example .env

# 2. Edit with your API keys
nano .env

# 3. Update these required variables:
#    - DEEPGRAM_API_KEY=your_key_here
#    - GROQ_API_KEY=your_key_here
#    - CEREBRAS_API_KEY=your_key_here (optional)

# 4. Verify configuration
docker-compose -f docker-compose-avr-production.yml config

# 5. Start services
docker-compose -f docker-compose-avr-production.yml up -d

# 6. Monitor health
docker-compose -f docker-compose-avr-production.yml ps
docker-compose -f docker-compose-avr-production.yml logs -f
```

### Health Check Verification
```bash
# Check service health status
docker ps --format "table {{.Names}}\t{{.Status}}"

# Check specific service health
docker inspect avr-asr-deepgram --format='{{.State.Health.Status}}'
docker inspect avr-llm-groq --format='{{.State.Health.Status}}'
docker inspect avr-tts-edge --format='{{.State.Health.Status}}'

# View health check logs
docker inspect avr-asr-deepgram --format='{{json .State.Health}}' | jq
```

### Resource Monitoring
```bash
# View resource usage
docker stats

# Check specific service resources
docker stats avr-asr-deepgram avr-llm-groq avr-tts-edge

# Check all bots
docker stats $(docker ps --filter "name=avr-bot-" --format "{{.Names}}")
```

## Benefits Achieved

### 1. **Security**
- ✅ No API keys in version control
- ✅ Secrets managed via environment files
- ✅ Easy rotation without code changes

### 2. **Reliability**
- ✅ Health checks ensure service readiness
- ✅ Proper dependency ordering prevents race conditions
- ✅ Automatic restart on failure

### 3. **Resource Management**
- ✅ Memory limits prevent OOM issues
- ✅ CPU limits ensure fair resource sharing
- ✅ Reservations guarantee minimum resources

### 4. **Scalability**
- ✅ Port conflicts resolved
- ✅ Multiple LLM providers supported
- ✅ Easy to add more bot instances

### 5. **Operations**
- ✅ Consistent network aliases for service discovery
- ✅ Configurable via environment variables
- ✅ Health monitoring built-in

## Configuration Matrix

### Service Ports
| Service | Port | Configurable |
|---------|------|--------------|
| ASR (Deepgram) | 6010 | Yes (ASR_PORT) |
| LLM (Groq) | 6002 | Yes (GROQ_PORT) |
| LLM (Cerebras) | 6003 | Yes (CEREBRAS_PORT) |
| TTS (Edge) | 6011 | Yes (TTS_PORT) |
| Bots | 9092-9111 | No (Fixed) |

### Resource Allocation
| Service | Memory Limit | Memory Reserve | CPU Limit |
|---------|-------------|----------------|-----------|
| ASR | 2GB | 1GB | 2 cores |
| LLM | 4GB | 2GB | 2 cores |
| TTS | 1GB | 512MB | 1 core |
| Bot (each) | 512MB | 256MB | 0.5 cores |

**Total Resources (20 bots)**:
- Memory: ~17GB limit, ~11GB reserved
- CPU: ~16 cores limit

## Troubleshooting

### Issue: Services not starting
```bash
# Check logs
docker-compose -f docker-compose-avr-production.yml logs

# Check specific service
docker-compose -f docker-compose-avr-production.yml logs avr-asr

# Verify environment variables loaded
docker-compose -f docker-compose-avr-production.yml config | grep -A 5 environment
```

### Issue: Health checks failing
```bash
# Check if service is responding
curl http://localhost:6010/health  # ASR
curl http://localhost:6002/health  # LLM Groq
curl http://localhost:6011/health  # TTS

# View detailed health status
docker inspect avr-asr-deepgram --format='{{json .State.Health}}' | jq
```

### Issue: Port conflicts
```bash
# Check what's using ports
sudo netstat -tlnp | grep -E '6010|6002|6003|6011|909[2-9]|91[0-1][0-1]'

# Or using lsof
sudo lsof -i :6010
sudo lsof -i :6002
```

### Issue: Resource limits too restrictive
Edit `.env` file and adjust:
```bash
# Increase memory limits
ASR_MEMORY_LIMIT=4G
LLM_MEMORY_LIMIT=8G

# Restart services
docker-compose -f docker-compose-avr-production.yml up -d
```

## Next Steps

1. **Create .env file**: Copy `.env.example` and add your API keys
2. **Review resource limits**: Adjust based on your server capacity
3. **Test deployment**: Start services and verify health checks
4. **Monitor performance**: Use `docker stats` to track resource usage
5. **Optimize as needed**: Adjust resource limits and configuration

## Additional Notes

- Health check intervals can be customized via environment variables
- Consider implementing Prometheus metrics endpoint in services
- Set up log aggregation for production monitoring
- Implement backup strategy for configuration files
- Document disaster recovery procedures

## References

- Docker Compose Documentation: https://docs.docker.com/compose/
- Docker Health Checks: https://docs.docker.com/engine/reference/builder/#healthcheck
- Resource Constraints: https://docs.docker.com/compose/compose-file/#resources
