# Troubleshooting: Control 1.21 - Adversarial Input Logging

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Events not appearing | Audit delay | Wait 15-30 minutes |
| Sentinel rule not firing | Query syntax error | Validate KQL |
| High false positive rate | Pattern too broad | Refine detection patterns |
| Encoding not detected | Pattern mismatch | Update regex patterns |

---

## Detailed Troubleshooting

### Issue: Detection Events Not Appearing

**Symptoms:** Known adversarial input not logged

**Resolution:**

1. Verify audit logging is enabled
2. Check retention period includes timeframe
3. Verify Copilot activities are in scope
4. Wait 15-30 minutes for processing

---

### Issue: Too Many False Positives

**Symptoms:** Legitimate queries triggering alerts

**Resolution:**

1. Review triggered events to identify patterns
2. Add exclusions for legitimate use cases
3. Increase confidence threshold
4. Add context requirements to rules

---

## Escalation Path

1. **Security Operations** - Detection rules
2. **Security Administrator** - Sentinel configuration
3. **Compliance** - Evidence retention
4. **Microsoft Support** - Audit logging issues

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Audit delay 15-30 min | Not real-time | Use Sentinel for faster detection |
| Pattern matching only | May miss novel attacks | Regular pattern updates |
| No native blocking | Must integrate with other controls | Use DLP or CA for blocking |

---

[Back to Control 1.21](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
