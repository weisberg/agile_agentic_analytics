# Raw Source Storage

Raw source preservation makes KB facts auditable.

## Storage Decisions

| Source | Default |
| --- | --- |
| small markdown/text/json | store in repo under `sources/raw/` or page sidecar |
| small PDF | store under raw source path with hash |
| audio/video/image/large binary | store externally and commit redirect pointer |
| connector payload | redact, then store normalized envelope and raw pointer |

## Redirect Pointer

```yaml
target: storage://kb-files/page-slug/source.mp4
storage_path: page-slug/source.mp4
size: 524288000
hash: sha256:abc123
mime: video/mp4
uploaded: 2026-05-20T12:00:00Z
type: raw-source
privacy_scope: personal
```

## Rules

- Raw source links are cited from the KB page.
- Large binaries do not belong in plugin source.
- Hashes are recorded before and after upload/restore when possible.
- Redacted publication artifacts must point back to private raw sources only
  through safe metadata.

