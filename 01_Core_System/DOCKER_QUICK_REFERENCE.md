# Docker Deployment - Quick Reference

## Files Created

1. **`.env.example`** - Environment variable template with all configuration options
2. **`deploy.sh`** - Interactive deployment script
3. **`DOCKER_DEPLOYMENT_FIXES_SUMMARY.md`** - Detailed documentation of all changes

## Quick Start

```bash
cd 01_Core_System

# 1. Create environment file
cp .env.example .env

# 2. Edit with your API keys
nano .env

# 3. Run deployment script
./deploy.sh
```

## Key Improvements

### 1. Port Conflict Fixed ✅
- Groq LLM: `6002`
- Cerebras LLM: `6003` (NEW - no conflict)

### 2. Environment Variables ✅
All API keys and configuration now in `.env` file:
```bash
DEEPGRAM_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
CEREBRAS_API_KEY=your_key_here  # Optional
```

### 3. Health Checks ✅
All services have health monitoring:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:${PORT}/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### 4. Resource Limits ✅
| Service | Memory | CPU |
|---------|--------|-----|
| ASR | 2GB | 2 cores |
| LLM | 4GB | 2 cores |
| TTS | 1GB | 1 core |
| Bot (each) | 512MB | 0.5 cores |

### 5. Network Aliases ✅
Standardized service discovery:
- `avr-asr` / `avr-asr-deepgram`
- `avr-llm` / `avr-llm-groq`
- `avr-llm-cerebras`
- `avr-tts` / `avr-tts-edge`

## Manual Commands

### Deploy Services
```bash
# All services
docker-compose -f docker-compose-avr-production.yml up -d

# Providers only (ASR + LLM + TTS)
docker-compose -f docker-compose-avr-production.yml up -d avr-asr avr-llm avr-tts

# Specific service
docker-compose -f docker-compose-avr-production.yml up -d avr-asr
```

### Check Status
```bash
# Service status
docker-compose -f docker-compose-avr-production.yml ps

# Health status
docker ps --format "table {{.Names}}\t{{.Status}}"

# Specific service health
docker inspect avr-asr-deepgram --format='{{.State.Health.Status}}'
```

### View Logs
```bash
# All services
docker-compose -f docker-compose-avr-production.yml logs -f

# Specific service
docker-compose -f docker-compose-avr-production.yml logs -f avr-asr

# Last 100 lines
docker-compose -f docker-compose-avr-production.yml logs --tail=100
```

### Resource Monitoring
```bash
# All services
docker stats

# Specific services
docker stats avr-asr-deepgram avr-llm-groq avr-tts-edge

# Continuous monitoring
watch -n 2 'docker stats --no-stream'
```

### Stop/Restart
```bash
# Stop all
docker-compose -f docker-compose-avr-production.yml down

# Stop specific service
docker-compose -f docker-compose-avr-production.yml stop avr-asr

# Restart all
docker-compose -f docker-compose-avr-production.yml restart

# Restart specific service
docker-compose -f docker-compose-avr-production.yml restart avr-asr
```

## Health Check Testing

```bash
# Test ASR health
curl http://localhost:6010/health

# Test LLM health
curl http://localhost:6002/health

# Test TTS health
curl http://localhost:6011/health

# Test bot health
curl http://localhost:9092/health
```

## Troubleshooting

### Issue: Services not starting
```bash
# Check Docker logs
docker-compose -f docker-compose-avr-production.yml logs

# Check specific service
docker logs avr-asr-deepgram

# Verify environment variables
docker-compose -f docker-compose-avr-production.yml config | grep -A 5 environment
```

### Issue: Health checks failing
```bash
# Check health status
docker inspect avr-asr-deepgram --format='{{json .State.Health}}' | jq

# View health check logs
docker inspect avr-asr-deepgram | jq '.[0].State.Health.Log'
```

### Issue: Port conflicts
```bash
# Check what's using ports
sudo netstat -tlnp | grep -E '6010|6002|6003|6011'

# Or using lsof
sudo lsof -i :6010
sudo lsof -i :6002
```

### Issue: Resource limits too low
Edit `.env` and increase:
```bash
ASR_MEMORY_LIMIT=4G
LLM_MEMORY_LIMIT=8G

# Then restart
docker-compose -f docker-compose-avr-production.yml restart
```

## Environment Variables Reference

### Required
```bash
DEEPGRAM_API_KEY=      # Required for ASR/TTS
GROQ_API_KEY=          # Required for LLM
```

### Optional
```bash
CEREBRAS_API_KEY=      # Alternative LLM provider

# Service Ports
ASR_PORT=6010
GROQ_PORT=6002
CEREBRAS_PORT=6003
TTS_PORT=6011

# ASR Configuration
ASR_LANGUAGE=en-US
ASR_MODEL=nova-2-phonecall

# LLM Configuration
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.6

# TTS Configuration
TTS_VOICE=en-US-AvaMultilingualNeural
TTS_RATE=+30%

# Bot Configuration
BOT_MIN_SPEECH_MS=150
BOT_VAD_SENSITIVITY=0
BOT_ASR_TIMEOUT_MS=2500

# Resource Limits
ASR_MEMORY_LIMIT=2G
LLM_MEMORY_LIMIT=4G
TTS_MEMORY_LIMIT=1G
BOT_MEMORY_LIMIT=512M
```

## Service Endpoints

| Service | URL | Description |
|---------|-----|-------------|
| ASR | http://localhost:6010 | Speech recognition |
| LLM (Groq) | http://localhost:6002 | Language model |
| LLM (Cerebras) | http://localhost:6003 | Alternative LLM |
| TTS | http://localhost:6011 | Text-to-speech |
| Bot-9092 | http://localhost:9092 | Voice agent 1 |
| Bot-9093 | http://localhost:9093 | Voice agent 2 |
| ... | ... | ... |
| Bot-9111 | http://localhost:9111 | Voice agent 20 |

## Production Checklist

- [ ] Create `.env` from `.env.example`
- [ ] Add `DEEPGRAM_API_KEY` to `.env`
- [ ] Add `GROQ_API_KEY` to `.env`
- [ ] Review resource limits for your server
- [ ] Run `./deploy.sh` or docker-compose command
- [ ] Verify all services are healthy
- [ ] Test health endpoints
- [ ] Monitor resource usage
- [ ] Check logs for errors
- [ ] Test bot connections
- [ ] Set up log rotation
- [ ] Configure monitoring/alerting
- [ ] Document any custom configuration

## Security Notes

- ✅ `.env` is in `.gitignore` - API keys won't be committed
- ✅ Use `.env.example` as template - contains no secrets
- ✅ Rotate API keys regularly
- ✅ Restrict network access to services
- ✅ Monitor for unauthorized access
- ✅ Keep Docker images updated

## Next Steps

1. **Monitor Performance**: Use `docker stats` to track resource usage
2. **Review Logs**: Check for any errors or warnings
3. **Optimize Resources**: Adjust limits based on actual usage
4. **Setup Monitoring**: Consider Prometheus/Grafana for metrics
5. **Backup Configuration**: Keep `.env` backed up securely
6. **Document Changes**: Update this file with any customizations

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Review documentation in `DOCKER_DEPLOYMENT_FIXES_SUMMARY.md`
3. Validate configuration: `docker-compose config`
4. Test health endpoints
