# Lessons Learned

## AI Employee Vault Development

This document captures key learnings, insights, and best practices discovered during the development and operation of the AI Employee Vault system.

---

## Scalability Notes

### What Works Well

- ✅ **Modular architecture** - Each watcher operates independently
- ✅ **File-based queue** - `Needs_Action/` provides simple, visible task storage
- ✅ **Polling-based design** - Easy to understand and debug
- ✅ **OAuth persistence** - Token files maintain sessions across runs

### Bottlenecks Encountered

- ⚠️ **WhatsApp browser instance** - Running headless browser continuously consumes resources
- ⚠️ **Polling frequency** - Too frequent polling can trigger rate limits
- ⚠️ **File system I/O** - Large numbers of markdown files may slow directory operations

### Recommendations for Scale

1. **Database migration** - Consider SQLite for high-volume message storage
2. **Message queue** - Redis or RabbitMQ for production workloads
3. **Containerization** - Docker for consistent deployment
4. **Horizontal scaling** - Run watchers on separate machines/containers

---

## Error Recovery Lessons

### Gmail Watcher

| Issue | Solution |
|-------|----------|
| Token expiration | Delete `token.json` and re-authenticate |
| API quota exceeded | Increase poll interval from 60s to 120s+ |
| Credential errors | Verify `credentials.json` is valid |

### WhatsApp Watcher

| Issue | Solution |
|-------|----------|
| Session expired | Re-scan QR code on WhatsApp Web |
| Messages not detected | Increase wait time for page load |
| Browser crashes | Use persistent user data directory |

### Social Posters (Gold Tier)

| Issue | Solution |
|-------|----------|
| Rate limit hit | Respect `RATE_LIMIT_POSTS_PER_DAY` |
| API changes | Use simulation mode during testing |
| Failed posts | Implement retry logic with backoff |

### General Patterns

```python
# Retry pattern that works:
for attempt in range(1, max_retries + 1):
    try:
        result = operation()
        break
    except Exception as e:
        if attempt == max_retries:
            raise
        time.sleep(delay * attempt)  # Exponential backoff
```

---

## Security Considerations

### Credentials Management

- ✅ **DO**: Store API keys in `.env` file
- ✅ **DO**: Add `.env` to `.gitignore`
- ✅ **DO**: Use OAuth 2.0 where available
- ❌ **DON'T**: Hardcode credentials in source files
- ❌ **DON'T**: Commit tokens to version control

### Session Security

- WhatsApp session data stored in `whatsapp_session/`
- Gmail tokens stored in `token.json`
- Consider encrypting sensitive session files
- Regularly rotate OAuth credentials

### Rate Limiting

- Implement client-side rate limiting
- Respect API rate limits to avoid bans
- Use `SIMULATE_SOCIAL=true` for testing
- Log all API calls for audit trail

### Input Validation

- Validate content length before posting (X: 280 chars)
- Sanitize user input in markdown files
- Escape special characters in API calls

---

## Operational Best Practices

### Monitoring

1. Check `Logs/` directory regularly
2. Monitor `social.json` for post history
3. Review `Needs_Action/` queue depth
4. Set up alerts for failed operations

### Maintenance

- Weekly: Review and archive processed items
- Monthly: Rotate API credentials
- Quarterly: Review rate limits and adjust
- As needed: Update dependencies

### Testing

```powershell
# Test in simulation mode first
$env:SIMULATE_SOCIAL="true"
python Social\facebook_poster.py

# Then enable for real
$env:SIMULATE_SOCIAL="false"
```

---

## Design Decisions

### Why File-Based Queue?

- **Pros**: Simple, visible, no database required, easy debugging
- **Cons**: Not ideal for high volume, no built-in ordering
- **Verdict**: Perfect for MVP and moderate workloads

### Why Polling Instead of Webhooks?

- **Pros**: Simpler implementation, works with all platforms
- **Cons**: Higher latency, more API calls
- **Verdict**: Trade-off acceptable for current scale

### Why Simulation Mode?

- **Pros**: Safe testing, no accidental posts, development friendly
- **Cons**: Doesn't test actual API integration
- **Verdict**: Essential for confident deployments

---

## Future Improvements

### Short Term
- [ ] Add webhook support for Gmail (push notifications)
- [ ] Implement post scheduling system
- [ ] Add engagement metrics tracking
- [ ] Create dashboard for monitoring

### Medium Term
- [ ] Database backend option (SQLite/PostgreSQL)
- [ ] Multi-account support for social posters
- [ ] Image/media upload support
- [ ] Analytics and reporting module

### Long Term
- [ ] AI-powered content generation
- [ ] Cross-platform post optimization
- [ ] Natural language task processing
- [ ] Full MCP server implementation

---

## Contributing

When adding new features:

1. Document lessons in this file
2. Update `architecture.md` if structure changes
3. Add tests for new functionality
4. Update `README.md` with new commands

---

*Last Updated: February 22, 2026*
*Version: Gold Tier v1.0*
