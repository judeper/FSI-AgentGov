# Setup Scripts (Documentation Examples)

This folder is reserved for **setup / bootstrap examples** referenced by control documentation.

- Keep scripts **small, auditable, and parameterized**.
- Prefer **portal steps as primary** (stable for most teams); scripts are an optional accelerator.
- Store **no secrets** in this repo. Use managed identity, Key Vault, or your organization’s secret store.

## Suggested contents (to be added as controls are completed)
- Power Platform: environment bootstrap helpers
- Purview: baseline policy creation/export helpers
- Entra: baseline Conditional Access policy exports

## Evidence note
If you use a setup script in production, capture:
- the exact command invocation
- operator identity
- timestamp
- output/logs
as part of your control evidence package.
